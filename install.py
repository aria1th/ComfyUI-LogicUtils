import launch
import pkg_resources

def get_installed_version(package: str):
    try:
        return pkg_resources.get_distribution(package).version
    except Exception:
        return None

def initialization():
    for pkg_name in ["chardet", "piexif"]:
        run_installation(pkg_name)

def run_installation(pkg_name: str):
    is_not_installed = get_installed_version(pkg_name) is None
    if not is_not_installed:
        return
    launch.run_pip(
        f'install -U "{pkg_name}"',
        f"Install {pkg_name}",
    )

initialization()
