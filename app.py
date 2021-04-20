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
        # res = live()
        # data = json.loads(res)
        message = "Currently Live\n"
        # for live in data['live']:
        #     message +=  live['title'] + '\n' + "https://youtu.be/" + live['yt_video_key'] + '\n'
        line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
    
    elif(command[0] == '/reddit'):
        if(command[1] == 'eli5'):
            token_auth = redditAuth()['access_token']
            post_data = getSubredditPopularPost("https://oauth.reddit.com/r/explainlikeimfive/top", token_auth)
            #get the comment endpoint
            
            if(len(command) > 2):
                if(command[2] == 'answer'):
                    message = getTopComment(post_data['children'][int(command[3])-1]['data']['url'], token_auth)
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
            else:
                #Get top 5
                message = "Top post in ELI5:\n"
                for i in range(0, 5): message += post_data['children'][i]['data']['title'] + "\n"
                line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
            #print(message)

anime_genre = {
    "Action": "1",	
    "Adventure": "2", 	
    "Cars": "3",	
    "Comedy": "4", 
    "Dementia": "5", 	
    "Demons": "6", 	
    "Mystery": "7", 	
    "Drama": "8", 	
    "Ecchi": "9", 	
    "Fantasy": "10", 	
    "Game": "11", 	
    "Hentai": "12", 	
    "Historical": "13", 	
    "Horror": "14", 	
    "Kids": "15", 	
    "Magic": "16", 	
    "Martial Arts": "17", 	
    "Mecha": "18", 	
    "Music": "19",	
    "Parody": "20", 	
    "Samurai": "21", 	
    "Romance": "22", 	
    "School": "23", 	
    "Sci Fi": "24", 	
    "Shoujo": "25", 	
    "Shoujo Ai": "26", 	
    "Shounen": "27", 	
    "Shounen Ai": "28", 	
    "Space": "29", 	
    "Sports": "30", 	
    "Super Power": "31", 	
    "Vampire": "32", 	
    "Yaoi": "33", 	
    "Yuri": "34",
    "Harem": "35", 	
    "Slice Of Life": "36", 	
    "Supernatural": "37", 	
    "Military": "38", 	
    "Police": "39", 	
    "Psychological": "40", 	
    "Thriller": "41", 	
    "Seinen": "42",	
    "Josei": "43"
}

def getAnimeGenre(genreName):
    for genre in anime_genre:
        if(genreName in genre.lower()):
            return anime_genre[genre]

def getImageUrl(urlPost):
    s = requests.Session()
    #response = s.get("https://api.instagram.com/oembed/?url=" + urlPost, cookies=s.cookies)
    response = s.get(urlPost + "media/?size=l")
    print(response.content)

def animeSearch(query, genre, sortby):
    #revieve array 

    print(f'https://api.jikan.moe/v3/search/anime?q=&genre={genre}&order_by={sortby}&sort=desc&limit=5')
    if(query == ''): 
        res = requests.get(f'https://api.jikan.moe/v3/search/anime?q=&genre={genre}&order_by={sortby}&sort=desc&limit=5')
    else:
        res = requests.get(f'https://api.jikan.moe/v3/search/anime?q={query}&genre={genre}&order_by={sortby}&sort=desc&limit=5')
    return res.content

def live():
    #revieve array 

    print(f'https://api.holotools.app/v1/live?hide_channel_desc=1&max_upcoming_hours=24')
    res = requests.get(f'https://api.holotools.app/v1/live?hide_channel_desc=1&max_upcoming_hours=24')
    return res.content

def redditAuth():
    client_auth = requests.auth.HTTPBasicAuth('31l0ejKTR-JCbw', 'HawEWet3HraYH5_VYTpRGtLlsuIn3A')
    post_data = {"grant_type": "password", "username": "IcyAcanthopterygii54", "password": "Motorracing087*"}
    headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
    response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)

    return response.json()

def getSubredditPopularPost(uri, token):
    headers = {"Authorization": "bearer " + token, "User-Agent": "ChangeMeClient/0.1 by YourUsername"}
    response = requests.get(uri, headers=headers)
    return (response.json()['data'])

def getTopComment(uri, token):
    headers = {"Authorization": "bearer " + token, "User-Agent": "ChangeMeClient/0.1 by YourUsername"}
    response = requests.get("https://oauth.reddit.com/" + uri[23:], headers=headers)
    return (response.json()[1]['data']['children'][0]['data']['body'])
    

import os
if __name__ == '__main__':
    #getStatusMahasiswa()
    #st = '/akademik status'
    #print()
    '''
    myMessage = "/akademik status"
    if(len(myMessage) >= 16):
        if(myMessage[0:1] == '/'):
            if(myMessage[1:9] == 'akademik'):
                if(myMessage[10:17]== 'status'):
                    print("test")
    '''
    token_auth = redditAuth()['access_token']
    post_data = getSubredditPopularPost("https://oauth.reddit.com/r/explainlikeimfive/top", token_auth)

    #get the comment endpoint
    getTopComment(post_data['children'][0]['data']['url'], token_auth)

    #getImageUrl("https://www.instagram.com/p/CLh68EDHSoS/")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
    
    '''
    myMessage = '/reddit /eli5 /answer /3'
    command = myMessage.split(' /')
    if(command[0] == '/reddit'):
        if(command[1] == 'eli5'):
            token_auth = redditAuth()['access_token']
            post_data = getSubredditPopularPost("https://oauth.reddit.com/r/explainlikeimfive/top", token_auth)
            #get the comment endpoint
            
            if(len(command) > 2):
                if(command[2] == 'answer'):
                    message = getTopComment(post_data['children'][int(command[3])-1]['data']['url'], token_auth)
                    #line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
            else:
                #Get top 5
                message = "Top post in ELI5:\n"
                for i in range(0, 5): message += post_data['children'][i]['data']['title'] + "\n"
                #line_bot_api.reply_message(event.reply_token, TextSendMessage(message))
            #print(message)
    '''
    
