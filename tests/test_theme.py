import cssutils
from bs4 import BeautifulSoup
import re

def is_light_color(color_str):
    """Determine if a CSS color string represents a light color."""
    try:
        if color_str.startswith('#'):
            if len(color_str) == 4:
                r = int(color_str[1]*2, 16)
                g = int(color_str[2]*2, 16)
                b = int(color_str[3]*2, 16)
            elif len(color_str) == 7:
                r = int(color_str[1:3], 16)
                g = int(color_str[3:5], 16)
                b = int(color_str[5:7], 16)
            else:
                return False
        elif color_str.startswith('rgb'):
            nums = color_str[4:-1].split(',')
            r = int(nums[0].strip())
            g = int(nums[1].strip())
            b = int(nums[2].strip())
        else:
            named_colors = {
                'white': (255, 255, 255),
                'black': (0, 0, 0),
                'red': (255, 0, 0),
                'green': (0, 128, 0),
                'blue': (0, 0, 255),
                'gray': (128, 128, 128),
                'grey': (128, 128, 128)
            }
            if color_str.lower() in named_colors:
                r, g, b = named_colors[color_str.lower()]
            else:
                return False
        def to_linear(c):
            c /= 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return ((c + 0.055) / 1.055) ** 2.4
        r_lin = to_linear(r)
        g_lin = to_linear(g)
        b_lin = to_linear(b)
        luminance = 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin
        return luminance > 0.5
    except Exception:
        return False

def selector_matches_rule(selector, rule):
    """Check if a selector exactly matches any part of a comma-separated rule selector."""
    parts = [part.strip() for part in rule.selectorText.split(',')]
    return selector in parts

def extract_color_from_value(value):
    """Extract a color from a CSS value string (e.g., from shorthand properties)."""
    if not value:
        return None
    tokens = value.split()
    for token in reversed(tokens):
        # Match hex color
        if re.match(r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$', token):
            return token
        # Match rgb() color
        if re.match(r'^rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)$', token):
            return token
    return None

def get_style(sheets, selector):
    """Get specified CSS properties for a selector from stylesheets, handling shorthand."""
    style = {}
    for sheet in sheets:
        for rule in sheet:
            if rule.type == cssutils.STYLE_RULE:
                if selector_matches_rule(selector, rule):
                    # Check longhand properties first
                    for prop in ['background-color', 'color', 
                                 'border-top-color', 'border-right-color', 
                                 'border-bottom-color', 'border-left-color']:
                        val = rule.style.getPropertyValue(prop)
                        if val:
                            style[prop] = val
                    # Handle shorthand properties
                    shorthand_map = {
                        'background': ['background-color'],
                        'border': ['border-top-color', 'border-right-color', 'border-bottom-color', 'border-left-color'],
                        'border-top': ['border-top-color'],
                        'border-right': ['border-right-color'],
                        'border-bottom': ['border-bottom-color'],
                        'border-left': ['border-left-color']
                    }
                    for shorthand, longhands in shorthand_map.items():
                        val = rule.style.getPropertyValue(shorthand)
                        if val:
                            color = extract_color_from_value(val)
                            if color:
                                for lh in longhands:
                                    # Only set if not already set by longhand (to avoid overriding)
                                    if lh not in style:
                                        style[lh] = color
    return style

def get_original_styles():
    """Parse original CSS files and return stylesheets."""
    css = cssutils.parseFile('style.css')
    left_page_css = cssutils.parseFile('left_page_style.css')
    return [css, left_page_css]

def test_regression_structure():
    """Ensure core HTML structure remains intact."""
    with open('index.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    assert soup.find('div', class_='top-container') is not None
    assert soup.find('div', class_='body') is not None
    assert soup.find('div', class_='navbar') is not None
    assert soup.find('div', class_='search-box') is not None
    assert soup.find('input', class_='search-input') is not None
    assert soup.find('div', class_='write-button') is not None
    assert soup.find('div', class_='notifications-icon') is not None
    assert soup.find('div', class_='profile') is not None
    assert soup.find('div', class_='body-left-page') is not None
    assert soup.find('div', class_='sample-blog-content') is not None
    assert soup.find('div', class_='staff-picks') is not None
    assert soup.find('div', class_='recommended-topics') is not None
    assert soup.find('div', class_='who-to-follow') is not None
    assert soup.find('div', class_='reading-list') is not None

def test_navbar_preserved():
    """Verify Navbar and descendants retain original light theme appearance."""
    # Expected original Navbar theme-relevant styles (extracted from original CSS)
    expected_navbar_styles = {
        '.navbar': {
            'background-color': 'white'
        },
        '.navbar-content': {
            'border-bottom-color': '#f2f2f2'
        },
        '.navbar-pages': {
            'color': '#6b6b6b'
        },
        '.current': {
            'color': '#242424',
            'border-bottom-color': '#242424'
        },
        '.add-topic-button': {
            # No explicit background-color or color in normal state; skip if not present
        },
        '.new-box': {
            'background-color': '#1a8917',
            'color': '#f2f2f2'
        }
    }
    
    current_sheets = get_original_styles()
    
    for selector, expected_props in expected_navbar_styles.items():
        current_style = get_style(current_sheets, selector)
        for prop, expected_value in expected_props.items():
            # Skip if expected value is empty (meaning we don't expect it to be set)
            if not expected_value:
                continue
            assert prop in current_style, f"Missing property {prop} for {selector} in current CSS"
            actual_value = current_style[prop]
            assert actual_value == expected_value, \
                f"Property {prop} for {selector} expected {expected_value}, got {actual_value}"

def test_top_header_dark():
    """Verify top/header components (outside Navbar) are dark theme."""
    current_sheets = get_original_styles()
    
    top_header_selectors = [
        '.top-container',
        '.search-box',
        '.search-input',
        '.write-button',
        '.write-text',
        '.notifications-icon',
        '.profile'
    ]
    
    for selector in top_header_selectors:
        current_style = get_style(current_sheets, selector)
        if 'background-color' in current_style:
            assert not is_light_color(current_style['background-color']), \
                f"{selector} background should be dark, got {current_style['background-color']}"
        if 'color' in current_style:
            assert is_light_color(current_style['color']), \
                f"{selector} text should be light, got {current_style['color']}"

def test_main_body_dark():
    """Verify main body/content components are dark theme."""
    current_sheets = get_original_styles()
    
    main_body_selectors = [
        '.writer-details-const',
        '.writer-details-var',
        '.blog-title',
        '.blog-desc',
        '.date-of-publish',
        '.claps-num',
        '.comment-num',
        '.blog-preview'
    ]
    
    for selector in main_body_selectors:
        current_style = get_style(current_sheets, selector)
        if selector == '.blog-preview':
            # Check border-color (we'll check all sides)
            for border_prop in ['border-top-color', 'border-right-color', 
                                'border-bottom-color', 'border-left-color']:
                if border_prop in current_style:
                    assert not is_light_color(current_style[border_prop]), \
                        f"{selector} {border_prop} should be dark, got {current_style[border_prop]}"
        else:
            if 'color' in current_style:
                assert is_light_color(current_style['color']), \
                    f"{selector} text should be light, got {current_style['color']}"

def test_right_sidebar_dark():
    """Verify right sidebar components are dark theme."""
    current_sheets = get_original_styles()
    
    sidebar_selectors = [
        '.staff-picks-anchor',
        '.profile-pic-anchor',
        '.profile-name-anchor',
        '.profile-name',
        '.pick-title',
        '.pick-date',
        '.see-full-list',
        '.topic-button-parent',
        '.topic-button-anchor',
        '.see-more-topics',
        '.account-name',
        '.account-desc',
        '.follow-button',
        '.see-more-suggestions',
        '.reading-list-content-text',
        '.redirect-buttons'
    ]
    
    for selector in sidebar_selectors:
        current_style = get_style(current_sheets, selector)
        if selector == '.topic-button-parent':
            # Check background-color, color, and border-color
            if 'background-color' in current_style:
                assert not is_light_color(current_style['background-color']), \
                    f"{selector} background should be dark, got {current_style['background-color']}"
            if 'color' in current_style:
                assert is_light_color(current_style['color']), \
                    f"{selector} text should be light, got {current_style['color']}"
            # Check border-color (we'll check all sides)
            for border_prop in ['border-top-color', 'border-right-color', 
                                'border-bottom-color', 'border-left-color']:
                if border_prop in current_style:
                    assert not is_light_color(current_style[border_prop]), \
                        f"{selector} {border_prop} should be dark, got {current_style[border_prop]}"
        elif selector == '.follow-button':
            if 'color' in current_style:
                assert is_light_color(current_style['color']), \
                    f"{selector} text should be light, got {current_style['color']}"
            for border_prop in ['border-top-color', 'border-right-color', 
                                'border-bottom-color', 'border-left-color']:
                if border_prop in current_style:
                    assert not is_light_color(current_style[border_prop]), \
                        f"{selector} {border_prop} should be dark, got {current_style[border_prop]}"
        else:
            if 'background-color' in current_style:
                assert not is_light_color(current_style['background-color']), \
                    f"{selector} background should be dark, got {current_style['background-color']}"
            if 'color' in current_style:
                assert is_light_color(current_style['color']), \
                    f"{selector} text should be light, got {current_style['color']}"

if __name__ == '__main__':
    # This allows running the tests directly with python
    test_regression_structure()
    test_navbar_preserved()
    test_top_header_dark()
    test_main_body_dark()
    test_right_sidebar_dark()
    print("All tests passed!")