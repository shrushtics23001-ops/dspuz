from typing import Dict, Any, Optional
import time
from dataclasses import dataclass
from enum import Enum

class ScoreModifier(Enum):
    PERFECT = 1.5
    GREAT = 1.2
    GOOD = 1.0
    OK = 0.8
    POOR = 0.5

@dataclass
class ScoreEvent:
    points: int
    modifier: ScoreModifier
    timestamp: float
    message: str = ""
    
    @property
    def modified_points(self) -> int:
        return int(self.points * self.modifier.value)

class ScoreSystem:
    def __init__(self, base_points: int = 100, time_limit: float = 60.0):
        self.base_points = base_points
        self.time_limit = time_limit  # Time in seconds
        self.start_time: Optional[float] = None
        self.score: int = 0
        self.multiplier: float = 1.0
        self.combo: int = 0
        self.max_combo: int = 0
        self.events: list[ScoreEvent] = []
        self.bonus_points: int = 0
        self.time_penalty: float = 0.0
        self.completed: bool = False
        self.perfect: bool = True
    
    def start(self):
        """Start the scoring system"""
        self.start_time = time.time()
    
    def add_score(self, points: int, modifier: ScoreModifier = ScoreModifier.GOOD, 
                 message: str = "") -> int:
        """Add points to the score with an optional modifier"""
        if self.completed:
            return 0
            
        event = ScoreEvent(
            points=points,
            modifier=modifier,
            timestamp=time.time() - (self.start_time or 0),
            message=message
        )
        
        self.events.append(event)
        
        # Update combo
        if modifier == ScoreModifier.POOR:
            self.combo = 0
            self.perfect = False
        else:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            
            # Increase multiplier based on combo
            if self.combo >= 10:
                self.multiplier = 2.0
            elif self.combo >= 5:
                self.multiplier = 1.5
        
        # Calculate modified points with current multiplier
        modified_points = int(event.modified_points * self.multiplier)
        self.score += modified_points
        
        return modified_points
    
    def add_time_penalty(self, seconds: float):
        """Add a time penalty"""
        if not self.completed:
            self.time_penalty += seconds
    
    def add_bonus(self, points: int, reason: str = ""):
        """Add bonus points"""
        if not self.completed:
            self.bonus_points += points
            self.events.append(ScoreEvent(
                points=points,
                modifier=ScoreModifier.PERFECT,
                timestamp=time.time() - (self.start_time or 0),
                message=f"Bonus: {reason}"
            ))
    
    def complete(self) -> Dict[str, Any]:
        """Complete the scoring and return the final results"""
        if self.completed:
            return self.get_results()
            
        self.completed = True
        end_time = time.time()
        
        # Calculate time bonus if within time limit
        time_taken = end_time - (self.start_time or end_time)
        time_bonus = 0
        
        if time_taken < self.time_limit / 2 and self.perfect:
            time_bonus = int(self.base_points * 2)
            self.add_bonus(time_bonus, "Perfect time bonus")
        elif time_taken < self.time_limit:
            time_bonus = int(self.base_points * (1 - time_taken / self.time_limit))
            if time_bonus > 0:
                self.add_bonus(time_bonus, "Time bonus")
        
        # Add combo bonus
        if self.max_combo >= 5:
            combo_bonus = self.max_combo * 10
            self.add_bonus(combo_bonus, f"Combo x{self.max_combo}")
        
        # Apply time penalty
        if self.time_penalty > 0:
            penalty = int(self.score * (self.time_penalty / 100.0))
            self.score = max(0, self.score - penalty)
            self.events.append(ScoreEvent(
                points=-penalty,
                modifier=ScoreModifier.POOR,
                timestamp=time_taken,
                message=f"Time penalty: -{penalty}"
            ))
        
        return self.get_results()
    
    def get_results(self) -> Dict[str, Any]:
        """Get the scoring results"""
        time_taken = 0.0
        if self.start_time is not None:
            time_taken = (time.time() - self.start_time) if not self.completed else \
                        (self.events[-1].timestamp if self.events else 0)
        
        # Calculate accuracy
        total_possible = sum(max(0, event.points) * event.modifier.value 
                           for event in self.events)
        actual_score = sum(event.modified_points for event in self.events)
        accuracy = min(100.0, (actual_score / total_possible * 100)) if total_possible > 0 else 100.0
        
        return {
            'score': self.score,
            'time_taken': time_taken,
            'accuracy': accuracy,
            'max_combo': self.max_combo,
            'bonus_points': self.bonus_points,
            'time_penalty': self.time_penalty,
            'perfect': self.perfect,
            'events': self.events,
            'completed': self.completed
        }
    
    def get_grade(self) -> str:
        """Get a letter grade based on performance"""
        if not self.completed:
            return ""
            
        results = self.get_results()
        accuracy = results['accuracy']
        
        if accuracy >= 99.0 and self.perfect:
            return "S+"
        elif accuracy >= 95.0:
            return "S"
        elif accuracy >= 90.0:
            return "A"
        elif accuracy >= 80.0:
            return "B"
        elif accuracy >= 70.0:
            return "C"
        elif accuracy >= 60.0:
            return "D"
        else:
            return "F"
