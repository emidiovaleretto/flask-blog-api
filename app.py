from flask import Flask, jsonify, request

app = Flask(__name__)
posts = [
  
    {"title": "My first post",
    "content": "This is my first post!",
    "author": "John Doe"},

    {"title": "My second post",
    "content": "This is my second post!",
    "author": "Jane Doe"},

    {"title": "My third post",
    "content": "This is my third post!",
    "author": "John Doe"}
]

@app.route('/')
def get_post():
    return jsonify(posts)


app.run(port=5000, host='localhost', debug=True)