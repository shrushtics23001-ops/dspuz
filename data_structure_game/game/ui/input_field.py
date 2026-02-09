import pygame
from typing import Optional, Callable, List, Tuple, Dict, Any
import string
from .component import UIComponent, UIEvent, UIEventType
from .text import Text

class InputField(UIComponent):
    """A text input field component"""
    
    def __init__(self, x: int, y: int, width: int, height: int = 30,
                 text: str = "", placeholder: str = "", parent: Optional[UIComponent] = None):
        super().__init__(x, y, width, height, parent)
        
        # Text properties
        self._text = text
        self.placeholder = placeholder
        self.font_size = 16
        self.font_name = 'Arial'
        self.text_color = (0, 0, 0)
        self.placeholder_color = (150, 150, 150)
        self.cursor_color = (0, 0, 0)
        self.selection_color = (200, 220, 255)
        
        # Cursor and selection
        self.cursor_pos = len(text)
        self.selection_start = None
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_blink_interval = 500  # ms
        
        # Text metrics
        self._text_surface = None
        self._text_rect = None
        self._text_offset = 0
        self._text_width = 0
        self._text_height = 0
        
        # Input constraints
        self.max_length = 0  # 0 means no limit
        self.allowed_chars = None  # None means all characters are allowed
        self.numeric_only = False
        self.multiline = False
        self.readonly = False
        
        # Visual styles
        self.styles.update({
            'background_color': (255, 255, 255),
            'border_color': (150, 150, 150),
            'border_width': 1,
            'border_radius': 4,
            'padding': (6, 8, 6, 8),  # top, right, bottom, left
            'focused_border_color': (66, 135, 245),
            'focused_border_width': 2,
            'hover_background_color': (250, 250, 250),
            'active_background_color': (255, 255, 255),
        })
        
        # State
        self._hovered = False
        self._pressed = False
        self._focused = False
        
        # Update text rendering
        self._update_text_surface()
    
    @property
    def text(self) -> str:
        """Get the current text"""
        return self._text
    
    @text.setter
    def text(self, value: str):
        """Set the text and update the display"""
        if self._text != value:
            self._text = value
            self.cursor_pos = min(self.cursor_pos, len(self._text))
            self.selection_start = None
            self._update_text_surface()
    
    def get_selected_text(self) -> str:
        """Get the currently selected text"""
        if self.selection_start is None:
            return ""
        
        start = min(self.selection_start, self.cursor_pos)
        end = max(self.selection_start, self.cursor_pos)
        return self._text[start:end]
    
    def delete_selection(self):
        """Delete the currently selected text"""
        if self.selection_start is None:
            return
        
        start = min(self.selection_start, self.cursor_pos)
        end = max(self.selection_start, self.cursor_pos)
        
        self._text = self._text[:start] + self._text[end:]
        self.cursor_pos = start
        self.selection_start = None
        self._update_text_surface()
    
    def insert_text(self, text: str):
        """Insert text at the current cursor position"""
        if self.readonly:
            return
        
        # Delete any selected text first
        if self.selection_start is not None:
            self.delete_selection()
        
        # Check length limit
        if self.max_length > 0 and len(self._text) + len(text) > self.max_length:
            return
        
        # Filter characters if needed
        if self.allowed_chars is not None:
            text = ''.join(c for c in text if c in self.allowed_chars)
        
        if self.numeric_only:
            # Only allow digits, decimal point, and minus sign
            allowed = set(string.digits + '.-')
            text = ''.join(c for c in text if c in allowed)
        
        # Insert the text
        self._text = self._text[:self.cursor_pos] + text + self._text[self.cursor_pos:]
        self.cursor_pos += len(text)
        self._update_text_surface()
    
    def _update_text_surface(self):
        """Update the rendered text surface"""
        if not hasattr(self, 'font_name') or not hasattr(self, 'font_size'):
            return
        
        # Get the font
        font = pygame.font.SysFont(self.font_name, self.font_size)
        
        # Determine what text to display
        display_text = self._text
        if not display_text and not self._focused and self.placeholder:
            display_text = self.placeholder
        
        # Render the text
        if display_text:
            self._text_surface = font.render(display_text, True, 
                                           self.placeholder_color if not self._text and not self._focused and self.placeholder 
                                           else self.text_color)
            self._text_rect = self._text_surface.get_rect()
            self._text_width, self._text_height = self._text_surface.get_size()
        else:
            # Create an empty surface with the correct height
            self._text_surface = None
            self._text_rect = pygame.Rect(0, 0, 0, font.get_height())
            self._text_width = 0
            self._text_height = font.get_height()
        
        # Update cursor and text position
        self._update_cursor_position()
    
    def _update_cursor_position(self):
        """Update the cursor position and text offset"""
        if not hasattr(self, 'font_name') or not hasattr(self, 'font_size'):
            return
        
        font = pygame.font.SysFont(self.font_name, self.font_size)
        
        # Calculate the width of the text before the cursor
        text_before_cursor = self._text[:self.cursor_pos]
        if text_before_cursor:
            text_width = font.size(text_before_cursor)[0]
        else:
            text_width = 0
        
        # Get the available width for the text
        padding_left = self.styles['padding'][3]
        padding_right = self.styles['padding'][1]
        available_width = self.width - padding_left - padding_right - 2  # Account for cursor
        
        # Adjust the text offset to keep the cursor visible
        cursor_screen_x = padding_left + text_width - self._text_offset
        
        if cursor_screen_x < padding_left:
            # Cursor is scrolled off to the left
            self._text_offset = max(0, text_width + padding_left - available_width // 3)
        elif cursor_screen_x > available_width:
            # Cursor is scrolled off to the right
            self._text_offset = text_width - available_width + padding_left + available_width // 3
        
        # Make sure the text doesn't scroll too far to the left
        if self._text_width < available_width:
            self._text_offset = 0
        else:
            max_offset = max(0, self._text_width - available_width + padding_left * 2)
            self._text_offset = min(self._text_offset, max_offset)
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the input field content"""
        # Draw the background
        bg_color = self.styles['background_color']
        border_color = self.styles['border_color']
        border_width = self.styles['border_width']
        
        # Adjust colors based on state
        if not self.enabled:
            bg_color = (240, 240, 240)
            border_color = (200, 200, 200)
        elif self._pressed:
            bg_color = self.styles.get('active_background_color', bg_color)
        elif self._hovered:
            bg_color = self.styles.get('hover_background_color', bg_color)
        
        if self._focused:
            border_color = self.styles.get('focused_border_color', border_color)
            border_width = self.styles.get('focused_border_width', border_width)
        
        # Draw the background
        bg_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
        border_radius = self.styles.get('border_radius', 0)
        
        if border_radius > 0:
            # Draw the background with rounded corners
            pygame.draw.rect(surface, bg_color, bg_rect, border_radius=border_radius)
            
            # Draw the border
            if border_width > 0 and border_color:
                pygame.draw.rect(
                    surface, 
                    border_color, 
                    bg_rect, 
                    border_width, 
                    border_radius=border_radius
                )
        else:
            # Draw the background with square corners
            pygame.draw.rect(surface, bg_color, bg_rect)
            
            # Draw the border
            if border_width > 0 and border_color:
                pygame.draw.rect(surface, border_color, bg_rect, border_width)
        
        # Set up the clipping area for the text
        clip_rect = pygame.Rect(
            abs_x + border_width,
            abs_y + border_width,
            self.width - border_width * 2,
            self.height - border_width * 2
        )
        
        old_clip = surface.get_clip()
        surface.set_clip(clip_rect)
        
        # Draw the text
        if self._text_surface:
            # Calculate text position with padding
            padding_top = self.styles['padding'][0]
            padding_left = self.styles['padding'][3]
            
            text_y = abs_y + (self.height - self._text_height) // 2
            text_x = abs_x + padding_left - self._text_offset
            
            # Draw any text selection
            if self._focused and self.selection_start is not None and self.selection_start != self.cursor_pos:
                self._draw_selection(surface, abs_x, text_y, padding_left)
            
            # Draw the text
            surface.blit(self._text_surface, (text_x, text_y))
            
            # Draw the cursor
            if self._focused and self.cursor_visible and not self.readonly:
                self._draw_cursor(surface, abs_x, text_y, padding_left)
        
        # Restore the clipping area
        surface.set_clip(old_clip)
    
    def _draw_selection(self, surface: pygame.Surface, abs_x: int, text_y: int, padding_left: int):
        """Draw the text selection highlight"""
        if not self._text:
            return
        
        font = pygame.font.SysFont(self.font_name, self.font_size)
        text_before_selection = self._text[:min(self.cursor_pos, self.selection_start)]
        selected_text = self.get_selected_text()
        
        # Calculate the position and size of the selection
        x = abs_x + padding_left + font.size(text_before_selection)[0] - self._text_offset
        width = font.size(selected_text)[0]
        
        # Draw the selection rectangle
        selection_rect = pygame.Rect(
            x,
            text_y,
            width,
            self._text_height
        )
        
        pygame.draw.rect(surface, self.selection_color, selection_rect)
        
        # Re-render the selected text with the appropriate colors
        if selected_text:
            selected_surface = font.render(selected_text, True, (0, 0, 0))
            surface.blit(selected_surface, (x, text_y))
    
    def _draw_cursor(self, surface: pygame.Surface, abs_x: int, text_y: int, padding_left: int):
        """Draw the text cursor"""
        if not hasattr(self, 'font_name') or not hasattr(self, 'font_size'):
            return
        
        font = pygame.font.SysFont(self.font_name, self.font_size)
        text_before_cursor = self._text[:self.cursor_pos]
        
        # Calculate the cursor position
        if text_before_cursor:
            cursor_x = abs_x + padding_left + font.size(text_before_cursor)[0] - self._text_offset
        else:
            cursor_x = abs_x + padding_left - self._text_offset
        
        # Draw the cursor
        cursor_rect = pygame.Rect(
            cursor_x,
            text_y,
            1,
            self._text_height
        )
        
        pygame.draw.rect(surface, self.cursor_color, cursor_rect)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle pygame events"""
        if not self.visible or not self.enabled:
            return False
        
        # Check if the mouse is over the input field
        mouse_pos = pygame.mouse.get_pos()
        mouse_over = self.point_in_component(mouse_pos)
        
        # Handle mouse events
        if event.type == pygame.MOUSEMOTION:
            # Update hover state
            was_hovered = self._hovered
            self._hovered = mouse_over
            
            # Change cursor to I-beam when over the input field
            if self._hovered and not was_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_IBEAM)
            elif not self._hovered and was_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
            # Handle text selection with mouse drag
            if self._pressed and self._focused:
                # Calculate the cursor position based on the mouse position
                self._update_cursor_from_mouse(mouse_pos[0])
                
                # If there's no selection yet, start one
                if self.selection_start is None and self.cursor_pos != self._last_click_pos:
                    self.selection_start = self._last_click_pos
                
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                self._pressed = True
                
                # Set focus to this input field
                if not self._focused:
                    self._focused = True
                    self.cursor_visible = True
                    self.cursor_timer = pygame.time.get_ticks()
                    self.dispatch_event(UIEvent(UIEventType.FOCUS, self))
                
                # Update cursor position
                self._update_cursor_from_mouse(mouse_pos[0])
                
                # Reset selection
                self.selection_start = None
                self._last_click_pos = self.cursor_pos
                self._last_click_time = pygame.time.get_ticks()
                
                # Handle double-click to select word
                current_time = pygame.time.get_ticks()
                if hasattr(self, '_last_click_time') and current_time - self._last_click_time < 300:  # 300ms double-click threshold
                    # Select the word under the cursor
                    if self._text:
                        # Find word boundaries
                        start = self.cursor_pos
                        while start > 0 and self._text[start-1] not in (' ', '\t', '\n'):
                            start -= 1
                        
                        end = self.cursor_pos
                        while end < len(self._text) and self._text[end] not in (' ', '\t', '\n'):
                            end += 1
                        
                        self.cursor_pos = end
                        self.selection_start = start
                        self._update_text_surface()
                
                return True
        
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                self._pressed = False
                return True
        
        # Handle keyboard events when focused
        if self._focused and not self.readonly:
            if event.type == pygame.KEYDOWN:
                # Reset cursor blink timer
                self.cursor_visible = True
                self.cursor_timer = pygame.time.get_ticks()
                
                # Handle special keys
                if event.key == pygame.K_BACKSPACE:
                    if self.selection_start is not None:
                        self.delete_selection()
                    elif self.cursor_pos > 0:
                        self._text = self._text[:self.cursor_pos-1] + self._text[self.cursor_pos:]
                        self.cursor_pos -= 1
                        self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_DELETE:
                    if self.selection_start is not None:
                        self.delete_selection()
                    elif self.cursor_pos < len(self._text):
                        self._text = self._text[:self.cursor_pos] + self._text[self.cursor_pos+1:]
                        self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_LEFT:
                    if event.mod & pygame.KMOD_CTRL:
                        # Move to previous word
                        while self.cursor_pos > 0 and self._text[self.cursor_pos-1] in (' ', '\t'):
                            self.cursor_pos -= 1
                        while self.cursor_pos > 0 and self._text[self.cursor_pos-1] not in (' ', '\t'):
                            self.cursor_pos -= 1
                    else:
                        # Move left one character
                        if self.cursor_pos > 0:
                            self.cursor_pos -= 1
                    
                    # Handle selection with shift
                    if not event.mod & pygame.KMOD_SHIFT:
                        self.selection_start = None
                    elif self.selection_start is None:
                        self.selection_start = self.cursor_pos + 1
                    
                    self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_RIGHT:
                    if event.mod & pygame.KMOD_CTRL:
                        # Move to next word
                        while self.cursor_pos < len(self._text) and self._text[self.cursor_pos] not in (' ', '\t'):
                            self.cursor_pos += 1
                        while self.cursor_pos < len(self._text) and self._text[self.cursor_pos] in (' ', '\t'):
                            self.cursor_pos += 1
                    else:
                        # Move right one character
                        if self.cursor_pos < len(self._text):
                            self.cursor_pos += 1
                    
                    # Handle selection with shift
                    if not event.mod & pygame.KMOD_SHIFT:
                        self.selection_start = None
                    elif self.selection_start is None:
                        self.selection_start = self.cursor_pos - 1
                    
                    self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_HOME:
                    # Move to start of line
                    self.cursor_pos = 0
                    
                    # Handle selection with shift
                    if not event.mod & pygame.KMOD_SHIFT:
                        self.selection_start = None
                    elif self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    
                    self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_END:
                    # Move to end of line
                    self.cursor_pos = len(self._text)
                    
                    # Handle selection with shift
                    if not event.mod & pygame.KMOD_SHIFT:
                        self.selection_start = None
                    elif self.selection_start is None:
                        self.selection_start = self.cursor_pos
                    
                    self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_RETURN and self.multiline:
                    # Insert newline in multiline mode
                    self.insert_text('\n')
                    return True
                
                elif event.key == pygame.K_v and event.mod & pygame.KMOD_CTRL:
                    # Paste from clipboard
                    try:
                        clipboard_text = pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8')
                        if clipboard_text:
                            self.insert_text(clipboard_text)
                    except:
                        pass
                    return True
                
                elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL and self.selection_start is not None:
                    # Copy selected text to clipboard
                    selected_text = self.get_selected_text()
                    if selected_text:
                        try:
                            pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode('utf-8'))
                        except:
                            pass
                    return True
                
                elif event.key == pygame.K_x and event.mod & pygame.KMOD_CTRL and self.selection_start is not None:
                    # Cut selected text to clipboard
                    selected_text = self.get_selected_text()
                    if selected_text:
                        try:
                            pygame.scrap.put(pygame.SCRAP_TEXT, selected_text.encode('utf-8'))
                            self.delete_selection()
                        except:
                            pass
                    return True
                
                elif event.key == pygame.K_a and event.mod & pygame.KMOD_CTRL:
                    # Select all text
                    if self._text:
                        self.selection_start = 0
                        self.cursor_pos = len(self._text)
                        self._update_text_surface()
                    return True
                
                elif event.key == pygame.K_ESCAPE:
                    # Deselect text
                    if self.selection_start is not None:
                        self.selection_start = None
                        self._update_text_surface()
                        return True
            
            elif event.type == pygame.TEXTINPUT:
                # Insert the typed character
                if not (event.text == '\r' and not self.multiline):  # Don't insert carriage return in single-line mode
                    self.insert_text(event.text)
                return True
        
        # Handle focus loss when clicking outside
        if event.type == pygame.MOUSEBUTTONDOWN and not mouse_over and self._focused:
            self._focused = False
            self.cursor_visible = False
            self.selection_start = None
            self.dispatch_event(UIEvent(UIEventType.BLUR, self))
            return False
        
        return False
    
    def _update_cursor_from_mouse(self, mouse_x: int):
        """Update the cursor position based on the mouse X coordinate"""
        if not hasattr(self, 'font_name') or not hasattr(self, 'font_size'):
            return
        
        font = pygame.font.SysFont(self.font_name, self.font_size)
        padding_left = self.styles['padding'][3]
        
        # Adjust mouse X to account for text offset and padding
        text_x = mouse_x - self.get_absolute_position()[0] - padding_left + self._text_offset
        
        # Find the cursor position that corresponds to this X coordinate
        if not self._text:
            self.cursor_pos = 0
        else:
            # Binary search to find the cursor position
            low = 0
            high = len(self._text)
            
            while low < high:
                mid = (low + high) // 2
                mid_text = self._text[:mid]
                mid_width = font.size(mid_text)[0]
                
                if mid_width < text_x:
                    low = mid + 1
                else:
                    high = mid
            
            # After the loop, low is the position where the cursor should be
            self.cursor_pos = low
            
            # If we're closer to the previous character, use that position
            if self.cursor_pos > 0:
                prev_text = self._text[:self.cursor_pos-1]
                prev_width = font.size(prev_text)[0]
                
                if abs(prev_width - text_x) < abs(font.size(self._text[:self.cursor_pos])[0] - text_x):
                    self.cursor_pos -= 1
        
        # Update the display
        self._update_text_surface()
    
    def update(self, dt: float):
        """Update the input field state"""
        if not self.visible:
            return
        
        # Update cursor blink
        if self._focused and not self.readonly:
            current_time = pygame.time.get_ticks()
            if current_time - self.cursor_timer > self.cursor_blink_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = current_time
    
    def set_focus(self, focused: bool):
        """Set the focus state of the input field"""
        if focused != self._focused:
            self._focused = focused
            self.cursor_visible = focused
            
            if focused:
                self.cursor_timer = pygame.time.get_ticks()
                self.dispatch_event(UIEvent(UIEventType.FOCUS, self))
                
                # If this component is getting focus, notify parent to manage focus
                if self.parent:
                    self.parent._child_got_focus(self)
            else:
                self.dispatch_event(UIEvent(UIEventType.BLUR, self))
    
    def set_text(self, text: str):
        """Set the text content"""
        if self._text != text:
            self._text = text
            self.cursor_pos = min(self.cursor_pos, len(self._text))
            self.selection_start = None
            self._update_text_surface()
    
    def clear(self):
        """Clear the input field"""
        self.set_text("")
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        needs_text_update = any(
            k in styles for k in 
            ['font_name', 'font_size', 'text_color', 'placeholder_color', 'padding']
        )
        
        super().set_style(**styles)
        
        if needs_text_update:
            self._update_text_surface()
    
    def set_readonly(self, readonly: bool):
        """Set whether the input field is read-only"""
        if self.readonly != readonly:
            self.readonly = readonly
            
            # Update cursor visibility
            if readonly:
                self.cursor_visible = False
            elif self._focused:
                self.cursor_visible = True
                self.cursor_timer = pygame.time.get_ticks()
