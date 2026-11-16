import os
from pathlib import Path

from utils import extract_title, TitleNotFoundError
from markdown_to_html_node import markdown_to_html_node

def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str = "/") -> None:
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    markdown_text = Path(from_path).read_text(encoding="utf-8")

    html_node = markdown_to_html_node(markdown_text)
    content_html = html_node.to_html()

    try:
        title = extract_title(markdown_text)
    except TitleNotFoundError as exc:
        raise RuntimeError(f"Cannot generate page – {exc}") from exc

    template = Path(template_path).read_text(encoding="utf-8")

    rendered = template.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

    rendered = rendered.replace("href=\"/", f"href=\"{basepath}")
    rendered = rendered.replace("src=\"/", f"src=\"{basepath}")

    dest_path_obj = Path(dest_path)
    dest_path_obj.parent.mkdir(parents=True, exist_ok=True)

    dest_path_obj.write_text(rendered, encoding="utf-8")

def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str = "/") -> None:
    """Recursively crawl ``dir_path_content`` and generate HTML pages for every
    Markdown file found.

    * ``dir_path_content`` – path to the source ``content`` directory.
    * ``template_path`` – path to the HTML template (containing ``{{ Title }}``
      and ``{{ Content }}``).
    * ``dest_dir_path`` – root of the generated site (e.g. ``public``).  The
      relative directory structure of the source files is preserved.
    """
    # Walk the directory tree
    for root, dirs, files in os.walk(dir_path_content):
        for fname in files:
            if not fname.lower().endswith('.md'):
                continue
            src_path = Path(root) / fname
            # Compute relative path from the content root
            rel_path = src_path.relative_to(dir_path_content)
            # Destination filename changes extension to .html
            dest_rel_path = rel_path.with_suffix('.html')
            dest_path = Path(dest_dir_path) / dest_rel_path
            generate_page(
                from_path=str(src_path),
                template_path=template_path,
                dest_path=str(dest_path),
                basepath=basepath,
            )