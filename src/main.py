from copy_static import copy_static_to_public
from generator import generate_pages_recursive

import sys

def main():
    basepath = "/"
    if len(sys.argv) >= 2:
        basepath = sys.argv[1]

    copy_static_to_public(
        "static", 
        "public",
    )
    generate_pages_recursive(
        "content", 
        "template.html", 
        "public",
    )


main()
