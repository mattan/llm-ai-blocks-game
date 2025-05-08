import os
from flask import Flask, render_template, jsonify, request, Blueprint

app = Flask(__name__)

# Assuming the sub-applications have their own static and template folders
# We need to tell Flask where to find them.

# Serve files from the blocks project
blocks_bp = Blueprint('blocks', __name__,
                        template_folder='blocks/templates',
                        static_folder='blocks/static', # Assuming a static folder exists
                        url_prefix='/blocks')

@blocks_bp.route('/')
def blocks_index():
    return render_template('index.html') # Assumes blocks/templates/index.html

app.register_blueprint(blocks_bp)

# Serve files from the messeges_ai project
messeges_ai_bp = Blueprint('messeges_ai', __name__,
                             template_folder='messeges_ai/templates',
                             static_folder='messeges_ai/static', # Assuming a static folder exists
                             url_prefix='/messeges_ai')

@messeges_ai_bp.route('/')
def messeges_ai_index():
    return render_template('index.html') # Assumes messeges_ai/templates/index.html

app.register_blueprint(messeges_ai_bp)

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True,port=os.environ.get("PORT", 5000)) 
