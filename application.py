from flask import jsonify, Flask, render_template, request, redirect, url_for, session, flash, g
import os
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import json
from flask import current_app
from urllib.request import urlopen
import boto3
from botocore.exceptions import ClientError
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

aws_session = boto3.Session(
        aws_access_key_id=settings.AWS_PUBLIC_KEY,
        aws_secret_access_key=settings.AWS_SERVER_SECRET_KEY,
)

DATABASE = '/tmp/tweets.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def bootstrapDB():
    try:
        db = get_db()
        print('connected')
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

    db.cursor().execute(query)
    print('bootstrapped')


def storeTweets(user, tweets):
    db = get_db()
    try:
        cur = db.cursor()
        tweet = None
    
        today = date.today()
        for tweet in tweets:
            created = parse(tweet[1])
            age = (today - created.date()).days
            score = round((int(tweet[2])+int(tweet[3]))*exp(age/3000), 2)
            query = f"INSERT OR IGNORE INTO TWEETS (UserID, TweetID, CreatedAt, RetweetCount, FavoriteCount, Score) VALUES('{user}', '{tweet[0]}', '{created}', {tweet[2]}, {tweet[3]}, {score})"
            cur.execute(query)
        db.commit()
    except Error as e:
        print(e)


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
            except:
                tweets = []
    else:
        response = twitter.post('collections/create.json?name=tweetlights.com')
        collectionID = response.json()['response']['timeline_id']

        response = table.put_item(
                Item={
                    'userid':username,
                    'collectionid':collectionID
                    }
                )
        flash('New tweetlights collection created. Now add your highlights!')
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
    bootstrapDB()
    resp = twitter.get("account/settings.json")
    screen_name = resp.json()['screen_name']
    session['screen_name'] = screen_name 
    session['collection_id'], collectionTweets = getCollectionInfo(session['screen_name']) 
    getAllTweets(session.get('screen_name'))
    query = f"SELECT * FROM TWEETS WHERE UserID='{screen_name}' ORDER BY Score Desc LIMIT 10"
    tweets = []
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(query)
        tweets = cur.fetchall()
    except Error as e:
        print(e)
    tweets = [x[1] for x in tweets]
    return render_template('profile.html', screen_name=screen_name, tweets=tweets, collection=collectionTweets) 

@app.route('/<username>')
def userHighlightsView(username):
    collection_id = getCollectionInfo(username)[0].split("-")[1]
    url = f'http://twitter.com/{username}/timelines/{collection_id}'
    return redirect(url, code=302)

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
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    sortType = request.form['sortType']
    index = int(request.form['index'])
   
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
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute(query)
        tweets = cur.fetchall()
    except Error as e:
        print(e)
    response = {}
    tweetIDs = [x[1] for x in tweets]
    response['tweets'] = tweetIDs
    response['index'] = index + len(tweetIDs)
    return jsonify(response)


@app.route('/saveHighlights', methods=['POST'])
def save_highlights():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
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

        query = 'collections/entries/curate.json?'
        data = json.dumps(data)
        resp = twitter.post(query, data)
    return jsonify('updates saved')

@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    query = "oauth/invalidate_token.json"

    resp = twitter.post(query)
    flash('You were signed out')
    del blueprint.token
    return redirect(url_for('home'))

@app.route('/delete')
def delete():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))

    #destroy collection
    screen_name = session['screen_name']
    collection_id = session['collection_id']
    query=f"collections/destroy.json?id={collection_id}"
    
    #delete profile from dynamodb
    dynamodb = aws_session.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('tweetlights_users')
    try:
        response = table.delete_item(
                Key={
                    'userid':screen_name
                    }
                )
    except ClientError as e:
        print(e)

    flash('profile deleted. sign in again to create a new tweetlights collection in the future.')
    return redirect(url_for('logout'))

if __name__=='__main__':
    print('running')
    #application.run(host='0.0.0.0', port=80)
    application.run(host='0.0.0.0', port='80')

