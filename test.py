import requests
from lxml import html
import pandas as pd
import asyncio
import subprocess, json

async def get_data(url):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    element = tree.xpath('//*[@id="content"]/div[7]/div/div/h1')[0]
    text = element.text
    return text

import re

def extract_nota_id(script_text):
    match = re.search(r'"nota_id":\s*"([^"]+)"', script_text)
    if match:
        return match.group(1)
    else:
        return None

def extract_comments(comment_id,last_comment=None):
    url = f'https://livecomments.viafoura.co/v4/livecomments/00000000-0000-4000-8000-5611d514abb3?limit=100&container_id={comment_id}&reply_limit=3&sorted_by=newest'
    if last_comment:
        url += f'&starting_from={last_comment}'
    response = requests.get(url)
    response = response.json()
    comments = dict()
    for comment in response.get('contents'):
        comments[comment.get("content_uuid")] = {
            "comment": comment.get("content"),
            'time': comment.get("date_created"),
            "total_likes": comment.get("total_likes"),
            "total_dislikes": comment.get("total_dislikes"),
            "total_replies": comment.get("total_replies"),
            "is_actor_ghostbanned": comment.get("is_actor_ghostbanned"),
        }
        if comment.get("is_actor_ghostbanned"):
            print(comment.get("content_uuid"))
    if len(comments) == 100:
        comments.update(extract_comments(comment_id,comment.get("content_uuid")))
    return comments


url = "https://www.lanacion.com.ar/politica/el-presidente-se-reunio-con-empresarios-de-china-y-genero-inquietud-en-estados-unidos-nid16052023/"

response = requests.get(url)
tree = html.fromstring(response.content)

# Use the provided XPath expression to find the desired table element
table_element = tree.xpath("/html/head/script[4]")[0]

# Convert the table element to a string and read it into a DataFrame
table_html = html.tostring(table_element)

# Display the resulting DataFrame
with open('arch.json','w') as f:
    comments = extract_comments(extract_nota_id(table_html.decode("utf-8")))
    print(len(comments))
    json.dump(comments,f)


