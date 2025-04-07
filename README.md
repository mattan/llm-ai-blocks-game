# Blocks Game

A simple web-based blocks game built with Flask.

## Requirements

- Python 3.13
- MySQL database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/mattan/llm-ai-blocks-game.git
cd llm-ai-blocks-game
```

2. Install Python 3.13:
```bash
# Windows
# Download and install from https://www.python.org/downloads/release/python-3130/

# Linux
sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.13
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

## Automatic Updates from GitHub

The application now supports automatic updates when pushing to GitHub:

### Setup on PythonAnywhere

1. Initial setup and installation:
```bash
# Navigate to your PythonAnywhere directory
cd /var/www/username_pythonanywhere_com

# Clone your repository (if not already done)
git clone https://github.com/username/repo-name.git .

# Run the setup script to install dependencies and restart the app
python setup.py
```

2. Configure GitHub webhook:
   - Go to your GitHub repository
   - Navigate to Settings > Webhooks > Add webhook
   - Set Payload URL to: `https://username.pythonanywhere.com/update`
   - Content type: `application/json`
   - Secret: Create a secure random secret
   - Select 'Just the push event'
   - Ensure 'Active' is checked
   - Click 'Add webhook'

3. Configure the webhook secret on PythonAnywhere:
   - Add the same secret to your environment variables
   - On PythonAnywhere, go to the Web tab
   - Under 'Environment variables', add:
     - Name: `GITHUB_WEBHOOK_SECRET`
     - Value: (the secret you created)

Now, whenever you push to GitHub, your PythonAnywhere site will automatically:
1. Pull the latest changes
2. Install any new dependencies
3. Restart the application

### Manual Update

You can also trigger an update manually by making a POST request to the update endpoint:

```bash
curl -X POST https://username.pythonanywhere.com/update
``` 