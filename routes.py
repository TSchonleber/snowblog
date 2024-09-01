from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from extensions import db
from models import Post, User
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import logging
import re
from flask_login import login_required, current_user, login_user, logout_user
import openai
from ai_utils import generate_image, text_chat
from openai import OpenAI
from io import BytesIO
import base64
import traceback  # Add this import

bp = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)

def extract_youtube_id(url):
    # This regex matches various forms of YouTube URLs
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})'
    match = re.match(youtube_regex, url)
    return match.group('id') if match else None

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class AIModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    api_type = db.Column(db.String(20), nullable=False)  # 'openai', 'fal', 'claude', 'gemini', etc.

@bp.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('home.html', posts=posts)

@bp.route('/post/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', post=post)

@bp.route('/post/new', methods=['GET', 'POST'])
def create_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['image_url']
        new_post = Post(title=title, content=content, file_url=image_url, created_at=datetime.utcnow())
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_post.html')

@bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title = request.form['title']
        post.content = request.form['content']
        post.file_url = request.form['image_url']
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('main.view_post', post_id=post.id))
    return render_template('edit_post.html', post=post)

@bp.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('main.home'))

@bp.route('/api/posts', methods=['GET', 'POST'])
def api_posts():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.created_at.desc()).all()
        print(f"Fetched {len(posts)} posts")
        return jsonify([post.to_dict() for post in posts])

    if request.method == 'POST':
        if not current_user.is_authenticated:
            return jsonify({"error": "You must be logged in to create a post"}), 401
        
        title = request.form.get('title')
        content = request.form.get('content', '')
        video_url = request.form.get('videoUrl')
        file = request.files.get('file')

        if not title:
            return jsonify({"error": "Title is required"}), 400

        new_post = Post(title=title, content=content, author=current_user)

        if video_url:
            youtube_id = extract_youtube_id(video_url)
            if youtube_id:
                new_post.video_url = f'https://www.youtube.com/embed/{youtube_id}'
            else:
                new_post.video_url = video_url

        if file and file.filename:
            filename = secure_filename(file.filename)
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            new_post.file_url = f'/uploads/{filename}'
            new_post.file_type = file.content_type.split('/')[0]
            logging.debug(f"File saved: {file_path}")

        try:
            db.session.add(new_post)
            db.session.commit()
            logging.debug(f"New post created: {new_post.to_dict()}")
            return jsonify(new_post.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error creating post: {str(e)}")
            return jsonify({"error": "An error occurred while creating the post"}), 500

@bp.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@bp.route('/api/posts/<int:post_id>', methods=['DELETE', 'PUT'])
@login_required
def manage_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and not current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403

    if request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()
        return jsonify({"message": "Post deleted successfully"}), 200

    if request.method == 'PUT':
        data = request.form
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename:
                filename = secure_filename(file.filename)
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                post.file_url = f'/uploads/{filename}'
                post.file_type = file.content_type.split('/')[0]
        
        db.session.commit()
        return jsonify(post.to_dict()), 200

@bp.route('/api/ai-models', methods=['GET'])
@login_required
def get_ai_models():
    models = AIModel.query.all()
    return jsonify([{'id': m.id, 'name': m.name, 'type': m.type, 'isActive': m.is_active, 'apiType': m.api_type} for m in models])

@bp.route('/api/ai-models', methods=['POST'])
@login_required
def add_ai_model():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    new_model = AIModel(name=data['name'], type=data['type'], is_active=data.get('isActive', True), api_type=data['apiType'])
    db.session.add(new_model)
    db.session.commit()
    return jsonify({'id': new_model.id, 'name': new_model.name, 'type': new_model.type, 'isActive': new_model.is_active, 'apiType': new_model.api_type}), 201

@bp.route('/api/ai/text', methods=['POST'])
@login_required
def ai_text_response():
    data = request.get_json()
    message = data.get('message')
    model_name = data.get('model')
    
    logging.info(f"Received text generation request. Message: {message}, Model: {model_name}")

    if not message:
        logging.error("No message provided in request")
        return jsonify({"error": "No message provided"}), 400

    try:
        response = text_chat(message, [], model_name)
        logging.info(f"Text generation successful. Response: {response[-1][1]}")
        return jsonify({"response": response[-1][1]})
    except Exception as e:
        logging.error(f"AI API error: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({"error": f"Failed to generate text: {str(e)}"}), 500

@bp.route('/api/ai/image', methods=['POST'])
@login_required
def ai_image_response():
    prompt = request.form.get('prompt', '')
    model = request.form.get('model', 'flux-dev')
    
    logging.info(f"Received request for model: {model}, prompt: {prompt}")
    
    uploaded_images = []
    for key, file in request.files.items():
        if key.startswith('image') and file.filename != '':
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            uploaded_images.append(file_path)

    try:
        image_data = generate_image(prompt, model, uploaded_images)
        if image_data:
            # Convert PIL Image to base64 string
            buffered = BytesIO()
            image_data.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return jsonify({"image_data": f"data:image/png;base64,{img_str}"})
        else:
            logging.error("Failed to generate image: No image data returned")
            return jsonify({"error": "Failed to generate image: No image data returned"}), 500
    except ValueError as e:
        logging.error(f"ValueError in image generation: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except TimeoutError as e:
        logging.error(f"TimeoutError in image generation: {str(e)}")
        return jsonify({"error": str(e)}), 504  # Gateway Timeout
    except ConnectionError as e:
        logging.error(f"ConnectionError in image generation: {str(e)}")
        return jsonify({"error": str(e)}), 503  # Service Unavailable
    except Exception as e:
        logging.error(f"AI API error: {str(e)}")
        return jsonify({"error": f"Failed to generate image: {str(e)}"}), 500

@bp.route('/api/test_posts', methods=['GET'])
def test_posts():
    posts = Post.query.all()
    return jsonify({
        'count': len(posts),
        'posts': [{'id': post.id, 'title': post.title} for post in posts]
    })

@bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    print('Login attempt:', data.get('username'))
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.check_password(data.get('password')):
        login_user(user)
        return jsonify({'message': 'Logged in successfully', 'user': user.to_dict()}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

@bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/auth/check-auth', methods=['GET'])
def check_auth():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': current_user.to_dict()}), 200
    return jsonify({'authenticated': False}), 200

@bp.route('/api/posts', methods=['GET'])
def get_posts():  # Changed function name from api_posts to get_posts
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return jsonify([post.to_dict() for post in posts])