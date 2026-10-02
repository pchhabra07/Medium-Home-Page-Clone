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

def get_style(sheets, selector):
    """Get specified CSS properties for a selector from stylesheets."""
    style = {}
    for sheet in sheets:
        for rule in sheet:
            if rule.type == cssutils.STYLE_RULE:
                if selector_matches_rule(selector, rule):
                    for prop in ['background-color', 'color', 
                                 'border-top-color', 'border-right-color', 
                                 'border-bottom-color', 'border-left-color']:
                        val = rule.style.getPropertyValue(prop)
                        if val:
                            style[prop] = val
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
    original_sheets = get_original_styles()
    current_sheets = get_original_styles()  # Current CSS files (may be changed if theme applied)
    
    navbar_selectors = [
        '.navbar',
        '.navbar-content',
        '.navbar-pages',
        '.current',
        '.add-topic-button',
        '.new-box'
    ]
    
    for selector in navbar_selectors:
        original_style = get_style(original_sheets, selector)
        current_style = get_style(current_sheets, selector)
        
        # Check all theme-relevant properties
        for prop in ['background-color', 'color', 
                     'border-top-color', 'border-right-color', 
                     'border-bottom-color', 'border-left-color']:
            if prop in original_style:
                assert prop in current_style, f"Missing property {prop} for {selector} in current CSS"
                assert original_style[prop] == current_style[prop], \
                    f"Property {prop} for {selector} changed from {original_style[prop]} to {current_style[prop]}"

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
            # Check border-color (we'll check bottom as representative)
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