import os
import json
from collecting import *
from ranking import *
from collecting import *
from helpers import Searcher, Post, load_post


def main():
    print("----------------------")
    print("main() function called")
    
    posts = []
    
    with open("filtered-posts.txt", "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        objs = [json.loads(line) for line in lines]
        # can not set obj here. Will all be pointer to the same variable
        posts = [load_post(obj) for obj in objs]
    
    # This is an account I made for this task
    username = "entityNoticing"
    password = "x!0123456789"
    searcher = Searcher(username, password)
    subreddits = ["chatgptpro", "machinelearning",  "gpt_4", "gpt3","deeplearning", "aipromptprogramming", "chatgpt", "chatgptcoding", "openai"]

    for post in posts:
        searcher.vis.add(post.url)
    
    posts = collect(subreddits, searcher)

    # Ranking the posts
    entity_counts = obtain_entity_counts(posts)
    rankings1, rankings2 = rank(entity_counts)

    with open("rankings1.txt", "w+") as f:
        f.write("Entity,WeeksMentioned\n")
        for e, wm in rankings1:
            f.write(e + "," + str(wm) + "\n")
    with open("rankings2.txt", "w+") as f:
        f.write("Entity,WeeklyGrowth\n")
        for e, wg in rankings2:
            f.write(e + "," + str(wg) + "\n")
    return


if __name__ == "__main__":
    main()