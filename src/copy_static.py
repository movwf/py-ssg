import os
import shutil

def copy_static_to_public(src: str = "static", dst: str = "public") -> None:
    """Recursively copy all contents from ``src`` to ``dst``.

    The destination directory is completely removed first to guarantee a clean
    copy. Each file that is copied is printed so the operation can be followed
    in the console.
    """
    # Remove destination if it exists
    if os.path.exists(dst):
        print(f"Removing existing destination: {dst}")
        shutil.rmtree(dst)
    # Re‑create destination directory
    os.makedirs(dst, exist_ok=True)
    def _copy_recursive(current_src: str, current_dst: str):
        for entry in os.listdir(current_src):
            src_path = os.path.join(current_src, entry)
            dst_path = os.path.join(current_dst, entry)
            if os.path.isfile(src_path):
                print(f"Copying file: {src_path} -> {dst_path}")
                shutil.copy2(src_path, dst_path)
            elif os.path.isdir(src_path):
                print(f"Creating directory: {dst_path}")
                os.makedirs(dst_path, exist_ok=True)
                _copy_recursive(src_path, dst_path)
    _copy_recursive(src, dst)
    print("Static assets have been copied to public.")
