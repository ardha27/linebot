import sys
import requests, json, requests.auth
from bs4 import BeautifulSoup
from flask import Flask, request,  abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('Exw6HGDtPSfMXmRUyHnF6dk+CjKjHS81Lg912+69m6/6+7IrxnXzB4OYvjSuO9LZlmMUGwkCq2Wtc78xaCSkd2QjSvhROQBIR+W3fiUUgNkzZ87+v6MjgYq5c643shmrwijeQdtR/iA5lFTJz+KS2gdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('45c4bc568a7e1c4cffd08efcec54eee9')

@app.route('/', methods=['GET'])
def handleRoute():
    return "hello"

@app.route('/callback', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print('Invalid signature. Please check your channel access token/channel secret.')
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    myMessage = event.message.text
    if 'zep' in myMessage:
        message = TextSendMessage(text='Yes I am Zep Bot')
        line_bot_api.reply_message(event.reply_token, message)

    command = myMessage.split(' /')
    
    if(command[0] == '/anime'):
        if(command[1] == 'search'):
            genreArg = command[2].split(', ')
            genreList = []
            for genre in genreArg:
                genreList.append(getAnimeGenre(genre))
            genreList = ','.join(genreList)
            #print(genreList)
            res = animeSearch('', genreList, command[3])
            data = json.loads(res)
            
            cnt = 0
            message = "title | score\n"
            for anime in data['results']:
                if(cnt == 5): break
                message += anime['title'] + ' | ' + str(anime['score']) + '\n'
                cnt += 1
            line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

    elif(command[0] == '/live'):
        res = livesearch()
        data = json.loads(res)
        message = "Currently Live\n\n"
        for live in data['live']:
            message += 'Channel : ' + live['channel']['name'] + '\n' + live['title'] + '\n' + 'Currrent View : ' + str(live['live_viewers']) + '\n' + 'https://youtu.be/' + live['yt_video_key'] + '\n' + '\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

    elif(command[0] == '/channel'):
        res = channelsearch(command[1])
        data = json.loads(res)
        message = "Search Channel\n\n"
        for channel in data['channels']:
            message += 'Channel : ' + channel['name'] + '\n' + 'Subscriber : ' + str(channel['subscriber_count']) + '\n' + 'Link : ' + 'www.youtube.com/channel/' + channel['yt_channel_id'] + '\n' + 'Twitter : '+ 'twitter.com/' + channel['twitter_link'] + '\n\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

    elif(command[0] == '/rank'):
        res = ranksearch()
        data = json.loads(res)
        message = "Subscriber Rank\n\n"
        cnt = 1
        for channel in data['channels']:
            message += cnt + '.' + '\n' + 'Channel : ' + channel['name'] + '\n' + 'Subscriber : ' + str(channel['subscriber_count']) + '\n' + 'Link : ' + 'www.youtube.com/channel/' + channel['yt_channel_id'] + '\n\n'
            cnt += 1
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))

def livesearch():
    #revieve array 
    res = requests.get('https://api.holotools.app/v1/live?hide_channel_desc=1&max_upcoming_hours=24')
    return res.content

def channelsearch(nama):
    res = requests.get(f'https://api.holotools.app/v1/channels/?name={nama}')
    return res.content

def ranksearch():
    #revieve array 
    res = requests.get('https://api.holotools.app/v1/channels/?sort=subscriber_count&order=desc&limit=10')
    return res.content
