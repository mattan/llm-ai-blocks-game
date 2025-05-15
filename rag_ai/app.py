import os
from flask import Flask, render_template, Blueprint


app = Blueprint("rag_ai",__name__, template_folder="..", url_prefix="/rag_ai")
app.html_name = "סוכן RAG"
app.html_creator = "אילון"
app.html_link = "https://www.facebook.com/groups/1188234756236379/user/100059177976123"
app.html_img = "/static/eilon.jpg"



@app.route('/')
def index():
    """Render the main game page."""
    return render_template('rag_ai/templates/index.html')
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
