import os
import cssutils

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_FILE = os.path.join(BASE_DIR, 'left_page_style.css')


def _get_blog_thumbnail_rules():
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css_content = f.read()
    stylesheet = cssutils.parseString(css_content)
    rules = []
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE and rule.selectorText == '.blog-thumbnail':
            rules.append(rule)
    return rules


def test_blog_thumbnail_dimensions_are_180px():
    """Acceptance Criteria: .blog-thumbnail div height and width must be 180px."""
    rules = _get_blog_thumbnail_rules()
    assert len(rules) >= 1, ".blog-thumbnail CSS rule must exist in left_page_style.css"
    assert len(rules) == 1, f"Expected exactly one .blog-thumbnail rule, found {len(rules)} duplicate rules"

    rule = rules[0]
    style = rule.style
    assert 'height' in style, "height property must be explicitly set for .blog-thumbnail"
    assert style['height'] == '180px', f"Expected height 180px, got {style['height']}"
    assert 'width' in style, "width property must be explicitly set for .blog-thumbnail"
    assert style['width'] == '180px', f"Expected width 180px, got {style['width']}"