import os
import cssutils
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE_DIR, 'left_page_style.css')
HTML_FILE = os.path.join(BASE_DIR, 'index.html')


def _get_blog_thumbnail_style():
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css_content = f.read()
    stylesheet = cssutils.parseString(css_content)
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE and rule.selectorText == '.blog-thumbnail':
            return rule.style
    return None


def test_blog_thumbnail_height_is_180px():
    style = _get_blog_thumbnail_style()
    assert style is not None, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    assert 'height' in style, "height property must be explicitly set for .blog-thumbnail"
    assert style['height'] == '180px', f"Expected height 180px, got {style['height']}"


def test_blog_thumbnail_width_is_180px():
    style = _get_blog_thumbnail_style()
    assert style is not None, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    assert 'width' in style, "width property must be explicitly set for .blog-thumbnail"
    assert style['width'] == '180px', f"Expected width 180px, got {style['width']}"


def test_blog_thumbnail_elements_exist_in_html():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    thumbnails = soup.find_all('div', class_='blog-thumbnail')
    assert len(thumbnails) > 0, "At least one div with class 'blog-thumbnail' must exist in index.html"


def test_blog_thumbnail_count_matches_sample_blogs():
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()
    soup = BeautifulSoup(html_content, 'html.parser')
    thumbnails = soup.find_all('div', class_='blog-thumbnail')
    assert len(thumbnails) == 10, f"Expected 10 blog-thumbnail divs, found {len(thumbnails)}"


def test_blog_thumbnail_preserves_background_image():
    style = _get_blog_thumbnail_style()
    assert style is not None, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    assert 'background-image' in style, "background-image must be explicitly set for .blog-thumbnail"
    assert 'profile_pic.jpg' in style['background-image'], "background-image should reference profile_pic.jpg"