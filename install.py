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
    pip_install = [sys.executable, '-s', '-m', 'pip', 'install', "-U"]
else:
    pip_install = [sys.executable, '-m', 'pip', 'install', "-U"]

def initialization():
    auto_install = os.environ.get("COMFYUI_LOGICUTILS_AUTO_INSTALL", "").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    if not auto_install:
        return

    try:
        import piexif
    except Exception:
        run_installation("piexif")
    try:
        import chardet
    except Exception:
        run_installation("chardet")
    try:
        from imgutils.tagging import get_wd14_tags
    except Exception:
        # dghs-imgutils currently pins numpy<2, which typically won't have wheels for
        # the latest Python releases right away (e.g. Python 3.13 in ComfyUI portable).
        if sys.version_info >= (3, 13):
            print(
                "Skipping auto-install of dghs-imgutils on Python >= 3.13 "
                "(tagger nodes will be disabled unless installed manually)."
            )
        else:
            run_installation("dghs-imgutils[gpu]")
    try:
        from Crypto.PublicKey import RSA
    except Exception:
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
