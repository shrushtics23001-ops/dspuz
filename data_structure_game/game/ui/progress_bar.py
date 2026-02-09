import pygame
from typing import Tuple, Optional, Dict, Any
from .component import UIComponent, UIEventType

class ProgressBar(UIComponent):
    """A progress bar component for displaying progress"""
    
    def __init__(self, x: int, y: int, width: int, height: int = 20,
                 min_value: float = 0, max_value: float = 100, value: float = 0,
                 parent: Optional[UIComponent] = None):
        super().__init__(x, y, width, height, parent)
        
        # Progress values
        self.min_value = min_value
        self.max_value = max(max_value, min_value + 0.001)  # Avoid division by zero
        self._value = min(max(value, min_value), max_value)
        
        # Visual styles
        self.styles.update({
            'background_color': (230, 230, 230),
            'fill_color': (76, 175, 80),  # Green
            'border_color': (200, 200, 200),
            'border_width': 1,
            'border_radius': 4,
            'show_text': True,
            'text_color': (0, 0, 0),
            'text_shadow': True,
            'text_shadow_color': (255, 255, 255, 128),
            'text_shadow_offset': (1, 1),
            'font_size': 12,
            'font_name': 'Arial',
            'smooth': True,
            'smooth_speed': 0.1,
        })
        
        # Smooth animation
        self._display_value = float(self._value)
        self._target_value = float(self._value)
        self._needs_redraw = True
    
    @property
    def value(self) -> float:
        """Get the current progress value"""
        return self._value
    
    @value.setter
    def value(self, val: float):
        """Set the progress value and update the display"""
        new_value = max(self.min_value, min(val, self.max_value))
        if abs(new_value - self._value) > 0.0001:  # Avoid unnecessary updates
            self._value = new_value
            self._target_value = float(new_value)
            
            if not self.styles['smooth']:
                self._display_value = self._target_value
            
            self._needs_redraw = True
    
    @property
    def progress(self) -> float:
        """Get the progress as a value between 0 and 1"""
        if self.max_value == self.min_value:
            return 0.0
        return (self._value - self.min_value) / (self.max_value - self.min_value)
    
    @progress.setter
    def progress(self, val: float):
        """Set the progress as a value between 0 and 1"""
        self.value = self.min_value + val * (self.max_value - self.min_value)
    
    def set_range(self, min_val: float, max_val: float):
        """Set the minimum and maximum values"""
        if min_val > max_val:
            min_val, max_val = max_val, min_val
            
        if abs(min_val - self.min_value) > 0.0001 or abs(max_val - self.max_value) > 0.0001:
            self.min_value = min_val
            self.max_value = max(max_val, min_val + 0.001)
            self._value = max(min(self._value, self.max_value), self.min_value)
            self._target_value = float(self._value)
            
            if not self.styles['smooth']:
                self._display_value = self._target_value
            
            self._needs_redraw = True
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the progress bar"""
        # Draw the background
        bg_rect = pygame.Rect(0, 0, self.width, self.height)
        border_radius = self.styles['border_radius']
        
        # Draw the background with rounded corners
        pygame.draw.rect(
            surface, 
            self.styles['background_color'], 
            bg_rect, 
            border_radius=border_radius
        )
        
        # Draw the border
        if self.styles['border_width'] > 0:
            pygame.draw.rect(
                surface, 
                self.styles['border_color'], 
                bg_rect, 
                self.styles['border_width'], 
                border_radius=border_radius
            )
        
        # Calculate the fill width based on the current display value
        if self.styles['smooth'] and abs(self._display_value - self._target_value) > 0.1:
            # Smoothly animate towards the target value
            self._display_value += (self._target_value - self._display_value) * self.styles['smooth_speed']
            self._needs_redraw = True
        else:
            self._display_value = self._target_value
        
        # Calculate the fill progress (0.0 to 1.0)
        if self.max_value > self.min_value:
            progress = (self._display_value - self.min_value) / (self.max_value - self.min_value)
        else:
            progress = 0.0
            
        fill_width = max(0, min(int(self.width * progress), self.width))
        
        # Draw the fill
        if fill_width > 0:
            # Create a surface for the fill with the same size as the progress bar
            fill_surface = pygame.Surface((fill_width, self.height), pygame.SRCALPHA)
            
            # Draw the fill with rounded corners on the left side if needed
            if progress >= 1.0 and border_radius > 0:
                # Full fill with rounded corners
                pygame.draw.rect(
                    fill_surface,
                    self.styles['fill_color'],
                    fill_surface.get_rect(),
                    border_radius=border_radius
                )
            else:
                # Partial fill with square corners or full fill with square corners
                fill_rect = pygame.Rect(0, 0, fill_width, self.height)
                
                # Only round the left corners if we're not at the very start
                if progress > 0 and border_radius > 0:
                    # Create a surface for the rounded corners
                    corner_size = min(border_radius * 2, fill_width, self.height)
                    corner_surface = pygame.Surface((corner_size, corner_size), pygame.SRCALPHA)
                    
                    # Draw the left side with rounded corners
                    pygame.draw.rect(
                        corner_surface,
                        self.styles['fill_color'],
                        corner_surface.get_rect(),
                        border_radius=border_radius
                    )
                    
                    # Blit the left rounded corners
                    fill_surface.blit(
                        corner_surface,
                        (0, 0),
                        area=pygame.Rect(0, 0, min(corner_size, fill_width), corner_size)
                    )
                    
                    # Draw the middle part
                    if fill_width > corner_size:
                        pygame.draw.rect(
                            fill_surface,
                            self.styles['fill_color'],
                            pygame.Rect(
                                corner_size // 2,
                                0,
                                fill_width - corner_size // 2,
                                self.height
                            )
                        )
                    
                    # Draw the bottom left corner if needed
                    if self.height > corner_size:
                        fill_surface.blit(
                            corner_surface,
                            (0, self.height - corner_size),
                            area=pygame.Rect(0, corner_size, min(corner_size, fill_width), corner_size)
                        )
                else:
                    # No rounded corners needed
                    pygame.draw.rect(fill_surface, self.styles['fill_color'], fill_rect)
            
            # Blit the fill surface onto the main surface
            surface.blit(fill_surface, (0, 0))
        
        # Draw the text if enabled
        if self.styles['show_text']:
            self._draw_progress_text(surface, progress)
    
    def _draw_progress_text(self, surface: pygame.Surface, progress: float):
        """Draw the progress text"""
        # Format the text
        if hasattr(self, 'text_format') and callable(self.text_format):
            text = self.text_format(self._value, self.min_value, self.max_value, progress)
        else:
            # Default format: "X%"
            percentage = int(progress * 100 + 0.5)  # Round to nearest integer
            text = f"{percentage}%"
        
        # Create a font
        font = pygame.font.SysFont(
            self.styles['font_name'],
            min(self.styles['font_size'], self.height - 4)
        )
        
        # Render the text
        text_surface = font.render(text, True, self.styles['text_color'])
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        
        # Draw text shadow if enabled
        if self.styles['text_shadow']:
            shadow_surface = font.render(text, True, self.styles['text_shadow_color'])
            shadow_rect = text_rect.move(
                self.styles['text_shadow_offset'][0],
                self.styles['text_shadow_offset'][1]
            )
            surface.blit(shadow_surface, shadow_rect)
        
        # Draw the text
        surface.blit(text_surface, text_rect)
    
    def set_text_formatter(self, formatter):
        """Set a custom text formatter function
        
        The formatter should be a callable with the signature:
        formatter(value: float, min_value: float, max_value: float, progress: float) -> str
        """
        self.text_format = formatter
        self._needs_redraw = True
    
    def update(self, dt: float):
        """Update the progress bar animation"""
        if self.styles['smooth'] and abs(self._display_value - self._target_value) > 0.1:
            self._needs_redraw = True
            
            # Apply easing for smoother animation
            self._display_value += (self._target_value - self._display_value) * self.styles['smooth_speed']
            
            # Snap to target when close enough
            if abs(self._display_value - self._target_value) < 0.1:
                self._display_value = self._target_value
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        needs_redraw = any(
            k in styles for k in 
            ['background_color', 'fill_color', 'border_color', 'border_width', 
             'border_radius', 'show_text', 'text_color', 'font_size', 'font_name',
             'text_shadow', 'text_shadow_color', 'text_shadow_offset']
        )
        
        super().set_style(**styles)
        
        if needs_redraw:
            self._needs_redraw = True
    
    def is_animating(self) -> bool:
        """Check if the progress bar is currently animating"""
        return self.styles['smooth'] and abs(self._display_value - self._target_value) > 0.1
