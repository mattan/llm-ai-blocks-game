import os
from flask import Flask, render_template, Blueprint, jsonify
from werkzeug.middleware.dispatcher import DispatcherMiddleware


app = Flask(__name__)

# Assuming the sub-applications have their own static and template folders
# We need to tell Flask where to find them.

# Serve files from the blocks project
blocks_bp = Blueprint('blocks', __name__,
                      template_folder='blocks/templates',
                      static_folder='blocks/static',  # Assuming a static folder exists
                      url_prefix='/blocks')

@blocks_bp.route('/')
def blocks_index():
    return render_template('index.html')  # Assumes blocks/templates/index.html

app.register_blueprint(blocks_bp)

# Serve files from the messeges_ai project
messeges_ai_bp = Blueprint('messeges_ai', __name__,
                           template_folder='messeges_ai/templates',
                           static_folder='messeges_ai/static',  # Assuming a static folder exists
                           url_prefix='/messeges_ai')

@messeges_ai_bp.route('/')
def messeges_ai_index():
    return render_template('index.html')  # Assumes messeges_ai/templates/index.html

app.register_blueprint(messeges_ai_bp)

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

    


if __name__ == '__main__':

    # ייבוא של אפליקציות המשנה
    # נניח שבתוך blocks/app.py יש אובייקט אפליקציה בשם 'application'
    # ובתוך messeges_ai/app.py יש אובייקט אפליקציה בשם 'application'
    from blocks.app import app as blocks_app # שנה את הנתיב בהתאם למבנה שלך
    from messeges_ai.app import app as messeges_ai_app # שנה את הנתיב

    # הגדרת ה-DispatcherMiddleware
    # המפתח הוא ה-prefix של ה-URL, והערך הוא אובייקט האפליקציה שיטפל בו
    application = DispatcherMiddleware(app, {
        '/blocks': blocks_app,
        '/messeges_ai': messeges_ai_app,
    })

    # כדי להריץ את האפליקציה הזו, תשתמש בשרת WSGI כמו Gunicorn או Waitress
    # לדוגמה: gunicorn main_site.app:application
    # אם אתה מריץ ישירות דרך פייתון (לצורכי פיתוח):
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True) 
