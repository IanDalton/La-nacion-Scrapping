import requests
from lxml import html
import pandas as pd
import asyncio
import subprocess, json
import re

async def extract_nota_id(script_text):
    match = re.search(r'"nota_id":\s*"([^"]+)"', script_text)
    if match:
        return match.group(1)
    else:
        return None

async def extract_comments(comment_id,last_comment=None,context_uuid = None):
    url = 'https://livecomments.viafoura.co/v4/livecomments/00000000-0000-4000-8000-5611d514abb3'
    if context_uuid:
        url += f'/{context_uuid}/comments'
    url += f'?limit=100&container_id={comment_id}&reply_limit=100&sorted_by=newest'
    if last_comment:
        url += f'&starting_from={last_comment}'
    print(url)
    response = requests.get(url)
    response = response.json()
    comments = dict()
    uuid = None
    try:
        for comment in response.get('contents'):
            if not uuid or uuid == last_comment or uuid != comment.get('content_container_uuid') :
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
        if len(comments) >= 100:
            new_comments = await extract_comments(comment_id,uuid,comment.get('content_container_uuid'))
            comments.update(new_comments)
    except TypeError:
        comments = response
    return comments

async def get_info(url:str):
    response = requests.get(url)
    tree = html.fromstring(response.content)
    table_element = tree.xpath("/html/head/script[4]")[0]
    table_html = html.tostring(table_element).decode("utf-8")
    title = url.split('/')
    title = title[len(title)-2]
    print(title)
    comments = await extract_comments(await extract_nota_id(table_html))
    print(len(comments))
    
    with open(f"{title}.json","w") as f:
        json.dump(comments,f)


async def main():
    urls = ["https://www.lanacion.com.ar/politica/la-carta-completa-de-cristina-kirchner-en-la-que-volvio-a-rechazar-ser-candidata-no-voy-a-entrar-en-nid16052023/",
            "https://www.lanacion.com.ar/politica/cristina-kirchner-no-sera-candidata-las-repercusiones-a-la-salida-del-congreso-del-pj-nid16052023/",
            "https://www.lanacion.com.ar/politica/cristina-kirchner-ratifico-que-no-sera-candidata-no-voy-a-ser-mascota-del-poder-nid16052023/"]

    async with asyncio.TaskGroup() as tg:
        for url in urls:
            tg.create_task(get_info(url))

asyncio.run(main())