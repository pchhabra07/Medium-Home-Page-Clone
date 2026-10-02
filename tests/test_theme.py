import cssutils
from bs4 import BeautifulSoup

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
            # Handle named colors (simplified)
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
        # Calculate relative luminance (ITU-R BT.709)
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

def get_rule(stylesheets, selector):
    """Find a CSS rule by selector in a list of stylesheets."""
    for sheet in stylesheets:
        for rule in sheet:
            if rule.type == cssutils.STYLE_RULE:
                if selector in rule.selectorText:
                    return rule
    return None

def test_theme_change():
    # Parse CSS files
    css = cssutils.parseFile('style.css')
    left_page_css = cssutils.parseFile('left_page_style.css')
    stylesheets = [css, left_page_css]
    
    # Parse HTML for regression check
    with open('index.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Regression: Ensure core components exist
    assert soup.find('div', class_='top-container') is not None, "top-container missing"
    assert soup.find('div', class_='body') is not None, "body div missing"
    assert soup.find('div', class_='navbar') is not None, "navbar missing"
    
    # Check .top-container: should be dark background, light text
    top_container_rule = get_rule(stylesheets, '.top-container')
    assert top_container_rule is not None, "Rule for .top-container not found"
    bg_color = top_container_rule.style.backgroundColor
    color = top_container_rule.style.color
    assert bg_color != '', "Background color not set for .top-container"
    assert color != '', "Text color not set for .top-container"
    assert not is_light_color(bg_color), f".top-container background should be dark, got {bg_color}"
    assert is_light_color(color), f".top-container text should be light, got {color}"
    
    # Check .body: should be dark background, light text
    body_rule = get_rule(stylesheets, '.body')
    assert body_rule is not None, "Rule for .body not found"
    bg_color = body_rule.style.backgroundColor
    color = body_rule.style.color
    assert bg_color != '', "Background color not set for .body"
    assert color != '', "Text color not set for .body"
    assert not is_light_color(bg_color), f".body background should be dark, got {bg_color}"
    assert is_light_color(color), f".body text should be light, got {color}"
    
    # Check .navbar: should be light background, dark text
    navbar_rule = get_rule(stylesheets, '.navbar')
    assert navbar_rule is not None, "Rule for .navbar not found"
    bg_color = navbar_rule.style.backgroundColor
    assert bg_color != '', "Background color not set for .navbar"
    assert is_light_color(bg_color), f".navbar background should be light, got {bg_color}"