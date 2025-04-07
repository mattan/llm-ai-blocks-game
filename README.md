# Blocks Game

A simple web-based blocks game built with Flask.

## Requirements

- Python 3.8 or higher
- MySQL database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mattan/llm-ai-blocks-game.git
cd llm-ai-blocks-game
```

2. Install Python (if not already installed):
```bash
# Windows
# Download and install from https://www.python.org/downloads/

# Linux
sudo apt update
sudo apt install python3 python3-pip
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the database:
   - Create a MySQL database named `blocks_game`
   - Update the `.env` file with your database credentials

## Running the Game

### Local Development
```bash
python app.py
```
Then open http://localhost:5000 in your browser.

### PythonAnywhere Deployment
1. SSH into your PythonAnywhere account
2. Run:
```bash
cd /home/Mattan/mysite
git clone https://github.com/mattan/llm-ai-blocks-game.git .
pip3 install -r requirements.txt
```
3. Reload your web app from the PythonAnywhere dashboard

## Game Rules
- Add blocks of different colors (RED, YELLOW, GREEN)
- Maximum 3 blocks can be stacked
- Exceeding the limit reduces hitpoints by 1
- Game ends when hitpoints reach 0

## New Features

### Saving and Loading Game State

The game now supports saving and loading game state in two ways:

1. **File Storage**
   ```python
   from blocks.blockes import save_to_file, load_from_file
   
   # Save game state to a file
   save_to_file("my_game.json")
   
   # Load game state from a file
   load_from_file("my_game.json")
   ```

2. **MySQL Database Storage**
   ```python
   from blocks.blockes import save_to_db, load_from_db
   
   # Save game state to the database
   save_to_db()
   
   # Load game state from the database
   load_from_db(game_id=1)
   ```

Make sure to configure your database connection in the `.env` file before using the database features. 