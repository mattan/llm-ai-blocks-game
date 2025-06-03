import os
from flask import Flask, render_template, Blueprint


app = Blueprint("token_manager",__name__, template_folder="..", url_prefix="/token_manager")
app.html_name = "מנהל הטוקנים"
app.description = "אופטימיזציה פשוטה של שימוש בטוקנים לבינה מלאכותית"
app.html_creator = "מתן"
app.html_link = "https://www.facebook.com/jju.ujj.5"
app.html_img = "/static/mattan.jpg"



@app.route('/')
def index():
    """Render the main game page."""
    return render_template('token_manager/templates/index.html')
    

@app.route('/log')
def show_log():
    log_path = os.path.join(os.path.dirname(__file__), 'gpt_log.txt')
    if not os.path.exists(log_path):
        log_content = 'No log entries yet.'
    else:
        with open(log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
    return f"""
    <html><head><title>GPT Log</title></head><body style='direction:rtl;font-family:Arial,sans-serif;background:#f4f4f4;padding:20px;'><div style='background:#fff;padding:20px;border-radius:8px;max-width:800px;margin:auto;'><h2>לוג שאלות ותשובות</h2><pre style='white-space:pre-wrap;'>{log_content}</pre><a href='/token_manager/'>חזרה</a></div></body></html>
    """


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
