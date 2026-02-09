import os
import yaml
from typing import Dict, List, Optional, Type, Any
from pathlib import Path
from enum import Enum
import random
from .puzzle import Puzzle, PuzzleType, PuzzleDifficulty
from .data_structures import Stack, Queue, LinkedList, BinaryTree, Graph

class LevelCategory(Enum):
    TUTORIAL = "tutorial"
    PRACTICE = "practice"
    CHALLENGE = "challenge"
    EXPERT = "expert"

class Level:
    def __init__(self, level_id: int, title: str, description: str, 
                 category: LevelCategory, difficulty: PuzzleDifficulty,
                 data_structure_type: Type, required_score: int = 0,
                 unlocks: List[int] = None):
        self.level_id = level_id
        self.title = title
        self.description = description
        self.category = category
        self.difficulty = difficulty
        self.data_structure_type = data_structure_type
        self.required_score = required_score
        self.unlocks = unlocks or []
        self.completed = False
        self.high_score = 0
        self.attempts = 0
        self.puzzle: Optional[Puzzle] = None
        
    def start(self):
        """Start the level by generating a new puzzle"""
        from .puzzle import PuzzleSolver
        self.puzzle = PuzzleSolver.generate_puzzle(
            self.data_structure_type, 
            self.difficulty
        )
        self.attempts += 1
        return self.puzzle
    
    def complete(self, score: int):
        """Mark the level as completed with the given score"""
        self.completed = True
        self.high_score = max(self.high_score, score)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert level to dictionary for saving"""
        return {
            'level_id': self.level_id,
            'title': self.title,
            'description': self.description,
            'category': self.category.value,
            'difficulty': self.difficulty.value,
            'data_structure': self.data_structure_type.__name__,
            'required_score': self.required_score,
            'unlocks': self.unlocks,
            'completed': self.completed,
            'high_score': self.high_score,
            'attempts': self.attempts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Level':
        """Create a Level instance from a dictionary"""
        # Map string data structure names to actual classes
        ds_map = {
            'Stack': Stack,
            'Queue': Queue,
            'LinkedList': LinkedList,
            'BinaryTree': BinaryTree,
            'Graph': Graph
        }
        
        return cls(
            level_id=data['level_id'],
            title=data['title'],
            description=data['description'],
            category=LevelCategory(data['category']),
            difficulty=PuzzleDifficulty(data['difficulty']),
            data_structure_type=ds_map[data['data_structure']],
            required_score=data.get('required_score', 0),
            unlocks=data.get('unlocks', [])
        )

class LevelManager:
    def __init__(self, levels_dir: str = None):
        self.levels: Dict[int, Level] = {}
        self.current_level_id: Optional[int] = None
        self.levels_dir = levels_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'levels'
        )
        self._load_levels()
    
    def _load_levels(self):
        """Load levels from YAML files in the levels directory"""
        levels_path = Path(self.levels_dir)
        levels_path.mkdir(exist_ok=True, parents=True)
        
        # Load default levels if no custom levels exist
        if not any(levels_path.iterdir()):
            self._create_default_levels()
            return
            
        for level_file in levels_path.glob('*.yaml'):
            try:
                with open(level_file, 'r') as f:
                    level_data = yaml.safe_load(f)
                    if isinstance(level_data, list):
                        for data in level_data:
                            self._add_level(data)
                    else:
                        self._add_level(level_data)
            except Exception as e:
                print(f"Error loading level from {level_file}: {e}")
    
    def _add_level(self, level_data: Dict[str, Any]):
        """Add a level from dictionary data"""
        try:
            level = Level.from_dict(level_data)
            self.levels[level.level_id] = level
        except Exception as e:
            print(f"Error creating level from data {level_data}: {e}")
    
    def _create_default_levels(self):
        """Create default levels if none exist"""
        default_levels = [
            {
                'level_id': 1,
                'title': 'Stack Basics',
                'description': 'Learn the basic operations of a stack',
                'category': 'tutorial',
                'difficulty': 1,
                'data_structure': 'Stack',
                'required_score': 0,
                'unlocks': [2, 3]
            },
            {
                'level_id': 2,
                'title': 'Queue Basics',
                'description': 'Learn the basic operations of a queue',
                'category': 'tutorial',
                'difficulty': 1,
                'data_structure': 'Queue',
                'required_score': 50,
                'unlocks': [4]
            },
            {
                'level_id': 3,
                'title': 'Stack Challenge',
                'description': 'Practice more with stacks',
                'category': 'practice',
                'difficulty': 2,
                'data_structure': 'Stack',
                'required_score': 70,
                'unlocks': [5]
            },
            {
                'level_id': 4,
                'title': 'Queue Challenge',
                'description': 'Practice more with queues',
                'category': 'practice',
                'difficulty': 2,
                'data_structure': 'Queue',
                'required_score': 70,
                'unlocks': [6]
            },
            {
                'level_id': 5,
                'title': 'Linked List Introduction',
                'description': 'Learn the basics of linked lists',
                'category': 'tutorial',
                'difficulty': 2,
                'data_structure': 'LinkedList',
                'required_score': 100,
                'unlocks': [7]
            },
            {
                'level_id': 6,
                'title': 'Binary Tree Basics',
                'description': 'Learn the basics of binary trees',
                'category': 'tutorial',
                'difficulty': 3,
                'data_structure': 'BinaryTree',
                'required_score': 120,
                'unlocks': [8]
            },
            {
                'level_id': 7,
                'title': 'Graph Traversal',
                'description': 'Learn about graph traversal algorithms',
                'category': 'challenge',
                'difficulty': 4,
                'data_structure': 'Graph',
                'required_score': 150,
                'unlocks': []
            },
            {
                'level_id': 8,
                'title': 'Advanced Challenges',
                'description': 'Test your skills with advanced problems',
                'category': 'expert',
                'difficulty': 5,
                'data_structure': 'Stack',
                'required_score': 200,
                'unlocks': []
            }
        ]
        
        # Save default levels to files
        for level_data in default_levels:
            self._add_level(level_data)
            
            # Save to file
            level_file = os.path.join(
                self.levels_dir,
                f"level_{level_data['level_id']}.yaml"
            )
            with open(level_file, 'w') as f:
                yaml.dump(level_data, f)
    
    def get_level(self, level_id: int) -> Optional[Level]:
        """Get a level by ID"""
        return self.levels.get(level_id)
    
    def get_available_levels(self) -> List[Level]:
        """Get all available levels that can be played"""
        return [
            level for level in self.levels.values() 
            if level.completed or level.required_score == 0 or 
               any(self.levels.get(uid, Level(0, '', '', LevelCategory.PRACTICE, 1, Stack, 0)).completed 
                   for uid in level.unlocks)
        ]
    
    def start_level(self, level_id: int) -> Optional[Puzzle]:
        """Start a level and return its puzzle"""
        level = self.get_level(level_id)
        if level:
            self.current_level_id = level_id
            return level.start()
        return None
    
    def complete_level(self, score: int) -> bool:
        """Mark the current level as completed with the given score"""
        if self.current_level_id is not None:
            level = self.get_level(self.current_level_id)
            if level:
                level.complete(score)
                self.save_progress()
                return True
        return False
    
    def save_progress(self):
        """Save the current progress to a save file"""
        save_data = {
            'current_level_id': self.current_level_id,
            'levels': {
                level_id: level.to_dict()
                for level_id, level in self.levels.items()
            }
        }
        
        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'save_game.yaml'
        )
        
        try:
            with open(save_path, 'w') as f:
                yaml.dump(save_data, f)
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def load_progress(self):
        """Load progress from a save file"""
        save_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'save_game.yaml'
        )
        
        if not os.path.exists(save_path):
            return
            
        try:
            with open(save_path, 'r') as f:
                save_data = yaml.safe_load(f)
                
                if not save_data:
                    return
                    
                self.current_level_id = save_data.get('current_level_id')
                
                levels_data = save_data.get('levels', {})
                for level_id, level_data in levels_data.items():
                    if level_id in self.levels:
                        level = self.levels[level_id]
                        level.completed = level_data.get('completed', False)
                        level.high_score = level_data.get('high_score', 0)
                        level.attempts = level_data.get('attempts', 0)
                        
        except Exception as e:
            print(f"Error loading saved game: {e}")
            # If there's an error, reset to default state
            self.current_level_id = None
            for level in self.levels.values():
                level.completed = False
                level.high_score = 0
                level.attempts = 0
