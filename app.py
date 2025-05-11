import os
import importlib
import toml
from flask import Flask, render_template, Blueprint, jsonify, request
from werkzeug.middleware.dispatcher import DispatcherMiddleware

app = Flask(__name__)
secrets = toml.load("./main_stie/secret.toml")
app.secret_key = secrets.get("FLASK_SECRET_KEY", "default_fallback_secret_key_for_dev")

blueprints_info = []

def register_blueprints(root_dir = '.'):
    """
    מחפש את כל תתי-התיקיות שמכילות קובץ app.py,
    מייבא את האובייקט app מכל אחד מהם, ורושם אותו כ-Blueprint
    """

    root_dir = '.' if os.path.basename(os.getcwd()) == 'main_site' else './mysite'
    

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
    return r"https://scontent.ftlv20-1.fna.fbcdn.net/v/t39.30808-6/488657718_10162663334768762_1199208800404180674_n.png?stp=dst-jpg_tt6&_nc_cat=111&ccb=1-7&_nc_sid=2285d6&_nc_eui2=AeHDT9Bj2dsITYn699RsrfsK0DTEvFjGxojQNMS8WMbGiApYnoVwIvcirXrvyKGBfXs&_nc_ohc=APK7CZ8wCx4Q7kNvwHoy5iT&_nc_oc=AdlCmnG7SqfGOLOVZp_P-as1sV0UFA_yk2Dlhy2hKhv9vnAq5L5RZpFHBeFtwZRNM0ZRXYEQmYHiggiIbxkjnQhl&_nc_zt=23&_nc_ht=scontent.ftlv20-1.fna&_nc_gid=csO9B-xftwdPqV6tw_LeEg&oh=00_AfKnzRiVI5bH2pQjbRHK8OTXtjvr_VaDxLjaziSR2qXGgQ&oe=6823AE3Chttps://scontent.ftlv20-1.fna.fbcdn.net/v/t39.30808-6/488657718_10162663334768762_1199208800404180674_n.png?stp=dst-jpg_tt6&_nc_cat=111&ccb=1-7&_nc_sid=2285d6&_nc_eui2=AeHDT9Bj2dsITYn699RsrfsK0DTEvFjGxojQNMS8WMbGiApYnoVwIvcirXrvyKGBfXs&_nc_ohc=APK7CZ8wCx4Q7kNvwHtjX2o&_nc_oc=AdlCmnG7SqfGOLOVZp_P-as1sV0UFA_yk2Dlhy2hKhv9vnAq5L5RZpFHBeFtwZRNM0ZRXYEQmYHiggiIbxkjnQhl&_nc_zt=23&_nc_ht=scontent.ftlv20-1.fna&_nc_gid=csO9B-xftwdPqV6tw_LeEg&oh=00_AfKnzRiVI5bH2pQjbRHK8OTXtjvr_VaDxLjaziSR2qXGgQ&oe=6823AE3C"
    

register_blueprints()
if __name__ == '__main__':
    # כדי להריץ את האפליקציה הזו, תשתמש בשרת WSGI כמו Gunicorn או Waitress
    # לדוגמה: gunicorn main_site.app:application
    # אם אתה מריץ ישירות דרך פייתון (לצורכי פיתוח):
    #from werkzeug.serving import run_simple
    #run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)
    app.run(debug=True,port=os.environ.get("PORT", 5000)) 
