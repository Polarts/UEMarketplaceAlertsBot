import functools
import json
import os
from typing import Sequence
import requests
import facebook
from datetime import datetime, timezone
from bs4 import BeautifulSoup
from django.utils import timezone

from .models import AppState, AssetSource, Asset, LogEntry

BASE_URL = 'https://www.unrealengine.com'

def seed_database():
    AppState.objects.create(
            play_state=AppState.PlayStates.PLAY,
            health_state=AppState.HealthStates.PENDING,
            last_posted=timezone.now()
    )
    AssetSource.objects.create(
        title='Free Monthly', 
        type=AssetSource.SourceTypes.SCRAPE, 
        post_title='New free monthly assets out now:',
        url='/marketplace/en-US/assets?tag=4910'
    )
    AssetSource.objects.create(
        title='Megascans',
        type=AssetSource.SourceTypes.JSON,
        post_title='New free megascans available:',
        url='/marketplace/api/assets/seller/Quixel+Megascans?lang=en-US&start=0&count=20&sortBy=effectiveDate&sortDir=DESC&priceRange=[0,0]'
    )


def append_log(source, type, text):
    LogEntry(
        time_stamp=timezone.now(),
        source=source,
        type=type,
        text=text
    ).save()

    status = AppState.objects.get(pk=1)
    if type == LogEntry.LogEntryTypes.LOG and status.health_state == 'PEND':
        status.health_state = 'GOOD'
    if type == LogEntry.LogEntryTypes.ERR:
        status.health_state = 'BAD'
        status.play_state = 'STOP'
    status.save()

def get_new_session():
    session = requests.Session()
    return session

def get_json_assets(session: requests.Session, source: AssetSource):

    if source.is_discontinued: return []

    request = session.get(BASE_URL + source.url)
    response = json.loads(request.text)

    json_assets = None
    asset_array = []

    try:
        source.is_discontinued = response['data']['sellerProfile']['isDiscontinued']
        source.save()
        if (source.is_discontinued):
            append_log(
                source='get_json_assets',
                type=LogEntry.LogEntryTypes.WARN,
                text=f'Asset source {source.title} has been discontinued!'
            )
            return asset_array
    except: pass

    try:
        json_assets = response['data']['elements']
    except KeyError:
        append_log(
            source='get_json_assets',
            type=LogEntry.LogEntryTypes.ERR,
            text=f'Failed to parse JSON[data][elements] from {source.title}, raw: {response}'
        )
        return asset_array

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
                source='scrape_assets',
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
                text='Asset already exists: ' + asset.title
            )
        except Asset.DoesNotExist:
            asset.time_stamp = timezone.now()
            asset.sent = False
            asset.save()
            append_log(
                source='persist_new_assets',
                type=LogEntry.LogEntryTypes.LOG,
                text='New asset added: ' + asset.title
            )
            new_assets += 1

    return new_assets

def post_new_assets(title, debug=False):

    assets = Asset.objects.filter(sent=False)
    
    # prepare message for posting
    message = title + '\n\n' \
        + functools.reduce(
            lambda a, b: {'message': a['message'] + b.title + '\n[' + b.description + ']\n' + b.link + '\n\n'}, 
            assets, 
            {'message': ''}
        )['message']

    if debug:
        return message
    else:
        fb_key = os.environ['FB_API_KEY']
        page_id = os.environ['PAGE_KEY']
        try:
            graph = facebook.GraphAPI(access_token=fb_key, version='3.1')

            api_request = graph.put_object(
                parent_object=page_id,
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
        except facebook.GraphAPIError as e:
            append_log(
                source='post_new_assets',
                type=LogEntry.LogEntryTypes.ERR,
                text="facebook.GraphAPIError: " + e.__str__()
            )

def run_bot(status, debug=False):
    if status.play_state == 'PLAY':
        
        status.last_run = datetime.now()
        status.save()
        append_log('run_bot', 0, f'Running bot at {status.last_run}')

        session = get_new_session()
        sources = AssetSource.objects.all()

        for source in sources:
            assets = []
            if (source.type == AssetSource.SourceTypes.SCRAPE):
                assets = scrape_assets(session, source)
            else:
                assets = get_json_assets(session, source)

            new_assets = persist_new_assets(assets)
            append_log('run_bot', 0, f'There are {new_assets} new assets')
            
            if new_assets > 0:
                result = post_new_assets(source.post_title, debug)
                if debug:
                    return result
    else:
        append_log('run_bot', 0, 'Bot did not run because it\'s on STOP')
        return 'Bot is on STOP!'
