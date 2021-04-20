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
    if '69' in myMessage:
        message = TextSendMessage(text='69? Nice. I am a bot lol')
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



def autentikasi():
    #Data-data yang diperlukan

    # Lakukan Autentikasi
    s = requests.Session()
    url = 'https://login.itb.ac.id/cas/login?service=https%3A%2F%2Fakademik.itb.ac.id%2Flogin%2FINA'
    cookies = {
        '_ga': 'GA1.3.933949927.1613036240',
        '_gid': 'GA1.3.2125425999.1613036240',
    }

    params = (
        ('service', 'https://akademik.itb.ac.id/login/INA'),
    )

    data = {
        'username': USERNAME_INA, 
        'password': PASSWORD_INA,
        'execution': '2fbc6a0a-45d5-427b-bf8c-eb5d513001dd_ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5Lno2WGFyaW5pVlZnV0I5WFJWdlpfdTZkZzVQNGFzdjhxTWlqdHJKYWQwal84ZnllTk51c0ZTT3F0QTJoWXd2ZVNCTGt6ekExQ05Ed0tLNjh1a0tKbzZITTdTVWpsbXdnZHhuLUQxcmMtLUE5emJfLVBERnUyeVJ0alRWbEdmT2xULWZ3akh0dnRhcjhVSlJNYkRURFB6anZiOXc3R19USGQzUnB0M3pGZDBVR1JFYy1tS2NxNHNCRUpMWGlFdTdxc2FZZmFONTBmRWQtRHY5aEFrcGV1elZOUmpkSkVodGdDeTVtUU5LMEp0NnRtTVdLcnhOVDhVUHB2Q1hLbWtuTXExTEd2MllNUFJNRGpBdVBjQTBPSGd0MXdOWXZmQVZ2Z3daTU5heTE5b0tyMjlvbTczbEd1QTFyTmJqTmJmN0k1NG9kV0NndEFKSXJlR2gxSnZrNkZvU1NncUl2dkpwekZJck55SVd6WHFzYWJVWm1ndHotY3JRZkZ2bUVKS0tfb19qVlE2Qnd0YTZGUjNmdFhnekJkeWkzUDhUU0hmeVRzX3k3REZ0cjJ2S0ZHSmRPeDVfR1JmVHRRRzJYWEdkRVA3OHNkVFJQZU1aSzAzUFk3QTNpdzE5VXYwbVRFVkRiUlA3MzVnbllkTk9GRHBvRUZnSEtpSUJiM0NqbTJGdEt0QTZPR3ZqVVJWNE9ENURmbEh1WUF2Y3JZdTluNk5uZVdxQ0JkOWJCNzQyZXppaGd0dnFYQmVxQUhBYmZNa1MxLWhUVzJOWm94TWQ4bkU1blZYUFJvSkZvNTRqY1o1QmZHWkFSWVlXSXdSclJubnNIWGNxRjFyN0FVNl90OUxWU1VfUS1VXzFiMFFTZ1hJNjU1X3I5VDhoODFCaUlpc2NFUGJnRHEwanVqSEpDMGxuWVVqcWwxVVlrWUtmdjNVeTBYbDRJbXI1V25sajhyYWtBWlpvamFVU2xiSE9fc3o1b3h1dkVsbVZKS1NmdzZSa0dYOEt4enlSa09hODFackJoZHc0b2JRTGVGcFpTNjltYzhzdk1oOExVMGdBMlkwTEZwbXVFbkdxWFdldHQwak9DNEJKTFlTcHNGM0gwdFFoYXp4a1otZGZ1YUVoOWU0Ukl5dzVnc0MxZEstc3QyVFZSNFJiWkdBMTRJOVJZUExqYVNEcy1vUnJwM3dfbUNadmhsSFhfU0FWOGgyNGlLcnBzRmktdTJENnZuZzFIYWswVzZUbHc1NzN4V3ZOdDNtVWswZlUxR1JIRVJOaDhQaWdEZkxnSTZDTUcwcnZjY0pNbHNCMFlHYWlfT0RlT1JwZUZDdkk3bTFEVWxDb1VxaV82Yzk5YnpvX0tJOUFCQXNUXzZBbWdVU3JmaHJxV1hsZy1kdk1TX0FBR2dmclBCNndPT2IyQ0VCeWtHX0lGd2o0UWNNdG9QRldvM3pJdkFwZ2QwZnUwSVVfaE1tS1RQSGV0d3RmR1ZWbEdSal9sVkN6LTk3VVZtb29YQks4VEZONlNQVGdSLXJiZWhPcEliOUhSNFNENUVLc3VVTEFiMVJMaTVTS0Ywa1NXZGN6dmdaSWthdjB0UGFveXhtektpSlBTMWZtc2FUT2Uxdms2bi1wSnJ0UExWWGZJT2tKaWpuYmFVTlNab3VNWE9PckhVZVVyUkJmTjFjUUZOSEJ0clNHSUt1R1pIQjdXSDFBa1RSeUcyX2RIMExmOTRGZzRSaW4xX1I1c1R5ZGM5bXNjZjdGUk03S2Fla3phOEZ5RUJoc0x3U0pIMU1GaHFIVnRvdkNKSTJNWDVib0dia085MFJ0dDE3SFZvMkwxcS1zcGZDSWt3QTdYdV9DcHVDbkJSSFc1ZmcwSXFWanVYeXJVZ0FtdzdpR1JVUTFNUTVOLXJ4Wndlekxndi1kNlFHeFhtZEtFVmRQTG5WdkJlQ1AwVTJGcURCWUpBa0lXRVByeFVZcC1fdF9Fb0xHQmFTN0RtZ1VNdkJNa1ZFMEZ3SFk5U3Z1NmxaX1IxQ20ydUdCcUFRUzBlVGdVVHB1VGRFUjJxbVdmRnhaYXVBOS01emhmUVJVT2VMd0o1T3YzMTdqRmFNSW12NFBUVFg4MWMxWHBRWmZoekhXZ2phQ0p4Y3RIY3VQdEhVakpFY1VwNXBTNHpxa0RWdWRvcHJCWG1YNWtISG1QZmttT212bVh5Qkg5S3YwUFdKc09fUlQwcWFRTWs0YUFOTDZMUEM4TXdjbWZmZHVleEZBa0YxZkRyRE9iYnl3cXRMVEU0Szg4WmJVZENHY3VyazZHNWV5dTltN1lHRUdFcWdnbmY1d2ZlVzdiV1JadmQ5N0tXTU9Bc3FSSDdwVWlUSDA3TUVhSUZ6YUdfanYxUkdfU0xJcmlJQ3lNSEt4ZVJKNDM5aWhJOVlfbUFpRnJSN1psVGRTOXBNdnlGX0lKY2JYaUVDeE5BLXNTUG5QSGpWV3FPVlB2TlNrN1k5bHdTRVdSclBTc3d1eEFnd0VjUF9rS3hOVURCb3JrcFFCaGZzN3RJOHJYbW5sWHpKM2RmWHA1NEo4dXVGNE96Tjljek11WDBncS13LXltSU4yRGZPYnNYSk16WHdmSmZ3bEFlb1NjM0xPWG5QWC10ZFFUcGhkNmlZQzZ5MVVYQjNJbU1wREZYNGUtM09pRjhGcXMyQnpBeG1JZm1kYllYMHg4Mk93YWNTYjVQWm5WUkdNR1o2M0JjVmpjaG9OT2JHcE1hejZRaUstN3IyaWUxeV83V1NjWjMweVQ4blZrVUdnVUZWMVg2NzdUWUItb2hnWDNmVEVPWkkyNXFkVDJQWmhGcWlqVWttaVFsYUVQOXUzQVRWdGo4RW1EdWZSMzdkVzItaHNEbGlwTnhmTDMza2hBZUttME5qTE1tWTgzWVZZczdna2dDYWxHUEV6MDBXbUpSc2RTMERjNF9md2szVFQ3cUYzblQ1QXE5X0NyTUlYdFIxel83Qnkwd2ZaSVFLbVVjWUgyY3BGck9JN2g1aXVhYUR0YmFZYThfcEJGQVcxYW5vdkN0X19KTXpzYnlvUmdDYllGazNhQjBFM2NlWWREdUV4bG03N3VudnlTTHEyUmxCT2JyZXk5azZoa1VjMmR1dTU5eWxwRWJGYTU0VUtKQ09JY0hyWEJ3OTNxdkgxQjVSRE16YTlVSzVORll4ek9UeFZ5WDN3TG5PUnBGalpMLVRxdFhHNUVFc1cwaG5XVXd0LWhndWN3RGJPdWxFdDBUUmFJQnNLMmU1NXFpNWFReGdjckpyaTNRV3F4d0hJZ0h3eFVkYkFDU0tpV2lNT05mNVVFZWh3X2tIUG5PMFFtY29DaTNZRmZ4d0NfWUg1UjMzaEdfRmpvYktJWVdZbDdIUGpveHFzaDFVeU92VmNSeGNkVTVDTkxVdFhMdE11ODZ2Q3hCaWhkUmRlT25Xck83LTFlS0cwNFY2WEJYdzNOOHNiNFdHRWRWTjRLOU9LRjdoUlY2RTM0djBFUlp6bEZaZ253OXREemQwTmdxZ2dJTmNtM3BKc3NkY0FMTDBnQ3E1LVR4VENtb2NSRHM1d0VuMlJ6UnlwbERGSWpoSDNVREh0WlQ4VEZxZ0NHbmlIcl9qY0VCTWhYYXNZRzRTeENoOU8tNW11ZXlNc0s3SDlkdDc1MElYd3J1cmI3QVo1cW14SG1zb01oeGRGMXJ6dmVUQ2wtMHpZWVNyamNfQ3NFVEhsR2Y3RlFjRy0zNGd4UC1aRldUTEE5eHFWTDhqTHppTUxwWEtVbnRmd0Q5ZGVtRjRXSXotZWY4SzlNVklxUkRhZTA4OVVid0N6UU51Wm1nXzB5dDU2NjVLT1IxS0p2YmJYNHQwTW1HQk5lQTdBZjd3X1hPTTN3V19ZcWVNd0xnRnpHTlN3U3lxWWxyMHlYWWpRUkdVa3VDOWduUWNzaGRodVlDcDVJbmMyRmNCcGhPblUzRGxRYjh4UllkdERac1h5aUg0Yl9GM0dmYkxMeGo4eko3bjRqdl9ZeU5pbjB5anByUzB4cG5zWEgydmdZZGxNMHpyTXItbUpCc3RRMnd1bmpWSlY1R0Y4czZNNkpUOF9NNnlKUU1XNUpDdE4tUTFlNXdfR0tqQy1PRW0zTEJVcTVGY09SYTZHWTB3ellKYUpvTzNSTlNWWlpOam9GU2RpbVNMa3ZlckI4MkRBNmFBRWtjZXN6ODBmWnBSYVJKXzRmR01MWERReWFjbHRQXzdGVFI4WENPTjNkeWs1SWNZeXBMSnBjRVgxcy1XSTBRbmhseGhLS2t5Q1pnTDB1UzdITV9nSzBPZ3hCR3JlckRRcy1XcVc2SlJaU2I5U3hWRUtjdlZ5bWhNejNuX3JQUHRBRjh3dEFCWXZTOS1YRWVyUDlJSEEudGdUM3hMWnlrM1VmVnhnb3Z0RjFDdDd6bHliTGQ4Y2RWTzBRN0FrTUdJaGY4Vl9NdTVfX0FBeDdOZ0VGam9nLWRyQjllVFdCUk56WndxSlVqM21yZEE=',
        '_eventId': 'submit',
        'geolocation': ''
    }

    #Post data
    response = s.post(url, cookies=cookies, data=data)
    if(response.status_code == 200):
        print('Berhasil login ke SIX...\n')
    return s
    


def getStatusMahasiswa():
    #untuk saat ini mengembalikan daftar kuliah saja
    session = autentikasi()
    statusMhs = BeautifulSoup(session.get('https://akademik.itb.ac.id/app/mahasiswa:13519165/statusmhs').content, features="lxml")

    status = ""
    daftarKuliah = statusMhs.select('table.table:nth-child(1)')
    tabelDaftarKuliah = daftarKuliah[0].find_all('tr')
    for kuliah in tabelDaftarKuliah:
        content = kuliah.find_all('td')
        if(len(content) > 0):
            kode = content[0].text
            matkul = content[1].text
            while(len(matkul) < 35): matkul += " "
            kelas = "K" + content[2].text
            sks = content[3].text + " SKS"
            kehadiran = content[4].text
            status += kode + " " + matkul + " " + kelas + " " + sks + " " + kehadiran + "\n"
    return status
    
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
    
