import pygame
from typing import Optional, Tuple, Dict, Any, List
from .component import UIComponent, UIEventType, UIEvent

class FontManager:
    """Manages font loading and caching"""
    _instance = None
    _fonts: Dict[Tuple[str, int, bool, bool], pygame.font.Font] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_font(cls, name: str, size: int, bold: bool = False, 
                italic: bool = False) -> pygame.font.Font:
        """Get a font with the specified properties"""
        key = (name, size, bold, italic)
        
        if key not in cls._fonts:
            try:
                font = pygame.font.SysFont(name, size, bold, italic)
                cls._fonts[key] = font
            except Exception as e:
                print(f"Error loading font {name}: {e}")
                # Fall back to default font
                font = pygame.font.SysFont(None, size, bold, italic)
                cls._fonts[key] = font
        
        return cls._fonts[key]

class Text(UIComponent):
    """A text display component"""
    
    def __init__(self, x: int, y: int, text: str = "", parent: Optional[UIComponent] = None):
        # Initialize with zero size, will be updated in _update_surface
        super().__init__(x, y, 0, 0, parent)
        
        self._text = text
        self._font_name = 'Arial'
        self._font_size = 16
        self._bold = False
        self._italic = False
        self._color = (0, 0, 0)  # Black by default
        self._antialias = True
        self._align = 'left'  # 'left', 'center', 'right'
        self._valign = 'top'  # 'top', 'middle', 'bottom'
        self._wrap = False
        self._max_width = 0  # 0 means no wrapping
        
        # Cached surfaces for rendering
        self._surface: Optional[pygame.Surface] = None
        self._rendered_rect: Optional[pygame.Rect] = None
        
        # Update the surface with the initial text
        self._update_surface()
    
    @property
    def text(self) -> str:
        """Get the current text"""
        return self._text
    
    @text.setter
    def text(self, value: str):
        """Set the text and update the surface"""
        if self._text != value:
            self._text = value
            self._update_surface()
    
    def set_font(self, name: str = None, size: int = None, 
                bold: bool = None, italic: bool = None):
        """Set font properties"""
        needs_update = False
        
        if name is not None and self._font_name != name:
            self._font_name = name
            needs_update = True
            
        if size is not None and self._font_size != size:
            self._font_size = size
            needs_update = True
            
        if bold is not None and self._bold != bold:
            self._bold = bold
            needs_update = True
            
        if italic is not None and self._italic != italic:
            self._italic = italic
            needs_update = True
            
        if needs_update:
            self._update_surface()
    
    def set_color(self, color: Tuple[int, int, int]):
        """Set the text color"""
        if self._color != color:
            self._color = color
            self._update_surface()
    
    def set_alignment(self, halign: str = None, valign: str = None):
        """Set text alignment"""
        needs_update = False
        
        if halign is not None and halign in ('left', 'center', 'right'):
            if self._align != halign:
                self._align = halign
                needs_update = True
                
        if valign is not None and valign in ('top', 'middle', 'bottom'):
            if self._valign != valign:
                self._valign = valign
                needs_update = True
                
        if needs_update:
            self._update_surface()
    
    def set_wrap(self, wrap: bool, max_width: int = 0):
        """Enable or disable text wrapping"""
        if wrap != self._wrap or (wrap and max_width > 0 and max_width != self._max_width):
            self._wrap = wrap
            self._max_width = max_width if wrap and max_width > 0 else 0
            self._update_surface()
    
    def _update_surface(self):
        """Update the rendered text surface"""
        if not self._text:
            self._surface = None
            self._rendered_rect = None
            self.set_size(0, 0)
            return
        
        font = FontManager.get_font(
            self._font_name, 
            self._font_size, 
            self._bold, 
            self._italic
        )
        
        if self._wrap and self._max_width > 0:
            # Handle text wrapping
            words = self._text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                # Test if adding this word would exceed the max width
                test_line = ' '.join(current_line + [word])
                test_width = font.size(test_line)[0]
                
                if test_width <= self._max_width:
                    current_line.append(word)
                else:
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Render each line
            line_surfaces = []
            total_height = 0
            max_width = 0
            
            for line in lines:
                if line:  # Only render non-empty lines
                    line_surface = font.render(line, self._antialias, self._color)
                else:
                    # For empty lines, use a small surface with just the height
                    line_surface = pygame.Surface((1, font.get_height()), pygame.SRCALPHA)
                
                line_surfaces.append(line_surface)
                max_width = max(max_width, line_surface.get_width())
                total_height += line_surface.get_height()
            
            # Create the final surface
            self._surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
            self._rendered_rect = self._surface.get_rect()
            
            # Blit each line
            y_offset = 0
            for line_surface in line_surfaces:
                x_offset = 0
                if self._align == 'center':
                    x_offset = (max_width - line_surface.get_width()) // 2
                elif self._align == 'right':
                    x_offset = max_width - line_surface.get_width()
                
                self._surface.blit(line_surface, (x_offset, y_offset))
                y_offset += line_surface.get_height()
            
            # Update component size
            self.set_size(max_width, total_height)
            
        else:
            # No wrapping, render as a single line
            self._surface = font.render(self._text, self._antialias, self._color)
            self._rendered_rect = self._surface.get_rect()
            
            # Update component size to match text
            self.set_size(
                self._rendered_rect.width,
                self._rendered_rect.height
            )
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the text"""
        if not self._surface or not self.visible:
            return
        
        # Calculate the position based on alignment
        x = abs_x
        y = abs_y
        
        if self._align == 'center':
            x += (self.width - self._surface.get_width()) // 2
        elif self._align == 'right':
            x += self.width - self._surface.get_width()
        
        if self._valign == 'middle':
            y += (self.height - self._surface.get_height()) // 2
        elif self._valign == 'bottom':
            y += self.height - self._surface.get_height()
        
        # Blit the text surface
        surface.blit(self._surface, (x, y))
    
    def get_text_size(self) -> Tuple[int, int]:
        """Get the size of the rendered text"""
        if self._surface:
            return self._surface.get_size()
        return (0, 0)
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        needs_update = False
        
        if 'color' in styles and styles['color'] != self._color:
            self._color = styles['color']
            needs_update = True
            
        if 'font_name' in styles and styles['font_name'] != self._font_name:
            self._font_name = styles['font_name']
            needs_update = True
            
        if 'font_size' in styles and styles['font_size'] != self._font_size:
            self._font_size = styles['font_size']
            needs_update = True
            
        if 'bold' in styles and styles['bold'] != self._bold:
            self._bold = styles['bold']
            needs_update = True
            
        if 'italic' in styles and styles['italic'] != self._italic:
            self._italic = styles['italic']
            needs_update = True
            
        if 'align' in styles and styles['align'] in ('left', 'center', 'right'):
            if self._align != styles['align']:
                self._align = styles['align']
                needs_update = True
                
        if 'valign' in styles and styles['valign'] in ('top', 'middle', 'bottom'):
            if self._valign != styles['valign']:
                self._valign = styles['valign']
                needs_update = True
        
        if needs_update:
            self._update_surface()
            
        super().set_style(**styles)
    
    def set_size(self, width: int, height: int):
        """Set the size of the text component"""
        # For text components, we usually want to maintain the size based on the text
        # But we'll allow manual resizing if needed
        super().set_size(width, height)
    
    def get_text_extents(self) -> Dict[str, int]:
        """Get text metrics"""
        font = FontManager.get_font(
            self._font_name, 
            self._font_size, 
            self._bold, 
            self._italic
        )
        
        # Get metrics for a typical character
        metrics = font.metrics('M')
        if metrics:
            ascent = font.get_ascent()
            descent = font.get_descent()
            height = font.get_height()
            
            return {
                'ascent': ascent,
                'descent': descent,
                'height': height,
                'line_height': height + 2  # Add some spacing
            }
        
        return {'ascent': 0, 'descent': 0, 'height': 0, 'line_height': 0}

class Label(Text):
    """A simple text label with some default styling"""
    
    def __init__(self, x: int, y: int, text: str = "", parent: Optional[UIComponent] = None):
        super().__init__(x, y, text, parent)
        
        # Default styles for labels
        self.styles.update({
            'font_name': 'Arial',
            'font_size': 16,
            'color': (0, 0, 0),
            'background_color': None,
            'padding': (2, 4, 2, 4)
        })
        
        # Apply styles
        self.set_style(
            font_name=self.styles['font_name'],
            font_size=self.styles['font_size'],
            color=self.styles['color']
        )
    
    def _render_content(self, surface: pygame.Surface, abs_x: int, abs_y: int):
        """Render the label with background"""
        # Draw background if specified
        bg_color = self.styles.get('background_color')
        if bg_color:
            bg_rect = pygame.Rect(abs_x, abs_y, self.width, self.height)
            border_radius = self.styles.get('border_radius', 0)
            
            if border_radius > 0:
                pygame.draw.rect(
                    surface, 
                    bg_color, 
                    bg_rect, 
                    border_radius=border_radius
                )
            else:
                pygame.draw.rect(surface, bg_color, bg_rect)
        
        # Let the parent class handle the text rendering
        super()._render_content(surface, abs_x, abs_y)

class Heading(Label):
    """A heading text component with larger font size"""
    
    def __init__(self, x: int, y: int, text: str = "", level: int = 1, 
                 parent: Optional[UIComponent] = None):
        super().__init__(x, y, text, parent)
        
        # Set font size based on heading level
        font_sizes = {1: 32, 2: 28, 3: 24, 4: 20, 5: 18, 6: 16}
        font_size = font_sizes.get(min(max(level, 1), 6), 16)
        
        self.set_style(
            font_name='Arial',
            font_size=font_size,
            bold=True,
            color=(50, 50, 50)
        )

class Paragraph(Label):
    """A multi-line text component with word wrapping"""
    
    def __init__(self, x: int, y: int, width: int, text: str = "", 
                 parent: Optional[UIComponent] = None):
        # Initialize with zero height, will be updated in _update_surface
        super().__init__(x, y, text, parent)
        
        # Set up for wrapping
        self.set_size(width, 0)  # Height will be calculated
        self.set_wrap(True, width)
        
        # Default styles for paragraphs
        self.styles.update({
            'font_name': 'Arial',
            'font_size': 14,
            'color': (30, 30, 30),
            'line_spacing': 1.2,
            'align': 'left',
            'valign': 'top'
        })
        
        # Apply styles
        self.set_style(
            font_name=self.styles['font_name'],
            font_size=self.styles['font_size'],
            color=self.styles['color'],
            align=self.styles['align']
        )
    
    def set_text(self, text: str):
        """Set the text and update the layout"""
        super().text = text
        self._update_paragraph_layout()
    
    def _update_paragraph_layout(self):
        """Update the paragraph layout after text or style changes"""
        if not self._text:
            self._surface = None
            self._rendered_rect = None
            self.set_size(self.width, 0)
            return
        
        font = FontManager.get_font(
            self.styles['font_name'],
            self.styles['font_size'],
            self.styles.get('bold', False),
            self.styles.get('italic', False)
        )
        
        # Split text into words
        words = self._text.split(' ')
        lines = []
        current_line = []
        
        # Calculate available width (accounting for padding)
        padding_left = self.styles.get('padding', (0, 0, 0, 0))[3]
        padding_right = self.styles.get('padding', (0, 0, 0, 0))[1]
        available_width = self.width - padding_left - padding_right
        
        # Build lines
        for word in words:
            # Test if adding this word would exceed the available width
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= available_width or not current_line:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Render each line
        line_surfaces = []
        total_height = 0
        max_width = 0
        line_height = int(font.get_height() * self.styles['line_spacing'])
        
        for line in lines:
            if line:  # Only render non-empty lines
                line_surface = font.render(line, self._antialias, self._color)
            else:
                # For empty lines, use a small surface with just the height
                line_surface = pygame.Surface((1, line_height), pygame.SRCALPHA)
            
            line_surfaces.append(line_surface)
            max_width = max(max_width, line_surface.get_width())
            total_height += line_surface.get_height()
        
        # Create the final surface
        self._surface = pygame.Surface(
            (max_width, total_height), 
            pygame.SRCALPHA
        )
        self._rendered_rect = self._surface.get_rect()
        
        # Blit each line with proper alignment and spacing
        y_offset = 0
        for i, line_surface in enumerate(line_surfaces):
            x_offset = 0
            
            # Horizontal alignment
            if self._align == 'center':
                x_offset = (max_width - line_surface.get_width()) // 2
            elif self._align == 'right':
                x_offset = max_width - line_surface.get_width()
            
            self._surface.blit(line_surface, (x_offset, y_offset))
            y_offset += line_height
        
        # Update component height to fit all lines
        self.set_size(self.width, total_height)
    
    def set_style(self, **styles):
        """Set one or more style properties"""
        needs_update = any(
            k in styles for k in 
            ['font_name', 'font_size', 'color', 'bold', 'italic', 'line_spacing', 'align']
        )
        
        super().set_style(**styles)
        
        if needs_update:
            self._update_paragraph_layout()
