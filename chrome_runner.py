import pathlib
import sys
import getopt

from selenium import webdriver

import config
from bot import AutoLikeBot
from filter import MyCustomFilter
from strategy import RunForeverWithBreaks


def configure_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={pathlib.Path(__file__).parent.absolute().joinpath('chrome-profile')}")

    # disable image loading for better performance
    # options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

    the_driver = webdriver.Chrome(executable_path=config.DRIVER_EXECUTABLE_PATH, options=options)

    # page loading time and wait time for page reload
    the_driver.set_page_load_timeout(5)
    the_driver.implicitly_wait(2)
    return the_driver


def main(argv):
    with AutoLikeBot(configure_chrome_driver(),
                     post_filter=MyCustomFilter(ignore_tags=config.IGNORE_TAGS),
                     running_strategy=RunForeverWithBreaks(200)) as bot:

        try:
            opts, args = getopt.getopt(argv,"helfp",["help","like_explore", "like_followings", "list_followings", "like_profile"])
        except getopt.GetoptError:
            print('chrome_runner.py [-h, --like_explore, --like_followings, --list_followings, --like_profile]')
            sys.exit(2)

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print('chrome_runner.py [-h, --like_explore, --like_followings, --list_followings, --like_profile')
                sys.exit()
            elif opt in ('-e', '--like_explore'):
                # Likes on random posts from Explore
                bot.like_from_explore()
            elif opt in ('-l', '--like_followings'):
                # Like every post from the list of people I follow
                bot.like_followings_list()
            elif opt in ('-f', '--list_followings'):
                # List all followings of the given profile (writes them into a text file)
                bot.list_all_followings()
            elif opt in ('-p', '--like_profile'):
                # Like all posts on given profile
                bot.like_all_posts_on_profile(config.TARGET_USERNAME)


if __name__ == '__main__':
    main(sys.argv[1:])
