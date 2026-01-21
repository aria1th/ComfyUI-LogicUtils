#https://github.com/ltdrdata/ComfyUI-Impact-Pack/blob/Main/install.py
import os
import sys
import subprocess
import threading
import locale

def handle_stream(stream, is_stdout):
    stream.reconfigure(encoding=locale.getpreferredencoding(), errors='replace')

    for msg in stream:
        if is_stdout:
            print(msg, end="", file=sys.stdout)
        else: 
            print(msg, end="", file=sys.stderr)

def process_wrap(cmd_str, cwd=None, handler=None):
    process = subprocess.Popen(cmd_str, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    if handler is None:
        handler = handle_stream

    stdout_thread = threading.Thread(target=handler, args=(process.stdout, True))
    stderr_thread = threading.Thread(target=handler, args=(process.stderr, False))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    return process.wait()

if "python_embeded" in sys.executable or "python_embedded" in sys.executable: #standalone python version
    pip_install = [sys.executable, '-s', '-m', 'pip', 'install', "-U", "--default-timeout=1000"]
else:
    pip_install = [sys.executable, '-m', 'pip', 'install', "-U", "--default-timeout=1000"]

def _imgutils_install_candidates() -> list[str]:
    """
    Decide which dghs-imgutils package variant to install first.

    - `dghs-imgutils[gpu]` includes optional GPU-related dependencies.
    - If GPU detection fails, default to CPU variant first.
    """
    variant = os.environ.get("COMFYUI_LOGICUTILS_IMGUTILS_VARIANT", "").strip().lower()
    if variant in {"gpu", "cuda"}:
        return ["dghs-imgutils[gpu]", "dghs-imgutils"]
    if variant in {"cpu"}:
        return ["dghs-imgutils", "dghs-imgutils[gpu]"]

    # auto
    try:
        import torch

        if getattr(torch, "cuda", None) is not None and torch.cuda.is_available():
            return ["dghs-imgutils[gpu]", "dghs-imgutils"]
    except Exception:
        pass
    return ["dghs-imgutils", "dghs-imgutils[gpu]"]

def initialization():
    try:
        import piexif
    except Exception:
        print("piexif not found, installing...")
        run_installation("piexif")
    try:
        import chardet
    except Exception:
        print("chardet not found, installing...")
        run_installation("chardet")
    try:
        from imgutils.tagging import get_wd14_tags
    except Exception:
        print("imgutils not found, installing...")
        for candidate in _imgutils_install_candidates():
            print(f"Trying to install {candidate}...")
            run_installation(candidate)
            try:
                from imgutils.tagging import get_wd14_tags  # noqa: F401
                break
            except Exception:
                continue
    try:
        from Crypto.PublicKey import RSA
    except Exception:
        print("pycryptodome not found, installing...")
        run_installation("pycryptodome")

def run_installation(pkg_name: str):
    print(f"Installing {pkg_name}...")
    try:
        if process_wrap(pip_install + [pkg_name]) == 0:
            print(f"Successfully installed {pkg_name}")
        else:
            print(f"Failed to install {pkg_name}")
    except Exception as e:
        print(f"Failed to install {pkg_name}: {e}")

if __name__ == "__main__":
    initialization()
    print("Installation completed.")
