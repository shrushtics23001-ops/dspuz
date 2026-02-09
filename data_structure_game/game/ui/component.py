import pygame
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum, auto

class UIEventType(Enum):
    CLICK = auto()
    HOVER = auto()
    PRESS = auto()
    RELEASE = auto()
    FOCUS = auto()
    BLUR = auto()
    CHANGE = auto()

@dataclass
class UIEvent:
    type: UIEventType
    target: 'UIComponent'
    data: Dict[str, Any] = None

class UIComponent:
    """Base class for all UI components"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 parent: Optional['UIComponent'] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.parent = parent
        self.children: List['UIComponent'] = []
        self.visible = True
        self.enabled = True
        self.focused = False
        self.hovered = False
        self.styles: Dict[str, Any] = {}
        self.event_listeners: Dict[UIEventType, List[Callable]] = {}
        self.rect = pygame.Rect(x, y, width, height)
        self.clip_rect: Optional[pygame.Rect] = None
        self.z_index = 0
        self.tag: str = ""
        self.id: str = ""
        self.classes: List[str] = []
        
        # Initialize default styles
        self.styles = {
            'background_color': None,
            'border_color': None,
            'border_width': 0,
            'border_radius': 0,
            'padding': (0, 0, 0, 0),  # top, right, bottom, left
            'margin': (0, 0, 0, 0),   # top, right, bottom, left
            'opacity': 255,
            'cursor': None
        }
    
    def add_event_listener(self, event_type: UIEventType, callback: Callable):
        """Add an event listener for this component"""
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(callback)
    
    def remove_event_listener(self, event_type: UIEventType, callback: Callable):
        """Remove an event listener"""
        if event_type in self.event_listeners:
            if callback in self.event_listeners[event_type]:
                self.event_listeners[event_type].remove(callback)
    
    def dispatch_event(self, event: UIEvent):
        """Dispatch an event to this component and its listeners"""
        # Call the corresponding method if it exists
        method_name = f"on_{event.type.name.lower()}"
        if hasattr(self, method_name):
            getattr(self, method_name)(event)
        
        # Call all registered listeners
        if event.type in self.event_listeners:
            for callback in self.event_listeners[event.type]:
                callback(event)
    
    def add_child(self, child: 'UIComponent'):
        """Add a child component"""
        if child not in self.children:
            self.children.append(child)
            child.parent = self
            self._update_child_positions()
    
    def remove_child(self, child: 'UIComponent') -> bool:
        """Remove a child component"""
        if child in self.children:
            self.children.remove(child)
            child.parent = None
            return True
        return False
    
    def _update_child_positions(self):
        """Update positions of child components based on layout"""
        # Basic implementation - can be overridden by layout managers
        pass
    
    def get_absolute_position(self) -> Tuple[int, int]:
        """Get the absolute position of this component"""
        if self.parent:
            parent_x, parent_y = self.parent.get_absolute_position()
            return (parent_x + self.x, parent_y + self.y)
        return (self.x, self.y)
    
    def get_absolute_rect(self) -> pygame.Rect:
        """Get the absolute rectangle of this component"""
        x, y = self.get_absolute_position()
        return pygame.Rect(x, y, self.width, self.height)
    
    def point_in_component(self, point: Tuple[int, int]) -> bool:
        """Check if a point is inside this component"""
        x, y = self.get_absolute_position()
        return (x <= point[0] < x + self.width and 
                y <= point[1] < y + self.height)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle a pygame event. Returns True if the event was handled."""
        if not self.visible or not self.enabled:
            return False
            
        handled = False
        
        # Let children handle the event first (reverse order for proper z-index)
        for child in reversed(self.children):
            if child.handle_event(event):
                handled = True
                break
        
        if handled:
            return True
            
        # Handle mouse events
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = pygame.mouse.get_pos()
            was_hovered = self.hovered
            self.hovered = self.point_in_component(mouse_pos)
            
            if self.hovered and not was_hovered:
                self.dispatch_event(UIEvent(UIEventType.HOVER, self))
                if self.styles.get('cursor'):
                    pygame.mouse.set_cursor(*pygame.cursors.tri_left)
            elif not self.hovered and was_hovered:
                self.dispatch_event(UIEvent(UIEventType.HOVER, self, {'exited': True}))
                if self.styles.get('cursor'):
                    pygame.mouse.set_cursor(*pygame.cursors.arrow)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.hovered:  # Left mouse button
                self.dispatch_event(UIEvent(UIEventType.PRESS, self))
                if not self.focused:
                    self.set_focus(True)
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.hovered:  # Left mouse button
                self.dispatch_event(UIEvent(UIEventType.CLICK, self))
                self.dispatch_event(UIEvent(UIEventType.RELEASE, self))
                return True
        
        # Handle keyboard events if focused
        elif self.focused and event.type in (pygame.KEYDOWN, pygame.KEYUP, pygame.TEXTINPUT):
            # Subclasses can handle these events
            pass
            
        return False
    
    def set_focus(self, focused: bool):
        """Set the focus state of this component"""
        if focused != self.focused:
            self.focused = focused
            if focused:
                self.dispatch_event(UIEvent(UIEventType.FOCUS, self))
                # If this component is getting focus, notify parent to manage focus
                if self.parent:
                    self.parent._child_got_focus(self)
            else:
                self.dispatch_event(UIEvent(UIEventType.BLUR, self))
    
    def _child_got_focus(self, child: 'UIComponent'):
        """Called when a child component receives focus"""
        # Remove focus from other children
        for c in self.children:
            if c != child and c.focused:
                c.set_focus(False)
        
        # Notify parent
        if self.parent:
            self.parent._child_got_focus(self)
    
    def update(self, dt: float):
        """Update the component state"""
        if not self.visible:
            return
            
        for child in self.children:
            child.update(dt)
    
    def render(self, surface: pygame.Surface):
        """Render the component to the given surface"""
        if not self.visible:
            return
            
        # Save the current clip rect
        old_clip = surface.get_clip()
        
        # Set the new clip rect if needed
        if self.clip_rect:
            surface.set_clip(self.clip_rect)
        
        # Get absolute position
        abs_x, abs_y = self.get_absolute_position()
        
        # Draw background if needed
        bg_color = self.styles.get('background_color')
        if bg_color:
            border_radius = self.styles.get('border_radius', 0)
            border_width = self.styles.get('border_width', 0)
            border_color = self.styles.get('border_color')
            
            # Draw the background
            bg_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            if border_radius > 0:
                pygame.draw.rect(surface, bg_color, bg_rect, 
                               border_radius=border_radius)
                if border_width > 0 and border_color:
                    pygame.draw.rect(surface, border_color, bg_rect, 
                                   border_width, border_radius=border_radius)
            else:
                pygame.draw.rect(surface, bg_color, bg_rect)
                if border_width > 0 and border_color:
                    pygame.draw.rect(surface, border_color, bg_rect, border_width)
        
        # Let the component draw its custom content
        self._render_content(surface, abs_x, abs_y)
        
        # Render children
        for child in sorted(self.children, key=lambda c: c.z_index):
            child.render(surface)
        
        # Restore the old clip rect
        surface.set_clip(old_clip)
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Override this method to render the component's content"""
        pass
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        for key, value in styles.items():
            if key in self.styles:
                self.styles[key] = value
        
        # Trigger a re-layout if needed
        if any(k in styles for k in ['width', 'height', 'padding', 'margin']):
            if self.parent:
                self.parent._update_child_positions()
    
    def get_style(self, name: str, default=None) -> Any:
        """Get a style property"""
        return self.styles.get(name, default)
    
    def set_position(self, x: int, y: int):
        """Set the position of this component"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_size(self, width: int, height: int):
        """Set the size of this component"""
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height
        
        # Notify children of size change
        self._update_child_positions()
    
    def show(self):
        """Show the component"""
        self.visible = True
    
    def hide(self):
        """Hide the component"""
        self.visible = False
    
    def enable(self):
        """Enable the component"""
        self.enabled = True
    
    def disable(self):
        """Disable the component"""
        self.enabled = False
    
    def find_by_id(self, element_id: str) -> Optional['UIComponent']:
        """Find a child component by ID"""
        if self.id == element_id:
            return self
            
        for child in self.children:
            found = child.find_by_id(element_id)
            if found:
                return found
                
        return None
    
    def find_by_class(self, class_name: str) -> List['UIComponent']:
        """Find all child components with the given class name"""
        result = []
        
        if class_name in self.classes:
            result.append(self)
            
        for child in self.children:
            result.extend(child.find_by_class(class_name))
            
        return result
    
    def __str__(self) -> str:
        return f"<{self.__class__.__name__} id='{self.id}'>"

class Container(UIComponent):
    """A simple container component that can hold other components"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 parent: Optional[UIComponent] = None):
        super().__init__(x, y, width, height, parent)
        self.layout = 'vertical'  # 'vertical' or 'horizontal' or 'none'
        self.spacing = 5
    
    def _update_child_positions(self):
        if self.layout == 'none':
            return
            
        x = self.styles.get('padding', (0, 0, 0, 0))[3]  # left padding
        y = self.styles.get('padding', (0, 0, 0, 0))[0]  # top padding
        
        max_height = 0
        
        for child in self.children:
            if not child.visible:
                continue
                
            if self.layout == 'vertical':
                child.set_position(x, y)
                y += child.height + self.spacing
                max_height = max(max_height, child.width)
            else:  # horizontal
                child.set_position(x, y)
                x += child.width + self.spacing
                max_height = max(max_height, child.height)
        
        # Update container size to fit all children if needed
        if self.layout == 'vertical':
            content_height = y - self.spacing + self.styles.get('padding', (0, 0, 0, 0))[2]  # bottom padding
            self.set_size(max(max_height, self.width), max(content_height, self.height))
        else:  # horizontal
            content_width = x - self.spacing + self.styles.get('padding', (0, 0, 0, 0))[1]  # right padding
            self.set_size(max(content_width, self.width), max(max_height, self.height))
