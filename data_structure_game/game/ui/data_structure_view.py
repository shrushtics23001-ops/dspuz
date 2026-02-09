import pygame
import math
from typing import List, Dict, Tuple, Optional, Any, Type, Union, Callable
from enum import Enum
from dataclasses import dataclass
from ..core.data_structures import (
    DataStructure, Stack, Queue, LinkedList, BinaryTree, Graph,
    LinkedListNode, BinaryTreeNode, OperationType
)
from .component import UIComponent, UIEvent, UIEventType
from .text import Text

# Constants for drawing
NODE_RADIUS = 20
NODE_COLOR = (100, 150, 255)
NODE_HOVER_COLOR = (150, 200, 255)
NODE_SELECTED_COLOR = (255, 200, 100)
NODE_BORDER_COLOR = (50, 100, 200)
NODE_BORDER_WIDTH = 2
NODE_TEXT_COLOR = (255, 255, 255)
NODE_TEXT_SIZE = 14

EDGE_COLOR = (150, 150, 150)
EDGE_WIDTH = 2
EDGE_ARROW_SIZE = 8

HIGHLIGHT_COLOR = (255, 200, 0)
HIGHLIGHT_WIDTH = 3

# Animation constants
ANIMATION_SPEED = 0.1
HIGHLIGHT_DURATION = 1000  # ms

class LayoutDirection(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    TREE = "tree"
    GRAPH = "graph"

@dataclass
class NodeStyle:
    """Style configuration for a node"""
    radius: int = NODE_RADIUS
    color: Tuple[int, int, int] = NODE_COLOR
    hover_color: Tuple[int, int, int] = NODE_HOVER_COLOR
    selected_color: Tuple[int, int, int] = NODE_SELECTED_COLOR
    border_color: Tuple[int, int, int] = NODE_BORDER_COLOR
    border_width: int = NODE_BORDER_WIDTH
    text_color: Tuple[int, int, int] = NODE_TEXT_COLOR
    text_size: int = NODE_TEXT_SIZE
    font_name: str = "Arial"

@dataclass
class EdgeStyle:
    """Style configuration for an edge"""
    color: Tuple[int, int, int] = EDGE_COLOR
    width: int = EDGE_WIDTH
    arrow_size: int = EDGE_ARROW_SIZE
    directed: bool = True

@dataclass
class AnimationState:
    """State for node/edge animations"""
    node_pos: Dict[Any, Tuple[float, float]]  # Target positions for nodes
    edge_points: Dict[Tuple[Any, Any], List[Tuple[float, float]]]  # Points for edges
    highlight_nodes: Dict[Any, int]  # Node IDs with highlight end time
    highlight_edges: Dict[Tuple[Any, Any], int]  # Edge IDs with highlight end time
    current_time: int = 0

class DataStructureView(UIComponent):
    """A component for visualizing data structures"""
    
    def __init__(self, x: int, y: int, width: int, height: int,
                 data_structure: Optional[DataStructure] = None,
                 layout: LayoutDirection = LayoutDirection.HORIZONTAL,
                 parent: Optional[UIComponent] = None):
        super().__init__(x, y, width, height, parent)
        
        # Data structure to visualize
        self._data_structure = data_structure
        self._layout = layout
        
        # Style configuration
        self.node_style = NodeStyle()
        self.edge_style = EdgeStyle()
        self.highlight_color = HIGHLIGHT_COLOR
        self.highlight_width = HIGHLIGHT_WIDTH
        
        # Animation state
        self._animation_state = AnimationState(
            node_pos={},
            edge_points={},
            highlight_nodes={},
            highlight_edges={}
        )
        self._last_update = 0
        self._is_animating = False
        
        # Interaction state
        self._hovered_node = None
        self._selected_node = None
        self._dragging = False
        self._drag_start = (0, 0)
        self._drag_offset = (0, 0)
        
        # Callbacks
        self.on_node_click = None
        self.on_edge_click = None
        
        # Initialize the layout
        self._update_layout()
    
    @property
    def data_structure(self) -> Optional[DataStructure]:
        """Get the current data structure"""
        return self._data_structure
    
    @data_structure.setter
    def data_structure(self, ds: Optional[DataStructure]):
        """Set the data structure to visualize"""
        if self._data_structure != ds:
            self._data_structure = ds
            self._update_layout()
    
    @property
    def layout(self) -> LayoutDirection:
        """Get the current layout direction"""
        return self._layout
    
    @layout.setter
    def layout(self, direction: LayoutDirection):
        """Set the layout direction"""
        if self._layout != direction:
            self._layout = direction
            self._update_layout()
    
    def _update_layout(self):
        """Update the layout of nodes and edges based on the data structure"""
        if not self._data_structure:
            self._animation_state.node_pos = {}
            self._animation_state.edge_points = {}
            self._is_animating = False
            return
        
        # Get the current time for animations
        current_time = pygame.time.get_ticks()
        self._animation_state.current_time = current_time
        
        # Update node positions based on layout
        if self._layout == LayoutDirection.HORIZONTAL:
            self._update_horizontal_layout()
        elif self._layout == LayoutDirection.VERTICAL:
            self._update_vertical_layout()
        elif self._layout == LayoutDirection.TREE:
            self._update_tree_layout()
        elif self._layout == LayoutDirection.GRAPH:
            self._update_graph_layout()
        
        # Update edge positions
        self._update_edge_positions()
        
        # Check if we need to animate
        self._check_animation_state()
    
    def _update_horizontal_layout(self):
        """Arrange nodes in a horizontal line"""
        if not self._data_structure:
            return
        
        nodes = self._get_nodes()
        if not nodes:
            return
        
        # Calculate spacing
        total_width = self.width - 2 * self.node_style.radius
        spacing = total_width / (len(nodes) + 1)
        
        # Update node positions
        center_y = self.height // 2
        for i, node in enumerate(nodes):
            x = int(self.node_style.radius + (i + 1) * spacing)
            self._set_node_position(node, x, center_y)
    
    def _update_vertical_layout(self):
        """Arrange nodes in a vertical line"""
        if not self._data_structure:
            return
        
        nodes = self._get_nodes()
        if not nodes:
            return
        
        # Calculate spacing
        total_height = self.height - 2 * self.node_style.radius
        spacing = total_height / (len(nodes) + 1)
        
        # Update node positions
        center_x = self.width // 2
        for i, node in enumerate(nodes):
            y = int(self.node_style.radius + (i + 1) * spacing)
            self._set_node_position(node, center_x, y)
    
    def _update_tree_layout(self):
        """Arrange nodes in a tree layout"""
        if not isinstance(self._data_structure, (BinaryTree, LinkedList)):
            return self._update_horizontal_layout()
        
        # For binary trees and linked lists, we can use a tree layout
        root = None
        if isinstance(self._data_structure, BinaryTree):
            root = self._data_structure.root
        elif isinstance(self._data_structure, LinkedList):
            root = self._data_structure.head
        
        if not root:
            return
        
        # Calculate tree depth and node positions
        depth = self._calculate_tree_depth(root)
        if depth == 0:
            return
        
        # Calculate level heights
        level_heights = []
        total_height = self.height - 2 * self.node_style.radius
        level_height = total_height / max(1, depth - 1)
        
        for i in range(depth):
            level_heights.append(int(self.node_style.radius + i * level_height))
        
        # Position nodes using a breadth-first traversal
        queue = [(root, 0, 0, self.width)]  # (node, level, left, right)
        
        while queue:
            node, level, left, right = queue.pop(0)
            
            # Calculate position
            x = (left + right) // 2
            y = level_heights[level] if level < len(level_heights) else level_heights[-1]
            
            # Update node position
            self._set_node_position(self._get_node_id(node), x, y)
            
            # Add children to queue
            if isinstance(node, BinaryTreeNode):
                if node.left:
                    queue.append((node.left, level + 1, left, x))
                if node.right:
                    queue.append((node.right, level + 1, x, right))
            elif isinstance(node, LinkedListNode) and node.next:
                queue.append((node.next, level, x, right))
    
    def _update_graph_layout(self):
        """Arrange nodes in a force-directed graph layout"""
        if not isinstance(self._data_structure, Graph):
            return self._update_horizontal_layout()
        
        # Simple force-directed graph layout
        nodes = list(self._data_structure.adjacency_list.keys())
        if not nodes:
            return
        
        # Initialize positions randomly if not set
        for node in nodes:
            if self._get_node_id(node) not in self._animation_state.node_pos:
                x = self.node_style.radius + (self.width - 2 * self.node_style.radius) * (hash(str(node)) % 100) / 100
                y = self.node_style.radius + (self.height - 2 * self.node_style.radius) * (hash(str(node) + "y") % 100) / 100
                self._set_node_position(self._get_node_id(node), x, y, immediate=True)
        
        # Simple force-directed layout simulation
        for _ in range(50):  # Number of iterations
            # Repulsive forces
            for i, node1 in enumerate(nodes):
                id1 = self._get_node_id(node1)
                x1, y1 = self._get_node_position(id1)
                
                for j in range(i + 1, len(nodes)):
                    node2 = nodes[j]
                    id2 = self._get_node_id(node2)
                    x2, y2 = self._get_node_position(id2)
                    
                    # Calculate distance
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = max(0.1, (dx * dx + dy * dy) ** 0.5)
                    
                    # Apply repulsive force (inverse square law)
                    force = 1000 / (dist * dist)
                    fx = force * dx / dist
                    fy = force * dy / dist
                    
                    # Update positions
                    self._animation_state.node_pos[id1] = (
                        max(self.node_style.radius, min(self.width - self.node_style.radius, x1 - fx * 0.5)),
                        max(self.node_style.radius, min(self.height - self.node_style.radius, y1 - fy * 0.5))
                    )
                    
                    self._animation_state.node_pos[id2] = (
                        max(self.node_style.radius, min(self.width - self.node_style.radius, x2 + fx * 0.5)),
                        max(self.node_style.radius, min(self.height - self.node_style.radius, y2 + fy * 0.5))
                    )
            
            # Attractive forces (springs for edges)
            for node1, neighbors in self._data_structure.adjacency_list.items():
                id1 = self._get_node_id(node1)
                x1, y1 = self._get_node_position(id1)
                
                for node2 in neighbors:
                    id2 = self._get_node_id(node2)
                    x2, y2 = self._get_node_position(id2)
                    
                    # Calculate distance
                    dx = x2 - x1
                    dy = y2 - y1
                    dist = max(0.1, (dx * dx + dy * dy) ** 0.5)
                    
                    # Apply attractive force (spring)
                    force = 0.01 * dist
                    fx = force * dx / dist
                    fy = force * dy / dist
                    
                    # Update positions
                    self._animation_state.node_pos[id1] = (
                        max(self.node_style.radius, min(self.width - self.node_style.radius, x1 + fx)),
                        max(self.node_style.radius, min(self.height - self.node_style.radius, y1 + fy))
                    )
                    
                    self._animation_state.node_pos[id2] = (
                        max(self.node_style.radius, min(self.width - self.node_style.radius, x2 - fx)),
                        max(self.node_style.radius, min(self.height - self.node_style.radius, y2 - fy))
                    )
    
    def _update_edge_positions(self):
        """Update the positions of all edges based on node positions"""
        if not self._data_structure:
            self._animation_state.edge_points = {}
            return
        
        edges = self._get_edges()
        edge_points = {}
        
        for edge in edges:
            node1, node2 = edge
            id1 = self._get_node_id(node1)
            id2 = self._get_node_id(node2)
            
            # Get node positions
            x1, y1 = self._get_node_position(id1)
            x2, y2 = self._get_node_position(id2)
            
            # Calculate edge points (with arrow for directed edges)
            if self.edge_style.directed:
                # Calculate arrow points
                angle = math.atan2(y2 - y1, x2 - x1)
                arrow_len = self.edge_style.arrow_size
                arrow_angle = math.pi / 6  # 30 degrees
                
                # Calculate arrow points
                x3 = x2 - arrow_len * math.cos(angle - arrow_angle)
                y3 = y2 - arrow_len * math.sin(angle - arrow_angle)
                x4 = x2 - arrow_len * math.cos(angle + arrow_angle)
                y4 = y2 - arrow_len * math.sin(angle + arrow_angle)
                
                # Adjust line end to account for node radius
                radius = self.node_style.radius
                x2 = x1 + (x2 - x1) * (1 - radius / max(1, ((x2-x1)**2 + (y2-y1)**2)**0.5))
                y2 = y1 + (y2 - y1) * (1 - radius / max(1, ((x2-x1)**2 + (y2-y1)**2)**0.5))
                
                edge_points[edge] = [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
            else:
                edge_points[edge] = [(x1, y1), (x2, y2)]
        
        self._animation_state.edge_points = edge_points
    
    def _get_nodes(self) -> List[Any]:
        """Get a list of nodes in the data structure"""
        if not self._data_structure:
            return []
        
        if isinstance(self._data_structure, (Stack, Queue)):
            return self._data_structure.elements
        elif isinstance(self._data_structure, LinkedList):
            nodes = []
            current = self._data_structure.head
            while current:
                nodes.append(current)
                current = current.next
            return nodes
        elif isinstance(self._data_structure, BinaryTree):
            nodes = []
            self._collect_tree_nodes(self._data_structure.root, nodes)
            return nodes
        elif isinstance(self._data_structure, Graph):
            return list(self._data_structure.adjacency_list.keys())
        else:
            return []
    
    def _collect_tree_nodes(self, node: Optional[BinaryTreeNode], nodes: List[BinaryTreeNode]):
        """Collect all nodes in a binary tree using in-order traversal"""
        if not node:
            return
        
        self._collect_tree_nodes(node.left, nodes)
        nodes.append(node)
        self._collect_tree_nodes(node.right, nodes)
    
    def _get_edges(self) -> List[Tuple[Any, Any]]:
        """Get a list of edges in the data structure"""
        if not self._data_structure:
            return []
        
        edges = []
        
        if isinstance(self._data_structure, (Stack, Queue)):
            # No edges for stack/queue (just ordered list)
            pass
        elif isinstance(self._data_structure, LinkedList):
            # Add edges between linked list nodes
            current = self._data_structure.head
            while current and current.next:
                edges.append((current, current.next))
                current = current.next
        elif isinstance(self._data_structure, BinaryTree):
            # Add edges between tree nodes
            self._collect_tree_edges(self._data_structure.root, edges)
        elif isinstance(self._data_structure, Graph):
            # Add all graph edges
            for node, neighbors in self._data_structure.adjacency_list.items():
                for neighbor in neighbors:
                    # Only add each edge once for undirected graphs
                    if (neighbor, node) not in edges:
                        edges.append((node, neighbor))
        
        return edges
    
    def _collect_tree_edges(self, node: Optional[BinaryTreeNode], edges: List[Tuple[Any, Any]]):
        """Collect all edges in a binary tree"""
        if not node:
            return
        
        if node.left:
            edges.append((node, node.left))
            self._collect_tree_edges(node.left, edges)
        
        if node.right:
            edges.append((node, node.right))
            self._collect_tree_edges(node.right, edges)
    
    def _get_node_id(self, node: Any) -> Any:
        """Get a unique identifier for a node"""
        # For primitive types, use the value itself as ID
        if isinstance(node, (int, float, str, bool)) or node is None:
            return node
        
        # For objects, use their memory address
        return id(node)
    
    def _get_node_position(self, node_id: Any) -> Tuple[float, float]:
        """Get the current position of a node"""
        if node_id in self._animation_state.node_pos:
            return self._animation_state.node_pos[node_id]
        
        # Default position (center)
        return (self.width // 2, self.height // 2)
    
    def _set_node_position(self, node_id: Any, x: float, y: float, immediate: bool = False):
        """Set the position of a node"""
        if immediate:
            self._animation_state.node_pos[node_id] = (x, y)
        else:
            # Smooth animation to the new position
            if node_id in self._animation_state.node_pos:
                current_x, current_y = self._animation_state.node_pos[node_id]
                self._animation_state.node_pos[node_id] = (
                    current_x + (x - current_x) * ANIMATION_SPEED,
                    current_y + (y - current_y) * ANIMATION_SPEED
                )
            else:
                self._animation_state.node_pos[node_id] = (x, y)
    
    def _calculate_tree_depth(self, node: Any, current_depth: int = 0) -> int:
        """Calculate the depth of a tree"""
        if not node:
            return current_depth
        
        if isinstance(node, BinaryTreeNode):
            return max(
                self._calculate_tree_depth(node.left, current_depth + 1),
                self._calculate_tree_depth(node.right, current_depth + 1)
            )
        elif isinstance(node, LinkedListNode):
            return self._calculate_tree_depth(node.next, current_depth + 1)
        else:
            return current_depth + 1
    
    def _check_animation_state(self):
        """Check if any animations are in progress"""
        self._is_animating = False
        
        # Check node positions
        for node_id, (x, y) in self._animation_state.node_pos.items():
            target_x, target_y = self._get_node_position(node_id)
            if abs(x - target_x) > 0.1 or abs(y - target_y) > 0.1:
                self._is_animating = True
                break
        
        # Check highlights
        current_time = pygame.time.get_ticks()
        if any(end_time > current_time for end_time in self._animation_state.highlight_nodes.values()):
            self._is_animating = True
        
        if any(end_time > current_time for end_time in self._animation_state.highlight_edges.values()):
            self._is_animating = True
    
    def highlight_node(self, node: Any, duration: int = HIGHLIGHT_DURATION):
        """Highlight a node for a specified duration"""
        node_id = self._get_node_id(node)
        self._animation_state.highlight_nodes[node_id] = pygame.time.get_ticks() + duration
        self._is_animating = True
    
    def highlight_edge(self, node1: Any, node2: Any, duration: int = HIGHLIGHT_DURATION):
        """Highlight an edge for a specified duration"""
        edge = (self._get_node_id(node1), self._get_node_id(node2))
        self._animation_state.highlight_edges[edge] = pygame.time.get_ticks() + duration
        self._is_animating = True
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the data structure visualization"""
        if not self._data_structure:
            return
        
        # Update animation state
        self._update_animation()
        
        # Draw edges first (behind nodes)
        self._draw_edges(surface, abs_x, abs_y)
        
        # Then draw nodes (on top of edges)
        self._draw_nodes(surface, abs_x, abs_y)
    
    def _draw_nodes(self, surface: pygame.Surface, offset_x: int, offset_y: int):
        """Draw all nodes in the data structure"""
        nodes = self._get_nodes()
        current_time = pygame.time.get_ticks()
        
        for node in nodes:
            node_id = self._get_node_id(node)
            x, y = self._get_node_position(node_id)
            
            # Check if node is hovered or selected
            is_hovered = (node_id == self._hovered_node)
            is_selected = (node_id == self._selected_node)
            is_highlighted = (
                node_id in self._animation_state.highlight_nodes and 
                self._animation_state.highlight_nodes[node_id] > current_time
            )
            
            # Draw the node
            self._draw_node(
                surface,
                int(offset_x + x),
                int(offset_y + y),
                str(getattr(node, 'value', node)),
                is_hovered,
                is_selected,
                is_highlighted
            )
    
    def _draw_node(self, surface: pygame.Surface, x: int, y: int, label: str,
                  is_hovered: bool = False, is_selected: bool = False,
                  is_highlighted: bool = False):
        """Draw a single node"""
        # Determine colors
        if is_highlighted:
            fill_color = self.highlight_color
            border_color = self.highlight_color
        elif is_selected:
            fill_color = self.node_style.selected_color
            border_color = self.node_style.border_color
        elif is_hovered:
            fill_color = self.node_style.hover_color
            border_color = self.node_style.border_color
        else:
            fill_color = self.node_style.color
            border_color = self.node_style.border_color
        
        # Draw the node circle
        pygame.draw.circle(
            surface,
            fill_color,
            (x, y),
            self.node_style.radius
        )
        
        # Draw the border
        if self.node_style.border_width > 0:
            pygame.draw.circle(
                surface,
                border_color,
                (x, y),
                self.node_style.radius,
                self.node_style.border_width
            )
        
        # Draw the label
        if label:
            font = pygame.font.SysFont(self.node_style.font_name, self.node_style.text_size)
            text_surface = font.render(str(label), True, self.node_style.text_color)
            text_rect = text_surface.get_rect(center=(x, y))
            surface.blit(text_surface, text_rect)
    
    def _draw_edges(self, surface: pygame.Surface, offset_x: int, offset_y: int):
        """Draw all edges in the data structure"""
        edges = self._get_edges()
        current_time = pygame.time.get_ticks()
        
        for edge in edges:
            node1, node2 = edge
            id1 = self._get_node_id(node1)
            id2 = self._get_node_id(node2)
            
            # Check if edge is highlighted
            is_highlighted = (
                (id1, id2) in self._animation_state.highlight_edges and 
                self._animation_state.highlight_edges[(id1, id2)] > current_time
            ) or (
                (id2, id1) in self._animation_state.highlight_edges and 
                self._animation_state.highlight_edges[(id2, id1)] > current_time
            )
            
            # Get the edge points from the animation state
            if edge in self._animation_state.edge_points:
                points = self._animation_state.edge_points[edge]
                
                # Draw the edge line
                if len(points) >= 2:
                    self._draw_edge(
                        surface,
                        points[0][0] + offset_x,
                        points[0][1] + offset_y,
                        points[1][0] + offset_x,
                        points[1][1] + offset_y,
                        is_highlighted
                    )
                
                # Draw the arrow for directed edges
                if self.edge_style.directed and len(points) >= 4:
                    self._draw_arrow(
                        surface,
                        points[1][0] + offset_x,
                        points[1][1] + offset_y,
                        points[2][0] + offset_x,
                        points[2][1] + offset_y,
                        points[3][0] + offset_x,
                        points[3][1] + offset_y,
                        is_highlighted
                    )
    
    def _draw_edge(self, surface: pygame.Surface, x1: float, y1: float, 
                  x2: float, y2: float, is_highlighted: bool = False):
        """Draw a line between two points"""
        color = self.highlight_color if is_highlighted else self.edge_style.color
        width = self.highlight_width if is_highlighted else self.edge_style.width
        
        pygame.draw.line(
            surface,
            color,
            (int(x1), int(y1)),
            (int(x2), int(y2)),
            width
        )
    
    def _draw_arrow(self, surface: pygame.Surface, x1: float, y1: float, 
                   x2: float, y2: float, x3: float, y3: float, 
                   is_highlighted: bool = False):
        """Draw an arrow (triangle) at the end of an edge"""
        color = self.highlight_color if is_highlighted else self.edge_style.color
        
        pygame.draw.polygon(
            surface,
            color,
            [
                (int(x1), int(y1)),
                (int(x2), int(y2)),
                (int(x3), int(y3))
            ]
        )
    
    def _update_animation(self):
        """Update the animation state"""
        current_time = pygame.time.get_ticks()
        
        # Update node positions with easing
        for node_id, (x, y) in list(self._animation_state.node_pos.items()):
            target_x, target_y = self._get_node_position(node_id)
            
            # Skip if already at target
            if abs(x - target_x) < 0.1 and abs(y - target_y) < 0.1:
                self._animation_state.node_pos[node_id] = (target_x, target_y)
                continue
            
            # Apply easing
            new_x = x + (target_x - x) * ANIMATION_SPEED
            new_y = y + (target_y - y) * ANIMATION_SPEED
            
            # Update position
            self._animation_state.node_pos[node_id] = (new_x, new_y)
        
        # Update edge positions
        self._update_edge_positions()
        
        # Check if any highlights have expired
        current_time = pygame.time.get_ticks()
        
        expired_nodes = [
            node_id for node_id, end_time in self._animation_state.highlight_nodes.items()
            if end_time <= current_time
        ]
        
        expired_edges = [
            edge for edge, end_time in self._animation_state.highlight_edges.items()
            if end_time <= current_time
        ]
        
        for node_id in expired_nodes:
            del self._animation_state.highlight_nodes[node_id]
        
        for edge in expired_edges:
            del self._animation_state.highlight_edges[edge]
        
        # Check if we're still animating
        self._check_animation_state()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse and keyboard events"""
        if not self.visible or not self.enabled:
            return False
        
        mouse_pos = pygame.mouse.get_pos()
        mouse_x = mouse_pos[0] - self.get_absolute_position()[0]
        mouse_y = mouse_pos[1] - self.get_absolute_position()[1]
        
        # Check if mouse is over any node
        hovered_node = self._get_node_at(mouse_x, mouse_y)
        
        # Update hover state
        if hovered_node != self._hovered_node:
            self._hovered_node = hovered_node
            self._needs_redraw = True
        
        # Handle mouse button events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if hovered_node is not None:
                    self._selected_node = hovered_node
                    self._dragging = True
                    
                    # Calculate offset from node center
                    node_x, node_y = self._get_node_position(hovered_node)
                    self._drag_offset = (node_x - mouse_x, node_y - mouse_y)
                    
                    # Trigger click callback
                    if self.on_node_click:
                        self.on_node_click(hovered_node)
                    
                    return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                if self._dragging:
                    self._dragging = False
                    return True
        
        elif event.type == pygame.MOUSEMOTION:
            if self._dragging and self._selected_node is not None:
                # Update node position while dragging
                new_x = mouse_x + self._drag_offset[0]
                new_y = mouse_y + self._drag_offset[1]
                
                # Keep node within bounds
                new_x = max(self.node_style.radius, min(self.width - self.node_style.radius, new_x))
                new_y = max(self.node_style.radius, min(self.height - self.node_style.radius, new_y))
                
                self._set_node_position(self._selected_node, new_x, new_y, immediate=True)
                self._update_edge_positions()
                self._needs_redraw = True
                return True
        
        return False
    
    def _get_node_at(self, x: float, y: float) -> Optional[Any]:
        """Get the node at the specified coordinates, or None if none found"""
        nodes = self._get_nodes()
        
        for node in nodes:
            node_id = self._get_node_id(node)
            node_x, node_y = self._get_node_position(node_id)
            
            # Calculate distance from mouse to node center
            dx = x - node_x
            dy = y - node_y
            distance_sq = dx * dx + dy * dy
            
            # Check if mouse is within node radius
            if distance_sq <= self.node_style.radius * self.node_style.radius:
                return node_id
        
        return None
    
    def update(self, dt: float):
        """Update the component state"""
        if not self.visible:
            return
        
        # Update animations
        if self._is_animating:
            self._update_animation()
    
    def is_animating(self) -> bool:
        """Check if the visualization is currently animating"""
        return self._is_animating
