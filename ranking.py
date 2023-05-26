import re
import time
import string
import numpy as np
from datetime import datetime


DEFAULT_KEYWORDS = [
    "OpenAI",
    "ChatGPT",
    "GPT 4",
    "GPT 3",
    "GPT4",
    "GPT3",
    "AGI",
    "AutoGPT",
    "ML",
    "DL",
    "NN",
    "NLP",
    "NLP",
    "RL",
    "CV",
    "DS",
    "Robotics",
    "Automation",
    "Algorithm",
    "Predictive Analytics",
    "Image Recognition",
    "Speech Recognition",
    "Sentiment Analysis",
    "Virtual Assistant",
    "Chatbot",
    "Recommendation Systems",
    "Decision Trees",
    "Data Mining",
    "Pattern Recognition",
    "Autonomous Vehicles",
    "Expert Systems",
    "Knowledge Representation",
    "Computer Graphics",
    "Cognitive Computing"
]

AVOID = list(["if", "we", "and", "but", "then", "of", "for", "in", "when", "what", "why", "who", "is", "at", "because", "from", "stand", "paying", "that", "open", "scale", "some"])
AVOID += [letter for letter in string.ascii_lowercase]
AVOID = set(AVOID)


common_words = [
"the",
"of",
"and",
"to",
"in",
"is",
"you",
"that",
"it",
"he",
"was",
"for",
"on",
"are",
"as",
"with",
"his",
"they",
"at",
"be",
"this",
"from",
"have",
"or",
"by",
"one",
"had",
"not",
"but",
"what",
"all",
"were",
"we",
"when",
"your",
"can",
"said",
"there",
"use",
"an",
"each",
"which",
"she",
"do",
"how",
"their",
"if",
"will",
"up",
"other",
"about",
"out",
"many",
"then",
"them",
"these",
"so",
"some",
"her",
"would",
"make",
"like",
"him",
"into",
"time",
"has",
"look",
"two",
"more",
"write",
"go",
"see",
"number",
"no",
"way",
"could",
"people",
"my",
"than",
"first",
"water",
"been",
"call",
"who",
"oil",
"its",
"now",
"find",
"long",
"down",
"day",
"did",
"get",
"come",
"made",
"may",
"part"
]

common_words += [s.capitalize() for s in common_words]


def ends_in_common(s):
    for word in common_words:
        if s == s[:len(s)-len(word)] + word:
            return True
    return False


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
        if not post.date:
            continue
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
    raw_entities = get_entities(posts)
    raw_entities = [s for s in raw_entities if s and s.lower() not in AVOID and not ends_in_common(s)]
    raw_entities += DEFAULT_KEYWORDS

    entities = []
    # Number of weekly mentions for each entity
    for i in range(len(raw_entities)):
        add = True
        curr = raw_entities[i].lower()
        for j in range(len(raw_entities)):
            if i != j:
                if curr.find(raw_entities[j].lower()) == 0:
                    add = False
                    break
        if add:
            entities.append(raw_entities[i])

    entities = raw_entities

    entity_counts = get_entity_counts(posts, entities)

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
    stat2 = list(map(list, stat2))
    return stat1, stat2
    
    


