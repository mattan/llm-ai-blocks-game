import enum
import json
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup
Base = declarative_base()

class BlockColors(enum.Enum):
    """
    Enumeration of available block colors in the game.
    
    Colors:
        RED: Red colored block
        YELLOW: Yellow colored block
        GREEN: Green colored block
    """
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"
    

class BlocksGame(Base):
    """
    Main game class that manages the state and logic of the blocks game.
    
    The game follows these rules:
    - Blocks of different colors can be added to a stack
    - There is a limit to how many blocks can be in the stack at once
    - If the limit is exceeded, hitpoints are reduced and the stack is cleared
    - Blocks can be removed one at a time from the top of the stack
    - The game continues until hitpoints reach zero
    """
    
    __tablename__ = 'blocks_game'
    
    id = Column(Integer, primary_key=True)
    blocks_json = Column(String(1000), default='[]')
    hitpoints = Column(Integer, default=10)
    LIMIT = 3  # Maximum number of blocks allowed
    
    def __init__(self):
        """
        Initialize a new game with default values.
        
        Sets up:
        - An empty blocks stack
        - Default hitpoints (10)
        - Block limit (3)
        """
        super().__init__()
        self.blocks = []
        self.hitpoints = 10
        self.LIMIT = 3  # Maximum number of blocks allowed
        
    @property
    def blocks(self):
        """
        Get the blocks list from the JSON string.
        
        Returns:
            list: The list of block colors
        """
        try:
            return json.loads(self.blocks_json)
        except (json.JSONDecodeError, TypeError):
            return []
            
    @blocks.setter
    def blocks(self, value):
        """
        Set the blocks list as a JSON string.
        
        Args:
            value (list): The list of block colors
        """
        self.blocks_json = json.dumps(value)
        
    def get_hitpoint(self):
        """
        Get the current hitpoints value.
        
        Returns:
            int: The current number of hitpoints remaining
        """
        return self.hitpoints
        
    def add_block(self, color):
        """
        Add a block of the specified color to the stack.
        
        If adding this block would exceed the limit:
        - Hitpoints are reduced by 1
        - All blocks are removed from the stack
        
        Args:
            color (BlockColors): The color of the block to add
        """
        blocks_list = self.blocks
        blocks_list.append(color.value)
        self.blocks = blocks_list
        
        # Check if we've exceeded the limit
        if len(blocks_list) > self.LIMIT:
            self.hitpoints -= 1  # Reduce hitpoints by 1
            self.blocks = []  # Clear all blocks
            
    def remove_block(self):
        """
        Remove and return the last block added to the stack.
        
        Returns:
            BlockColors or None: The removed block, or None if the stack is empty
        """
        blocks_list = self.blocks
        
        # No blocks to remove
        if not blocks_list:
            return None
            
        # Normal case - remove and return the last block
        color_value = blocks_list.pop()
        self.blocks = blocks_list
        return BlockColors(color_value)
        
    def reset_state(self):
        """
        Reset the game to its initial state.
        
        This resets:
        - The blocks stack to empty
        - Hitpoints to the initial value (10)
        """
        self.blocks = []
        self.hitpoints = 10
        
    def save_to_file(self, filename="game_state.json"):
        """
        Save the current game state to a JSON file.
        
        Args:
            filename (str): The name of the file to save to
        """
        game_state = {
            "blocks": self.blocks,
            "hitpoints": self.hitpoints
        }
        
        with open(filename, 'w') as f:
            json.dump(game_state, f)
            
    @classmethod
    def load_from_file(cls, filename="game_state.json"):
        """
        Load a game state from a JSON file.
        
        Args:
            filename (str): The name of the file to load from
            
        Returns:
            BlocksGame: A new game instance with the loaded state
        """
        if not os.path.exists(filename):
            return cls()
            
        with open(filename, 'r') as f:
            game_state = json.load(f)
            
        game = cls()
        game.blocks = game_state.get("blocks", [])
        game.hitpoints = game_state.get("hitpoints", 10)
        
        return game
        
    def save_to_db(self):
        """
        Save the current game state to the MySQL database.
        """
        # Get database connection from environment variables
        db_url = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/blocks_game")
        engine = create_engine(db_url)
        
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Save the game state
            session.merge(self)
            session.commit()
        finally:
            session.close()
        
    @classmethod
    def load_from_db(cls, game_id=1):
        """
        Load a game state from the MySQL database.
        
        Args:
            game_id (int): The ID of the game to load
            
        Returns:
            BlocksGame: A game instance with the loaded state
        """
        # Get database connection from environment variables
        db_url = os.getenv("DATABASE_URL", "mysql+pymysql://user:password@localhost/blocks_game")
        engine = create_engine(db_url)
        
        # Create tables if they don't exist
        Base.metadata.create_all(engine)
        
        # Create a session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        try:
            # Try to load the game
            game = session.query(cls).filter_by(id=game_id).first()
            
            if not game:
                # If no game exists, create a new one
                game = cls()
                game.id = game_id
                session.add(game)
                session.commit()
            
            return game
        finally:
            session.close()


# Create a single global instance for backwards compatibility with tests
_game_instance = BlocksGame()

# Wrapper functions to maintain the same API
def get_hitpoint():
    """
    Get the current hitpoints from the game instance.
    
    This is a wrapper function for backwards compatibility.
    
    Returns:
        int: The current number of hitpoints
    """
    return _game_instance.get_hitpoint()

def add_block(color):
    """
    Add a block to the game instance.
    
    This is a wrapper function for backwards compatibility.
    
    Args:
        color (BlockColors): The color of the block to add
    """
    return _game_instance.add_block(color)

def remove_block():
    """
    Remove a block from the game instance.
    
    This is a wrapper function for backwards compatibility.
    
    Returns:
        BlockColors or None: The removed block, or None if no blocks remain
    """
    return _game_instance.remove_block()

def reset_state():
    """
    Reset the game instance to its initial state.
    
    This is a wrapper function for backwards compatibility.
    """
    return _game_instance.reset_state()

def save_to_file(filename="game_state.json"):
    """
    Save the current game state to a file.
    
    Args:
        filename (str): The name of the file to save to
    """
    return _game_instance.save_to_file(filename)

def load_from_file(filename="game_state.json"):
    """
    Load a game state from a file.
    
    Args:
        filename (str): The name of the file to load from
    """
    global _game_instance
    _game_instance = BlocksGame.load_from_file(filename)

def save_to_db():
    """
    Save the current game state to the database.
    """
    return _game_instance.save_to_db()

def load_from_db(game_id=1):
    """
    Load a game state from the database.
    
    Args:
        game_id (int): The ID of the game to load
    """
    global _game_instance
    _game_instance = BlocksGame.load_from_db(game_id)