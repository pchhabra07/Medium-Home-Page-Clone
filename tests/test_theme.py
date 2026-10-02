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

def get_style(sheets, selector):
    """Get specified CSS properties for a selector from stylesheets."""
    style = {}
    for sheet in sheets:
        for rule in sheet:
            if rule.type == cssutils.STYLE_RULE:
                if selector in rule.selectorText:
                    for prop in ['background-color', 'color', 
                                 'border-top-color', 'border-right-color', 
                                 'border-bottom-color', 'border-left-color']:
                        val = rule.style.getPropertyValue(prop)
                        if val:
                            style[prop] = val
    return style

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

def get_original_styles():
    """Parse original CSS files and return stylesheets."""
    css = cssutils.parseFile('style.css')
    left_page_css = cssutils.parseFile('left_page_style.css')
    return [css, left_page_css]

def test_navbar_remains_light_theme():
    """Verify Navbar and descendants retain light theme appearance."""
    original_sheets = get_original_styles()
    with open('index.html', 'r') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
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
        # For Navbar, we expect background to remain light and text to remain dark
        if 'background-color' in original_style:
            assert is_light_color(original_style['background-color']), \
                f"Original {selector} background should be light: {original_style['background-color']}"
        if 'color' in original_style:
            assert not is_light_color(original_style['color']), \
                f"Original {selector} text should be dark: {original_style['color']}"

def test_top_header_becomes_dark_theme():
    """Verify top/header components (outside Navbar) become dark theme."""
    original_sheets = get_original_styles()
    # Modify the CSS files to simulate the change? 
    # But note: we are testing the current state. The test should pass after the theme change.
    # We are writing the test to be run after the theme change has been applied.
    # So we will parse the current CSS files (which should be the changed ones).
    # However, we are given the original codebase. We are writing the test for the future state.
    # We will assume that the CSS files have been updated to dark mode for non-Navbar.
    # We will parse the current CSS files (which are the same as the original if no change made).
    # The test will fail on the original and pass after the change.
    modified_sheets = get_original_styles()  # In reality, after change, these would be different
    
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
        modified_style = get_style(modified_sheets, selector)
        if 'background-color' in modified_style:
            assert not is_light_color(modified_style['background-color']), \
                f"{selector} background should be dark, got {modified_style['background-color']}"
        if 'color' in modified_style:
            assert is_light_color(modified_style['color']), \
                f"{selector} text should be light, got {modified_style['color']}"

def test_main_body_becomes_dark_theme():
    """Verify main body/content components become dark theme."""
    modified_sheets = get_original_styles()
    
    main_body_selectors = [
        '.writer-details-const',
        '.writer-details-var',
        '.blog-title',
        '.blog-desc',
        '.date-of-publish',
        '.claps-num',
        '.comment-num',
        '.blog-preview'  # for border-color
    ]
    
    for selector in main_body_selectors:
        modified_style = get_style(modified_sheets, selector)
        if selector == '.blog-preview':
            # Check border-color (we'll check bottom as representative)
            for border_prop in ['border-top-color', 'border-right-color', 
                                'border-bottom-color', 'border-left-color']:
                if border_prop in modified_style:
                    assert not is_light_color(modified_style[border_prop]), \
                        f"{selector} {border_prop} should be dark, got {modified_style[border_prop]}"
        else:
            if 'color' in modified_style:
                assert is_light_color(modified_style['color']), \
                    f"{selector} text should be light, got {modified_style['color']}"

def test_right_sidebar_becomes_dark_theme():
    """Verify right sidebar components become dark theme."""
    modified_sheets = get_original_styles()
    
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
        modified_style = get_style(modified_sheets, selector)
        if selector == '.topic-button-parent':
            # Check background-color, color, and border-color
            if 'background-color' in modified_style:
                assert not is_light_color(modified_style['background-color']), \
                    f"{selector} background should be dark, got {modified_style['background-color']}"
            if 'color' in modified_style:
                assert is_light_color(modified_style['color']), \
                    f"{selector} text should be light, got {modified_style['color']}"
            # Check border-color (we'll check top as representative)
            for border_prop in ['border-top-color', 'border-right-color', 
                                'border-bottom-color', 'border-left-color']:
                if border_prop in modified_style:
                    assert not is_light_color(modified_style[border_prop]), \
                        f"{selector} {border_prop} should be dark, got {modified_style[border_prop]}"
        elif selector == '.follow-button':
            if 'color' in modified_style:
                assert is_light_color(modified_style['color']), \
                    f"{selector} text should be light, got {modified_style['color']}"
            for border_prop in ['border-top-color', 'border-right-color', 
                                'border-bottom-color', 'border-left-color']:
                if border_prop in modified_style:
                    assert not is_light_color(modified_style[border_prop]), \
                        f"{selector} {border_prop} should be dark, got {modified_style[border_prop]}"
        else:
            if 'background-color' in modified_style:
                assert not is_light_color(modified_style['background-color']), \
                    f"{selector} background should be dark, got {modified_style['background-color']}"
            if 'color' in modified_style:
                assert is_light_color(modified_style['color']), \
                    f"{selector} text should be light, got {modified_style['color']}"