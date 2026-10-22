import os
import cssutils
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE_DIR, 'left_page_style.css')
HTML_FILE = os.path.join(BASE_DIR, 'index.html')


def _get_blog_thumbnail_rule():
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css_content = f.read()
    stylesheet = cssutils.parseString(css_content)
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE and rule.selectorText == '.blog-thumbnail':
            return rule
    return None


def test_blog_thumbnail_height_is_180px():
    """Acceptance Criteria: blog-thumbnail div height must be 180px."""
    rule = _get_blog_thumbnail_rule()
    assert rule is not None, ".blog-thumbnail CSS rule must exist in left_page_style.css"

    style = rule.style
    assert 'height' in style, "height property must be explicitly set for .blog-thumbnail"
    assert style['height'] == '180px', f"Expected height 180px, got {style['height']}"


def test_blog_thumbnail_width_is_180px():
    """Acceptance Criteria: blog-thumbnail div width must be 180px."""
    rule = _get_blog_thumbnail_rule()
    assert rule is not None, ".blog-thumbnail CSS rule must exist in left_page_style.css"

    style = rule.style
    assert 'width' in style, "width property must be explicitly set for .blog-thumbnail"
    assert style['width'] == '180px', f"Expected width 180px, got {style['width']}"


def test_blog_thumbnail_elements_remain_in_html():
    """Regression: blog-thumbnail div elements must remain present in index.html."""
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    thumbnails = soup.find_all('div', class_='blog-thumbnail')

    assert len(thumbnails) > 0, "At least one blog-thumbnail div must exist in index.html"