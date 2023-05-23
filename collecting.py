import re
import requests
import time
from bs4 import BeautifulSoup


def get_posts(subreddit, searcher):
    subredditURL = "https://www.reddit.com/r/" + subreddit + "/new/"
    searcher.driver.get(subredditURL)
    posts = searcher.get_subreddit_posts(subreddit, subredditURL)
    return posts


def collect(subreddits, searcher):
    posts = []
    for subreddit in subreddits:
        posts += get_posts(subreddit, searcher)
    return posts

