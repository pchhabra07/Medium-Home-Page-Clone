import os
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time

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
    # Handle rgba()
    elif color_str.startswith('rgba('):
        match = re.match(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*[\d.]+\s*\)', color_str)
        if match:
            r, g, b = map(int, match.groups()[:3])
            return (r, g, b)
    # Handle named colors (basic ones)
    named_colors = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 128, 0),
        'blue': (0, 0, 255),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
        'darkgray': (169, 169, 169),
        'darkgrey': (169, 169, 169),
        'lightgray': (211, 211, 211),
        'lightgrey': (211, 211, 211)
    }
    if color_str in named_colors:
        return named_colors[color_str]
    return None

def rgb_to_luminance(rgb):
    """Convert RGB tuple to luminance value (0-1)."""
    if rgb is None:
        return None
    r, g, b = rgb
    # Normalize to 0-1 range
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    # Apply sRGB gamma correction
    def gamma_correct(c):
        if c <= 0.03928:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4
    r_linear = gamma_correct(r_norm)
    g_linear = gamma_correct(g_norm)
    b_linear = gamma_correct(b_norm)
    return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

def is_dark_color(color_str):
    """Check if color is dark (luminance < 0.5)."""
    rgb = color_to_rgb(color_str)
    lum = rgb_to_luminance(rgb)
    return lum is not None and lum < 0.5

def is_light_color(color_str):
    """Check if color is light (luminance > 0.5)."""
    rgb = color_to_rgb(color_str)
    lum = rgb_to_luminance(rgb)
    return lum is not None and lum > 0.5

def test_dark_mode_rendering():
    """Test that the page renders in dark mode with proper colors."""
    # Set up headless Firefox
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(options=opts)
    
    try:
        # Get the absolute path to index.html
        file_path = os.path.abspath("index.html")
        driver.get(f"file://{file_path}")
        
        # Give the page a moment to load
        time.sleep(1)
        
        # Define elements to check for dark backgrounds
        dark_background_selectors = [
            "body",
            ".top-container",
            ".navbar",
            ".search-box"
        ]
        
        # Define elements to check for light text
        light_text_selectors = [
            ".search-input",
            ".write-text",
            ".navbar-pages",
            ".blog-title",
            ".blog-desc",
            ".follow-button"
        ]
        
        # Define elements to check for light borders (for interactive elements)
        light_border_selectors = [
            ".follow-button"
        ]
        
        # Check dark backgrounds
        for selector in dark_background_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            assert len(elements) > 0, f"Element not found: {selector}"
            for el in elements:
                bg_color = el.value_of_css_property("background-color")
                # Handle transparent backgrounds (should be dark via inheritance)
                if bg_color in ("transparent", "rgba(0, 0, 0, 0)"):
                    # Check parent background instead? For simplicity, we'll require explicit dark background
                    # But make an exception for body which might be transparent
                    if selector != "body":
                        assert False, f"Element {selector} has transparent background - expected dark background"
                else:
                    assert is_dark_color(bg_color), f"Background color not dark for {selector}: {bg_color}"
        
        # Check light text
        for selector in light_text_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            assert len(elements) > 0, f"Element not found: {selector}"
            for el in elements:
                color = el.value_of_css_property("color")
                assert is_light_color(color), f"Text color not light for {selector}: {color}"
        
        # Check light borders for interactive elements
        for selector in light_border_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            assert len(elements) > 0, f"Element not found: {selector}"
            for el in elements:
                # Check all border sides
                for side in ["top", "right", "bottom", "left"]:
                    border_color = el.value_of_css_property(f"border-{side}-color")
                    assert is_light_color(border_color), f"Border color not light for {selector} side {side}: {border_color}"
        
        # Check for leftover light backgrounds on major surfaces
        light_background_selectors = [
            "body",
            ".top-container",
            ".navbar",
            ".search-box",
            ".right-page"
        ]
        
        for selector in light_background_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for el in elements:
                bg_color = el.value_of_css_property("background-color")
                # Skip transparent backgrounds (they inherit)
                if bg_color in ("transparent", "rgba(0, 0, 0, 0)"):
                    continue
                # Assert that it's NOT a light background (luminance <= 0.7 to allow some mid-tones)
                assert not is_light_color(bg_color) or rgb_to_luminance(color_to_rgb(bg_color)) <= 0.7, \
                    f"Major surface {selector} has light background: {bg_color}"
        
    finally:
        driver.quit()

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