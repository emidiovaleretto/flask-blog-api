import jwt
from functools import wraps
from flask import jsonify, request, make_response
from datetime import datetime, timedelta
from database_config import Author, Post, app, db, SECRET_KEY

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = None
        # Verify if x-access-token exists in the request header
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        # If token is not found, return a 401 Unauthorized response
        if not token:
            return jsonify({'message': 'Token not found.'}, 401)

        try:
            response = jwt.decode(token, SECRET_KEY)
            # If token is valid, get the user_id from the token
            author = Author.query.filter_by(id_author=response['id_author']).first()
        except:
            return jsonify({'message': 'Token is invalid.'}, 401)
        return func(author, *args, **kwargs)
    return decorated


@app.route('/login')
def login():
    auth = request.authorization
    if not auth or not auth.username or not auth.password:
        return make_response(
            "Invalid login", 401, {
                'WWW-Authenticate': 'Basic realm="Login required"'
                })

    user = Author.query.filter_by(name=auth.username).first()
    if not user:
        return make_response("Invalid login", 401, {
                'WWW-Authenticate': 'Basic realm="Login required"'
                })

    time_to_expiry = datetime.utcnow() + timedelta(minutes=30)
    if auth.password == user.password:
        token = jwt.encode({
            'id_author': user.id_author,
            'exp': time_to_expiry
        }, SECRET_KEY)
        return jsonify({'token': token.decode('utf-8')})
    return make_response("Invalid login", 401, {
                'WWW-Authenticate': 'Basic realm="Login required"'
                })

@app.route('/posts')
@token_required
def get_posts(author):
    posts = Post.query.all()
    list_of_posts = []
    for post in posts:
        current_post = {}
        current_post['id_post'] = post.id_post
        current_post['title'] = post.title
        current_post['author'] = {
            'id_author': Author.query.all()[0].id_author,
            'name': Author.query.all()[0].name,
            }

        list_of_posts.append(current_post)

    return jsonify({
        'posts': list_of_posts
        }, 200) if list_of_posts else jsonify({
            'message': 'No posts found'
            }, 404)

@app.route('/posts/<int:id_post>', methods=['GET'])
@token_required
def get_post(author, id_post):
    post = Post.query.filter_by(id_post=id_post).first()
    if post:
        return jsonify({
            'id_post': post.id_post,
            'title': post.title,
            'author': {
                'id_author': Author.query.all()[0].id_author,
                'name': Author.query.all()[0].name,
            }}, 200)
    else:
        return jsonify({
            'message': 'Post not found'
            }, 404)

@app.route('/posts', methods=['POST'])
@token_required
def create_post(author):
    try:
        response = Post(
            title=request.get_json().get('title'),
            id_author = Author.query.all()[0].id_author
            )
        db.session.add(response)
        db.session.commit()
        return jsonify({
            'message': 'Post created successfully'
            }, 201)
    except:
        return jsonify({
            'message': 'Something went wrong while creating the post.'
            }, 404)
    
@app.route('/posts/<int:index>', methods=['PUT'])
@token_required
def update_post(author, index):
    post_to_update = request.get_json()
    post = Post.query.filter_by(id_post=index).first()

    if not post:
        return jsonify({"message": "Post not found"}, 404)

    try:
        post.title = post_to_update['title']
    except:
        pass
    try:
        post.id_author = post_to_update['id_author']
    except:
        pass

    db.session.commit()

    return jsonify({
        'message': 'Post updated successfully'
        }, 200)

@app.route('/posts/<int:id_post>', methods=['DELETE'])
@token_required
def delete_post(author, id_post):
    post_to_delete = Post.query.filter_by(id_post=id_post).first()
    if not post_to_delete:
        return jsonify({'message': 'Post not found'}, 404)

    db.session.delete(post_to_delete)
    db.session.commit()

    return jsonify({'message': 'Post deleted successfully'}, 200)

@app.route('/authors')
@token_required
def get_all_authors(author):
    authors = Author.query.all()
    list_authors = []
    for author in authors:
        current_author = {}
        current_author['id_author'] = author.id_author
        current_author['name'] = author.name
        current_author['email'] = author.email
        list_authors.append(current_author)
    return jsonify(list_authors)

@app.route('/authors/<int:id_author>', methods=['GET'])
@token_required
def get_author(author, id_author):
    author = Author.query.filter_by(id_author=id_author).first()
    if not author:
        return jsonify({'message': 'Author not found'}, 404)
    current_author = {}
    current_author['id_author'] = author.id_author
    current_author['name'] = author.name
    current_author['email'] = author.email
    return jsonify(current_author)

@app.route('/authors', methods=['POST'])
@token_required
def create_author(author):
    try:
        response = Author(
            name=request.get_json().get('name'), 
            password=request.get_json().get('password'), 
            email=request.get_json().get('email'),
            )
        db.session.add(response)
        db.session.commit()

        return jsonify({
            'message': f'Author [{response.name}] created successfully'
            }, 200)
    except:
        return jsonify({
            'message': 'Something went wrong while creating the author.'
            }, 400)

@app.route('/authors/<int:id_author>', methods=['PUT'])
@token_required
def update_author(author, id_author):
    author_to_update = request.get_json()
    author = Author.query.filter_by(id_author=id_author).first()
    if not author:
        return jsonify({'message': 'Author not found'}, 404)
    try:
        author.name = author_to_update['name']
    except:
        pass
    try:
        author.password = author_to_update['password']
    except:
        pass
    try:
        author.email = author_to_update['email']
    except:
        pass

    db.session.commit()
    
    return jsonify({
        'message': f'Author [{author.name}] updated successfully'
        }, 200)

@app.route('/authors/<int:id_author>', methods=['DELETE'])
@token_required
def delete_author(author, id_author):
    author_to_delete = Author.query.filter_by(id_author=id_author).first()
    if not author_to_delete:
        return jsonify({'message': 'Author not found'}, 404)

    db.session.delete(author_to_delete)
    db.session.commit()

    return jsonify({
        'message': f'Author [{author_to_delete.name}] deleted successfully'
        }, 200)

if __name__ == '__main__':
    app.run(port=5000, host='localhost', debug=True)