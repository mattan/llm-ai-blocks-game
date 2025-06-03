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
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
