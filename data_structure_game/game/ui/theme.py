"""
Theme and styling for the Data Structure Game UI.
Defines a consistent color scheme and styling across all UI components.
"""
from typing import Dict, Any, Tuple

# Color Palette
COLORS = {
    # Primary Colors
    'primary': (63, 81, 181),     # Indigo
    'primary_light': (159, 168, 218),
    'primary_dark': (40, 53, 147),
    'secondary': (255, 152, 0),   # Orange
    'secondary_light': (255, 183, 77),
    'secondary_dark': (245, 124, 0),
    
    # Background Colors
    'background': (250, 250, 255),  # Very light blue-gray
    'surface': (255, 255, 255),     # White
    'panel': (245, 245, 250),       # Slightly darker than background
    
    # Text Colors
    'text_primary': (33, 33, 33),   # Dark gray
    'text_secondary': (97, 97, 97), # Medium gray
    'text_light': (255, 255, 255),  # White
    'text_disabled': (189, 189, 189), # Light gray
    
    # Status Colors
    'success': (46, 125, 50),       # Green
    'error': (198, 40, 40),         # Red
    'warning': (237, 108, 2),       # Orange
    'info': (2, 136, 209),          # Blue
    
    # Grayscale
    'gray_50': (250, 250, 250),
    'gray_100': (245, 245, 245),
    'gray_200': (238, 238, 238),
    'gray_300': (224, 224, 224),
    'gray_400': (189, 189, 189),
    'gray_500': (158, 158, 158),
    'gray_600': (117, 117, 117),
    'gray_700': (97, 97, 97),
    'gray_800': (66, 66, 66),
    'gray_900': (33, 33, 33),
}

# Typography
TYPOGRAPHY = {
    'font_family': 'Arial, sans-serif',
    'font_sizes': {
        'h1': 28,
        'h2': 24,
        'h3': 20,
        'h4': 18,
        'body1': 16,
        'body2': 14,
        'caption': 12,
        'button': 15,
    },
    'font_weights': {
        'light': 300,
        'regular': 400,
        'medium': 500,
        'bold': 700,
    },
}

# Shadows
SHADOWS = {
    'xs': '0 1px 3px rgba(0,0,0,0.08)',
    'sm': '0 2px 4px rgba(0,0,0,0.1)',
    'md': '0 4px 6px rgba(0,0,0,0.1)',
    'lg': '0 10px 15px rgba(0,0,0,0.1)',
    'xl': '0 20px 25px rgba(0,0,0,0.1)',
}

# Border Radius
BORDER_RADIUS = {
    'none': 0,
    'sm': 4,
    'md': 8,
    'lg': 12,
    'xl': 16,
    'full': 9999,
}

# Spacing
SPACING = {
    'xxs': 4,
    'xs': 8,
    'sm': 12,
    'md': 16,
    'lg': 24,
    'xl': 32,
    'xxl': 48,
}

def get_theme() -> Dict[str, Any]:
    """Return the complete theme configuration."""
    return {
        'colors': COLORS,
        'typography': TYPOGRAPHY,
        'shadows': SHADOWS,
        'border_radius': BORDER_RADIUS,
        'spacing': SPACING,
    }

def get_button_style(variant: str = 'primary') -> Dict[str, Any]:
    """Get button style based on variant."""
    base_style = {
        'font_size': TYPOGRAPHY['font_sizes']['button'],
        'font_weight': TYPOGRAPHY['font_weights']['medium'],
        'padding': (SPACING['sm'], SPACING['md']),
        'border_radius': BORDER_RADIUS['md'],
        'border_width': 1,
        'transition': 'all 0.2s ease',
        'shadow': SHADOWS['sm'],
        'hover_shadow': SHADOWS['md'],
        'active_shadow': SHADOWS['xs'],
    }
    
    if variant == 'primary':
        return {
            **base_style,
            'background_color': COLORS['primary'],
            'hover_color': COLORS['primary_dark'],
            'active_color': COLORS['primary_dark'],
            'text_color': COLORS['text_light'],
            'border_color': COLORS['primary_dark'],
        }
    elif variant == 'secondary':
        return {
            **base_style,
            'background_color': COLORS['secondary'],
            'hover_color': COLORS['secondary_dark'],
            'active_color': COLORS['secondary_dark'],
            'text_color': COLORS['text_light'],
            'border_color': COLORS['secondary_dark'],
        }
    elif variant == 'outline':
        return {
            **base_style,
            'background_color': 'transparent',
            'hover_color': f"rgba({COLORS['primary'][0]}, {COLORS['primary'][1]}, {COLORS['primary'][2]}, 0.1)",
            'active_color': f"rgba({COLORS['primary'][0]}, {COLORS['primary'][1]}, {COLORS['primary'][2]}, 0.2)",
            'text_color': COLORS['primary'],
            'border_color': COLORS['primary'],
            'shadow': 'none',
            'hover_shadow': 'none',
            'active_shadow': 'none',
        }
    else:  # default
        return {
            **base_style,
            'background_color': COLORS['gray_100'],
            'hover_color': COLORS['gray_200'],
            'active_color': COLORS['gray_300'],
            'text_color': COLORS['text_primary'],
            'border_color': COLORS['gray_300'],
        }

def get_panel_style() -> Dict[str, Any]:
    """Get default panel styling."""
    return {
        'background_color': COLORS['surface'],
        'border_radius': BORDER_RADIUS['md'],
        'border_width': 1,
        'border_color': COLORS['gray_200'],
        'shadow': SHADOWS['sm'],
        'padding': SPACING['md'],
    }

def get_card_style() -> Dict[str, Any]:
    """Get card styling."""
    return {
        'background_color': COLORS['surface'],
        'border_radius': BORDER_RADIUS['md'],
        'border_width': 1,
        'border_color': COLORS['gray_200'],
        'shadow': SHADOWS['sm'],
        'padding': SPACING['lg'],
        'hover_shadow': SHADOWS['md'],
        'transition': 'all 0.2s ease',
    }

def get_text_style(variant: str = 'body1') -> Dict[str, Any]:
    """Get text styling based on variant."""
    return {
        'font_size': TYPOGRAPHY['font_sizes'].get(variant, TYPOGRAPHY['font_sizes']['body1']),
        'color': COLORS['text_primary'],
        'line_height': 1.5,
        'font_family': TYPOGRAPHY['font_family'],
    }
