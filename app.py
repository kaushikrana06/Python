from flask import Flask, request, jsonify
import requests
import datetime
from email.utils import parsedate_to_datetime

app = Flask(__name__)

# Replace with the actual base URL of the existing API
YLYTIC_API_BASE_URL = "https://app.ylytic.com/ylytic/test"

def fetch_comments():
    response = requests.get(YLYTIC_API_BASE_URL)
    if response.status_code == 200:
        return response.json().get('comments', [])
    else:
        return []

def filter_by_author(comments, author):
    return [comment for comment in comments if author.lower() in comment['author'].lower()]

def filter_by_date_range(comments, start_date, end_date):
    start = datetime.datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.datetime.strptime(end_date, "%d-%m-%Y")
    return [comment for comment in comments if start <= parsedate_to_datetime(comment['at']).replace(tzinfo=None) <= end]

def filter_by_likes(comments, like_from, like_to):
    return [comment for comment in comments if like_from <= comment['like'] <= like_to]

def filter_by_replies(comments, reply_from, reply_to):
    return [comment for comment in comments if reply_from <= comment['reply'] <= reply_to]

def filter_by_text(comments, search_text):
    return [comment for comment in comments if search_text.lower() in comment['text'].lower()]

@app.route('/search', methods=['GET'])
def search_comments():
    comments = fetch_comments()

    search_author = request.args.get('search_author')
    at_from = request.args.get('at_from')
    at_to = request.args.get('at_to')
    like_from = request.args.get('like_from', 0, type=int)
    like_to = request.args.get('like_to', float('inf'), type=int)
    reply_from = request.args.get('reply_from', 0, type=int)
    reply_to = request.args.get('reply_to', float('inf'), type=int)
    search_text = request.args.get('search_text')

    if search_author:
        comments = filter_by_author(comments, search_author)
    if at_from and at_to:
        comments = filter_by_date_range(comments, at_from, at_to)
    comments = filter_by_likes(comments, like_from, like_to)
    comments = filter_by_replies(comments, reply_from, reply_to)
    if search_text:
        comments = filter_by_text(comments, search_text)

    return jsonify(comments)

if __name__ == '__main__':
    app.run(debug=True)
