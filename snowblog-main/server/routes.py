from flask import jsonify, request, render_template_string, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from server import db
from server.models import Post, User
from server.email import send_password_reset_email, send_email_confirmation
from urllib.parse import urlparse

def init_routes(app):
    @app.route('/api/posts', methods=['GET'])
    def get_posts():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return jsonify([post.to_dict() for post in posts])

    @app.route('/api/posts', methods=['POST'])
    def create_post():
        data = request.json or request.form
        new_post = Post(title=data['title'], content=data['content'], image_url=data.get('image_url'))
        db.session.add(new_post)
        db.session.commit()
        return jsonify(new_post.to_dict()), 201

    @app.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            flash('You can only edit your own posts.')
            return redirect(url_for('home'))
        if request.method == 'POST':
            post.title = request.form['title']
            post.content = request.form['content']
            post.image_url = request.form['image_url']
            db.session.commit()
            return redirect(url_for('home'))
        return render_template_string(base_template.replace('{% block content %}{% endblock %}', edit_post_template), post=post)

    @app.route('/post/<int:post_id>/delete', methods=['POST'])
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.user_id != current_user.id:
            flash('You can only delete your own posts.')
            return redirect(url_for('home'))
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('home'))

    @app.route('/')
    def home():
        posts = Post.query.order_by(Post.created_at.desc()).all()
        return render_template_string(base_template.replace('{% block content %}{% endblock %}', home_template), posts=posts)

    @app.route('/new_post', methods=['GET', 'POST'])
    @login_required
    def new_post():
        if request.method == 'POST':
            new_post = Post(
                title=request.form['title'],
                content=request.form['content'],
                image_url=request.form['image_url'],
                user_id=current_user.id
            )
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('home'))
        return render_template_string(base_template.replace('{% block content %}{% endblock %}', new_post_template))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            if User.query.filter_by(username=username).first():
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('register'))
            if User.query.filter_by(email=email).first():
                flash('Email already registered. Please use a different email.')
                return redirect(url_for('register'))
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('login'))
        return render_template_string(register_template)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        print("Login route accessed")  # Debug print
        if current_user.is_authenticated:
            print("User already authenticated")  # Debug print
            return redirect(url_for('home'))
        if request.method == 'POST':
            print("POST request received")  # Debug print
            username = request.form['username']
            password = request.form['password']
            print(f"Attempting login for user: {username}")  # Debug print
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                print("Invalid username or password")  # Debug print
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=request.form.get('remember_me'))
            print(f"User {username} logged in successfully")  # Debug print
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        return render_template_string(login_template)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/reset_password_request', methods=['GET', 'POST'])
    def reset_password_request():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        if request.method == 'POST':
            user = User.query.filter_by(email=request.form['email']).first()
            if user:
                send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password')
            return redirect(url_for('login'))
        return render_template_string(reset_password_request_template)

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        user = User.verify_reset_token(token)
        if not user:
            return redirect(url_for('home'))
        if request.method == 'POST':
            user.set_password(request.form['password'])
            db.session.commit()
            flash('Your password has been reset.')
            return redirect(url_for('login'))
        return render_template_string(reset_password_template)

# HTML templates
base_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Terrence's Treasure Trove</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: #f4f4f4; }
        .container { width: 80%; margin: auto; overflow: hidden; padding: 20px; }
        header { background: #35424a; color: white; padding: 20px 0; }
        header a { color: #ffffff; text-decoration: none; text-transform: uppercase; font-size: 16px; }
        header ul { padding: 0; margin: 0; list-style: none; }
        header li { display: inline; padding: 0 20px 0 20px; }
        header #branding { float: left; }
        header #branding h1 { margin: 0; }
        header nav { float: right; margin-top: 10px; }
        .highlight, header .current a { color: #e8491d; font-weight: bold; }
        .post { background: #fff; padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .btn { display: inline-block; padding: 10px 30px; background: #35424a; color: #ffffff; text-decoration: none; border: none; border-radius: 5px; cursor: pointer; transition: background-color 0.3s; }
        .btn:hover { background-color: #e8491d; }
        form div { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; }
        input[type="text"], input[type="url"], textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        textarea { height: 150px; }
        .form-container { max-width: 400px; margin: 20px auto; padding: 20px; background: #fff; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .form-container h1 { text-align: center; color: #35424a; }
        .form-container input[type="text"], .form-container input[type="password"], .form-container input[type="email"] { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .form-container input[type="submit"] { width: 100%; padding: 10px; background: #35424a; color: #fff; border: none; border-radius: 4px; cursor: pointer; }
        .form-container input[type="submit"]:hover { background: #e8491d; }
        .flash-messages { list-style-type: none; padding: 0; }
        .flash-message { background: #f8d7da; color: #721c24; padding: 10px; margin-bottom: 10px; border-radius: 4px; }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <div id="branding">
                <h1><span class="highlight">Terrence's</span> Treasure Trove</h1>
            </div>
            <nav>
                <ul>
                    <li class="current"><a href="{{ url_for('home') }}">Home</a></li>
                    {% if current_user.is_authenticated %}
                        <li><a href="{{ url_for('new_post') }}">New Post</a></li>
                        <li><a href="{{ url_for('logout') }}">Logout</a></li>
                    {% else %}
                        <li><a href="{{ url_for('login') }}">Login</a></li>
                        <li><a href="{{ url_for('register') }}">Register</a></li>
                    {% endif %}
                </ul>
            </nav>
        </div>
    </header>
    <div class="container">
        {% with messages = get_flashed_messages() %}
        {% if messages %}
            <ul class="flash-messages">
            {% for message in messages %}
                <li class="flash-message">{{ message }}</li>
            {% endfor %}
            </ul>
        {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
</body>
</html>
'''

home_template = '''
<h1>Recent Posts</h1>
{% for post in posts %}
    <div class="post">
        <h2>{{ post.title }}</h2>
        <p>{{ post.content }}</p>
        {% if post.image_url %}
            <img src="{{ post.image_url }}" alt="{{ post.title }}" style="max-width: 100%; height: auto; margin-top: 10px;">
        {% endif %}
        <p><small>Created at: {{ post.created_at }} by {{ post.user.username }}</small></p>
        {% if current_user.is_authenticated and current_user.id == post.user_id %}
            <a href="{{ url_for('edit_post', post_id=post.id) }}" class="btn">Edit</a>
            <form action="{{ url_for('delete_post', post_id=post.id) }}" method="post" style="display: inline;">
                <input type="submit" value="Delete" class="btn" onclick="return confirm('Are you sure you want to delete this post?');">
            </form>
        {% endif %}
    </div>
{% endfor %}
'''

new_post_template = '''
<h1>Create New Post</h1>
<form method="post">
    <div>
        <label for="title">Title:</label>
        <input type="text" id="title" name="title" required>
    </div>
    <div>
        <label for="content">Content:</label>
        <textarea id="content" name="content" required></textarea>
    </div>
    <div>
        <label for="image_url">Image URL (optional):</label>
        <input type="url" id="image_url" name="image_url">
    </div>
    <div>
        <input type="submit" value="Create Post" class="btn">
    </div>
</form>
'''

edit_post_template = '''
<h1>Edit Post</h1>
<form method="post">
    <div>
        <label for="title">Title:</label>
        <input type="text" id="title" name="title" value="{{ post.title }}" required>
    </div>
    <div>
        <label for="content">Content:</label>
        <textarea id="content" name="content" required>{{ post.content }}</textarea>
    </div>
    <div>
        <label for="image_url">Image URL (optional):</label>
        <input type="url" id="image_url" name="image_url" value="{{ post.image_url }}">
    </div>
    <div>
        <input type="submit" value="Update Post" class="btn">
    </div>
</form>
'''

login_template = '''
<div class="form-container">
    <h1>Sign In</h1>
    <form action="" method="post" novalidate>
        <div>
            <input type="text" id="username" name="username" placeholder="Username" required>
        </div>
        <div>
            <input type="password" id="password" name="password" placeholder="Password" required>
        </div>
        <div>
            <label>
                <input type="checkbox" name="remember_me"> Remember Me
            </label>
        </div>
        <div>
            <input type="submit" value="Sign In">
        </div>
    </form>
    <p>New User? <a href="{{ url_for('register') }}">Click to Register!</a></p>
    <p><a href="{{ url_for('reset_password_request') }}">Forgot Password?</a></p>
</div>
'''

register_template = '''
<div class="form-container">
    <h1>Register</h1>
    <form action="" method="post">
        <div>
            <input type="text" id="username" name="username" placeholder="Username" required>
        </div>
        <div>
            <input type="email" id="email" name="email" placeholder="Email" required>
        </div>
        <div>
            <input type="password" id="password" name="password" placeholder="Password" required>
        </div>
        <div>
            <input type="submit" value="Register">
        </div>
    </form>
    <p>Already have an account? <a href="{{ url_for('login') }}">Click to Sign In!</a></p>
</div>
'''

reset_password_request_template = '''
<h1>Reset Password</h1>
<form action="" method="post">
    <p>
        <label for="email">Email</label>
        <input type="email" id="email" name="email" required>
    </p>
    <p><input type="submit" value="Reset Password"></p>
</form>
'''

reset_password_template = '''
<h1>Reset Your Password</h1>
<form action="" method="post">
    <p>
        <label for="password">New Password</label>
        <input type="password" id="password" name="password" required>
    </p>
    <p><input type="submit" value="Reset Password"></p>
</form>
'''