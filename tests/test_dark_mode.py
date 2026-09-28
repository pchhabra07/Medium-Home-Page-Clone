import os
import re
from bs4 import BeautifulSoup

def parse_css(css_text):
    """Parse CSS text into a list of (selector, declarations) tuples."""
    # Remove CSS comments
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    # Split into rules
    rules = []
    for rule in css_text.split('}'):
        if '{' not in rule:
            continue
        selector, declarations = rule.split('{', 1)
        selector = selector.strip()
        declarations = declarations.strip()
        if not selector or not declarations:
            continue
        # Parse declarations
        decls = {}
        for decl in declarations.split(';'):
            if ':' not in decl:
                continue
            prop, val = decl.split(':', 1)
            decls[prop.strip()] = val.strip()
        rules.append((selector, decls))
    return rules

def color_to_rgb(color_str):
    """Convert color string to (r, g, b) tuple. Returns None if unsupported."""
    color_str = color_str.strip().lower()
    # Handle hex colors
    if color_str.startswith('#'):
        if len(color_str) == 4:
            r = int(color_str[1] * 2, 16)
            g = int(color_str[2] * 2, 16)
            b = int(color_str[3] * 2, 16)
            return (r, g, b)
        elif len(color_str) == 7:
            r = int(color_str[1:3], 16)
            g = int(color_str[3:5], 16)
            b = int(color_str[5:7], 16)
            return (r, g, b)
    # Handle rgb()
    elif color_str.startswith('rgb('):
        match = re.match(r'rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', color_str)
        if match:
            r, g, b = map(int, match.groups())
            return (r, g, b)
    # Handle named colors (basic ones)
    named_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 128, 0),
        'blue': (0, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128)
    }
    if color_str in named_colors:
        return named_colors[color_str]
    return None

def is_dark_color(color_str):
    """Check if color is dark (max RGB < 100)."""
    rgb = color_to_rgb(color_str)
    if rgb is None:
        return False
    return max(rgb) < 100

def is_light_color(color_str):
    """Check if color is light (min RGB > 150)."""
    rgb = color_to_rgb(color_str)
    if rgb is None:
        return False
    return min(rgb) > 150

def test_dark_mode_css_rules():
    """Test that CSS contains dark mode rules for background and text colors."""
    # Read CSS files
    css_files = ['style.css', 'left_page_style.css']
    all_rules = []
    for css_file in css_files:
        with open(css_file, 'r') as f:
            css_text = f.read()
        rules = parse_css(css_text)
        all_rules.extend(rules)
    
    # Check for dark mode background and text rules
    has_dark_background = False
    has_light_text = False
    
    for selector, declarations in all_rules:
        if '.dark-mode' in selector:
            if 'background-color' in declarations:
                if is_dark_color(declarations['background-color']):
                    has_dark_background = True
            if 'color' in declarations:
                if is_light_color(declarations['color']):
                    has_light_text = True
    
    assert has_dark_background, "No dark mode background color rule found in CSS"
    assert has_light_text, "No dark mode text color rule found in CSS"

def test_page_structure_intact():
    """Test that essential page elements are present in HTML."""
    with open('index.html', 'r') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Check for essential elements
    assert soup.find('div', class_='logo_img') is not None, "Logo image missing"
    assert soup.find('input', class_='search-input') is not None, "Search input missing"
    assert soup.find('div', class_='write-button') is not None, "Write button missing"
    assert soup.find('div', class_='navbar-pages', string='For you') is not None, "Current navbar item missing"
    assert soup.find('div', class_='blog-title') is not None, "Blog title missing"
    assert soup.find('div', class_='blog-desc') is not None, "Blog description missing"