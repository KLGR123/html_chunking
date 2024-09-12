import cssutils
import tiktoken
from bs4 import BeautifulSoup, Tag


def count_tokens(text: str) -> int:
    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
    tokens = encoder.encode(text)
    return len(tokens)


def clean_html(html: str, attr_max_len: int = 0) -> str:
    soup = BeautifulSoup(html, "lxml")
    removed_content = []

    css_texts = [style.get_text() for style in soup.find_all('style')]
    for css_text in css_texts:
        sheet = cssutils.parseString(css_text)
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                selector = rule.selectorText
                if '::' in selector or ':after' in selector or ':before' in selector:
                    continue
                if 'display' in rule.style and 'none' in rule.style['display']:
                    for element in soup.select(selector):
                        removed_content.append(element.get_text())
                        element.decompose()
                elif 'visibility' in rule.style and 'hidden' in rule.style['visibility']:
                    for element in soup.select(selector):
                        removed_content.append(element.get_text())
                        element.decompose()

    for tag in ['script', 'style']:
        for element in soup.find_all(tag):
            removed_content.append(element.get_text())
            element.decompose()

    for elem in soup.find_all(style=lambda value: value and ('display:none' in value or 'display: none' in value or 'visibility:hidden' in value or 'visibility: hidden' in value)):
        elem.decompose()

    attr_to_remove = ['href', 'src', 'd', 'url', 'data-url', 'data-src', 'data-src-hq']

    for attr in attr_to_remove:
        for tag in soup.find_all(attrs={attr: True}):
            if attr_max_len and len(tag[attr]) > attr_max_len:
                tag[attr] = tag[attr][:attr_max_len] + "..."

    for element in soup.find_all(attrs={"aria-hidden": "true"}):
        removed_content.append(element.get_text())
        element.decompose()

    for element in soup.find_all(attrs={"tabindex": "-1"}):
        removed_content.append(element.get_text())
        element.decompose()

    cleaned_html = str(soup)
    removed_content_text = "\n".join(removed_content)
    return cleaned_html, removed_content_text


def split_html_by_dom(html_string: str, max_token: int):
    chunks = []
    soup = BeautifulSoup(html_string, 'html.parser')
    traverse_dom(soup, chunks, k=max_token)
    return chunks


def format_attrs(attrs):
    formatted_attrs = {}
    for key, value in attrs.items():
        if isinstance(value, list):
            value = ' '.join(value) if value else ''
        formatted_attrs[key] = value
    return formatted_attrs


def build_full_content(path, node):
    opening_tags = ''.join(
        [
            "<" + p['tag'] + ''.join([' {}="{}"'.format(key, value) for key, value in p['attrs'].items()]) + ">"
            for p in path
        ]
    )
    node_content = str(node)
    closing_tags = ''.join(["</" + p['tag'] + ">" for p in reversed(path)])
    return opening_tags + node_content + closing_tags


def traverse_dom(node, chunks, k, path=[]):
    if not node.name:
        return

    node_length = count_tokens(str(node))
    if node_length < k:
        full_content = build_full_content(path, node)

        if full_content.startswith('<[document]>'):
            full_content = full_content[len('<[document]>'):].strip()
        if full_content.endswith('</[document]>'):
            full_content = full_content[:-len('</[document]>')].strip()

        chunks.append({'tag': node.name, 'attrs': node.attrs, 'content': full_content, 'path': path.copy()})
        return

    for child in node.children:
        if child.name:
            path.append({'tag': node.name, 'attrs': format_attrs(node.attrs)})
            traverse_dom(child, chunks, k, path)
            path.pop()


def get_common_root_path(soup1, soup2):
    path1 = []
    path2 = []

    while soup1 and soup2 and soup1.name == soup2.name and soup1.attrs == soup2.attrs:
        path1.append(soup1)
        path2.append(soup2)
        if len(soup1.contents) > 0 and len(soup2.contents) > 0:
            soup1 = next((child for child in soup1.contents if child.name), None)
            soup2 = next((child for child in soup2.contents if child.name), None)
        else:
            break

    return path1, path2


def merge_html_chunk(html_1, html_2):
    soup1 = BeautifulSoup(html_1, 'html.parser')
    soup2 = BeautifulSoup(html_2, 'html.parser')

    path1, path2 = get_common_root_path(soup1, soup2)
    common_parent1 = path1[-1] if path1 else soup1
    common_parent2 = path2[-1] if path2 else soup2

    for element in common_parent2.contents:
        if element not in common_parent1.contents:
            common_parent1.append(element)

    return str(soup1)


def merge_html_chunks(html_chunks, k: int):
    merged_chunks = []
    current_chunk = html_chunks[0]

    for i in range(1, len(html_chunks)):
        next_chunk = html_chunks[i]
        merged = merge_html_chunk(current_chunk, next_chunk)
        
        if count_tokens(merged) <= k:
            current_chunk = merged
        else:
            merged_chunks.append(current_chunk)
            current_chunk = next_chunk

    merged_chunks.append(current_chunk)
    return merged_chunks


def get_html_chunks(html: str, max_tokens: int, is_clean_html: bool = True, attr_cutoff_len: int = 40) -> list:
    html, removed = clean_html(html, attr_cutoff_len) if is_clean_html else html
    chunks = split_html_by_dom(html, max_token=max_tokens)
    chunks = [chunk['content'] for chunk in chunks]
    merged_chunks = merge_html_chunks(chunks, k=max_tokens)
    return merged_chunks