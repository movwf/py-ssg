import unittest
from textnode import TextNode, TextType
from inline_markdown import (
    split_nodes_delimiter,
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_image,
    split_nodes_link,
    text_to_textnodes,
)


class TestSplitNodesDelimiter(unittest.TestCase):
    def test_delim_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_bold(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_italic(self):
        node = TextNode("This is *italic* text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_italic_underscore(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_multiple_same_delimiters(self):
        node = TextNode(
            "Here is `code1` and also `code2` inline", TextType.TEXT
        )
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("code1", TextType.CODE),
            TextNode(" and also ", TextType.TEXT),
            TextNode("code2", TextType.CODE),
            TextNode(" inline", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_at_start(self):
        node = TextNode("`code` at the beginning", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("code", TextType.CODE),
            TextNode(" at the beginning", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_at_end(self):
        node = TextNode("At the end `code`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("At the end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_exact_match(self):
        node = TextNode("**bold text only**", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        expected = [
            TextNode("bold text only", TextType.BOLD),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_consecutive(self):
        node = TextNode("`first``second`", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("first", TextType.CODE),
            TextNode("second", TextType.CODE),
        ]
        self.assertEqual(new_nodes, expected)

    def test_delim_no_delimiters(self):
        node = TextNode("Just plain text with no delimiters", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        expected = [
            TextNode("Just plain text with no delimiters", TextType.TEXT),
        ]
        self.assertEqual(new_nodes, expected)

    def test_preserve_non_text_nodes(self):
        node1 = TextNode("already bold", TextType.BOLD)
        node2 = TextNode("text with `code` block", TextType.TEXT)
        node3 = TextNode("already link", TextType.LINK, "https://boot.dev")
        new_nodes = split_nodes_delimiter([node1, node2, node3], "`", TextType.CODE)
        expected = [
            TextNode("already bold", TextType.BOLD),
            TextNode("text with ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" block", TextType.TEXT),
            TextNode("already link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(new_nodes, expected)

    def test_chaining_delimiters(self):
        node = TextNode(
            "This has **bold** and *italic* and `code` in it", TextType.TEXT
        )
        nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
        nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" in it", TextType.TEXT),
        ]
        self.assertEqual(nodes, expected)

    def test_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes, [])

    def test_empty_list(self):
        new_nodes = split_nodes_delimiter([], "`", TextType.CODE)
        self.assertEqual(new_nodes, [])

    def test_unclosed_delimiter_raises_exception(self):
        node = TextNode("Invalid `code block syntax", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "`", TextType.CODE)

    def test_unclosed_delimiter_bold_raises_exception(self):
        node = TextNode("Invalid **bold syntax text", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_unclosed_delimiter_among_multiple_nodes(self):
        node1 = TextNode("Valid text", TextType.TEXT)
        node2 = TextNode("Invalid *italic syntax", TextType.TEXT)
        with self.assertRaises(ValueError):
            split_nodes_delimiter([node1, node2], "*", TextType.ITALIC)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        matches = extract_markdown_images(text)
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_extract_markdown_images_no_images(self):
        text = "This is text with no images at all."
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_images_with_links(self):
        text = "This text has a link [to boot dev](https://www.boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_empty_alt(self):
        text = "This is an image with empty alt: ![](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_empty_string(self):
        matches = extract_markdown_images("")
        self.assertListEqual([], matches)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_extract_markdown_links_multiple(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        matches = extract_markdown_links(text)
        self.assertListEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            matches,
        )

    def test_extract_markdown_links_no_links(self):
        text = "This is text with no links at all."
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)

    def test_extract_markdown_links_ignores_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and a [link](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "https://www.boot.dev")], matches)

    def test_extract_markdown_links_empty_anchor(self):
        text = "This is a link with empty text: [](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("", "https://www.boot.dev")], matches)

    def test_extract_markdown_links_empty_string(self):
        matches = extract_markdown_links("")
        self.assertListEqual([], matches)

    def test_extract_markdown_links_exclamation_in_text(self):
        text = "Wow! Check out [Boot.dev](https://boot.dev)!"
        matches = extract_markdown_links(text)
        self.assertListEqual([("Boot.dev", "https://boot.dev")], matches)


class TestSplitNodesImage(unittest.TestCase):
    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_image_single(self):
        node = TextNode(
            "Hello ![world](https://example.com/world.png) here",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("world", TextType.IMAGE, "https://example.com/world.png"),
                TextNode(" here", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_image_at_start(self):
        node = TextNode(
            "![start](https://example.com/start.png) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("start", TextType.IMAGE, "https://example.com/start.png"),
                TextNode(" text after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_image_at_end(self):
        node = TextNode(
            "text before ![end](https://example.com/end.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("text before ", TextType.TEXT),
                TextNode("end", TextType.IMAGE, "https://example.com/end.png"),
            ],
            new_nodes,
        )

    def test_split_image_only(self):
        node = TextNode(
            "![only](https://example.com/only.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("only", TextType.IMAGE, "https://example.com/only.png"),
            ],
            new_nodes,
        )

    def test_split_images_consecutive(self):
        node = TextNode(
            "![first](https://example.com/1.png)![second](https://example.com/2.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.IMAGE, "https://example.com/1.png"),
                TextNode("second", TextType.IMAGE, "https://example.com/2.png"),
            ],
            new_nodes,
        )

    def test_split_images_multiple_identical(self):
        node = TextNode(
            "![same](https://example.com/same.png) and ![same](https://example.com/same.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("same", TextType.IMAGE, "https://example.com/same.png"),
                TextNode(" and ", TextType.TEXT),
                TextNode("same", TextType.IMAGE, "https://example.com/same.png"),
            ],
            new_nodes,
        )

    def test_split_images_no_images(self):
        node = TextNode("Plain text with no images", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Plain text with no images", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_images_with_link_unaffected(self):
        node = TextNode(
            "This has a [link](https://boot.dev) but no image",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This has a [link](https://boot.dev) but no image", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_images_empty_alt(self):
        node = TextNode(
            "Text with ![](https://example.com/empty.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("Text with ", TextType.TEXT),
                TextNode("", TextType.IMAGE, "https://example.com/empty.png"),
            ],
            new_nodes,
        )

    def test_split_images_empty_list(self):
        new_nodes = split_nodes_image([])
        self.assertListEqual([], new_nodes)

    def test_split_images_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_image([node])
        self.assertListEqual([TextNode("", TextType.TEXT)], new_nodes)

    def test_split_images_preserve_non_text_nodes(self):
        node1 = TextNode("bold text", TextType.BOLD)
        node2 = TextNode("This is an ![img](https://example.com/img.png)", TextType.TEXT)
        node3 = TextNode("code block", TextType.CODE)
        new_nodes = split_nodes_image([node1, node2, node3])
        self.assertListEqual(
            [
                TextNode("bold text", TextType.BOLD),
                TextNode("This is an ", TextType.TEXT),
                TextNode("img", TextType.IMAGE, "https://example.com/img.png"),
                TextNode("code block", TextType.CODE),
            ],
            new_nodes,
        )

    def test_split_images_multiple_text_nodes(self):
        node1 = TextNode("Image one: ![one](https://example.com/1.png)", TextType.TEXT)
        node2 = TextNode("Image two: ![two](https://example.com/2.png)", TextType.TEXT)
        new_nodes = split_nodes_image([node1, node2])
        self.assertListEqual(
            [
                TextNode("Image one: ", TextType.TEXT),
                TextNode("one", TextType.IMAGE, "https://example.com/1.png"),
                TextNode("Image two: ", TextType.TEXT),
                TextNode("two", TextType.IMAGE, "https://example.com/2.png"),
            ],
            new_nodes,
        )


class TestSplitNodesLink(unittest.TestCase):
    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_link_single(self):
        node = TextNode(
            "Hello [world](https://example.com) here",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("world", TextType.LINK, "https://example.com"),
                TextNode(" here", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_link_at_start(self):
        node = TextNode(
            "[start](https://example.com/start) text after",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("start", TextType.LINK, "https://example.com/start"),
                TextNode(" text after", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_link_at_end(self):
        node = TextNode(
            "text before [end](https://example.com/end)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("text before ", TextType.TEXT),
                TextNode("end", TextType.LINK, "https://example.com/end"),
            ],
            new_nodes,
        )

    def test_split_link_only(self):
        node = TextNode(
            "[only](https://example.com/only)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("only", TextType.LINK, "https://example.com/only"),
            ],
            new_nodes,
        )

    def test_split_links_consecutive(self):
        node = TextNode(
            "[first](https://example.com/1)[second](https://example.com/2)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("first", TextType.LINK, "https://example.com/1"),
                TextNode("second", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )

    def test_split_links_multiple_same(self):
        node = TextNode(
            "[same](https://example.com) and [same](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("same", TextType.LINK, "https://example.com"),
                TextNode(" and ", TextType.TEXT),
                TextNode("same", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_links_no_links(self):
        node = TextNode("Plain text with no links", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Plain text with no links", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_links_ignores_images(self):
        node = TextNode(
            "This is an ![image](https://example.com/img.png) and a [link](https://boot.dev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is an ![image](https://example.com/img.png) and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            new_nodes,
        )

    def test_split_links_empty_anchor(self):
        node = TextNode(
            "Text with [](https://example.com)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("Text with ", TextType.TEXT),
                TextNode("", TextType.LINK, "https://example.com"),
            ],
            new_nodes,
        )

    def test_split_links_empty_list(self):
        new_nodes = split_nodes_link([])
        self.assertListEqual([], new_nodes)

    def test_split_links_empty_text_node(self):
        node = TextNode("", TextType.TEXT)
        new_nodes = split_nodes_link([node])
        self.assertListEqual([TextNode("", TextType.TEXT)], new_nodes)

    def test_split_links_preserve_non_text_nodes(self):
        node1 = TextNode("bold text", TextType.BOLD)
        node2 = TextNode("This is a [link](https://boot.dev)", TextType.TEXT)
        node3 = TextNode("image", TextType.IMAGE, "https://example.com/img.png")
        new_nodes = split_nodes_link([node1, node2, node3])
        self.assertListEqual(
            [
                TextNode("bold text", TextType.BOLD),
                TextNode("This is a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
                TextNode("image", TextType.IMAGE, "https://example.com/img.png"),
            ],
            new_nodes,
        )

    def test_split_links_multiple_text_nodes(self):
        node1 = TextNode("Link one: [one](https://example.com/1)", TextType.TEXT)
        node2 = TextNode("Link two: [two](https://example.com/2)", TextType.TEXT)
        new_nodes = split_nodes_link([node1, node2])
        self.assertListEqual(
            [
                TextNode("Link one: ", TextType.TEXT),
                TextNode("one", TextType.LINK, "https://example.com/1"),
                TextNode("Link two: ", TextType.TEXT),
                TextNode("two", TextType.LINK, "https://example.com/2"),
            ],
            new_nodes,
        )


class TestSplitNodesChaining(unittest.TestCase):
    def test_split_image_and_link(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and a [link](https://boot.dev)",
            TextType.TEXT,
        )
        nodes = split_nodes_image([node])
        nodes = split_nodes_link(nodes)
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            nodes,
        )

    def test_split_multiple_images_and_links(self):
        node = TextNode(
            "Start ![img1](https://example.com/1.png) middle [link1](https://example.com/1) then ![img2](https://example.com/2.png) end [link2](https://example.com/2)",
            TextType.TEXT,
        )
        nodes = split_nodes_image([node])
        nodes = split_nodes_link(nodes)
        self.assertListEqual(
            [
                TextNode("Start ", TextType.TEXT),
                TextNode("img1", TextType.IMAGE, "https://example.com/1.png"),
                TextNode(" middle ", TextType.TEXT),
                TextNode("link1", TextType.LINK, "https://example.com/1"),
                TextNode(" then ", TextType.TEXT),
                TextNode("img2", TextType.IMAGE, "https://example.com/2.png"),
                TextNode(" end ", TextType.TEXT),
                TextNode("link2", TextType.LINK, "https://example.com/2"),
            ],
            nodes,
        )


class TestTextToTextNodes(unittest.TestCase):
    def test_text_to_textnodes_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_star_italic(self):
        text = "This has *star italic* and **bold text** with `some code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This has ", TextType.TEXT),
            TextNode("star italic", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold text", TextType.BOLD),
            TextNode(" with ", TextType.TEXT),
            TextNode("some code", TextType.CODE),
        ]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_both_italics(self):
        text = "Text with *asterisk* and _underscore_ italics"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Text with ", TextType.TEXT),
            TextNode("asterisk", TextType.ITALIC),
            TextNode(" and ", TextType.TEXT),
            TextNode("underscore", TextType.ITALIC),
            TextNode(" italics", TextType.TEXT),
        ]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_plain_text(self):
        text = "Just plain text without any formatting."
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just plain text without any formatting.", TextType.TEXT)]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_empty(self):
        nodes = text_to_textnodes("")
        self.assertListEqual(nodes, [])

    def test_text_to_textnodes_bold_only(self):
        text = "**bold only**"
        nodes = text_to_textnodes(text)
        expected = [TextNode("bold only", TextType.BOLD)]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_code_only(self):
        text = "`code only`"
        nodes = text_to_textnodes(text)
        expected = [TextNode("code only", TextType.CODE)]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_image_only(self):
        text = "![image](https://example.com/pic.png)"
        nodes = text_to_textnodes(text)
        expected = [TextNode("image", TextType.IMAGE, "https://example.com/pic.png")]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_link_only(self):
        text = "[link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [TextNode("link", TextType.LINK, "https://boot.dev")]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_consecutive_formatting(self):
        text = "**bold**_italic_`code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC),
            TextNode("code", TextType.CODE),
        ]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_urls_with_underscores(self):
        text = "Check ![my_image](https://example.com/pic_1.png) and [my_link](https://example.com/path_1)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Check ", TextType.TEXT),
            TextNode("my_image", TextType.IMAGE, "https://example.com/pic_1.png"),
            TextNode(" and ", TextType.TEXT),
            TextNode("my_link", TextType.LINK, "https://example.com/path_1"),
        ]
        self.assertListEqual(nodes, expected)

    def test_text_to_textnodes_multiple_same_delimiters(self):
        text = "Here is **bold1** and **bold2** with `code1` and `code2`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Here is ", TextType.TEXT),
            TextNode("bold1", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("bold2", TextType.BOLD),
            TextNode(" with ", TextType.TEXT),
            TextNode("code1", TextType.CODE),
            TextNode(" and ", TextType.TEXT),
            TextNode("code2", TextType.CODE),
        ]
        self.assertListEqual(nodes, expected)




if __name__ == "__main__":
    unittest.main()
