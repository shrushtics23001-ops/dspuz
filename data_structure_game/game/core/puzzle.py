from typing import List, Dict, Any, Optional, Type, Union
from dataclasses import dataclass
from enum import Enum
import random
from .data_structures import DataStructure, Stack, Queue, LinkedList, BinaryTree, Graph, OperationType

class PuzzleType(Enum):
    OPERATION = "operation"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"

class PuzzleDifficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXPERT = 4

@dataclass
class PuzzleStep:
    operation: OperationType
    parameters: list
    expected_result: Any
    hint: str = ""

class Puzzle:
    def __init__(self, puzzle_id: str, title: str, description: str, 
                 difficulty: PuzzleDifficulty, puzzle_type: PuzzleType,
                 data_structure_type: Type[DataStructure]):
        self.puzzle_id = puzzle_id
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.puzzle_type = puzzle_type
        self.data_structure_type = data_structure_type
        self.steps: List[PuzzleStep] = []
        self.current_step = 0
        self.solved = False
        self.data_structure: Optional[DataStructure] = None
        self.initialize_structure()
    
    def initialize_structure(self):
        """Initialize the appropriate data structure based on type"""
        if self.data_structure_type == Stack:
            self.data_structure = Stack()
        elif self.data_structure_type == Queue:
            self.data_structure = Queue()
        elif self.data_structure_type == LinkedList:
            self.data_structure = LinkedList()
        elif self.data_structure_type == BinaryTree:
            self.data_structure = BinaryTree()
        elif self.data_structure_type == Graph:
            self.data_structure = Graph()
    
    def add_step(self, step: PuzzleStep):
        """Add a step to the puzzle"""
        self.steps.append(step)
    
    def get_current_step(self) -> Optional[PuzzleStep]:
        """Get the current step of the puzzle"""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def check_solution(self, user_input: Any) -> bool:
        """Check if the user's solution is correct for the current step"""
        current_step = self.get_current_step()
        if not current_step:
            return False
            
        # Get the operation and execute it on the data structure
        operation = getattr(self.data_structure, current_step.operation.value, None)
        if not operation:
            return False
            
        try:
            result = operation(*current_step.parameters)
            
            # Compare the result with expected result
            if result == current_step.expected_result:
                self.current_step += 1
                if self.current_step >= len(self.steps):
                    self.solved = True
                return True
        except Exception as e:
            print(f"Error executing operation: {e}")
            
        return False
    
    def get_hint(self) -> str:
        """Get a hint for the current step"""
        current_step = self.get_current_step()
        if current_step and current_step.hint:
            return current_step.hint
        return "No hint available for this step."
    
    def reset(self):
        """Reset the puzzle to its initial state"""
        self.current_step = 0
        self.solved = False
        self.initialize_structure()

class PuzzleSolver:
    """Helper class to generate and solve puzzles"""
    
    @staticmethod
    def generate_stack_puzzle(difficulty: PuzzleDifficulty = PuzzleDifficulty.EASY) -> Puzzle:
        """Generate a stack-based puzzle"""
        puzzle = Puzzle(
            puzzle_id=f"stack_{random.randint(1000, 9999)}",
            title="Stack Operations",
            description="Perform stack operations to achieve the target state.",
            difficulty=difficulty,
            puzzle_type=PuzzleType.OPERATION,
            data_structure_type=Stack
        )
        
        # Add steps based on difficulty
        if difficulty == PuzzleDifficulty.EASY:
            puzzle.add_step(PuzzleStep(
                operation=OperationType.PUSH,
                parameters=[5],
                expected_result=True,
                hint="Use the push operation to add an element to the stack."
            ))
            puzzle.add_step(PuzzleStep(
                operation=OperationType.PUSH,
                parameters=[10],
                expected_result=True,
                hint="Add another element to the stack."
            ))
            puzzle.add_step(PuzzleStep(
                operation=OperationType.POP,
                parameters=[],
                expected_result=10,
                hint="Remove the top element from the stack."
            ))
            
        # Add more difficulty levels...
        
        return puzzle
    
    @staticmethod
    def generate_queue_puzzle(difficulty: PuzzleDifficulty = PuzzleDifficulty.EASY) -> Puzzle:
        """Generate a queue-based puzzle"""
        puzzle = Puzzle(
            puzzle_id=f"queue_{random.randint(1000, 9999)}",
            title="Queue Operations",
            description="Perform queue operations to achieve the target state.",
            difficulty=difficulty,
            puzzle_type=PuzzleType.OPERATION,
            data_structure_type=Queue
        )
        
        if difficulty == PuzzleDifficulty.EASY:
            puzzle.add_step(PuzzleStep(
                operation=OperationType.ENQUEUE,
                parameters=["A"],
                expected_result=True,
                hint="Use enqueue to add an element to the queue."
            ))
            puzzle.add_step(PuzzleStep(
                operation=OperationType.ENQUEUE,
                parameters=["B"],
                expected_result=True,
                hint="Add another element to the queue."
            ))
            puzzle.add_step(PuzzleStep(
                operation=OperationType.DEQUEUE,
                parameters=[],
                expected_result="A",
                hint="Remove the first element from the queue (FIFO)."
            ))
            
        return puzzle
    
    # Add similar generator methods for other data structures...
    
    @staticmethod
    def generate_puzzle(data_structure_type: Type[DataStructure], 
                       difficulty: PuzzleDifficulty = PuzzleDifficulty.EASY) -> Puzzle:
        """Generate a puzzle for the specified data structure"""
        if data_structure_type == Stack:
            return PuzzleSolver.generate_stack_puzzle(difficulty)
        elif data_structure_type == Queue:
            return PuzzleSolver.generate_queue_puzzle(difficulty)
        # Add other data structure types...
        
        raise ValueError(f"Unsupported data structure type: {data_structure_type}")
