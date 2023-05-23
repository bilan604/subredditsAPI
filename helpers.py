import re
import time
import random
import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
#import tracemalloc
#tracemalloc.start()


class Post(object):
    def __init__(self, url=""):
        self.url = url
        self.date = ""
        self.title = ""
        self.content = ""
        self.comments = []
        self.weeks_ago = -1
        self.subreddit = ""
        self.author = ""  # unused
    
    def to_dict(self):
        post_dict = {
            "url": self.url,
            "date": self.date,
            "title": self.title,
            "content": self.content,
            "comments": self.comments,
            "author": self.author,
            "weeks_ago": self.weeks_ago,
            "subreddit": self.subreddit
        }
        return post_dict

def load_post(obj):
    post = Post(obj["url"])
    post.date = obj["date"]
    post.title = obj["title"]
    post.content = obj["content"]
    post.comments = obj["comments"]
    post.author = obj["author"]
    post.weeks_ago = obj["weeks_ago"]
    post.subreddit = obj["subreddit"]
    return post
    

class Searcher(object):
    
    def __init__(self, username, password):
        self.driver = webdriver.Chrome(executable_path="chromedriver.exe")
        self.subreddit_posts = {}
        self.vis = set({})
        self.finished = set({})
        self.initialize(username, password)

    def initialize(self, username, password):
        loginURL = "https://www.reddit.com/login/?dest=https%3A%2F%2Fwww.reddit.com%2F"
        self.driver.get(loginURL)
        self.get_waited("//input[@id='loginUsername']").send_keys(username)
        self.get_waited("//input[@id='loginPassword']").send_keys(password)
        self.get_waited("//button[@class='AnimatedForm__submitButton m-full-width']").click()
        time.sleep(4)
        return
        
    def get_waited(self, xpath):
        return WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, xpath)))
    
    def filter_tags(self, s):
        inTag = False
        currString = ""
        response = []
        for letter in s:
            if letter == "<":
                inTag = True
                if currString:
                    response.append(currString)
                currString = ""
            elif letter == ">":
                inTag = False
            else:
                if not inTag:
                    currString += letter
        if currString:
            response += currString
        
        return "".join(response)

    def get_nontags(self, s):
        return re.sub("<.+?>", "", s).strip()

    def get_texts(self, property, args={}):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        if args:
            tags = soup.find_all(property, args)
        else:
            tags = soup.find_all(property)
        texts = [self.get_nontags(str(tag)) for tag in tags]
        return texts


    def extract_property_values(self, property, tags):
        property_values = []
        for tag in tags:
            if type(tag) != str:
                tag = str(tag)
            lst = tag.split(property+"=")
            if len(lst) == 1:
                continue
            value = "".join(lst[1:])
            value = value[1:]
            value = value[:value.index("\"")]
            property_values.append(value)
        return property_values


    def filter_by_contains_property(self, property_names, tags):
        filtered_tags = []
        for tag in tags:
            if type(tag) != str:
                tag = str(tag)
            matching_properties = 0
            property_values = tag.split(" ")
            for property_value in property_values:
                if "=" not in property_value:
                    continue
                if property_value.split("=")[0] in property_names:
                    matching_properties += 1
            if matching_properties == len(property_names):
                filtered_tags.append(tag)
        return filtered_tags        

    def get_similar_questions(self, soup):
        similar_questions = soup.find_all("span", {"class": "CSkcDe"})
        similar_questions = list(map(str, similar_questions))
        similar_questions = list(map(self.filter_tags, similar_questions))
        return similar_questions

    def get_answers(self, soup):
        answers = soup.find_all("span", {"class": "hgKElc"})
        answers = list(map(str, answers))
        answers = list(map(self.filter_tags, answers))
        return answers

    def fill_post(self, post, postURL=""):
        if not postURL:
            postURL = post.url
        print("filling post:", postURL)

        self.driver.get(postURL)
        date_item = self.get_waited("//span[@data-testid='post_timestamp']").text   
        date_item = date_item.strip()
        print(f" {str(date_item)=} ")

        current_date = datetime.now().date()
        # Subtract x days
        if "hours" in date_item:
            days_ago_str = "0"
        elif "days" in date_item:
            days_ago_str = date_item[:date_item.index(" ")]
        elif "weeks" in date_item:
            days_ago_str = str(int(date_item[:date_item.index(" ")]) * 7)
        elif "months" in date_item:
            days_ago_str = str(int(date_item[:date_item.index(" ")]) * 30)
        else:
            days_ago_str = None

        if days_ago_str:
            x = int(days_ago_str) # Number of days to subtract
            post.weeks_ago = x // 7
            post_date = current_date - timedelta(days=x)
            year = str(post_date.year)
            month = str(post_date.month).zfill(2)  # zfill adds leading zeros if necessary
            day = str(post_date.day).zfill(2)
            post_date_string = "-".join([year, month, day])
            post.date = post_date_string
            print(f"{post.date=} {post.weeks_ago}\n")

        # Note, returns a list but will be length 1
        titles = self.get_texts("h1")
        if titles:
            post.title = titles[0]
        
        # Load comments
        prev = 0
        for __load_results__ in range(6):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Check if anything new has loaded
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            ps = [str(p) for p in soup.find_all("p")]
            if len(ps) == prev:
                break
            else:
                prev = len(ps)

        ps = self.get_texts("p")
        if not ps:
            print("no <p> tags found!", postURL)
            return post
        if ps[0].strip() == "no comments yet":
            return ps
        
        for i in range(1, len(ps)):
            post.comments.append(ps[i])

        return post


    def get_subreddit_posts(self, subreddit, subredditURL):
        if subreddit in self.finished:
            return []
        
        # Get the subreddit's post's links
        subreddit_post_links = []
        
        # Load the posts.
        for __load_results__ in range(6000):
            # Wait for the page to load and the new search results to appear
            time.sleep(1)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        time.sleep(10)
        
        

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        anchor_tags = soup.find_all('a')
        anchor_tags = self.filter_by_contains_property(["href"], anchor_tags)
        subreddit_post_links += self.extract_property_values("href", anchor_tags)

        # Filter the links
        target = "/r/"+subreddit+"/comments/"
        postURLs = [url for url in subreddit_post_links if target.lower() in url.lower()]
        postURLs = [url for url in postURLs]
        for i in range(len(postURLs)):
            if "www.reddit.com" not in postURLs[i]:
                postURLs[i] = "https://www.reddit.com" + postURLs[i]
        
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(len(subreddit_post_links))
        print(f"{subreddit_post_links[0]=}\n")
        print(f"{subreddit_post_links[-1]=}\n")

        posts = []
        for postURL in postURLs:
            if postURL not in self.vis:
                self.vis.add(postURL)
            else:
                print("skipping", postURL)
                continue
            post = Post(postURL)
            # Collect data for the post
            try:
                self.fill_post(post)
                if post.weeks_ago >= 52:
                    self.finished.add(subreddit)
                post.subreddit = subreddit
                posts.append(post)

                # Save the data (I'm using a local cache)
                with open("posts.txt", "a") as f:
                    obj = post.to_dict()
                    s = json.dumps(obj)
                    f.write(s+"\n")
            # Due to the request not responding
            except Exception as e:
                print(e)
        # Optionally Memoize it
        self.subreddit_posts[subreddit] = posts
        return posts
