import os
import cssutils
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE_DIR, 'left_page_style.css')
HTML_FILE = os.path.join(BASE_DIR, 'index.html')


def _get_blog_thumbnail_styles():
    """Return all CSS style declarations for .blog-thumbnail rules."""
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css_content = f.read()
    stylesheet = cssutils.parseString(css_content)
    styles = []
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE and rule.selectorText == '.blog-thumbnail':
            styles.append(rule.style)
    return styles


def test_blog_thumbnail_height_is_180px():
    styles = _get_blog_thumbnail_styles()
    assert len(styles) > 0, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    height_rules = [s for s in styles if 'height' in s]
    assert len(height_rules) > 0, "height property must be explicitly set for .blog-thumbnail"
    for style in height_rules:
        assert style['height'] == '180px', f"Expected height 180px, got {style['height']}"


def test_blog_thumbnail_width_is_180px():
    styles = _get_blog_thumbnail_styles()
    assert len(styles) > 0, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    width_rules = [s for s in styles if 'width' in s]
    assert len(width_rules) > 0, "width property must be explicitly set for .blog-thumbnail"
    for style in width_rules:
        assert style['width'] == '180px', f"Expected width 180px, got {style['width']}"


def test_blog_thumbnail_elements_exist_in_html():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    thumbnails = soup.find_all('div', class_='blog-thumbnail')
    assert len(thumbnails) > 0, "At least one div with class 'blog-thumbnail' must exist in index.html"


def test_blog_thumbnail_preserves_background_image():
    styles = _get_blog_thumbnail_styles()
    assert len(styles) > 0, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    bg_rules = [s for s in styles if 'background-image' in s]
    assert len(bg_rules) > 0, "background-image must be explicitly set for .blog-thumbnail"
    for style in bg_rules:
        assert 'profile_pic.jpg' in style['background-image'], "background-image should reference profile_pic.jpg"