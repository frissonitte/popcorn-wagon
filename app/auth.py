from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.extensions import db, login_manager
from app.utils.db_utils import get_user_by_username
from app.utils.auth_utils import hash_pw, verify_pw
from app.models import User

auth = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) 

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please provide both username and password', 'danger')
            return redirect(url_for('auth.login'))

        user = get_user_by_username(username)

        if user and verify_pw(user.hash, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')

        if not username or not password or not password_confirmation:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('auth.register'))

        if password != password_confirmation:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = get_user_by_username(username)
        if existing_user:
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.register'))

        hashed_password = hash_pw(password)
        new_user = User(username=username, hash=hashed_password)
        db.session.add(new_user) 
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

@auth.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)