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
        'blocks': [block.value for block in game.blocks]
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

if __name__ == '__main__':
    app.run(debug=True) 