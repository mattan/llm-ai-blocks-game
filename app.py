import os
from flask import Flask, render_template, Blueprint, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware


# ייבוא של אפליקציות המשנה
# נניח שבתוך blocks/app.py יש אובייקט אפליקציה בשם 'application'
# ובתוך messeges_ai/app.py יש אובייקט אפליקציה בשם 'application'
from blocks.app import app as blocks_app # שנה את הנתיב בהתאם למבנה שלך
from messeges_ai.app import app as messeges_ai_app # שנה את הנתיב
from yentel.app import app as yentel_app # שנה את הנתיב


app = Flask(__name__)

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')


@app.route('/update', methods=['POST'])
def update():
    """Update the application by pulling from git repository."""
    import subprocess
    # Define the Git repository path
    git_repo_path = '/home/Mattan/mysite'

    output = subprocess.check_output(
            ['git', 'pull'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path  # Specify the working directory
        )
    return jsonify(output)

    



# הגדרת ה-DispatcherMiddleware
# המפתח הוא ה-prefix של ה-URL, והערך הוא אובייקט האפליקציה שיטפל בו
application = DispatcherMiddleware(app, {
    '/blocks': blocks_app,
    '/messeges_ai': messeges_ai_app,
    '/yentel': yentel_app,
})

if __name__ == '__main__':
    # כדי להריץ את האפליקציה הזו, תשתמש בשרת WSGI כמו Gunicorn או Waitress
    # לדוגמה: gunicorn main_site.app:application
    # אם אתה מריץ ישירות דרך פייתון (לצורכי פיתוח):
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)
