try:
    from .screens import SinaraX
except ImportError:
    from screens import SinaraX


def main():
    SinaraX().run()


if __name__ == "__main__":
    main()
