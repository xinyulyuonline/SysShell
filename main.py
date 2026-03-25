"""
main.py
-------
Entry point for SysShell.

Run with:
    python main.py
"""

from shell.app import SysShellApp


def main():
    app = SysShellApp()
    app.run()


if __name__ == "__main__":
    main()
