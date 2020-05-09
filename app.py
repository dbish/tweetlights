from flask import jsonify, Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import os
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
import json
from flask import current_app
from urllib.request import urlopen
import boto3
import settings

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

def getCollectionID(username):
    dynamodb = aws_session.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('tweetlights_users');
    response = table.get_item(
            Key={
                'userid':username
                }
            )
    if 'Item' in response:
        if 'collectionid' in response['Item']:
            return response['Item']['collectionid']
    
    response = twitter.post('collections/create.json?name=tweetlights.com')
    collectionID = response.json()['response']['timeline_id']

    response = table.put_item(
            Item={
                'userid':username,
                'collectionid':collectionID
                }
            )
    return collectionID

@app.route('/')
def home():
    return render_template('index.html')


@app.route("/profile")
def profile():
    if not twitter.authorized:
        return redirect(url_for("twitter.login"))
    resp = twitter.get("account/settings.json")
    assert resp.ok
    screen_name = resp.json()['screen_name']
    session['screen_name'] = screen_name 
    session['collection_id'] = getCollectionID(session['screen_name']) 
    return render_template('profile.html', screen_name = screen_name) 

@app.route('/<username>')
def userHighlightsView(username):
    collection_id = getCollectionID(username).split("-")[1]
    return render_template('highlightsview.html', screen_name=username, collection_id=collection_id)

def getMoreTweets(user, lastTweetID):
    
    query = "statuses/user_timeline.json?screen_name=%s&count=10"%user
    
    if lastTweetID:
        print(lastTweetID)
        print(lastTweetID+1)
        print(str(lastTweetID+1))
        query+="&max_id=%s"%str(lastTweetID+1)
    tweets = twitter.get(query).json()
    tweetIDs = [str(x['id']) for x in tweets]
    return tweetIDs


@app.route('/getTweets', methods=['POST'])
def get_tweets():
    print('tweets requested')
    tweetIDs = getMoreTweets(session.get('screen_name'), None)
    print(tweetIDs)
    return jsonify(tweetIDs)


@app.route('/saveHighlights', methods=['POST'])
def save_highlights():
    updatedHighlights = json.loads(request.form['data'])
    collectionID = session['collection_id']
    print('collectionid: %s'%collectionID)
    username = session['screen_name']
    print(updatedHighlights)
    print(updatedHighlights[0])
    query = 'collections/entries/add.json?tweet_id=%s&id=%s'%(updatedHighlights[0], collectionID)
    print(query)
    resp = twitter.post(query)
    print(resp.json())
    return jsonify('ok')

@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))

if __name__=='__main__':
    socketio.run(app, host='0.0.0.0', port=80)

