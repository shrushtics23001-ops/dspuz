import pygame
from typing import Optional, List, Tuple, Dict, Any, Callable
from .component import UIComponent, UIEvent, UIEventType

class Panel(UIComponent):
    """A container component that can hold other components and has a background"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 parent: Optional[UIComponent] = None):
        super().__init__(x, y, width, height, parent)
        
        # Default styles for panel
        self.styles.update({
            'background_color': (240, 240, 240),
            'border_color': (200, 200, 200),
            'border_width': 1,
            'border_radius': 0,
            'padding': (10, 10, 10, 10),  # top, right, bottom, left
            'shadow': False,
            'shadow_color': (0, 0, 0, 100),
            'shadow_offset': (2, 2),
            'scrollable': False,
            'scroll_x': 0,
            'scroll_y': 0,
            'clip_children': True
        })
        
        # Create a surface for the panel content
        self._content_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self._content_rect = pygame.Rect(0, 0, width, height)
        
        # Scroll bars
        self._vscroll_visible = False
        self._hscroll_visible = False
        self._scrollbar_size = 12
        self._scrollbar_color = (180, 180, 180)
        self._scrollbar_hover_color = (160, 160, 160)
        self._scrollbar_active_color = (140, 140, 140)
        self._scrollbar_hovered = False
        self._scrollbar_pressed = False
        self._scrollbar_drag_start = None
        
        # Content size (for scrolling)
        self._content_width = width
        self._content_height = height
        
        # Scroll bar thumbs
        self._vscroll_thumb = pygame.Rect(0, 0, 0, 0)
        self._hscroll_thumb = pygame.Rect(0, 0, 0, 0)
        self._update_scroll_bars()
    
    def _update_scroll_bars(self):
        """Update the scroll bars based on content size and viewport"""
        # Check if vertical scroll bar is needed
        self._vscroll_visible = (
            self.styles['scrollable'] and 
            self._content_height > self.height
        )
        
        # Check if horizontal scroll bar is needed
        self._hscroll_visible = (
            self.styles['scrollable'] and 
            self._content_width > self.width - (self._scrollbar_size if self._vscroll_visible else 0)
        )
        
        # Update content rectangle
        content_width = self.width
        content_height = self.height
        
        if self._vscroll_visible:
            content_width -= self._scrollbar_size
        if self._hscroll_visible:
            content_height -= self._scrollbar_size
        
        # Update content surface size if needed
        if (self._content_surface.get_width() != content_width or 
            self._content_surface.get_height() != content_height):
            self._content_surface = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
        
        self._content_rect.size = (content_width, content_height)
        
        # Update scroll thumb sizes and positions
        if self._vscroll_visible:
            # Calculate thumb height based on visible area ratio
            visible_ratio = self.height / self._content_height
            thumb_height = max(30, int(self.height * visible_ratio))
            
            # Calculate thumb position based on scroll position
            scroll_range = self._content_height - self.height
            thumb_y = int((self.styles['scroll_y'] / scroll_range) * (self.height - thumb_height))
            
            self._vscroll_thumb = pygame.Rect(
                self.width - self._scrollbar_size,
                thumb_y,
                self._scrollbar_size,
                thumb_height
            )
        
        if self._hscroll_visible:
            # Calculate thumb width based on visible area ratio
            visible_ratio = (self.width - (self._scrollbar_size if self._vscroll_visible else 0)) / self._content_width
            thumb_width = max(30, int((self.width - (self._scrollbar_size if self._vscroll_visible else 0)) * visible_ratio))
            
            # Calculate thumb position based on scroll position
            scroll_range = self._content_width - self.width + (self._scrollbar_size if self._vscroll_visible else 0)
            thumb_x = int((self.styles['scroll_x'] / scroll_range) * (self.width - thumb_width - (self._scrollbar_size if self._vscroll_visible else 0)))
            
            self._hscroll_thumb = pygame.Rect(
                thumb_x,
                self.height - self._scrollbar_size,
                thumb_width,
                self._scrollbar_size
            )
    
    def set_content_size(self, width: int, height: int):
        """Set the size of the content area (for scrolling)"""
        if self._content_width != width or self._content_height != height:
            self._content_width = max(width, self.width - (self._scrollbar_size if self._vscroll_visible else 0))
            self._content_height = max(height, self.height - (self._scrollbar_size if self._hscroll_visible else 0))
            self._update_scroll_bars()
    
    def scroll_to(self, x: int = None, y: int = None):
        """Scroll to the specified position"""
        scroll_x = self.styles['scroll_x']
        scroll_y = self.styles['scroll_y']
        
        if x is not None:
            max_scroll_x = max(0, self._content_width - self.width + (self._scrollbar_size if self._vscroll_visible else 0))
            scroll_x = max(0, min(x, max_scroll_x))
        
        if y is not None:
            max_scroll_y = max(0, self._content_height - self.height + (self._scrollbar_size if self._hscroll_visible else 0))
            scroll_y = max(0, min(y, max_scroll_y))
        
        if scroll_x != self.styles['scroll_x'] or scroll_y != self.styles['scroll_y']:
            self.styles['scroll_x'] = scroll_x
            self.styles['scroll_y'] = scroll_y
            self._update_scroll_bars()
            return True
        
        return False
    
    def scroll_by(self, dx: int, dy: int):
        """Scroll by the specified amount"""
        return self.scroll_to(
            self.styles['scroll_x'] + dx,
            self.styles['scroll_y'] + dy
        )
    
    def _render_scroll_bars(self, surface: pygame.Surface):
        """Render the scroll bars"""
        if not self.styles['scrollable']:
            return
        
        # Draw vertical scroll bar
        if self._vscroll_visible:
            # Track
            track_rect = pygame.Rect(
                self.width - self._scrollbar_size,
                0,
                self._scrollbar_size,
                self.height - (self._scrollbar_size if self._hscroll_visible else 0)
            )
            pygame.draw.rect(surface, (220, 220, 220), track_rect)
            
            # Thumb
            thumb_color = self._scrollbar_active_color if self._scrollbar_pressed else \
                         self._scrollbar_hover_color if self._scrollbar_hovered else \
                         self._scrollbar_color
            
            pygame.draw.rect(surface, thumb_color, self._vscroll_thumb, border_radius=6)
            pygame.draw.rect(
                surface, 
                (255, 255, 255, 100), 
                self._vscroll_thumb.inflate(-4, -4), 
                border_radius=4
            )
        
        # Draw horizontal scroll bar
        if self._hscroll_visible:
            # Track
            track_rect = pygame.Rect(
                0,
                self.height - self._scrollbar_size,
                self.width - (self._scrollbar_size if self._vscroll_visible else 0),
                self._scrollbar_size
            )
            pygame.draw.rect(surface, (220, 220, 220), track_rect)
            
            # Thumb
            thumb_color = self._scrollbar_active_color if self._scrollbar_pressed else \
                         self._scrollbar_hover_color if self._scrollbar_hovered else \
                         self._scrollbar_color
            
            pygame.draw.rect(surface, thumb_color, self._hscroll_thumb, border_radius=6)
            pygame.draw.rect(
                surface, 
                (255, 255, 255, 100), 
                self._hscroll_thumb.inflate(-4, -4), 
                border_radius=4
            )
        
        # Draw corner between scroll bars if both are visible
        if self._vscroll_visible and self._hscroll_visible:
            corner_rect = pygame.Rect(
                self.width - self._scrollbar_size,
                self.height - self._scrollbar_size,
                self._scrollbar_size,
                self._scrollbar_size
            )
            pygame.draw.rect(surface, (220, 220, 220), corner_rect)
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the panel content"""
        # Draw shadow if enabled
        if self.styles['shadow'] and self.styles['background_color']:
            shadow_surface = pygame.Surface(
                (self.width, self.height), 
                pygame.SRCALPHA
            )
            shadow_color = self.styles['shadow_color']
            if isinstance(shadow_color, tuple) and len(shadow_color) == 3:
                shadow_color = (*shadow_color, 100)  # Add alpha if not present
            
            shadow_offset = self.styles['shadow_offset']
            shadow_rect = pygame.Rect(
                shadow_offset[0], 
                shadow_offset[1], 
                self.width, 
                self.height
            )
            
            pygame.draw.rect(
                shadow_surface, 
                shadow_color, 
                shadow_rect,
                border_radius=self.styles['border_radius']
            )
            
            surface.blit(shadow_surface, (0, 0))
        
        # Draw the panel background
        bg_rect = pygame.Rect(0, 0, self.width, self.height)
        bg_color = self.styles['background_color']
        border_color = self.styles['border_color']
        border_width = self.styles['border_width']
        border_radius = self.styles['border_radius']
        
        if bg_color:
            if border_radius > 0:
                pygame.draw.rect(
                    surface, 
                    bg_color, 
                    bg_rect, 
                    border_radius=border_radius
                )
                
                if border_width > 0 and border_color:
                    pygame.draw.rect(
                        surface, 
                        border_color, 
                        bg_rect, 
                        border_width, 
                        border_radius=border_radius
                    )
            else:
                pygame.draw.rect(surface, bg_color, bg_rect)
                
                if border_width > 0 and border_color:
                    pygame.draw.rect(
                        surface, 
                        border_color, 
                        bg_rect, 
                        border_width
                    )
        
        # Draw scroll bars if needed
        self._render_scroll_bars(surface)
    
    def render(self, surface: pygame.Surface):
        """Render the panel and its children"""
        if not self.visible:
            return
        
        # Save the current clip rect
        old_clip = surface.get_clip()
        
        # Set the panel's clip rect
        panel_rect = pygame.Rect(
            self.get_absolute_position()[0],
            self.get_absolute_position()[1],
            self.width,
            self.height
        )
        
        if self.styles['clip_children']:
            surface.set_clip(panel_rect)
        
        # Render the panel background and borders
        self._render_content(surface, *self.get_absolute_position())
        
        # Set up the content surface for children
        content_abs_x, content_abs_y = self.get_absolute_position()
        
        # Apply padding
        padding_top, padding_right, padding_bottom, padding_left = self.styles['padding']
        content_abs_x += padding_left - self.styles['scroll_x']
        content_abs_y += padding_top - self.styles['scroll_y']
        
        # Save the current state
        old_surface = surface
        
        try:
            # Create a temporary surface for the content
            temp_surface = pygame.Surface(
                (self._content_rect.width, self._content_rect.height), 
                pygame.SRCALPHA
            )
            
            # Render children to the temporary surface
            for child in sorted(self.children, key=lambda c: c.z_index):
                # Only render visible children that intersect with the visible area
                if child.visible:
                    child_rect = child.get_absolute_rect()
                    visible_rect = pygame.Rect(
                        -content_abs_x,
                        -content_abs_y,
                        self.width,
                        self.height
                    )
                    
                    if child_rect.colliderect(visible_rect):
                        child.render(temp_surface)
            
            # Blit the content surface to the main surface
            surface.blit(
                temp_surface, 
                (content_abs_x, content_abs_y),
                area=pygame.Rect(
                    max(0, -content_abs_x + panel_rect.x),
                    max(0, -content_abs_y + panel_rect.y),
                    min(self._content_rect.width, panel_rect.width - padding_left - padding_right),
                    min(self._content_rect.height, panel_rect.height - padding_top - padding_bottom)
                )
            )
            
        finally:
            # Restore the original surface and clip rect
            surface = old_surface
            surface.set_clip(old_clip)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        if not self.visible or not self.enabled:
            return False
        
        # Check if the event is within the panel's bounds
        mouse_pos = pygame.mouse.get_pos()
        in_bounds = self.point_in_component(mouse_pos)
        
        # Handle scroll wheel events
        if in_bounds and event.type == pygame.MOUSEWHEEL:
            if self.styles['scrollable']:
                # Scroll vertically by default, horizontally if shift is held
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.scroll_by(-event.y * 20, 0)
                else:
                    self.scroll_by(0, -event.y * 20)
                return True
        
        # Handle scroll bar dragging
        if self._scrollbar_pressed and event.type == pygame.MOUSEMOTION:
            if self._vscroll_visible and self._scrollbar_drag_start is not None:
                # Calculate new scroll position based on mouse movement
                dy = mouse_pos[1] - self._scrollbar_drag_start[1]
                scroll_range = self._content_height - self.height + (self._scrollbar_size if self._hscroll_visible else 0)
                thumb_range = self.height - self._vscroll_thumb.height - (self._scrollbar_size if self._hscroll_visible else 0)
                
                if thumb_range > 0:
                    scroll_y = int((dy / thumb_range) * scroll_range)
                    self.scroll_to(y=scroll_y)
                
                return True
            
            elif self._hscroll_visible and self._scrollbar_drag_start is not None:
                # Calculate new scroll position based on mouse movement
                dx = mouse_pos[0] - self._scrollbar_drag_start[0]
                scroll_range = self._content_width - self.width + (self._scrollbar_size if self._vscroll_visible else 0)
                thumb_range = self.width - self._hscroll_thumb.width - (self._scrollbar_size if self._vscroll_visible else 0)
                
                if thumb_range > 0:
                    scroll_x = int((dx / thumb_range) * scroll_range)
                    self.scroll_to(x=scroll_x)
                
                return True
        
        # Handle scroll bar clicks
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._vscroll_visible and self._vscroll_thumb.collidepoint(
                mouse_pos[0] - self.get_absolute_position()[0],
                mouse_pos[1] - self.get_absolute_position()[1]
            ):
                self._scrollbar_pressed = True
                self._scrollbar_drag_start = mouse_pos
                return True
            
            elif self._hscroll_visible and self._hscroll_thumb.collidepoint(
                mouse_pos[0] - self.get_absolute_position()[0],
                mouse_pos[1] - self.get_absolute_position()[1]
            ):
                self._scrollbar_pressed = True
                self._scrollbar_drag_start = mouse_pos
                return True
            
            # Click on track to page up/down
            elif self._vscroll_visible and (
                mouse_pos[0] > self.get_absolute_position()[0] + self.width - self._scrollbar_size
            ):
                if mouse_pos[1] < self._vscroll_thumb.y + self.get_absolute_position()[1]:
                    # Page up
                    self.scroll_by(0, -self.height)
                else:
                    # Page down
                    self.scroll_by(0, self.height)
                return True
            
            elif self._hscroll_visible and (
                mouse_pos[1] > self.get_absolute_position()[1] + self.height - self._scrollbar_size
            ):
                if mouse_pos[0] < self._hscroll_thumb.x + self.get_absolute_position()[0]:
                    # Page left
                    self.scroll_by(-self.width, 0)
                else:
                    # Page right
                    self.scroll_by(self.width, 0)
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._scrollbar_pressed:
                self._scrollbar_pressed = False
                self._scrollbar_drag_start = None
                return True
        
        # Update scroll bar hover state
        if event.type == pygame.MOUSEMOTION:
            if self._vscroll_visible and self._vscroll_thumb.collidepoint(
                mouse_pos[0] - self.get_absolute_position()[0],
                mouse_pos[1] - self.get_absolute_position()[1]
            ) or (self._hscroll_visible and self._hscroll_thumb.collidepoint(
                mouse_pos[0] - self.get_absolute_position()[0],
                mouse_pos[1] - self.get_absolute_position()[1]
            )):
                if not self._scrollbar_hovered:
                    self._scrollbar_hovered = True
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                if self._scrollbar_hovered:
                    self._scrollbar_hovered = False
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        # Let children handle the event
        if in_bounds:
            # Adjust mouse position for scrolling and padding
            rel_x = mouse_pos[0] - self.get_absolute_position()[0] - self.styles['padding'][3] + self.styles['scroll_x']
            rel_y = mouse_pos[1] - self.get_absolute_position()[1] - self.styles['padding'][0] + self.styles['scroll_y']
            
            # Create a new event with adjusted coordinates
            if hasattr(event, 'pos'):
                new_event = pygame.event.Event(
                    event.type,
                    {
                        **event.__dict__,
                        'pos': (rel_x, rel_y),
                        'rel': (event.rel if hasattr(event, 'rel') else (0, 0))
                    }
                )
            else:
                new_event = event
            
            # Let children handle the event (in reverse order for proper z-index)
            for child in reversed(self.children):
                if child.visible and child.enabled and child.handle_event(new_event):
                    return True
        
        return False
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        needs_scroll_update = any(
            k in styles for k in 
            ['scrollable', 'scroll_x', 'scroll_y', 'clip_children']
        )
        
        super().set_style(**styles)
        
        if needs_scroll_update:
            self._update_scroll_bars()
    
    def set_size(self, width: int, height: int):
        """Set the size of the panel"""
        if width != self.width or height != self.height:
            super().set_size(width, height)
            self._update_scroll_bars()
            
            # Update content surface size
            content_width = width - (self._scrollbar_size if self._vscroll_visible else 0)
            content_height = height - (self._scrollbar_size if self._hscroll_visible else 0)
            
            if (content_width > 0 and content_height > 0 and 
                (self._content_surface.get_width() != content_width or 
                 self._content_surface.get_height() != content_height)):
                self._content_surface = pygame.Surface((content_width, content_height), pygame.SRCALPHA)
                self._content_rect.size = (content_width, content_height)
    
    def add_child(self, child: 'UIComponent'):
        """Add a child component"""
        super().add_child(child)
        
        # Update content size if the child is outside the current bounds
        if self.styles['scrollable']:
            child_rect = child.get_absolute_rect()
            content_right = child_rect.right - self.get_absolute_position()[0] - self.styles['padding'][3]
            content_bottom = child_rect.bottom - self.get_absolute_position()[1] - self.styles['padding'][0]
            
            new_width = max(self._content_width, content_right + self.styles['padding'][1])
            new_height = max(self._content_height, content_bottom + self.styles['padding'][2])
            
            if new_width != self._content_width or new_height != self._content_height:
                self.set_content_size(new_width, new_height)
    
    def remove_child(self, child: 'UIComponent') -> bool:
        """Remove a child component"""
        if super().remove_child(child):
            # Update content size if needed
            if self.styles['scrollable'] and self.children:
                max_right = max(
                    c.get_absolute_rect().right - self.get_absolute_position()[0] - self.styles['padding'][3]
                    for c in self.children
                )
                max_bottom = max(
                    c.get_absolute_rect().bottom - self.get_absolute_position()[1] - self.styles['padding'][0]
                    for c in self.children
                )
                
                new_width = max(0, max_right + self.styles['padding'][1])
                new_height = max(0, max_bottom + self.styles['padding'][2])
                
                if new_width != self._content_width or new_height != self._content_height:
                    self.set_content_size(new_width, new_height)
            
            return True
        
        return False
