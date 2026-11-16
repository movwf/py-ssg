from markdown_blocks import markdown_to_blocks, block_to_block_type, BlockType
from inline_markdown import text_to_textnodes
from textnode import text_node_to_html_node
from parentnode import ParentNode
from leafnode import LeafNode


def _inline_children(text: str):
    """Convert inline markdown text to a list of HTMLNode objects."""
    nodes = text_to_textnodes(text)
    return [text_node_to_html_node(n) for n in nodes]


def _heading_to_node(block: str) -> ParentNode:
    # block starts with one or more '#'
    parts = block.split(' ', 1)
    level = len(parts[0])  # number of '#'
    tag = f'h{level}'
    content = parts[1] if len(parts) > 1 else ''
    children = _inline_children(content)
    return ParentNode(tag, children)


def _paragraph_to_node(block: str) -> ParentNode:
    return ParentNode('p', _inline_children(block))


def _unordered_list_to_node(block: str) -> ParentNode:
    """Convert a markdown unordered list block to a <ul> node.
    Each line starts with "- ".
    """
    lines = block.split('\n')
    items = []
    for line in lines:
        # Remove leading "- "
        content = line[2:] if line.startswith('- ') else line
        items.append(ParentNode('li', _inline_children(content)))
    return ParentNode('ul', items)


def _ordered_list_to_node(block: str) -> ParentNode:
    """Convert a markdown ordered list block to an <ol> node.
    Each line starts with "1. ", "2. " etc.
    """
    lines = block.split('\n')
    items = []
    for line in lines:
        # Find the first dot after a number and a space
        parts = line.split('. ', 1)
        content = parts[1] if len(parts) == 2 else line
        items.append(ParentNode('li', _inline_children(content)))
    return ParentNode('ol', items)



def _code_to_node(block: str) -> ParentNode:
    # Remove the opening and closing backticks line
    lines = block.split('\n')
    # First line may be ``` or ```lang
    # Last line should be ```
    # Keep everything between them as raw code (including possible leading newline)
    code_lines = lines[1:-1]
    code_text = "\n".join(code_lines)
    # Ensure trailing newline as in expected output
    if not code_text.endswith('\n'):
        code_text += '\n'
    code_node = LeafNode('code', code_text)
    return ParentNode('pre', [code_node])

def _quote_to_node(block: str) -> ParentNode:
    """Convert a markdown block that consists of lines prefixed with ``>``
    into a <blockquote> node. The leading ``>`` (and optional space) is stripped
    from each line before converting inline markdown.
    """
    # Split into lines and strip the leading '>' (and following space if present)
    lines = block.split('\n')
    stripped = [line[2:] if line.startswith('> ') else line[1:] for line in lines]
    content = '\n'.join(stripped)
    children = _inline_children(content)
    return ParentNode('blockquote', children)
    
def markdown_to_html_node(markdown: str) -> ParentNode:
    """Convert a full markdown document into a single ParentNode (a <div>)."""
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.PARAGRAPH:
            children.append(_paragraph_to_node(block))
        elif block_type == BlockType.HEADING:
            children.append(_heading_to_node(block))
        elif block_type == BlockType.CODE:
            children.append(_code_to_node(block))
        elif block_type == BlockType.QUOTE:
            children.append(_quote_to_node(block))
        elif block_type == BlockType.UNORDERED_LIST:
            children.append(_unordered_list_to_node(block))
        elif block_type == BlockType.ORDERED_LIST:
            children.append(_ordered_list_to_node(block))
        else:
            # For simplicity, treat other block types as plain paragraph
            children.append(_paragraph_to_node(block))
    return ParentNode('div', children)
