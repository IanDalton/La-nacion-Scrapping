from lxml import html
import requests

from lxml import etree
from lxml import html

def get_xpath(html_content, search_text):
    tree = html.fromstring(html_content)
    element = tree.xpath(f"//*[contains(text(), '{search_text}')]")
    if element:
        return etree.ElementTree(tree).getpath(element[0])
    else:
        return None

    
url = "https://www.lanacion.com.ar/seguridad/tigre-baleo-en-la-cara-a-un-vecino-en-una-discusion-huyo-en-un-auto-robado-y-fue-atrapado-por-la-nid16052023/"

import json
response = requests.get(url)
with open('arch.json','w') as f:
    
    json.dump(get_xpath(response.content, "2KB5ITLJDRDEBIIFS3GFQLXQHM"),f)


