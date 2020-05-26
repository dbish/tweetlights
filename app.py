from flask import jsonify, Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import os
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import json
from flask import current_app
from urllib.request import urlopen
import boto3
import settings
from datetime import datetime, date
from dateutil.parser import parse
import sqlite3
from sqlite3 import Error
from math import exp

application = Flask(__name__)
app = application
app.config['DEBUG'] = True
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY


blueprint = make_twitter_blueprint(
    api_key ="YS0WnopsuCk49XgS38QnxaWVl",
    api_secret="m77dm2DW37qjvuID3ut1Kh6TcLS3Aq9QTP6JyRNBKrRllArXoq",
    redirect_url="/profile"
)
app.register_blueprint(blueprint, url_prefix="/login")
socketio = SocketIO(app)

aws_session = boto3.Session(
        aws_access_key_id=settings.AWS_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
)

conn = None

try:
    conn = sqlite3.connect(':memory:')
    print(sqlite3.version)
except Error as e:
    print(e)

query = """CREATE TABLE IF NOT EXISTS TWEETS (
          UserID varchar(255),
          TweetID varchar(255) PRIMARY KEY,
          CreatedAt datetime,
          RetweetCount int,
          FavoriteCount int,
          Score real
        );"""

conn.cursor().execute(query)

def storeTweets(user, tweets):
    with conn:
        cur = conn.cursor()
        tweet = None
        #query = f"INSERT INTO TWEETS (UserID, TweetID, CreatedAt, RetweetCount, FavoriteCount) VALUES  ({tweet[0], %s, %s, %s, %s)"
    
        today = date.today()
        for tweet in tweets:
            created = parse(tweet[1])
            age = (today - created.date()).days
            score = round((int(tweet[2])+int(tweet[3]))*exp(age/3000), 2)
            query = f"INSERT OR IGNORE INTO TWEETS (UserID, TweetID, CreatedAt, RetweetCount, FavoriteCount, Score) VALUES('{user}', '{tweet[0]}', '{created}', {tweet[2]}, {tweet[3]}, {score})"
            cur.execute(query)
        #connection.commit()
        #connection.close()


def getCollectionInfo(username):
    dynamodb = aws_session.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('tweetlights_users');
    response = table.get_item(
            Key={
                'userid':username
                }
            )
    tweets = []

    if 'Item' in response:
        if 'collectionid' in response['Item']:
            collectionID = response['Item']['collectionid']
            response = twitter.get('collections/entries.json?id=%s'%collectionID)
            try:
                tweets = list(response.json()['objects']['tweets'].keys())
                print(tweets)
            except:
                print('missing tweets')
            #tweets = response.json()['tweets'].keys()
    else:
        response = twitter.post('collections/create.json?name=tweetlights.com')
        collectionID = response.json()['response']['timeline_id']

        response = table.put_item(
                Item={
                    'userid':username,
                    'collectionid':collectionID
                    }
                )
    return collectionID, tweets

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return 'no favicon'

@app.route("/profile")
def profile():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    assert resp.ok
    screen_name = resp.json()['screen_name']
    session['screen_name'] = screen_name 
    session['collection_id'], collectionTweets = getCollectionInfo(session['screen_name']) 
    getAllTweets(session.get('screen_name'))
    #query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY CreatedAt Desc LIMIT 10"
    query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY Score Desc LIMIT 10"
    #query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY FavoriteCount Desc LIMIT 10"
    tweets = []
    with conn:
        cur = conn.cursor()
        cur.execute(query)
        tweets = cur.fetchall()
    tweets = [x[1] for x in tweets]
    return render_template('profile.html', screen_name=screen_name, tweets=tweets, collection=collectionTweets) 

@app.route('/<username>')
def userHighlightsView(username):
    collection_id = getCollectionInfo(username)[0].split("-")[1]
    url = f'http://twitter.com/{username}/timelines/{collection_id}'
    return redirect(url, code=302)
    #return render_template('highlightsview.html', screen_name=username, collection_id=collection_id)

def getAllTweets(user):
    allTweets = []
    tweets = getMoreTweets(user, None, 200)
    loops = 1
    while tweets:
        allTweets = allTweets + tweets
        lastTweetID = tweets[-1][0]
        tweets  = getMoreTweets(user, lastTweetID, 200)
        loops = loops + 1

    storeTweets(user, allTweets)
    

def getMoreTweets(user, lastTweetID, count):
    query = "statuses/user_timeline.json?screen_name=%s&count=%i&include_rts=false"%(user, count)
    
    if lastTweetID:
        lastTweetID = int(lastTweetID) 
        query+="&max_id=%s"%str(lastTweetID-1)
    tweets = twitter.get(query).json()
    tweetData = [(str(x['id']), str(x['created_at']), str(x['retweet_count']), str(x['favorite_count'])) for x in tweets]
    return tweetData


@app.route('/getTweets', methods=['POST'])
def get_tweets():
    sortType = request.form['sortType']
    index = int(request.form['index'])
    #tweets = getMoreTweets(session.get('screen_name'), None, 10)
    #getAllTweets(session.get('screen_name'))
    #tweetIDs = [x[0] for x in tweets]
   
    screen_name = session.get('screen_name')
    if sortType == 'favorites':
        query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY FavoriteCount Desc LIMIT 10 OFFSET {index}"
    elif sortType == 'retweets':
        query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY RetweetCount Desc LIMIT 10 OFFSET {index}"
    elif sortType == 'recency':
        query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY CreatedAt Desc LIMIT 10 OFFSET {index}"
    else:
        query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY Score Desc LIMIT 10 OFFSET {index}"


    tweets = []
    with conn:
        cur = conn.cursor()
        cur.execute(query)
        tweets = cur.fetchall()
    response = {}
    tweetIDs = [x[1] for x in tweets]
    response['tweets'] = tweetIDs
    response['index'] = index + len(tweetIDs)
    return jsonify(response)


@app.route('/saveHighlights', methods=['POST'])
def save_highlights():
    addedHighlights = json.loads(request.form['add'])
    removedHighlights = json.loads(request.form['remove'])
    collectionID = session['collection_id']
    username = session['screen_name']
    if len(addedHighlights) > 0 or len(removedHighlights) > 0:
        data = {}
        data['id'] = collectionID
        changes = []
        for tweet in addedHighlights:
            change = {}
            change['op'] = 'add'
            change['tweet_id'] = tweet
            changes.append(change)

        for tweet in removedHighlights:
            change = {}
            change['op'] = 'remove'
            change['tweet_id'] = tweet
            changes.append(change)

        data['changes'] = changes

        #query = 'collections/entries/add.json?tweet_id=%s&id=%s'%(updatedHighlights[0], collectionID)
        query = 'collections/entries/curate.json?'
        data = json.dumps(data)
        resp = twitter.post(query, data)
    return jsonify('ok')

@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))

if __name__=='__main__':
    socketio.run(app, host='0.0.0.0', port=80)

