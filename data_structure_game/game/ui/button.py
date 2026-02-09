import pygame
from typing import Optional, Callable, Tuple, Any, Dict
from .component import UIComponent, UIEventType, UIEvent

class Button(UIComponent):
    """A clickable button component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str = "", parent: Optional[UIComponent] = None):
        super().__init__(x, y, width, height, parent)
        
        self.text = text
        self._font = pygame.font.SysFont('Arial', 16)
        self._text_surface: Optional[pygame.Surface] = None
        self._text_rect: Optional[pygame.Rect] = None
        
        # Default styles
        self.styles.update({
            'background_color': (200, 200, 200),
            'hover_background_color': (180, 180, 180),
            'pressed_background_color': (160, 160, 160),
            'disabled_background_color': (230, 230, 230),
            'text_color': (0, 0, 0),
            'disabled_text_color': (150, 150, 150),
            'border_radius': 5,
            'border_width': 2,
            'border_color': (100, 100, 100),
            'font_size': 16,
            'font_name': 'Arial',
            'padding': (8, 12, 8, 12)  # top, right, bottom, left
        })
        
        # State
        self._pressed = False
        self._hovered = False
        self._needs_redraw = True
        
        # Generate text surface
        self._update_text_surface()
    
    def _update_text_surface(self):
        """Update the text surface and its rectangle"""
        if not self.text:
            self._text_surface = None
            self._text_rect = None
            return
            
        font = pygame.font.SysFont(
            self.styles['font_name'], 
            self.styles['font_size']
        )
        
        text_color = self.styles['disabled_text_color'] if not self.enabled else self.styles['text_color']
        self._text_surface = font.render(self.text, True, text_color)
        self._text_rect = self._text_surface.get_rect()
        
        # Center the text
        padding_top, padding_right, padding_bottom, padding_left = self.styles['padding']
        content_width = self.width - padding_left - padding_right
        content_height = self.height - padding_top - padding_bottom
        
        self._text_rect.center = (
            padding_left + content_width // 2,
            padding_top + content_height // 2
        )
    
    def set_text(self, text: str):
        """Set the button text"""
        if self.text != text:
            self.text = text
            self._update_text_surface()
    
    def set_font(self, font_name: str, font_size: int):
        """Set the button font"""
        if (self.styles['font_name'] != font_name or 
            self.styles['font_size'] != font_size):
            self.styles['font_name'] = font_name
            self.styles['font_size'] = font_size
            self._update_text_surface()
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the button content"""
        # Draw the button background
        bg_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        border_radius = self.styles['border_radius']
        
        # Determine the background color based on state
        if not self.enabled:
            bg_color = self.styles['disabled_background_color']
        elif self._pressed:
            bg_color = self.styles['pressed_background_color']
        elif self._hovered:
            bg_color = self.styles['hover_background_color']
        else:
            bg_color = self.styles['background_color']
        
        # Draw the background
        if border_radius > 0:
            pygame.draw.rect(surface, bg_color, bg_rect, 
                           border_radius=border_radius)
            
            # Draw border if needed
            if self.styles['border_width'] > 0:
                pygame.draw.rect(
                    surface, 
                    self.styles['border_color'], 
                    bg_rect, 
                    self.styles['border_width'],
                    border_radius=border_radius
                )
        else:
            pygame.draw.rect(surface, bg_color, bg_rect)
            
            # Draw border if needed
            if self.styles['border_width'] > 0:
                pygame.draw.rect(
                    surface, 
                    self.styles['border_color'], 
                    bg_rect, 
                    self.styles['border_width']
                )
        
        # Draw the text if it exists
        if self._text_surface and self._text_rect:
            surface.blit(
                self._text_surface,
                (abs_x + self._text_rect.x, abs_y + self._text_rect.y)
            )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        if not self.visible or not self.enabled:
            return False
        
        # Let the parent handle the event first
        if super().handle_event(event):
            return True
        
        # Handle mouse events
        if event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            was_hovered = self._hovered
            self._hovered = self.point_in_component(mouse_pos)
            
            if self._hovered != was_hovered:
                self._needs_redraw = True
                
                # Dispatch hover events
                if self._hovered:
                    self.dispatch_event(UIEvent(UIEventType.HOVER, self))
                else:
                    self.dispatch_event(UIEvent(UIEventType.HOVER, self, {'exited': True}))
            
            return self._hovered
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self._hovered:  # Left mouse button
                self._pressed = True
                self._needs_redraw = True
                self.dispatch_event(UIEvent(UIEventType.PRESS, self))
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self._pressed:  # Left mouse button
                self._pressed = False
                self._needs_redraw = True
                
                # Only trigger click if the mouse is still over the button
                if self._hovered:
                    self.dispatch_event(UIEvent(UIEventType.CLICK, self))
                
                self.dispatch_event(UIEvent(UIEventType.RELEASE, self))
                return True
        
        return False
    
    def on_hover(self, event: UIEvent):
        """Called when the mouse enters or exits the button"""
        if not hasattr(event, 'exited') or not event.exited:
            pygame.mouse.set_cursor(*pygame.cursors.tri_left)
        else:
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
    
    def on_press(self, event: UIEvent):
        """Called when the button is pressed"""
        pass
    
    def on_click(self, event: UIEvent):
        """Called when the button is clicked"""
        pass
    
    def on_release(self, event: UIEvent):
        """Called when the button is released"""
        pass
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        needs_text_update = any(
            k in styles for k in ['font_name', 'font_size', 'text_color', 'padding']
        )
        
        super().set_style(**styles)
        
        if needs_text_update:
            self._update_text_surface()
    
    def set_enabled(self, enabled: bool):
        """Enable or disable the button"""
        if self.enabled != enabled:
            self.enabled = enabled
            self._update_text_surface()
    
    def is_pressed(self) -> bool:
        """Check if the button is currently pressed"""
        return self._pressed
    
    def is_hovered(self) -> bool:
        """Check if the mouse is hovering over the button"""
        return self._hovered
