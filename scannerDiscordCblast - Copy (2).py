import random
import time

import requests
import json
import traceback
#from playsound import playsound
from textblob import TextBlob
import data
import tweepy

from datetime import datetime

from TDAinteract import getOptionsPrice

from discord_webhook import DiscordWebhook, DiscordEmbed

def getTrades(doneTweets):

    working_ = False
    while working_ is False:

        tryCnt = 0

        try:

            # SETUP NECESSITIES

            # discord
            headers = {
                'authorization': 'ODc3NzUxMDgzMTgxNjcwNDYw.GF6ar2.d2Ichfm4bT5T0FYJDxJ-gzJrm9TIyzQKFiaocU',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'

            }


            enhancedText = []

            try:


                if tryCnt > 0:

                    headers = {
                        'authorization': 'ODc3NzUxMDgzMTgxNjcwNDYw.GF6ar2.d2Ichfm4bT5T0FYJDxJ-gzJrm9TIyzQKFiaocU',
                        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; HTC One M9 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.3'
                    }

                else:

                    headers = {
                        'authorization': 'ODc3NzUxMDgzMTgxNjcwNDYw.GF6ar2.d2Ichfm4bT5T0FYJDxJ-gzJrm9TIyzQKFiaocU',
                        'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'
                    }

                cblast = requests.get('https://discord.com/api/v9/channels/972215994770673664/messages?limit=2',
                                     headers=headers)

                cblastText = [x['content'] for x in json.loads(cblast.text)]

                tryCnt = 0

            except Exception as exception:

                tryCnt += 1
                if tryCnt >= 2:
                    time.sleep(1)

                #traceback.print_exc()
                #print('no em alerts')
                pass




            messages = [['**CBlast**',cblastText]]

            #print(messages)

            trades = []

            doneMsgs = []

            for message in messages:

                if len(message[1]) > 0:
                    for msg in message[1]:

                        continueOn = False

                        for compareMsg in doneMsgs:

                            if msg.lower() in compareMsg.lower() or compareMsg.lower() in msg.lower():

                                continueOn = True

                        if continueOn: continue

                        if 'lotto' in msg.lower(): lotto = True
                        else: lotto = False

                        price = 'N/A'
                        exp = 'N/A'
                        strike = 'N/A'
                        side = 'N/A'
                        ticker = 'N/A'

                        msg = msg.lower()

                        if len(msg.split(' ')) >= 3 and ('$' in msg or '@' in msg or '/' in msg):

                            watchingForPrice = False

                            leftover = msg

                            if '**CBlast**' in message[0] or '**CBlast CHALLENGE**' in message[0] or '**Eva**' in message[0] or '**Enhanced Market**' in \
                                    message[0] or '**GHOST**' in message[0] or '**StockSnipa**' in message[0]:

                                msgs = []

                                try:
                                    int(msg.split(' ')[1])
                                except:
                                    msg = ' '.join(msg.split(' ')[:1] + ['1'] + msg.split(' ')[1:])

                                #if '**GHOST**' in message[0]:
                                    #print(msg)

                                try:

                                    ticker = msg.split(' ')[2]
                                    strike = round(float(msg.split(' ')[3][:-1]))
                                    exp = msg.split(' ')[4].replace('/2022', '')
                                    side = msg.split(' ')[3][-1]
                                    try:
                                        price = float(msg.split(' ')[5].replace('@', ''))
                                    except:
                                        try:
                                            price = float(msg.split(' ')[6])
                                        except:
                                            traceback.print_exc()
                                            pass
                                except Exception as exception:
                                    traceback.print_exc()
                                    pass

                            if lotto and 'lotto' not in msg.lower(): msg = msg + ' lotto'


                            try:
                                doneMsgs.append(msg)

                                trades.append([message[0], msg, price, strike, side.upper(), exp, ticker.upper()])
                            except:
                                continue

            working_ = True

        except Exception as exception:

            traceback.print_exc()

            #time.sleep(5)
            pass

    return trades,doneTweets





def getSentiment(ticker):

    consumer_key = "lZFrvKB1igcUkTgpwkCRGTFNq"
    consumer_secret = "kz9t4mwLEW7tsDmD0sgnZfr9nrf6ei1o2nhK2gjjjqitUk0qVy"
    access_token = "1334537394721234944-Oz2wLp7DzpMpjqpf5Q0V3kdgAZ4eUm"
    access_token_secret = "Q59PkDVQtkBJmvaZO3enYQKWRifz43lvZJOwX0A5TzRSq"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    tickeraverage = 0

    if '$' not in ticker: ticker = '$' + ticker.strip()

    if len(ticker) <= 15:
        try:

            tweets = api.search_tweets(q=ticker, count=100, tweet_mode='extended')

        except:

            return None



        avg = []

        try:

            tweets_ = [x.full_text for x in tweets]

        except:

            return None

        for tweet in tweets_:
            blob = TextBlob(tweet.strip().replace('\n', ''))
            avg.append(blob.sentiment.polarity)

        cnt = 0.0
        for num in avg:
            cnt = cnt + num

        tickeraverage = cnt / len(avg)

    return tickeraverage


doneTweets = []
doneMessages = []
firstMessages,doneTweets = getTrades(doneTweets)
doneMessages = firstMessages
first = True


while True:

    trades,doneTweets = getTrades(doneTweets)

    #print(trades)

    if first:
        messages = [x for x in firstMessages if x not in doneMessages]
    else:
        trades, doneTweets = getTrades(doneTweets)
        messages = [x for x in trades if x not in doneMessages]
    #print(messages)
    for message in messages[::-1]:

        naCnt = 0

        # send discord webhook msg

        url = 'https://discord.com/api/webhooks/966414944381833356/L83Sx8lM-pjHwi7DpM9AGkB4UZhyJ0rBP1imadyBUpr-xiHT9B7vPd6N_YDONsBZ860d'
        username = '[ ' + message[0].replace('*','') + ' ]'
        content = message[0] + ' **Alert** @everyone'

        print(username.replace('*','') + ' | ' + message[1].upper())

        webhook = DiscordWebhook(url=url, username='Nyria', content=content)
        # create embed object for webhook

        if 'stc' in message[1].lower() or 'exited' in message[1].lower() or 'trimmed' in message[1].lower():
            color = 'eb3455'
        else:
            color = '00FFE4'

        embed = DiscordEmbed(title=username.replace('*', ''), description=message[1], color=color)

        # set timestamp (default is now)
        embed.set_timestamp()

        fields = ['TICKER', 'PRICE', 'STRIKE', 'SIDE', 'EXP', 'SENTIMENT', 'CURRENT PRICE']

        # def getOptionsPrice(stock='SPY', key='', exp='', side='', strike='', sell=False, full=''):

        try:

            currentPrice = getOptionsPrice(stock=message[6].replace('$', ''), exp=message[5], side=message[4],
                                           strike=message[3], full=True)

        except Exception as exception:
            # print(currentPrice)
            # traceback.print_exc()
            currentPrice = 'N/A'

        if currentPrice is None: currentPrice = 'N/A'

        messageDict = {'ticker': message[6].upper(), 'price': message[2], 'strike': message[3],
                       'side': message[4].upper(), 'exp': message[5], 'sentiment': 'N/A', 'current price': currentPrice}

        '''
        sideText = ''

        if messageDict['ticker'].lower() != 'n/a':

            if message[4].lower() != 'n/a':
                try:
                    if message[4].lower() == 'p': sideText = ' puts'
                    if message[4].lower() == 'c': sideText = ' calls'
                except:
                    sideText = ''

            sentiment = getSentiment('$' + message[6] + sideText)

            if sentiment is not None:
                if sentiment > .05: sentimentTxt = 'Good'
                if sentiment > .07: sentimentTxt = 'Very Good'
                if sentiment < .07: sentimentTxt = 'Average'
                if sentiment < .05: sentimentTxt = 'Poor'
                if sentiment < .03: sentimentTxt = 'Very Poor'

                messageDict['sentiment'] = sentimentTxt

        '''

        for elem in fields:
            if str(messageDict[elem.lower()]).lower() != 'n/a':
                if elem == 'current price':
                    name = '**CURRENT PRICE**'
                    value = str(messageDict['current price'][0]) + ',' + str(messageDict['current price'][1])
                else:
                    name = '**' + elem + '**'
                    embed.add_embed_field(name=name, value=str(messageDict[elem.lower()]))

            else:
                naCnt += 1

        # add embed object to webhook
        webhook.add_embed(embed)

        # likely a trade alert
        if naCnt < 4:

            url = 'https://discord.com/api/webhooks/966414944381833356/L83Sx8lM-pjHwi7DpM9AGkB4UZhyJ0rBP1imadyBUpr-xiHT9B7vPd6N_YDONsBZ860d'
            content = message[0] + ' **Alert** @everyone'
            webhook = DiscordWebhook(url=url, username='Nyria', content=content)
            webhook.add_embed(embed)
            response = webhook.execute()

        # not likely a trade alert
        if naCnt >= 4:
            url = 'https://discord.com/api/webhooks/966424534787952640/YPGnzblikr95-_U0qP0EA5McpHUN5qegDtZXZ73K_pKHeLW3dK4myWXbg2a9YkPFwT8J'
            content = ''
            webhook = DiscordWebhook(url=url, username='Nyria', content=content)
            webhook.add_embed(embed)
            response = webhook.execute()

        if 'qqq' in message[1].lower() or 'spy' in message[1].lower() or 'tsla' in message[1].lower() or 'aapl' in \
                message[1].lower() or 'amd' in message[1].lower():
            url = 'https://discord.com/api/webhooks/966467480644112464/c27m67SCBuOTIWLYpQx0pSkPU-6GVol4xD0M2_jB6SQy_muDTt89fYl4Dt1ayGxgBGAY'
            content = '@everyone'
            webhook = DiscordWebhook(url=url, username='Nyria', content=content)
            webhook.add_embed(embed)
            response = webhook.execute()

        doneMessages.append(message)

        if random.randint(0,3) == 1:
            time.sleep(1)

    first = False
