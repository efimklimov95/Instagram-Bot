import logging
import random
from time import sleep

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

import config
from filter import PostFilter
from post_parser import parse_explore
from strategy import RunForeverStrategy
from tracker import post_tracker
from utils import rand_wait_sec

logging.basicConfig(handlers=[logging.StreamHandler()],
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname).4s] %(message)s',
                    datefmt='%a %d %H:%M:%S')

logger = logging.getLogger()


class AutoLikeBot:
    def __init__(self, driver: WebDriver, post_filter=PostFilter(), running_strategy=RunForeverStrategy()):
        self.driver = driver
        self.post_filter = post_filter
        self.running_strategy = running_strategy

    def __enter__(self):
        if not config.SKIP_LOGIN:
            self.log_in()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()
        logger.info(post_tracker.stats)
        return None

    def like_from_explore(self):
        max_id = 0

        while True:
            try:
                posts = self.fetch_posts_from_explore(max_id)
            except TimeoutException:
                continue
            random.shuffle(posts)
            for post in posts:
                if self.post_filter.should_like(post):
                    self.like_post(post)

                    if not self.running_strategy.should_continue_run():
                        return
                else:
                    post_tracker.skipped_post(post)

            max_id += 1

    def log_in(self):
        self.driver.get("https://www.instagram.com/")
        try:
            self.wait_until(ec.presence_of_element_located((By.NAME, 'username')))

            try:
                self.driver.find_element_by_name('username').send_keys(config.USERNAME)
                self.driver.find_element_by_name('password').send_keys(config.PASSWORD)
                self.driver.find_element_by_xpath(
                    '//*[@id="react-root"]/section/main/article/div[2]/div[1]/div/form/div/div[4]/button').click()

            except NoSuchElementException as e:
                logger.warning(f"Could not find element. Error: {e}")
                return

        except TimeoutException:
            pass

        try:
            # remember this browser prompt
            self.driver.find_element_by_xpath(
                '//*[@id="react-root"]/section/main/div/div/div/section/div/button').click()
        except NoSuchElementException:
            pass

        try:
            # turn on notifications prompt
            self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div/div[3]/button[2]").click()
            logger.debug("Skipping turn on notifications")
        except NoSuchElementException:
            pass

        self.wait_until(ec.presence_of_element_located((By.CLASS_NAME, 'C3uDN')))

    def fetch_posts_from_explore(self, max_id=0):
        text = self.load_pre_from_url(
            f"https://www.instagram.com/explore/grid/?is_prefetch=false&omit_cover_media=false&module=explore_popular&use_sectional_payload=true&cluster_id=explore_all%3A0&include_fixed_destinations=true&max_id={max_id}")
        return parse_explore(text)

    def load_pre_from_url(self, url):
        self.open_and_switch_to_tab(url)
        try:
            self.wait_until(ec.presence_of_element_located((By.TAG_NAME, 'pre')), timeout=7)
            return self.driver.find_element_by_tag_name('pre').text
        finally:
            self.close_and_open_tab()

    def open_and_switch_to_tab(self, url):
        handles = self.driver.window_handles
        self.driver.execute_script(f"window.open('{url}');")
        # index based
        self.driver.switch_to.window(self.driver.window_handles[len(handles)])

    def close_and_open_tab(self, tab_index=0):
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def like_post(self, post):

        self.open_and_switch_to_tab(post.post_link)
        try:
            self.wait_until(ec.presence_of_element_located((By.CLASS_NAME, 'fr66n')))
            self.driver.find_element_by_class_name('fr66n').click()
            post_tracker.liked_post(post)
            logger.info(f"Liked {post}")
            rand_wait_sec()
            return True

        # post might get removed
        except (NoSuchElementException, TimeoutException):
            return False
        finally:
            self.close_and_open_tab()

    def like_post_by_link(self, post_link):

        self.open_and_switch_to_tab(post_link)
        try:
            self.wait_until(ec.presence_of_element_located((By.CLASS_NAME, 'fr66n')))
            self.driver.find_element_by_class_name('fr66n').click()
            logger.info(f"Liked {post_link}")
            rand_wait_sec()
            return True

        # post might get removed
        except (NoSuchElementException, TimeoutException):
            return False
        finally:
            self.close_and_open_tab()

    def like_following_list(self):
        following_list = self.fetch_following_list()

        for following in following_list:
            try:
                userurl = f"https://www.instagram.com/{following}/"
                post_links = self.fetch_posts_links_from_profile(userurl)
            except TimeoutException:
                continue

            print("Post Links")
            i = 1
            for link in post_links:
                print(f"{i}.    {link}")
                i += 1
                self.like_post_by_link(link)


    def fetch_following_list(self):
        following_list = []

        self.driver.get(config.USER_LINK)

        self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div[1]/header/section/ul/li[3]/a').click()
        self.wait_until(ec.presence_of_element_located((By.CLASS_NAME, 'PZuss')), timeout=7)

        following_list_webelement = self.driver.find_element_by_class_name('PZuss')

        self.wait_until(ec.presence_of_element_located((By.CLASS_NAME, 'FPmhX')), timeout=7)
        following_list_subwebelement = following_list_webelement.find_elements_by_class_name('FPmhX')

        for following in following_list_subwebelement:
            following_list.append(following.text)

        return following_list

    def fetch_posts_links_from_profile(self, userurl):
        self.open_and_switch_to_tab(userurl)
        post_links_list = set()

        try:
            self.wait_until(ec.presence_of_element_located((By.CLASS_NAME, 'v1Nh3')), timeout=7)
            # Scroll the page down to the bottom so all posts appear in DOM
            scrolldown = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
            match = False
            while(match==False):
                try:
                    last_count = scrolldown
                    sleep(3)
                    scrolldown = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var scrolldown=document.body.scrollHeight;return scrolldown;")
                    if last_count==scrolldown:
                        match=True

                    self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                    posts = self.driver.find_elements_by_class_name('v1Nh3')

                    for post in posts:
                        post_link = post.find_element_by_xpath('.//a')
                        post_links_list.add(post_link.get_attribute('href'))

                except Exception as e:
                    print(type(e))    # the exception instance
                    print(e.args)     # arguments stored in .args
                    print(e)          # __str__ allows args to be printed directly,
                                      # but may be overridden in exception subclasses
                    pass
        except Exception as e:
            print(type(e))    # the exception instance
            print(e.args)     # arguments stored in .args
            print(e)          # __str__ allows args to be printed directly,
                              # but may be overridden in exception subclasses
            return post_links_list
        finally:
            self.close_and_open_tab()
        return post_links_list

    def wait_until(self, condition, timeout=5):
        WebDriverWait(self.driver, timeout).until(condition)
