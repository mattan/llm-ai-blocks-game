import os
from flask import Flask, render_template, Blueprint


app = Blueprint("cursor_log_count",__name__, template_folder="templates", url_prefix="/cursor_log_count")
app.html_name = "Cursor Log Count"
app.html_creator = "איתמר"
app.html_link = "https://www.facebook.com/itamar.ho"  
app.html_img = "/static/itamar.ho.jpg"  


@app.route('/')
def index():
    """Render the main page."""
    return render_template('cursor_log_count/templates/index.html')
    


if __name__ == '__main__':
   # Consider using a different port if 5001 is taken or for separation
   app.run(debug=True, host='0.0.0.0', port=5002) 