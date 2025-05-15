import os
import importlib
import toml
from flask import Flask, render_template, jsonify, request, redirect

app = Flask(__name__)

blueprints_info = []

def register_blueprints(root_dir = '.'):
    """
    מחפש את כל תתי-התיקיות שמכילות קובץ app.py,
    מייבא את האובייקט app מכל אחד מהם, ורושם אותו כ-Blueprint
    """

    root_dir = '.' if os.path.basename(os.getcwd()) == 'main_site' else './mysite'
    secrets = toml.load(f"{root_dir}/secret.toml")
    app.secret_key = secrets.get("FLASK_SECRET_KEY", "default_fallback_secret_key_for_dev")
    

    # עוברים על כל התיקיות תחת תיקיית השורש
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # מדלגים על תיקיית השורש עצמה
        if dirpath == root_dir:
            continue
        
        # בודקים אם קיים קובץ app.py בתיקייה הנוכחית
        if 'app.py' in filenames:
            try:
                                
                # טעינת המודול
                module = importlib.import_module(os.path.basename(dirpath) + ".app")
                
                # בדיקה אם יש אובייקט app במודול
                if hasattr(module, 'app'):
                    sub_app = getattr(module, 'app')
                    
                    # רישום ה-Blueprint
                    app.register_blueprint(sub_app)
                    
                    # חילוץ השדות הנדרשים
                    blueprint_info = {
                        'name': getattr(sub_app, 'name', ''),
                        'html_name': getattr(sub_app, 'html_name', 'אפליקציה ללא שם'),
                        'html_creator': getattr(sub_app, 'html_creator', 'אנונימי'),
                        'html_link': getattr(sub_app, 'html_link', ''),
                        'html_img': getattr(sub_app, 'html_img', '')
                    }
                    
                    blueprints_info.append(blueprint_info)
                    
            except Exception as e:
                blueprint_info = {
                        'name': dirpath,
                        'html_name': "",
                        'html_creator': str(e),
                        'html_link': "",
                        'html_img': ""
                    }
                    
                blueprints_info.append(blueprint_info)
                print(f"שגיאה בייבוא {dirpath}/app.py: {e}")


def get_redirect_uri():
    """
    Gets the appropriate redirect URI based on the current host.
    This function dynamically determines if we're on localhost or a production server.
    """
    if 'PYTHONANYWHERE_SITE' in os.environ:
        # Production environment (PythonAnywhere)
        return 'https://mattan.pythonanywhere.com/login/google/callback'
    elif os.environ.get('FLASK_ENV') == 'production':
        # Other production environment
        return 'https://yourdomain.com/login/google/callback'
    else:
        # Local development
        port = os.environ.get("PORT", 5001)
        return f'http://localhost:{port}/login/google/callback'


@app.route('/')
def index():
    """Render the main game page."""
    print(blueprints_info)
    return render_template('index.html',blueprints = blueprints_info)

@app.route('/2')
def index2():
    """Render the main game page."""
    print(blueprints_info)
    return render_template('index2.html',blueprints = blueprints_info)


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


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), 'favicon.ico')
    

@app.route('/login/google/callback')
def google_callback_redirect():
    """מפנה קריאות חזרה של Google OAuth לבלופרינט המתאים"""
    # מעביר את פרמטרי ה-query string לכתובת המלאה
    return redirect('/messeges_aoti/login/google/callback' + '?' + request.query_string.decode())


register_blueprints()
if __name__ == '__main__':
    # כדי להריץ את האפליקציה הזו, תשתמש בשרת WSGI כמו Gunicorn או Waitress
    # לדוגמה: gunicorn main_site.app:application
    # אם אתה מריץ ישירות דרך פייתון (לצורכי פיתוח):
    #from werkzeug.serving import run_simple
    #run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)
    app.run(debug=True,port=os.environ.get("PORT", 5001)) 
