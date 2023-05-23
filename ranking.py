import re
import time
import string
import numpy as np
from datetime import datetime



def calculate_days_ago(date_str):
    current_date = datetime.now().date()
    given_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    days_ago = (current_date - given_date).days
    return days_ago


def filter_spacing(s):
    s = re.sub(" +", " ", s)
    s = s.strip()
    return s


def get_phrases(s):
    s = re.sub("\n", ". ", s)
    s = re.sub("[_|-|,|\\|\\//]", " ", s)
    s = re.sub("[\'|\"|?|-|\']", "", s)
    lst = s.split(". ")
    lst = [s.strip() for s in lst if len(s) > 2]
    lst = [filter_spacing(s) for s in lst]
    
    # decapitalize
    lst = [s[0].lower() + s[1:] for s in lst]
    return lst


def countLU(s):
    l,u = 0,0
    for ltr in s:
        if ltr == ltr.lower():
            l += 1
        else:
            u += 1
    return l,u


def get_entities(posts):
    entities = set({})
    alphabet = string.ascii_lowercase
    text = ""
    for post in posts:
        text += post.content
        for comment in post.comments:
            text += comment
    
    
    phrases = get_phrases(text)
    for i in range(len(phrases)):
        tokens = phrases[i].split(" ")
        for token in tokens:
            if token.find("(link)") == 0:
                entity = re.sub("\(.+?\)", "", token)
                entities.add(entity)
                continue

            l,u = countLU(token)
            if l > 1 and u > 1 and all([letter in alphabet for letter in token.lower()]):
                entities.add(token)
    entities = list(entities)
    return entities


def get_entity_counts(posts, entities: list[str]):
    # Use this allow lowercase matching
    names = {entity.lower(): entity for entity in entities}

    entity_counts = {entity: [0] * 100 for entity in entities}
    for post in posts:
        weeksAgo = calculate_days_ago(post.date) // 7
        if weeksAgo > 4:
            continue
        s = post.content + "\n"
        for comment in post.comments:
            s += comment
        s = s.lower()
        for word in s.split(" "):
            if word in names:
                entity_counts[names[word]][weeksAgo] += 1
    return entity_counts


def obtain_entity_counts(posts: list=[]):
    # strings that can be considered entities
    entities = get_entities(posts)
    # Number of weekly mentions for each entity
    entity_counts = get_entity_counts(posts, entities)
    print(entity_counts)
    return entity_counts
    

def rank(entity_counts):

    def get_stat2(entities):
        stat2 = []
        for e in entities:
            growth = []
            for i in range(1, 5):
                stat = (entities[e][i] - entities[e][i-1]) / entities[e][i-1]
                growth.append(stat)
            stat2.append([e, sum(growth)/len(growth)])
        return stat2


    mentioned = lambda x: all([xi >= 2 for xi in x])
    count_mentions = lambda x: len([xi for xi in x if xi >= 2])
    # filter them
    entities = {e: entity_counts[e] for e in entity_counts if mentioned(entity_counts[e][:4])}

    # number of weeks with at least 2 mentions
    stat1 = {e: count_mentions(entities[e][:52]) for e in entities}
    stat1 = sorted(stat1.items(), key=lambda x: x[1], reverse=True)

    # avg growth
    stat2 = get_stat2(entities)
    stat2 = sorted(stat2, key=lambda x: x[1], reverse=True)
    return stat1, stat2
    
    


