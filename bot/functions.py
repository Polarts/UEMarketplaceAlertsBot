import functools
import json
from typing import Sequence
import requests
import facebook
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from django.utils import timezone

from .models import AssetSource, Asset, LogEntry

BASE_URL = 'https://www.unrealengine.com'

def append_log(source, type, text):
    LogEntry(
        time_stamp=timezone.now(),
        source=source,
        type=type,
        text=text
    ).save()

def get_new_session():
    session = requests.Session()
    return session

def get_json_assets(session: requests.Session, source: AssetSource):

    request = session.get(BASE_URL + source.url)
    response = json.loads(request.text)

    json_assets = response['data']['elements']
    asset_array = []

    for asset in json_assets:
        
        title = asset['title']
        
        description = functools.reduce(
            lambda a, b: { 'desc': a['desc'] + b['name'] },
            asset['categories'],
            {'desc': ''}
        )['desc']

        link = BASE_URL +'/marketplace/en-US/product/' + asset['urlSlug']

        try:
            asset_array.append(Asset(
                title=title,
                description=description,
                link=link,
                source=source
            ))
        except TypeError:
            append_log(
                source='get_json_assets',
                type=LogEntry.LogEntryTypes.ERR,
                text="An error occured while creating Asset from the following: "+title+", "+link+", "+description
            )


    return asset_array

def scrape_assets(session: requests.Session, source: AssetSource):

    request = session.get(BASE_URL + source.url)
    response = BeautifulSoup(request.text, 'lxml')

    scraped_assets = response.select('article.asset')
    asset_array = []

    for asset in scraped_assets:

        h3a = asset.select('h3 a')[0]

        title = h3a.text

        categories = asset.select('.details .categories')
        description = ''
        for i in range(len(categories)):
            cat_item = categories[i].select('.mock-ellipsis-item-cat')
            if len(cat_item) > 0:
                description += cat_item[0].text + (',' if i < len(categories)-1 else '')

        link = BASE_URL + h3a['href']

        try:
            asset_array.append(Asset(
                title=title,
                description=description,
                link=link,
                source=source
            ))
        except TypeError:
            append_log(
                source='get_json_assets',
                type=LogEntry.LogEntryTypes.ERR,
                text="An error occured while creating Asset from the following: "+title+", "+link+", "+description
            )

    return asset_array

def persist_new_assets(assets: Sequence[Asset]):
    new_assets = 0
    for asset in assets:
        try:
            existing_asset = Asset.objects.get(title__exact=asset.title)
            append_log(
                source='persist_new_assets',
                type=LogEntry.LogEntryTypes.LOG,
                text='Article already exists: ' + asset.title
            )
            # if time.month < datetime.now().month or time.year < datetime.now().year:
            #     table.update({'sent': False}, Query().title == asset['title'])
            #     new_assets += 1
            #     append_log(
            #         source='persist_new_assets',
            #         type=LogEntry.LogEntryTypes.LOG,
            #         text='Updated ' + asset['title'] + 'to unsent'
            #     )
        except Asset.DoesNotExist:
            asset.time_stamp = timezone.now()
            asset.sent = False
            asset.save()
            append_log(
                source='persist_new_assets',
                type=LogEntry.LogEntryTypes.LOG,
                text='New article added: ' + asset.title
            )
            new_assets += 1

    return new_assets

def post_new_assets(title, debug=False):

    assets = Asset.objects.filter(sent=False)
    
    # prepare message for posting
    message = title + '\n\n' \
        + functools.reduce(
            lambda a, b: {'message': a['message'] + b['title'] + '\n[' + b['description'] + ']\n' + b['link'] + '\n\n'}, 
            assets, 
            {'message': ''}
        )['message']

    if debug:
        return message
    else:
        # load keys
        keys = json.load(open('keys.json'))
        graph = facebook.GraphAPI(access_token=keys['api_key'], version='3.1')

        api_request = graph.put_object(
            parent_object=keys['page_key'],
            connection_name='feed',
            message=message
        )

        if 'id' in api_request:
            append_log(
                source='post_new_assets',
                type=LogEntry.LogEntryTypes.LOG,
                text='Successfully posted on facebook!'
            )
            for asset in assets:
                asset.sent = True
                asset.save()
