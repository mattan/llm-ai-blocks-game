import os
from flask import Flask, render_template, Blueprint


app = Blueprint("cursor_log_count",__name__, template_folder="templates", url_prefix="/cursor_log_count")
app.html_name = "Cursor Log Count"
app.html_creator = "AI Assistant"
app.html_link = ""  # Add a relevant link if you have one
app.html_img = ""   # Add a relevant image URL if you have one



@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')
    


if __name__ == '__main__':
   # Consider using a different port if 5001 is taken or for separation
   app.run(debug=True, host='0.0.0.0', port=5002) 