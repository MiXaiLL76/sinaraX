try:
    from .screens import SinaraX, sinaraX_version
except ImportError:
    from screens import SinaraX, sinaraX_version

import argparse


def main():
    config = argparse.ArgumentParser(prog="SinaraX")
    config.add_argument(
        "--version", action="version", version=f"%(prog)s: {sinaraX_version}"
    )
    app = SinaraX()
    app.config = config.parse_args()
    app.run()


if __name__ == "__main__":
    main()
