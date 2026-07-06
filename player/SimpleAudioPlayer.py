import sys

from app import SimpleAudioPlayerApp


def main():
    initial_paths = [arg for arg in sys.argv[1:] if arg]
    app = SimpleAudioPlayerApp(False, initial_paths=initial_paths)
    app.MainLoop()


if __name__ == "__main__":
    main()
