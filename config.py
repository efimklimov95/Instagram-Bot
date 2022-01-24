import pathlib

USERNAME = ''  # Instagram account

PASSWORD = ''  # Instagram password

# Executable path for chrome driver
DRIVER_EXECUTABLE_PATH = pathlib.Path(__file__).parent.absolute().joinpath("chromedriver")

IGNORE_TAGS = []  # Exact case non sensitive matching

SKIP_LOGIN = False  # Skip log in flow. Useful if you have profile with cookies saved

# Username of a target profile
TARGET_USERNAME = ''