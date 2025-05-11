import os
from flask import Flask, render_template, Blueprint


app = Blueprint("rag_ai",__name__, template_folder="..", url_prefix="/rag_ai")
app.html_name = "סוכן RAG"
app.html_creator = "אילון"
app.html_link = "https://www.facebook.com/groups/1188234756236379/user/100059177976123"
app.html_img = "https://scontent.ftlv20-1.fna.fbcdn.net/v/t39.30808-6/358107480_668938901755370_6377983421291591040_n.jpg?_nc_cat=111&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=MhzRgnUiQAIQ7kNvwEXzCOJ&_nc_oc=Admzv-nuRdDqIOIpPX52lGUbmmJ4uMUQQb9qS0lv9XfstfMR_1SxWIuPLpr50ZCWODQAmg9C7CP6V-uUXjKI9awR&_nc_zt=23&_nc_ht=scontent.ftlv20-1.fna&_nc_gid=FnifHyWLSHmOPG8UvWRwew&oh=00_AfID2lFmVKzMoo-hx9-9vMCbQHkHq0CjO-TD3rbJh9xl-Q&oe=6826C81A"



@app.route('/')
def index():
    """Render the main game page."""
    return render_template('rag_ai/templates/index.html')
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
