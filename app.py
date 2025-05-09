import os
from flask import Flask, render_template, Blueprint, jsonify, request
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


@app.route('/favicon.ico')
def favicon():
    return r"https://scontent.ftlv20-1.fna.fbcdn.net/v/t39.30808-6/488657718_10162663334768762_1199208800404180674_n.png?stp=dst-jpg_tt6&_nc_cat=111&ccb=1-7&_nc_sid=2285d6&_nc_eui2=AeHDT9Bj2dsITYn699RsrfsK0DTEvFjGxojQNMS8WMbGiApYnoVwIvcirXrvyKGBfXs&_nc_ohc=APK7CZ8wCx4Q7kNvwHoy5iT&_nc_oc=AdlCmnG7SqfGOLOVZp_P-as1sV0UFA_yk2Dlhy2hKhv9vnAq5L5RZpFHBeFtwZRNM0ZRXYEQmYHiggiIbxkjnQhl&_nc_zt=23&_nc_ht=scontent.ftlv20-1.fna&_nc_gid=csO9B-xftwdPqV6tw_LeEg&oh=00_AfKnzRiVI5bH2pQjbRHK8OTXtjvr_VaDxLjaziSR2qXGgQ&oe=6823AE3Chttps://scontent.ftlv20-1.fna.fbcdn.net/v/t39.30808-6/488657718_10162663334768762_1199208800404180674_n.png?stp=dst-jpg_tt6&_nc_cat=111&ccb=1-7&_nc_sid=2285d6&_nc_eui2=AeHDT9Bj2dsITYn699RsrfsK0DTEvFjGxojQNMS8WMbGiApYnoVwIvcirXrvyKGBfXs&_nc_ohc=APK7CZ8wCx4Q7kNvwHtjX2o&_nc_oc=AdlCmnG7SqfGOLOVZp_P-as1sV0UFA_yk2Dlhy2hKhv9vnAq5L5RZpFHBeFtwZRNM0ZRXYEQmYHiggiIbxkjnQhl&_nc_zt=23&_nc_ht=scontent.ftlv20-1.fna&_nc_gid=csO9B-xftwdPqV6tw_LeEg&oh=00_AfKnzRiVI5bH2pQjbRHK8OTXtjvr_VaDxLjaziSR2qXGgQ&oe=6823AE3C"
    
    
app.register_blueprint(blocks_app)
app.register_blueprint(messeges_ai_app)
app.register_blueprint(yentel_app)



# הגדרת ה-DispatcherMiddleware
# המפתח הוא ה-prefix של ה-URL, והערך הוא אובייקט האפליקציה שיטפל בו
application = DispatcherMiddleware(app, {
    '/blocks': blocks_app,
    '/messeges_ai': messeges_ai_app,
    '/yentel': yentel_app,
})



###############################################
# don't code review this
###############################################

@app.route('/debug/')
def debug_routes():
    debug_info = []
    debug_info.append("<h2>הגדרות DispatcherMiddleware:</h2>")
    debug_info.append("<ul>")
    debug_info.append("<li>אפליקציה ראשית: / (root)</li>")
    debug_info.append("<li>תת-אפליקציה: /blocks -> blocks_app</li>")
    debug_info.append("<li>תת-אפליקציה: /messeges_ai -> messeges_ai_app</li>")
    debug_info.append("<li>תת-אפליקציה: /yentel -> yentel_app</li>")
    debug_info.append("</ul>")
    
    debug_info.append("<h2>פרטי בקשה נוכחית:</h2>")
    debug_info.append("<ul>")
    debug_info.append(f"<li>URL: {request.url}</li>")
    debug_info.append(f"<li>Path: {request.path}</li>")
    debug_info.append(f"<li>Host: {request.host}</li>")
    debug_info.append(f"<li>Script Root: {request.script_root}</li>")
    debug_info.append("</ul>")
    
    debug_info.append("<h2>נתיבים מוגדרים:</h2>")
    apps = {
        'app (ראשי)': app,
        'blocks_app': blocks_app,
        'messeges_ai_app': messeges_ai_app,
        'yentel_app': yentel_app
    }
    
    for name, flask_app in apps.items():
        debug_info.append(f"<h3>{name}:</h3><ul>")
        for rule in flask_app.url_map.iter_rules():
            if not str(rule).startswith('/static'):
                debug_info.append(f"<li>{rule} ({', '.join(rule.methods)})</li>")
        debug_info.append("</ul>")
    
    # קישורים לבדיקה
    debug_info.append("<h2>קישורים לבדיקה:</h2>")
    debug_info.append("<ul>")
    debug_info.append('<li><a href="/">דף ראשי</a></li>')
    debug_info.append('<li><a href="/blocks/">blocks</a></li>')
    debug_info.append('<li><a href="/messeges_ai/">messeges_ai</a></li>')
    debug_info.append('<li><a href="/yentel/">yentel</a></li>')
    debug_info.append("</ul>")
    
    html = f"""
    <!DOCTYPE html>
    <html dir="rtl">
    <head>
        <title>דיבוג Flask DispatcherMiddleware</title>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; direction: rtl; }}
            h1, h2, h3 {{ color: #333; }}
            ul {{ margin-bottom: 20px; }}
            li {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <h1>דיבוג Flask DispatcherMiddleware</h1>
        {''.join(debug_info)}
    </body>
    </html>
    """
    
    return html




if __name__ == '__main__':
    # כדי להריץ את האפליקציה הזו, תשתמש בשרת WSGI כמו Gunicorn או Waitress
    # לדוגמה: gunicorn main_site.app:application
    # אם אתה מריץ ישירות דרך פייתון (לצורכי פיתוח):
    #from werkzeug.serving import run_simple
    #run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)
    app.run(debug=True,port=os.environ.get("PORT", 5000)) 