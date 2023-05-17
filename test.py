
from lxml import html
import pandas as pd
import asyncio, aiohttp 
import subprocess, json
import re

async def extract_nota_id(script_text):
    match = re.search(r'"nota_id":\s*"([^"]+)"', script_text)
    if match:
        return match.group(1)
    else:
        return None

async def get_redirected_url_async(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return str(response.url)

async def extract_comments(session, comment_id, last_comment=None, context_uuid=None):
    url = 'https://livecomments.viafoura.co/v4/livecomments/00000000-0000-4000-8000-5611d514abb3'
    if context_uuid:
        url += f'/{context_uuid}/comments'
    url += f'?limit=100&container_id={comment_id}&reply_limit=100&sorted_by=newest'
    if last_comment:
        url += f'&starting_from={last_comment}'
    print(url)
    async with session.get(url) as response:
        response_json = await response.json()
    comments = dict()
    uuid = None
    try:
        for comment in response_json.get('contents'):
            if not uuid or uuid == last_comment or uuid != comment.get('content_container_uuid'):
                uuid = comment.get("content_uuid")
            comments[comment.get("content_uuid")] = {
                "comment": comment.get("content"),
                'time': comment.get("date_created"),
                "total_likes": comment.get("total_likes"),
                "total_dislikes": comment.get("total_dislikes"),
                "total_replies": comment.get("total_replies"),
                "is_actor_ghostbanned": comment.get("is_actor_ghostbanned"),
            }
            #print(comment.get("content_uuid"),comment.get("actor_uuid"))
            if comment.get("is_actor_ghostbanned"):
                print(comment.get("content_uuid"))
        if len(comments) >= 50 and uuid != last_comment:
            print(len(comments))
            new_comments = await extract_comments(session, comment_id, last_comment=uuid,context_uuid= comment.get('content_container_uuid'))
            comments.update(new_comments)
    except TypeError:
        comments = response_json
    return comments


async def get_info(session, url:str):
    url = await get_redirected_url_async(url)
    print(url)
    async with session.get(url) as response:
        response_text = await response.text()
    tree = html.fromstring(response_text)
    table_element = tree.xpath("/html/head/script[4]")[0]
    table_html = html.tostring(table_element).decode("utf-8")
    title = url.split('/')
    title = title[len(title)-2]
    print(title)
    comments = await extract_comments(session,await extract_nota_id(table_html))
    print(len(comments))
    
    with open(f"{title}.json","w") as f:
        json.dump(comments,f)


async def main():
    urls = [
            "https://lanacion.com.ar/2754655"]

    async with aiohttp.ClientSession() as session:
        async with asyncio.TaskGroup() as tg:
            for url in urls:
                tg.create_task(get_info(session, url))

asyncio.run(main())