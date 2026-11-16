import unittest
from markdown_blocks import (
    markdown_to_blocks,
    BlockType,
    block_to_block_type,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_heading_and_paragraph(self):
        md = """
# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
                "- This is the first list item in a list block\n- This is a list item\n- This is another list item",
            ],
        )

    def test_markdown_to_blocks_excessive_newlines(self):
        md = """


# Heading



Paragraph with lots of space before and after




Another paragraph


"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "# Heading",
                "Paragraph with lots of space before and after",
                "Another paragraph",
            ],
        )

    def test_markdown_to_blocks_single_block(self):
        md = "Just a single block of text."
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["Just a single block of text."])

    def test_markdown_to_blocks_empty_string(self):
        blocks = markdown_to_blocks("")
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_only_newlines_and_whitespace(self):
        md = "\n\n   \n\n\t\n\n\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_leading_and_trailing_spaces(self):
        md = "   Block 1 with leading spaces   \n\n   Block 2 with leading spaces   "
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "Block 1 with leading spaces",
                "Block 2 with leading spaces",
            ],
        )

    def test_markdown_to_blocks_code_block(self):
        md = """
```python
def hello():
    print("world")
```

A paragraph after code block.
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "```python\ndef hello():\n    print(\"world\")\n```",
                "A paragraph after code block.",
            ],
        )

    def test_markdown_to_blocks_ordered_list(self):
        md = """
1. First item
2. Second item
3. Third item

Paragraph following ordered list.
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "1. First item\n2. Second item\n3. Third item",
                "Paragraph following ordered list.",
            ],
        )


class TestBlockToBlockType(unittest.TestCase):
    def test_block_to_block_type_headings(self):
        self.assertEqual(block_to_block_type("# Heading 1"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## Heading 2"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("### Heading 3"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("#### Heading 4"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("##### Heading 5"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### Heading 6"), BlockType.HEADING)

    def test_block_to_block_type_heading_invalid(self):
        self.assertEqual(block_to_block_type("####### Heading 7"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("#Heading without space"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("#"), BlockType.PARAGRAPH)

    def test_block_to_block_type_code(self):
        code = "```\ncode block here\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_block_to_block_type_code_with_language(self):
        code = "```python\ndef hello():\n    return 'world'\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_block_to_block_type_code_empty_body(self):
        code = "```\n```"
        self.assertEqual(block_to_block_type(code), BlockType.CODE)

    def test_block_to_block_type_code_invalid(self):
        self.assertEqual(block_to_block_type("```code```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```\nunclosed code"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("unopened code\n```"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("```"), BlockType.PARAGRAPH)

    def test_block_to_block_type_quote_single_line(self):
        self.assertEqual(block_to_block_type("> This is a quote"), BlockType.QUOTE)
        self.assertEqual(block_to_block_type(">This is a quote without space"), BlockType.QUOTE)

    def test_block_to_block_type_quote_multiline(self):
        quote = "> Quote line 1\n> Quote line 2\n>Quote line 3"
        self.assertEqual(block_to_block_type(quote), BlockType.QUOTE)

    def test_block_to_block_type_quote_invalid(self):
        quote = "> Quote line 1\nMissing angle bracket"
        self.assertEqual(block_to_block_type(quote), BlockType.PARAGRAPH)

    def test_block_to_block_type_unordered_list_single(self):
        self.assertEqual(block_to_block_type("- Only one item"), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_multiline(self):
        ul = "- First item\n- Second item\n- Third item"
        self.assertEqual(block_to_block_type(ul), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_unordered_list_invalid(self):
        self.assertEqual(block_to_block_type("-Item without space"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("- Item 1\nNot a list item"), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_single(self):
        self.assertEqual(block_to_block_type("1. Only item"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_multiline(self):
        ol = "1. Item 1\n2. Item 2\n3. Item 3\n4. Item 4"
        self.assertEqual(block_to_block_type(ol), BlockType.ORDERED_LIST)

    def test_block_to_block_type_ordered_list_invalid_start(self):
        ol = "2. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(ol), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_invalid_increment(self):
        ol = "1. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(ol), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_invalid_format(self):
        self.assertEqual(block_to_block_type("1.Item without space"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1) Item with parenthesis"), BlockType.PARAGRAPH)
        self.assertEqual(block_to_block_type("1. Item 1\nItem 2"), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph(self):
        para = "This is a regular paragraph with some **bold** and _italic_ text."
        self.assertEqual(block_to_block_type(para), BlockType.PARAGRAPH)

    def test_block_to_block_type_paragraph_multiline(self):
        para = "This is a regular paragraph\nspanning across multiple lines\nwithout any block markers."
        self.assertEqual(block_to_block_type(para), BlockType.PARAGRAPH)



if __name__ == "__main__":
    unittest.main()
