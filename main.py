import os
import json
from collecting import *
from ranking import *
from collecting import *
from helpers import Searcher, Post, load_post


def get_idx(e, rs):
    for i, r in enumerate(rs):
        if r[0] == e:
            return i
    return -1

def main():
    print("----------------------")
    print("main() function called")
    
    
    posts = []
    
    with open("posts.txt", "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        objs = [json.loads(line) for line in lines]
        # can not set obj here. Will all be pointer to the same variable
        posts = [load_post(obj) for obj in objs]
    
    # This is an account I made for this task
    username = "entityNoticing"
    password = "x!0123456789"
    searcher = Searcher(username, password)
    subreddits = ["deeplearning", "chatgptpro", "aipromptprogramming", "machinelearning",  "gpt_4", "gpt3", "chatgpt", "chatgptcoding", "openai"]

    for post in posts:
        searcher.vis.add(post.url)
        

    
    posts = collect(subreddits, searcher)

    # Ranking the posts
    entity_counts = obtain_entity_counts(posts)
    rankings1, rankings2 = rank(entity_counts)

    with open("rankings.txt", "w+") as f:
        f.write("Entity,MentionsRank,GrowthRank\n")
        for e in entity_counts:
            rank_1 = get_idx(e, rankings1)
            rank_2 = get_idx(e, rankings2)
            items = [e, str(rank_1), str(rank_2)]
            f.write(",".join(items) + "\n")
    return


if __name__ == "__main__":
    main()