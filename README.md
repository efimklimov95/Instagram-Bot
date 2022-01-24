### What is it?

Multi-purpose Instagram bot that emulates user actions to like posts, search through lists of followers/followings of given profiles, and more.

### Requirements

-   `selenium`

### Getting Started

To get started:

-   Download chrome driver from https://chromedriver.chromium.org/ for your OS. Make sure it matches your Chrome version.
-   Put your username, password, and username of a target profile (e.g. to search through someone else's followings list) in the config file.
-   Run chrome_runner.py with appropriate parameters.  
    `python chrome_runner.py -h` for help

You can easily change the bot to use any driver supported by selenium, just change the options object to match parameters to a driver of your choice.

### Component description

-   [Runner](chrome_runner.py): configures webdriver, reads config, and calls bot’s functions depending on given arguments.
-   [Bot](bot.py): the core code that will interact with pages through webdriver.
-   [Parser](post_parser.py): code for parsing explore content, individual posts, and any other data. Transforms data into Python primitives.
-   [Filter](filter.py): determines whether the bot should like a post if it satisfies certain criteria.
-   [Tracker](tracker.py): tracks what posts bot liked, how many it liked/skipped, and other stats.
-   [Strategy](strategy.py): defines when the bot should stop running or maybe it should never stop.
