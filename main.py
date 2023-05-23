from __future__ import print_function
import os
import json
import asyncio
from collecting import *
from ranking import *
from sheets import *
from helpers import Searcher, Post, load_post
import tracemalloc
tracemalloc.start()



def get_mtx(rankings1, rankings2):
    colNames = ["Entity","MentionsRank","GrowthRank"]
    mtx = [colNames]
    for e in entity_counts:
        rank_1 = get_idx(e, rankings1)
        rank_2 = get_idx(e, rankings2)
        mtx.append([e, str(rank_1), str(rank_2)])
    return mtx


async def main():
    print("----------------------")
    print("main() function called")
    
    posts = []
    
    with open("posts.txt", "r") as f:
        lines = f.readlines()
        lines = [l.strip() for l in lines]
        objs = [json.loads(line) for line in lines]
        posts = [load_post(obj) for obj in objs]
    
    # This is an account I made for this task
    username = "entityNoticing"
    password = "x!0123456789"
    searcher = Searcher(username, password)
    subreddits = ["gpt_4", "gpt3", "chatgpt", "chatgptpro", "aipromptprogramming", "machinelearning", "deeplearning", "chatgptcoding", "openai"]

    for post in posts:
        searcher.vis.add(post.url)

    ##########
    posts = collect(subreddits, searcher)

    # Ranking the posts
    entity_counts = obtain_entity_counts(posts)
    rankings1, rankings2 = rank(entity_counts)

       
    client = await asyncio.create_task(get_authorized_client())
    # get the instance of the Spreadsheet
    sheet = client.open('RedditAPI')
    print(sheet)
    # get the first sheet of the Spreadsheet
    sheet_instance = await asyncio.create_task(get_sheet_instance(sheet, 2))
    
    # Saving data
    objs = []
    with open("posts.txt", "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line:
                objs.append(json.loads(line))

    cols = list(objs[0].keys())
    for i, col in enumerate(cols):
        sheet_instance.update_cell(1, i+1, col)
        for row in range(len(objs)):
            sheet_instance.update_cell(row+2, i+1, objs[row][col])
    
    # updating
    mtx = get_mtx(rankings1, rankings2)
    rankings_sheet = await asyncio.create_task(get_sheet_instance(sheet, 2))
    rankings_sheet = make_sheet(rankings_sheet, mtx)
    return


if __name__ == "__main__":
    asyncio.run(main())
