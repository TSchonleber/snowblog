from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_from_directory
from extensions import db
from models import Post
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import logging
import re
from flask_login import login_required, current_user
import openai
from ai_utils import generate_image, text_chat
from openai import OpenAI
from io import BytesIO
import base64

bp = Blueprint('main', __name__)

logging.basicConfig(level=logging.DEBUG)

def extract_youtube_id(url):
    # This regex matches various forms of YouTube URLs
    youtube_regex = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})'
    match = re.match(youtube_regex, url)
    return match.group('id') if match else None

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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
@login_required
def api_posts():
    if request.method == 'GET':
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts])
    
    elif request.method == 'POST':
        logging.debug(f"Received POST request: {request.form}")
        logging.debug(f"Files in request: {request.files}")

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
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
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

@bp.route('/api/posts/<int:post_id>', methods=['GET', 'PUT', 'DELETE'])
def api_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == 'GET':
        return jsonify({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'file_url': post.file_url,
            'file_type': post.file_type,
            'video_url': post.video_url,
            'created_at': post.created_at.isoformat()
        })

    elif request.method == 'PUT':
        data = request.json
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.video_url = data.get('videoUrl', post.video_url)
        db.session.commit()
        return jsonify({
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'file_url': post.file_url,
            'file_type': post.file_type,
            'video_url': post.video_url,
            'created_at': post.created_at.isoformat()
        })

    elif request.method == 'DELETE':
        db.session.delete(post)
        db.session.commit()
        return '', 204

@bp.route('/api/ai/text', methods=['POST'])
@login_required
def ai_text_response():
    data = request.get_json()
    message = data.get('message')
    history = data.get('history', [])
    model = data.get('model', 'gpt-3.5-turbo')

    if not message:
        return jsonify({"error": "No message provided"}), 400

    try:
        updated_history = text_chat(message, history, model)
        return jsonify({"history": updated_history})
    except Exception as e:
        logging.error(f"AI API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/ai/image', methods=['POST'])
@login_required
def ai_image_response():
    data = request.get_json()
    prompt = data.get('prompt')
    model = data.get('model', 'flux-dev')
    
    logging.info(f"Received request for model: {model}, prompt: {prompt}")
    
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    try:
        image_data = generate_image(prompt, model)
        if image_data:
            # Convert PIL Image to base64 string
            buffered = BytesIO()
            image_data.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return jsonify({"image_data": f"data:image/png;base64,{img_str}"})
        else:
            logging.error("Failed to generate image: No image data returned")
            return jsonify({"error": "Failed to generate image"}), 500
    except Exception as e:
        logging.error(f"AI API error: {str(e)}")
        return jsonify({"error": str(e)}), 500