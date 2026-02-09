"""
Game Screen

This module implements the main game screen where players interact with data structure puzzles.
It combines various UI components to create an interactive experience with a professional UI.
"""
import pygame
import time
from typing import Dict, Any, Optional, List, Tuple, Callable

# Import core game components
from game.core.puzzle import Puzzle, PuzzleType, PuzzleDifficulty
from game.core.level import Level
from game.core.scoring import ScoreSystem, ScoreEvent

# Import UI components
from game.ui.component import UIComponent, Container
from game.ui.button import Button
from game.ui.text import Label, Heading, Paragraph
from game.ui.panel import Panel
from game.ui.input_field import InputField
from game.ui.progress_bar import ProgressBar
from game.ui.data_structure_view import DataStructureView, Node, Edge, LayoutType
from game.ui.theme import (
    get_theme, get_button_style, get_panel_style, 
    get_card_style, get_text_style, COLORS
)

# Initialize theme
theme = get_theme()

class GameScreen(Container):
    """Main game screen that handles the puzzle solving interface."""
    
    def __init__(self, rect: pygame.Rect, level: Level, on_back: Callable[[], None] = None):
        """Initialize the game screen with the current level.
        
        Args:
            rect: The pygame.Rect defining the screen's position and size
            level: The current Level object containing the puzzle to solve
            on_back: Callback function to return to the previous screen
        """
        super().__init__(rect)
        
        # Store references
        self.level = level
        self.puzzle = level.get_current_puzzle()
        self.on_back = on_back
        
        # Initialize scoring system
        self.score_system = ScoreSystem()
        self.start_time = time.time()
        
        # UI state
        self.is_puzzle_solved = False
        self.show_hint = False
        self.current_step = 0
        
        # Initialize UI components
        self._init_ui()
        
        # Setup the initial puzzle state
        self._setup_puzzle()
    
    def _init_ui(self) -> None:
        """Initialize all UI components."""
        # Main container for the game screen
        self.main_panel = Panel(self.rect, {
            'background_color': (240, 240, 245),
            'border_radius': 10,
            'border_width': 2,
            'border_color': (200, 200, 210),
            'padding': 20
        })
        self.add_child(self.main_panel)
        
        # Header section
        self._init_header()
        
        # Main content area
        self._init_content_area()
        
        # Controls section
        self._init_controls()
        
        # Status bar
        self._init_status_bar()
    
    def _init_header(self) -> None:
        """Initialize the header section with level info and navigation."
        # Header panel
        header_rect = pygame.Rect(0, 0, self.rect.width, 80)
        self.header = Panel(header_rect, {
            'background_color': (230, 230, 240),
            'border_radius': [10, 10, 0, 0],
            'border_width': [0, 0, 2, 0],
            'border_color': (200, 200, 210),
            'padding': 15
        })
        self.main_panel.add_child(self.header)
        
        # Back button
        back_btn = Button(
            pygame.Rect(20, 20, 40, 40), 
            "←",
            on_click=self._on_back_clicked,
            style={
                'background_color': (220, 220, 230),
                'hover_color': (210, 210, 225),
                'active_color': (200, 200, 220),
                'text_color': (80, 80, 90),
                'font_size': 24,
                'border_radius': 8,
                'border_width': 2,
                'border_color': (190, 190, 200)
            }
        )
        self.header.add_child(back_btn)
        
        # Level title
        self.level_title = Heading(
            pygame.Rect(80, 15, self.rect.width - 200, 30),
            f"Level {self.level.level_id}: {self.level.title}",
            style={
                'font_size': 24,
                'color': (60, 60, 70),
                'align': 'left'
            }
        )
        self.header.add_child(self.level_title)
        
        # Score display
        self.score_label = Label(
            pygame.Rect(self.rect.width - 200, 15, 180, 25),
            "Score: 0",
            style={
                'font_size': 18,
                'color': (80, 80, 90),
                'align': 'right'
            }
        )
        self.header.add_child(self.score_label)
        
        # Progress indicator
        progress_text = f"Puzzle {self.level.current_puzzle_index + 1}/{len(self.level.puzzles)}"
        self.progress_label = Label(
            pygame.Rect(self.rect.width - 200, 45, 180, 20),
            progress_text,
            style={
                'font_size': 16,
                'color': (100, 100, 110),
                'align': 'right'
            }
        )
        self.header.add_child(self.progress_label)
    
    def _init_content_area(self) -> None:
        """Initialize the main content area with puzzle visualization and instructions."
        content_rect = pygame.Rect(0, 80, self.rect.width, self.rect.height - 180)
        self.content_panel = Panel(content_rect, {
            'background_color': (250, 250, 255),
            'padding': 15
        })
        self.main_panel.add_child(self.content_panel)
        
        # Split content into left (instructions) and right (visualization) panels
        left_width = int(self.content_panel.rect.width * 0.4)
        right_width = self.content_panel.rect.width - left_width - 20
        
        # Instructions panel
        instructions_rect = pygame.Rect(0, 0, left_width, self.content_panel.rect.height)
        self.instructions_panel = Panel(instructions_rect, {
            'background_color': (245, 245, 250),
            'border_radius': 8,
            'border_width': 1,
            'border_color': (220, 220, 230),
            'padding': 15
        })
        self.content_panel.add_child(self.instructions_panel)
        
        # Instructions title
        instructions_title = Heading(
            pygame.Rect(0, 0, left_width - 30, 30),
            "Instructions",
            style={
                'font_size': 20,
                'color': (60, 60, 70),
                'align': 'left'
            }
        )
        self.instructions_panel.add_child(instructions_title)
        
        # Instructions text
        self.instructions_text = Paragraph(
            pygame.Rect(0, 40, left_width - 30, self.content_panel.rect.height - 100),
            self.puzzle.description,
            style={
                'font_size': 16,
                'color': (80, 80, 90),
                'line_spacing': 1.4
            }
        )
        self.instructions_panel.add_child(self.instructions_text)
        
        # Hint button
        self.hint_button = Button(
            pygame.Rect(0, self.content_panel.rect.height - 45, 120, 35),
            "Show Hint",
            on_click=self._on_hint_clicked,
            style={
                'background_color': (100, 150, 255),
                'hover_color': (80, 130, 240),
                'active_color': (60, 110, 220),
                'text_color': (255, 255, 255),
                'font_size': 14,
                'border_radius': 6,
                'border_width': 1,
                'border_color': (70, 100, 200)
            }
        )
        self.instructions_panel.add_child(self.hint_button)
        
        # Hint text (initially hidden)
        self.hint_text = Paragraph(
            pygame.Rect(0, 40, left_width - 30, 100),
            "",
            style={
                'font_size': 14,
                'color': (100, 100, 120),
                'font_style': 'italic',
                'visible': False
            }
        )
        self.instructions_panel.add_child(self.hint_text)
        
        # Visualization panel
        visualization_rect = pygame.Rect(left_width + 20, 0, right_width, self.content_panel.rect.height)
        self.visualization_panel = Panel(visualization_rect, {
            'background_color': (255, 255, 255),
            'border_radius': 8,
            'border_width': 1,
            'border_color': (220, 220, 230),
            'padding': 15
        })
        self.content_panel.add_child(self.visualization_panel)
        
        # Data structure view
        self.ds_view = DataStructureView(
            pygame.Rect(10, 10, right_width - 20, visualization_rect.height - 20),
            layout_type=LayoutType.HORIZONTAL  # Default layout, can be changed based on puzzle type
        )
        self.visualization_panel.add_child(self.ds_view)
    
    def _init_controls(self) -> None:
        """Initialize the controls section with action buttons."
        controls_rect = pygame.Rect(0, self.rect.height - 100, self.rect.width, 80)
        self.controls_panel = Panel(controls_rect, {
            'background_color': (235, 235, 245),
            'border_radius': [0, 0, 10, 10],
            'border_width': [2, 0, 0, 0],
            'border_color': (200, 200, 210),
            'padding': 15
        })
        self.main_panel.add_child(self.controls_panel)
        
        # Action buttons
        button_width = 120
        button_height = 40
        spacing = 20
        
        # Reset button
        self.reset_button = Button(
            pygame.Rect(spacing, 15, button_width, button_height),
            "Reset",
            on_click=self._on_reset_clicked,
            style={
                'background_color': (250, 180, 100),
                'hover_color': (240, 160, 80),
                'active_color': (230, 140, 70),
                'text_color': (255, 255, 255),
                'font_size': 16,
                'border_radius': 6,
                'border_width': 1,
                'border_color': (200, 120, 50)
            }
        )
        self.controls_panel.add_child(self.reset_button)
        
        # Check solution button
        self.check_button = Button(
            pygame.Rect(spacing * 2 + button_width, 15, button_width, button_height),
            "Check Solution",
            on_click=self._on_check_clicked,
            style={
                'background_color': (100, 200, 100),
                'hover_color': (80, 180, 80),
                'active_color': (60, 160, 70),
                'text_color': (255, 255, 255),
                'font_size': 16,
                'border_radius': 6,
                'border_width': 1,
                'border_color': (50, 150, 50)
            }
        )
        self.controls_panel.add_child(self.check_button)
        
        # Next puzzle button (initially hidden)
        self.next_button = Button(
            pygame.Rect(self.rect.width - button_width - spacing, 15, button_width, button_height),
            "Next Puzzle",
            on_click=self._on_next_clicked,
            style={
                'background_color': (100, 150, 255),
                'hover_color': (80, 130, 240),
                'active_color': (60, 110, 220),
                'text_color': (255, 255, 255),
                'font_size': 16,
                'border_radius': 6,
                'border_width': 1,
                'border_color': (70, 100, 200),
                'visible': False
            }
        )
        self.controls_panel.add_child(self.next_button)
    
    def _init_status_bar(self) -> None:
        """Initialize the status bar at the bottom of the screen."
        status_rect = pygame.Rect(0, self.rect.height - 20, self.rect.width, 20)
        self.status_bar = Panel(status_rect, {
            'background_color': (50, 60, 70),
            'padding': [5, 0, 5, 0]
        })
        self.main_panel.add_child(self.status_bar)
        
        # Status message
        self.status_message = Label(
            pygame.Rect(10, 0, status_rect.width - 20, 20),
            "Ready to start!",
            style={
                'font_size': 12,
                'color': (220, 220, 220),
                'align': 'left'
            }
        )
        self.status_bar.add_child(self.status_message)
        
        # Timer
        self.timer_label = Label(
            pygame.Rect(10, 0, status_rect.width - 20, 20),
            "00:00",
            style={
                'font_size': 12,
                'color': (220, 220, 220),
                'align': 'right'
            }
        )
        self.status_bar.add_child(self.timer_label)
    
    def _setup_puzzle(self) -> None:
        """Set up the puzzle visualization and initial state."""
        # Clear any existing nodes and edges
        self.ds_view.clear()
        
        # Set layout based on puzzle type
        if self.puzzle.puzzle_type in [PuzzleType.STACK, PuzzleType.QUEUE, PuzzleType.LINKED_LIST]:
            self.ds_view.set_layout(LayoutType.HORIZONTAL)
        elif self.puzzle.puzzle_type == PuzzleType.BINARY_TREE:
            self.ds_view.set_layout(LayoutType.TREE)
        elif self.puzzle.puzzle_type == PuzzleType.GRAPH:
            self.ds_view.set_layout(LayoutType.GRAPH)
        
        # Add initial nodes and edges based on the puzzle's initial state
        for node_id, node_data in self.puzzle.initial_state.get('nodes', {}).items():
            self.ds_view.add_node(Node(
                node_id=node_id,
                label=node_data.get('label', str(node_id)),
                value=node_data.get('value', ''),
                position=node_data.get('position', (0, 0)),
                style=node_data.get('style', {})
            ))
        
        for edge_data in self.puzzle.initial_state.get('edges', []):
            self.ds_view.add_edge(Edge(
                source_id=edge_data['source'],
                target_id=edge_data['target'],
                directed=edge_data.get('directed', False),
                weight=edge_data.get('weight'),
                style=edge_data.get('style', {})
            ))
        
        # Update the visualization
        self.ds_view.update_layout()
        
        # Reset step counter and other state
        self.current_step = 0
        self.is_puzzle_solved = False
        self.show_hint = False
        
        # Update UI state
        self._update_ui_state()
    
    def _update_ui_state(self) -> None:
        """Update the UI state based on the current puzzle state."""
        # Update button states
        self.check_button.set_enabled(not self.is_puzzle_solved)
        self.reset_button.set_enabled(not self.is_puzzle_solved)
        self.hint_button.set_visible(not self.is_puzzle_solved and not self.show_hint)
        self.next_button.set_visible(self.is_puzzle_solved and self.level.has_next_puzzle())
        
        # Update hint text visibility
        self.hint_text.set_visible(self.show_hint)
        if self.show_hint and not self.hint_text.text:
            self.hint_text.set_text(self.puzzle.get_hint())
        
        # Update status message
        if self.is_puzzle_solved:
            self.status_message.set_text("Puzzle solved! Great job!")
        
        # Update score display
        self.score_label.set_text(f"Score: {self.score_system.get_current_score()}")
    
    def _on_back_clicked(self, event: pygame.event.Event) -> None:
        """Handle back button click event."""
        if self.on_back:
            self.on_back()
    
    def _on_reset_clicked(self, event: pygame.event.Event) -> None:
        """Handle reset button click event."""
        self._setup_puzzle()
        self.status_message.set_text("Puzzle reset to initial state.")
        
        # Record reset event
        self.score_system.record_event(ScoreEvent.RESET_PUZZLE)
    
    def _on_check_clicked(self, event: pygame.event.Event) -> None:
        """Handle check solution button click event."""
        if self.is_puzzle_solved:
            return
        
        # Check if the current state matches the solution
        is_correct = self.puzzle.check_solution(self._get_current_state())
        
        if is_correct:
            self.is_puzzle_solved = True
            
            # Calculate time taken
            time_taken = int(time.time() - self.start_time)
            minutes = time_taken // 60
            seconds = time_taken % 60
            
            # Record completion event
            self.score_system.record_event(
                ScoreEvent.PUZZLE_SOLVED,
                data={
                    'time_taken': time_taken,
                    'hints_used': 1 if self.show_hint else 0,
                    'resets_used': self.score_system.get_event_count(ScoreEvent.RESET_PUZZLE)
                }
            )
            
            # Update UI
            self.status_message.set_text(f"Correct! Puzzle solved in {minutes}m {seconds}s.")
            self._update_ui_state()
            
            # Mark level as completed if this was the last puzzle
            if not self.level.has_next_puzzle():
                self.level.mark_completed()
                self.status_message.set_text(
                    f"Level completed! Final score: {self.score_system.get_current_score()}"
                )
        else:
            self.status_message.set_text("Not quite right. Try again!")
            
            # Record incorrect attempt
            self.score_system.record_event(ScoreEvent.INCORRECT_ATTEMPT)
    
    def _on_next_clicked(self, event: pygame.event.Event) -> None:
        """Handle next puzzle button click event."""
        if self.level.has_next_puzzle():
            self.level.next_puzzle()
            self.puzzle = self.level.get_current_puzzle()
            self._setup_puzzle()
            self.status_message.set_text("Loading next puzzle...")
    
    def _on_hint_clicked(self, event: pygame.event.Event) -> None:
        """Handle hint button click event."""
        if not self.show_hint:
            self.show_hint = True
            self.status_message.set_text("Hint displayed. Points may be deducted.")
            
            # Record hint usage
            self.score_system.record_event(ScoreEvent.HINT_USED)
            
            # Update UI
            self._update_ui_state()
    
    def _get_current_state(self) -> Dict[str, Any]:
        """Get the current state of the data structure for solution checking."""
        nodes = {}
        edges = []
        
        for node in self.ds_view.get_nodes():
            nodes[node.node_id] = {
                'label': node.label,
                'value': node.value,
                'position': node.position,
                'style': node.style
            }
        
        for edge in self.ds_view.get_edges():
            edges.append({
                'source': edge.source_id,
                'target': edge.target_id,
                'directed': edge.directed,
                'weight': edge.weight,
                'style': edge.style
            })
        
        return {
            'nodes': nodes,
            'edges': edges
        }
    
    def update(self, dt: float) -> None:
        """Update the game screen state.
        
        Args:
            dt: Time elapsed since the last update in seconds
        """
        super().update(dt)
        
        # Update timer
        if not self.is_puzzle_solved:
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.timer_label.set_text(f"{minutes:02d}:{seconds:02d}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        # Let the parent class handle the event first
        if super().handle_event(event):
            return True
            
        # Handle additional events if needed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.on_back:
                self.on_back()
                return True
                
        return False
