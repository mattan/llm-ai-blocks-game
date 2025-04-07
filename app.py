import os
from flask import Flask, render_template, jsonify, request
from blockes import BlocksGame, BlockColors

app = Flask(__name__)
game = BlocksGame()

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('index.html')

@app.route('/api/game/state')
def get_game_state():
    """Get the current game state."""
    return jsonify({
        'hitpoints': game.get_hitpoint(),
        'blocks': game.blocks
    })

@app.route('/api/game/add_block', methods=['POST'])
def add_block():
    """Add a block to the game."""
    color = request.json.get('color')
    if color not in [c.value for c in BlockColors]:
        return jsonify({'error': 'Invalid color'}), 400
    
    game.add_block(BlockColors(color))
    return jsonify({'success': True})

@app.route('/api/game/remove_block', methods=['POST'])
def remove_block():
    """Remove the top block from the game."""
    block = game.remove_block()
    return jsonify({
        'success': True,
        'removed_block': block.value if block else None
    })

@app.route('/api/game/reset', methods=['POST'])
def reset_game():
    """Reset the game state."""
    game.reset_state()
    return jsonify({'success': True})

@app.route('/update', methods=['POST'])
def update():
    """Update the application by pulling from git repository."""
    import subprocess
    import hmac
    import hashlib
    
    # If you want to add GitHub webhook secret validation:
    if 'X-Hub-Signature' in request.headers:
        signature = request.headers.get('X-Hub-Signature')
        secret = os.environ.get('GITHUB_WEBHOOK_SECRET', '').encode()
        if secret:
            hmac_obj = hmac.new(secret, request.data, hashlib.sha1)
            expected_signature = f'sha1={hmac_obj.hexdigest()}'
            if not hmac.compare_digest(signature, expected_signature):
                return jsonify({'error': 'Invalid signature'}), 403
    
    results = {'success': True, 'actions': []}
    
    # Execute git pull
    try:
        output = subprocess.check_output(
            ['git', 'pull'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        results['actions'].append({'action': 'git_pull', 'output': output, 'success': True})
    except subprocess.CalledProcessError as e:
        results['actions'].append({'action': 'git_pull', 'output': e.output, 'success': False})
        results['success'] = False
    
    # Install any new dependencies
    try:
        pip_output = subprocess.check_output(
            ['pip', 'install', '-r', 'requirements.txt'],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        results['actions'].append({'action': 'install_dependencies', 'output': pip_output, 'success': True})
    except subprocess.CalledProcessError as e:
        results['actions'].append({'action': 'install_dependencies', 'output': e.output, 'success': False})
        results['success'] = False
    
    # Touch the WSGI file to restart the app
    try:
        # Get absolute path to wsgi.py
        wsgi_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wsgi.py')
        subprocess.check_output(
            ['touch', wsgi_path],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        results['actions'].append({'action': 'restart_app', 'output': 'Application restarted', 'success': True})
    except subprocess.CalledProcessError as e:
        results['actions'].append({'action': 'restart_app', 'output': e.output, 'success': False})
        results['success'] = False
    
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True,port=os.environ.get("PORT", 5000)) 