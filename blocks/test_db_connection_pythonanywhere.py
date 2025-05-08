import os
import sys
import unittest
from dotenv import load_dotenv
from sqlalchemy import create_engine
from blockes import BlocksGame, BlockColors

class TestDatabaseConnection(unittest.TestCase):
    """Test database connection and save/load functionality for PythonAnywhere."""
    
    def setUp(self):
        """Set up the test environment."""
        # Load environment variables
        load_dotenv()
        
        # Use PythonAnywhere MySQL database connection details
        # Replace with your actual PythonAnywhere MySQL credentials
        username = "mattan"  # Your PythonAnywhere username
        password = "your_mysql_password"  # Your MySQL password
        hostname = "mattan.mysql.pythonanywhere-services.com"
        database_name = "mattan$blocks_game"  # PythonAnywhere uses username$database format
        
        # Construct the database URL
        self.db_url = f"mysql+pymysql://{username}:{password}@{hostname}/{database_name}"
        
        # Override the environment variable to ensure we're using the right connection
        os.environ["DATABASE_URL"] = self.db_url
        print(f"Using database URL: {self.db_url}")
        
        # Create a fresh game instance
        self.game = BlocksGame()
        self.game.reset_state()
        
    def test_database_connection(self):
        """Test if we can connect to the database."""
        try:
            engine = create_engine(self.db_url)
            connection = engine.connect()
            print("Successfully connected to the database!")
            connection.close()
        except Exception as e:
            self.fail(f"Failed to connect to database: {str(e)}")
    
    def test_save_and_load(self):
        """Test saving and loading game state from the database."""
        # Modify the game state
        self.game.add_block(BlockColors.RED)
        self.game.add_block(BlockColors.GREEN)
        
        initial_blocks = self.game.blocks.copy()
        initial_hitpoints = self.game.get_hitpoint()
        
        print(f"Initial game state - Blocks: {initial_blocks}, Hitpoints: {initial_hitpoints}")
        
        # Save to database
        try:
            self.game.save_to_db()
            print("Successfully saved game to database")
        except Exception as e:
            self.fail(f"Failed to save to database: {str(e)}")
        
        # Create a new game instance and load from database
        new_game = BlocksGame()
        
        try:
            new_game = BlocksGame.load_from_db(game_id=1)
            print("Successfully loaded game from database")
        except Exception as e:
            self.fail(f"Failed to load from database: {str(e)}")
        
        # Verify the state was saved correctly
        loaded_blocks = new_game.blocks
        loaded_hitpoints = new_game.get_hitpoint()
        
        print(f"Loaded game state - Blocks: {loaded_blocks}, Hitpoints: {loaded_hitpoints}")
        
        self.assertEqual(initial_blocks, loaded_blocks, "Blocks don't match after load")
        self.assertEqual(initial_hitpoints, loaded_hitpoints, "Hitpoints don't match after load")

if __name__ == '__main__':
    # Run the test
    unittest.main() 