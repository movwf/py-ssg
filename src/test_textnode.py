import unittest
from textnode import TextNode, TextType, text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq(self):
        node = TextNode("This is a link node", TextType.LINK)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_type(self):
        node = TextNode("same", TextType.LINK)
        node2 = TextNode("same", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_url(self):
        node = TextNode("same", TextType.LINK, "https://")
        node2 = TextNode("same", TextType.LINK, None)
        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")
        self.assertEqual(html_node.to_html(), "This is a text node")

    def test_bold(self):
        node = TextNode("Bold content", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "Bold content")
        self.assertEqual(html_node.to_html(), "<b>Bold content</b>")

    def test_italic(self):
        node = TextNode("Italic content", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "Italic content")
        self.assertEqual(html_node.to_html(), "<i>Italic content</i>")

    def test_code(self):
        node = TextNode("code snippet", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "code")
        self.assertEqual(html_node.value, "code snippet")
        self.assertEqual(html_node.to_html(), "<code>code snippet</code>")

    def test_link(self):
        node = TextNode("Click here", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "a")
        self.assertEqual(html_node.value, "Click here")
        self.assertEqual(html_node.props, {"href": "https://www.boot.dev"})
        self.assertEqual(html_node.to_html(), '<a href="https://www.boot.dev">Click here</a>')

    def test_image(self):
        node = TextNode("Alt text", TextType.IMAGE, "https://www.boot.dev/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(
            html_node.props,
            {"src": "https://www.boot.dev/image.png", "alt": "Alt text"},
        )
        self.assertEqual(
            html_node.to_html(),
            '<img src="https://www.boot.dev/image.png" alt="Alt text"></img>',
        )

    def test_invalid_type(self):
        node = TextNode("Invalid text", "not_a_type")
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)


if __name__ == "__main__":
    unittest.main()
