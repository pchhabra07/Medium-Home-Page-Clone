import os
import re
from bs4 import BeautifulSoup

def test_dark_mode_theme():
    # Parse HTML file
    with open('index.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    body = soup.find('body')
    assert body is not None, "Body tag not found"
    
    # Check body has dark-mode class
    classes = body.get('class', [])
    assert 'dark-mode' in classes, f"Expected 'dark-mode' in body classes, got {classes}"
    
    # Read and combine CSS files
    css_files = ['style.css', 'left_page_style.css']
    css_content = ''
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, 'r') as f:
                css_content += f.read() + '\n'
    
    # Remove CSS comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Parse CSS rules
    rules = []
    for rule in css_content.split('}'):
        if '{' not in rule:
            continue
        selector_part, props_part = rule.split('{', 1)
        selector = selector_part.strip()
        props = {}
        for declaration in props_part.split(';'):
            if ':' not in declaration:
                continue
            prop, val = declaration.split(':', 1)
            prop = prop.strip()
            val = val.strip()
            if prop and val:
                props[prop] = val
        rules.append({'selector': selector, 'properties': props})
    
    # Define selector patterns for dark mode
    bg_patterns = ['body.dark-mode', '.dark-mode body']
    text_patterns = ['body.dark-mode .blog-title', '.dark-mode .blog-title']
    
    # Extract background-color for body in dark mode
    bg_color = None
    for rule in rules:
        if any(pattern in rule['selector'] for pattern in bg_patterns):
            if 'background-color' in rule['properties']:
                bg_color = rule['properties']['background-color']
    
    assert bg_color is not None, "Missing background-color for body in dark mode"
    
    # Extract color for blog title in dark mode
    text_color = None
    for rule in rules:
        if any(pattern in rule['selector'] for pattern in text_patterns):
            if 'color' in rule['properties']:
                text_color = rule['properties']['color']
    
    assert text_color is not None, "Missing color for .blog-title in dark mode"
    
    # Convert color strings to RGB tuples
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 3:
            hex_str = ''.join([c*2 for c in hex_str])
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))
    
    def color_to_rgb(color_str):
        color_str = color_str.strip()
        # Handle hex colors
        if color_str.startswith('#'):
            return hex_to_rgb(color_str)
        # Handle rgb() and rgba()
        if color_str.startswith('rgb(') or color_str.startswith('rgba('):
            nums = re.findall(r'\d+', color_str)
            if len(nums) >= 3:
                return tuple(int(nums[i]) for i in range(3))
        # Handle named colors (basic)
        color_map = {
            'black': (0, 0, 0),
            'white': (255, 255, 255),
            'red': (255, 0, 0),
            'green': (0, 128, 0),
            'blue': (0, 0, 255)
        }
        if color_str.lower() in color_map:
            return color_map[color_str.lower()]
        return None
    
    bg_rgb = color_to_rgb(bg_color)
    text_rgb = color_to_rgb(text_color)
    
    assert bg_rgb is not None, f"Could not parse background color: {bg_color}"
    assert text_rgb is not None, f"Could not parse text color: {text_color}"
    
    # Calculate relative luminance (WCAG formula)
    def rgb_to_luminance(rgb):
        r, g, b = [x/255.0 for x in rgb]
        r = r/12.92 if r <= 0.03928 else ((r+0.055)/1.055)**2.4
        g = g/12.92 if g <= 0.03928 else ((g+0.055)/1.055)**2.4
        b = b/12.92 if b <= 0.03928 else ((b+0.055)/1.055)**2.4
        return 0.2126*r + 0.7152*g + 0.0722*b
    
    bg_lum = rgb_to_luminance(bg_rgb)
    text_lum = rgb_to_luminance(text_rgb)
    
    # Calculate contrast ratio
    lighter = max(bg_lum, text_lum)
    darker = min(bg_lum, text_lum)
    contrast = (lighter + 0.05) / (darker + 0.05)
    
    # Check contrast ratio meets WCAG AA for normal text (>=4.5)
    assert contrast >= 4.5, f"Insufficient contrast: {contrast} < 4.5"
    
    # Verify existing content remains present
    title_tag = soup.find('title')
    assert title_tag is not None, "Title tag missing"
    assert "Medium" in title_tag.string, f"Expected 'Medium' in title, got '{title_tag.string}'"
    
    # Verify a sample content element exists
    sample_text = soup.find(string=re.compile("Lorem ipsum"))
    assert sample_text is not None, "Sample content missing"