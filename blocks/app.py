import os
from flask import Flask, render_template, jsonify, request, Blueprint, current_app
import datetime
import subprocess
from .blockes import BlocksGame, BlockColors

app = Blueprint("blocks", __name__, template_folder="..", url_prefix="/blocks")
app.html_name = "פרויקט בלוקים"
app.description = "משחק זיהוי תבניות \n השחקן מנסה להבין את התנהגות הבינה המלאכותית"


game = BlocksGame()

@app.route('/')
def index():
    """Render the main game page."""
    return render_template('blocks/templates/index.html')

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

@app.route('/api/game/save_file', methods=['POST'])
def save_game_file():
    """Save the current game state to a file."""
    filename = request.json.get('filename', 'game_state.json')
    try:
        game.save_to_file(filename)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/load_file', methods=['POST'])
def load_game_file():
    """Load a game state from a file."""
    filename = request.json.get('filename', 'game_state.json')
    try:
        global game
        game = BlocksGame.load_from_file(filename)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/save_db', methods=['POST'])
def save_game_db():
    """Save the current game state to the database."""
    try:
        game.save_to_db()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/game/load_db', methods=['POST'])
def load_game_db():
    """Load a game state from the database."""
    game_id = request.json.get('game_id', 1)
    try:
        global game
        game = BlocksGame.load_from_db(game_id)
        return jsonify({'success': True, 'game_id': game_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/git/last_update', methods=['GET'])
def get_last_git_update():
    """Get the timestamp of the last Git update."""
    import subprocess
    import datetime
    import os
    
    # Define the Git repository path
    git_repo_path = '/home/Mattan/mysite'
    
    try:
        # Check if the specified directory exists and is a Git repository
        if not os.path.exists(os.path.join(git_repo_path, '.git')):
            return jsonify({
                'success': False,
                'error': f'Not a Git repository at {git_repo_path}',
                'formatted_date': 'Git info unavailable'
            })
            
        # Get the last commit date - run in the specified directory
        output = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=iso'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path  # Specify the working directory
        ).strip()
        
        # Parse the date
        last_update = datetime.datetime.fromisoformat(output)
        
        return jsonify({
            'success': True,
            'last_update': last_update.isoformat(),
            'formatted_date': last_update.strftime('%Y-%m-%d %H:%M:%S')
        })
    except subprocess.CalledProcessError as e:
        return jsonify({
            'success': False,
            'error': f'Git command failed in {git_repo_path}: {e.output}',
            'formatted_date': 'Git info unavailable'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'formatted_date': 'Git info unavailable'
        }), 500

@app.route('/update', methods=['POST'])
def update():
    """Update the application by pulling from git repository."""
    import subprocess
    import hmac
    import hashlib
    import datetime
    import time
    
    # Define the Git repository path
    git_repo_path = '/home/Mattan/mysite'
    
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
    
    # Execute git pull in the specified directory
    try:
        output = subprocess.check_output(
            ['git', 'pull'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path  # Specify the working directory
        )
        results['actions'].append({'action': 'git_pull', 'output': output, 'success': True})
    except subprocess.CalledProcessError as e:
        results['actions'].append({'action': 'git_pull', 'output': e.output, 'success': False})
        results['success'] = False
    
    # Install any new dependencies - assuming requirements.txt is in the git repo
    try:
        pip_output = subprocess.check_output(
            ['pip', 'install', '-r', 'requirements.txt'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path  # Specify the working directory
        )
        results['actions'].append({'action': 'install_dependencies', 'output': pip_output, 'success': True})
    except subprocess.CalledProcessError as e:
        results['actions'].append({'action': 'install_dependencies', 'output': e.output, 'success': False})
        results['success'] = False
    
    # More effective way to restart the Flask application
    try:
        # Try multiple methods to restart the Flask application
        restart_methods = []
        
        # Method 1: Try PythonAnywhere API if we're on that platform
        try:
            try:
                import requests
                pa_api_available = True
            except ImportError:
                pa_api_available = False
                
            if pa_api_available:
                username = 'Mattan'  # Replace with your PythonAnywhere username if different
                token = os.environ.get('PYTHONANYWHERE_API_TOKEN')
                
                if token:
                    response = requests.post(
                        f'https://www.pythonanywhere.com/api/v0/user/{username}/webapps/{username}.pythonanywhere.com/reload/',
                        headers={'Authorization': f'Token {token}'}
                    )
                    if response.status_code == 200:
                        restart_methods.append("PythonAnywhere API reload")
        except Exception as e:
            # Just log the error but continue with other methods
            print(f"Error with PythonAnywhere API: {str(e)}")
        
        # Method 2: Create a .reload file that can be watched by the WSGI server
        reload_file = os.path.join(git_repo_path, 'tmp', 'restart.txt')
        os.makedirs(os.path.dirname(reload_file), exist_ok=True)
        with open(reload_file, 'w') as f:
            f.write(f"Restart triggered at {datetime.datetime.now().isoformat()}")
        restart_methods.append("Created restart.txt file")
            
        # Method 3: If running in debug mode with reloader, modify this file
        # This will cause the auto-reloader to detect the change and restart
        if app.debug:
            with open(__file__, 'a') as f:
                f.write(f"\n# Trigger reload: {datetime.datetime.now().isoformat()}")
            restart_methods.append("Modified app file for auto-reload")
            
        results['actions'].append({
            'action': 'restart_app', 
            'output': f'Application restart initiated using methods: {", ".join(restart_methods)}', 
            'success': True
        })
    except Exception as e:
        results['actions'].append({
            'action': 'restart_app', 
            'output': f'Error restarting app: {str(e)}', 
            'success': False
        })
        results['success'] = False
    
    # Push changes back to Git
    try:
        # Add all files
        git_add = subprocess.check_output(
            ['git', 'add', '.'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path
        )
        
        # Commit changes
        git_commit = subprocess.check_output(
            ['git', 'commit', '-m', 'Update from web UI - version changed to v4'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path
        )
        
        # Push to remote repository
        git_push = subprocess.check_output(
            ['git', 'push'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path
        )
        
        results['actions'].append({'action': 'git_push', 'output': f"{git_add}\n{git_commit}\n{git_push}", 'success': True})
    except subprocess.CalledProcessError as e:
        results['actions'].append({'action': 'git_push', 'output': e.output, 'success': False})
        # Don't mark the whole process as failed if just the push fails
    
    # Get the last commit date from the specified directory
    try:
        last_commit_output = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=iso'],
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=git_repo_path  # Specify the working directory
        ).strip()
        
        # Parse the date
        last_update = datetime.datetime.fromisoformat(last_commit_output)
        
        results['last_update'] = last_update.isoformat()
        results['formatted_date'] = last_update.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        results['last_update_error'] = str(e)
    
    return jsonify(results)


if __name__ == '__main__':
    app.run(debug=True,port=os.environ.get("PORT", 5000)) 
