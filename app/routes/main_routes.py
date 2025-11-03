from flask import Blueprint, redirect, url_for, session, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def root():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('auth.login'))
    return render_template('index.html', username=session['username']) # username 변수는 index.html 템플릿에서 사용되는 변수