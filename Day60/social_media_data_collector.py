from flask import Flask, render_template_string, request, jsonify
import tweepy
import praw
from googleapiclient.discovery import build
from datetime import datetime
import json

app = Flask(__name__)

# Configuration - Replace with your actual API credentials
TWITTER_BEARER_TOKEN = "YOUR_TWITTER_BEARER_TOKEN"
REDDIT_CLIENT_ID = "YOUR_REDDIT_CLIENT_ID"
REDDIT_CLIENT_SECRET = "YOUR_REDDIT_CLIENT_SECRET"
REDDIT_USER_AGENT = "YOUR_APP_NAME"
YOUTUBE_API_KEY = "YOUR_YOUTUBE_API_KEY"

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Social Media Data Collector</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .platform-section {
            margin: 30px 0;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .platform-section h2 {
            color: #555;
            margin-top: 0;
        }
        input, button {
            padding: 10px;
            margin: 5px 0;
            font-size: 14px;
        }
        input {
            width: 300px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            cursor: pointer;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
            max-height: 400px;
            overflow-y: auto;
        }
        .post {
            margin: 10px 0;
            padding: 10px;
            background-color: white;
            border-left: 3px solid #4CAF50;
        }
        .error {
            color: red;
            padding: 10px;
            background-color: #ffe6e6;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📱 Social Media Data Collector</h1>
        
        <!-- Twitter Section -->
        <div class="platform-section">
            <h2>🐦 Twitter/X</h2>
            <input type="text" id="twitter-query" placeholder="Enter search query (e.g., #python)">
            <input type="number" id="twitter-count" placeholder="Number of tweets (max 100)" value="10">
            <button onclick="searchTwitter()">Search Twitter</button>
            <div id="twitter-results" class="results"></div>
        </div>

        <!-- Reddit Section -->
        <div class="platform-section">
            <h2>🤖 Reddit</h2>
            <input type="text" id="reddit-subreddit" placeholder="Subreddit name (e.g., python)">
            <input type="number" id="reddit-count" placeholder="Number of posts (max 100)" value="10">
            <button onclick="searchReddit()">Get Reddit Posts</button>
            <div id="reddit-results" class="results"></div>
        </div>

        <!-- YouTube Section -->
        <div class="platform-section">
            <h2>📺 YouTube</h2>
            <input type="text" id="youtube-query" placeholder="Enter search query">
            <input type="number" id="youtube-count" placeholder="Number of videos (max 50)" value="10">
            <button onclick="searchYouTube()">Search YouTube</button>
            <div id="youtube-results" class="results"></div>
        </div>
    </div>

    <script>
        function searchTwitter() {
            const query = document.getElementById('twitter-query').value;
            const count = document.getElementById('twitter-count').value;
            const resultsDiv = document.getElementById('twitter-results');
            
            resultsDiv.innerHTML = '<p>Loading...</p>';
            
            fetch('/api/twitter', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query, count: count})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                } else {
                    let html = `<h3>Found ${data.tweets.length} tweets:</h3>`;
                    data.tweets.forEach(tweet => {
                        html += `
                            <div class="post">
                                <strong>@${tweet.author}</strong><br>
                                ${tweet.text}<br>
                                <small>Likes: ${tweet.likes} | Retweets: ${tweet.retweets} | ${tweet.created_at}</small>
                            </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                }
            })
            .catch(error => {
                resultsDiv.innerHTML = `<div class="error">Error: ${error}</div>`;
            });
        }

        function searchReddit() {
            const subreddit = document.getElementById('reddit-subreddit').value;
            const count = document.getElementById('reddit-count').value;
            const resultsDiv = document.getElementById('reddit-results');
            
            resultsDiv.innerHTML = '<p>Loading...</p>';
            
            fetch('/api/reddit', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({subreddit: subreddit, count: count})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                } else {
                    let html = `<h3>Found ${data.posts.length} posts from r/${subreddit}:</h3>`;
                    data.posts.forEach(post => {
                        html += `
                            <div class="post">
                                <strong>${post.title}</strong><br>
                                ${post.selftext ? post.selftext.substring(0, 200) + '...' : ''}<br>
                                <small>Score: ${post.score} | Comments: ${post.comments} | by u/${post.author} | ${post.created_at}</small>
                            </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                }
            })
            .catch(error => {
                resultsDiv.innerHTML = `<div class="error">Error: ${error}</div>`;
            });
        }

        function searchYouTube() {
            const query = document.getElementById('youtube-query').value;
            const count = document.getElementById('youtube-count').value;
            const resultsDiv = document.getElementById('youtube-results');
            
            resultsDiv.innerHTML = '<p>Loading...</p>';
            
            fetch('/api/youtube', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query: query, count: count})
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    resultsDiv.innerHTML = `<div class="error">${data.error}</div>`;
                } else {
                    let html = `<h3>Found ${data.videos.length} videos:</h3>`;
                    data.videos.forEach(video => {
                        html += `
                            <div class="post">
                                <strong>${video.title}</strong><br>
                                Channel: ${video.channel}<br>
                                ${video.description.substring(0, 150)}...<br>
                                <small>Views: ${video.views} | Published: ${video.published_at}</small><br>
                                <a href="https://www.youtube.com/watch?v=${video.video_id}" target="_blank">Watch Video</a>
                            </div>
                        `;
                    });
                    resultsDiv.innerHTML = html;
                }
            })
            .catch(error => {
                resultsDiv.innerHTML = `<div class="error">Error: ${error}</div>`;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/twitter', methods=['POST'])
def get_twitter_data():
    try:
        data = request.json
        query = data.get('query', '')
        count = int(data.get('count', 10))
        
        # Initialize Twitter API client
        client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN)
        
        # Search for tweets
        tweets = client.search_recent_tweets(
            query=query,
            max_results=min(count, 100),
            tweet_fields=['created_at', 'public_metrics', 'author_id'],
            expansions=['author_id'],
            user_fields=['username']
        )
        
        # Format results
        results = []
        if tweets.data:
            users = {user.id: user.username for user in tweets.includes['users']}
            
            for tweet in tweets.data:
                results.append({
                    'text': tweet.text,
                    'author': users.get(tweet.author_id, 'Unknown'),
                    'created_at': str(tweet.created_at),
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count']
                })
        
        return jsonify({'tweets': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/reddit', methods=['POST'])
def get_reddit_data():
    try:
        data = request.json
        subreddit_name = data.get('subreddit', 'python')
        count = int(data.get('count', 10))
        
        # Initialize Reddit API client
        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT
        )
        
        # Get subreddit posts
        subreddit = reddit.subreddit(subreddit_name)
        posts = subreddit.hot(limit=min(count, 100))
        
        # Format results
        results = []
        for post in posts:
            results.append({
                'title': post.title,
                'author': str(post.author),
                'score': post.score,
                'comments': post.num_comments,
                'selftext': post.selftext,
                'url': post.url,
                'created_at': datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify({'posts': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/youtube', methods=['POST'])
def get_youtube_data():
    try:
        data = request.json
        query = data.get('query', '')
        count = int(data.get('count', 10))
        
        # Initialize YouTube API client
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Search for videos
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=min(count, 50),
            type='video'
        ).execute()
        
        # Format results
        results = []
        for item in search_response.get('items', []):
            video_id = item['id']['videoId']
            snippet = item['snippet']
            
            # Get video statistics
            video_stats = youtube.videos().list(
                part='statistics',
                id=video_id
            ).execute()
            
            stats = video_stats['items'][0]['statistics'] if video_stats['items'] else {}
            
            results.append({
                'video_id': video_id,
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'description': snippet['description'],
                'published_at': snippet['publishedAt'],
                'views': stats.get('viewCount', 'N/A')
            })
        
        return jsonify({'videos': results})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
