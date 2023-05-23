import os
import json
from ranking import *
from helpers import Post, load_post

"""

objs = []
with open("posts.txt", "r") as f:
    lines = f.readlines()
    lines = [l.strip() for l in lines]
    objs = [json.loads(line) for line in lines]
    for i, o in enumerate(objs):
        if "weeks_ago" not in o:
            print(i, o["url"])
        else:
            print("-------------------")
    # can not set obj here. Will all be pointer to the same variable
posts = [load_post(obj) for obj in objs]
###########
print(posts)

rank(posts)

"""













