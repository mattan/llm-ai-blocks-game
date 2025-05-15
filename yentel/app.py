import os
from flask import Flask, render_template, Blueprint


app = Blueprint("yentel",__name__, template_folder="..", url_prefix="/yentel")
app.html_name = "ינטל הכרויות (החדש)"
app.html_creator = "הודיה"
app.html_link = "https://www.facebook.com/hodaya.netzer"
app.html_img = "/static/hodaya.netzer.jpg"



@app.route('/')
def index():
    """Render the main game page."""
    return render_template('yentel/templates/index.html')
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
