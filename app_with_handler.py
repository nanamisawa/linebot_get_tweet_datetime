# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import app
#######################
#added by minegishi
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import datetime
import threading


def get_tweet_num():
    with open("acount.text","r") as f:
        acount = f.read()
    html = urlopen("https://twitter.com/{}?lang=ja".format(acount))
    bsObj = BeautifulSoup(html,"lxml")
    text = bsObj.find("span",{"class","ProfileNav-value"})
    return text.attrs['data-count']


def get_tweet_time():
    with open("tweet_count.text","w") as f:
        f.write("なし\n")
    while True:
        tweet_num = get_tweet_num()
        time.sleep(10)
        print("[Twitter]",tweet_num,get_tweet_num())
        if tweet_num == get_tweet_num():
            print('[Twitter] 変化なし\n')
        else:
            with open("tweet_count.text","a") as f:
                now = str(datetime.datetime.now()) + "\n"
                f.write(now)


thread_1 = threading.Thread(target=get_tweet_time)
thread_1.start()
#################
#################


app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
#channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
#channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
channel_secret = '0f86b69f0a800dd187cc698c1405a6be'
channel_access_token = 'Yd3v4gGnu6m7E/xYVP5fedy23cGyRtZinOipora4+qpOROaZJMAHQTzQB1jP/V0miUFHuolbxZ8LX3UNY+c5XJpX382kEQEdSHSojK8/u/tbzChaCVujPBPUyt0Eq+S1ox6F9oW2obixnetWDbTydwdB04t89/1O/w1cDnyilFU='
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'



@handler.add(MessageEvent, message=TextMessage)
def message_text(event):


    text = ""
    with open("tweet_count.text","r") as f:
        text = f.read()
    
    if "@" in event.message.text:
        #uid(global) update
        text=event.message.text
        acount = text.replace("@","")
        with open("acount.text","w") as f:
            f.write(acount)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=acount+" を追加しました。 ")
        )

    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text = text )
        )


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', default=8000, help='port')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
