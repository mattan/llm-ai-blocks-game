import os
from flask import Flask, render_template, Blueprint


app = Flask(__name__)



@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')
    


if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=5001) # Using port 5001 to avoid common conflicts 
