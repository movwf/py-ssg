import unittest
from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_eq(self):
        node = HTMLNode(
                "a",
                "Google",
                [],
                {
                    "href": "https://google.com",
                }
        )
        self.assertEqual(isinstance(node, HTMLNode), True)

    def test_props_parse(self):
        node = HTMLNode(
                "a",
                "Google",
                [],
                {
                    "href": "https://google.com",
                    "target": "_blank"
                }
        )
        self.assertNotEqual(node.props_to_html(), "")


    def test_debug(self):
        node = HTMLNode(
                "a",
                "Google",
                [
                    HTMLNode("img", "Test", [], { "src": "https://google.com/logo.webp" })
                ],
                {
                    "href": "https://google.com",
                    "target": "_blank"
                }
        )
        self.assertNotEqual(node, None)

    def test_parse_not_available(self):
        node = HTMLNode("h1", "Hello", [])

        with self.assertRaises(NotImplementedError):
            node.to_html()

if __name__ == "__main__":
    unittest.main()
