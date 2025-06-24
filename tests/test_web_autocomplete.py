import os
import pytest

pytestmark = pytest.mark.timeout(10, method='thread')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
HTML_FILE = os.path.join(BASE_DIR, 'web_autocomplete', 'index.html')
JS_FILE = os.path.join(BASE_DIR, 'web_autocomplete', 'script.js')
CSS_FILE = os.path.join(BASE_DIR, 'web_autocomplete', 'style.css')


def test_index_structure():
    assert os.path.exists(HTML_FILE)
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        data = f.read()
    assert 'id="treeContainer"' in data
    assert 'role="tree"' in data
    assert 'id="helpDialog"' in data
    # ensure linked assets
    assert 'script.js' in data
    assert 'style.css' in data


def test_script_key_functions():
    assert os.path.exists(JS_FILE)
    with open(JS_FILE, 'r', encoding='utf-8') as f:
        js = f.read()
    for snippet in ['const MODEL_ID', 'function fetchCompletions', 'async function seedTree']:
        assert snippet in js


def test_style_contains_classes():
    assert os.path.exists(CSS_FILE)
    with open(CSS_FILE, 'r', encoding='utf-8') as f:
        css = f.read()
    assert '.node[tabindex="0"]' in css
    assert 'dialog' in css
