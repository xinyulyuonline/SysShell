"""
shell/commands.py
-----------------
Command registry and all built-in command implementations for SysShell.

Built-in commands: help, echo, clear, exit, ls, cd, cat
Any unrecognised command is forwarded to the operating system via subprocess.

Usage
-----
handler = CommandHandler(
    output_callback=lambda text: print(text),
    clear_callback=lambda: print("\\033[2J"),
)
handler.run("echo hello world")
handler.register("mycommand", lambda args: ...)
"""

import os
import subprocess


class CommandHandler:
    """Parses and dispatches shell commands.

    Parameters
    ----------
    output_callback:
        Called with a ``str`` whenever a command produces output.
    clear_callback:
        Called (with no arguments) when the ``clear`` command runs.
    """

    def __init__(self, output_callback, clear_callback):
        self.cwd = os.path.expanduser("~")
        self._output = output_callback
        self._clear = clear_callback
        self._commands = {
            "help": self._cmd_help,
            "echo": self._cmd_echo,
            "clear": self._cmd_clear,
            "exit": self._cmd_exit,
            "ls": self._cmd_ls,
            "cd": self._cmd_cd,
            "cat": self._cmd_cat,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register(self, name, func):
        """Register a custom command.

        Parameters
        ----------
        name:
            The command keyword the user will type.
        func:
            Callable that accepts a ``list[str]`` of arguments.
        """
        self._commands[name] = func

    def run(self, line):
        """Parse *line* and execute the appropriate command."""
        parts = line.strip().split()
        if not parts:
            return
        cmd, args = parts[0], parts[1:]
        if cmd in self._commands:
            self._commands[cmd](args)
        else:
            self._run_system(cmd, args)

    # ------------------------------------------------------------------
    # Built-in commands
    # ------------------------------------------------------------------

    def _cmd_help(self, args):
        built_ins = ", ".join(sorted(self._commands.keys()))
        self._output(
            f"Built-in commands: {built_ins}\n"
            "Any other command is passed to the system shell."
        )

    def _cmd_echo(self, args):
        self._output(" ".join(args))

    def _cmd_clear(self, args):
        self._clear()

    def _cmd_exit(self, args):
        raise SystemExit(0)

    def _cmd_ls(self, args):
        path = args[0] if args else self.cwd
        try:
            entries = sorted(os.listdir(path))
            self._output("  ".join(entries) if entries else "(empty)")
        except OSError as exc:
            self._output(f"ls: {exc.strerror}: {path}")

    def _cmd_cd(self, args):
        target = args[0] if args else os.path.expanduser("~")
        try:
            os.chdir(target)
            self.cwd = os.getcwd()
        except OSError as exc:
            self._output(f"cd: {exc.strerror}: {target}")

    def _cmd_cat(self, args):
        if not args:
            self._output("cat: missing file operand")
            return
        for path in args:
            try:
                with open(path) as fh:
                    self._output(fh.read().rstrip())
            except OSError as exc:
                self._output(f"cat: {exc.strerror}: {path}")

    # ------------------------------------------------------------------
    # System command fallback
    # ------------------------------------------------------------------

    def _run_system(self, cmd, args):
        try:
            result = subprocess.run(
                [cmd] + args,
                capture_output=True,
                text=True,
                cwd=self.cwd,
            )
            if result.stdout:
                self._output(result.stdout.rstrip())
            if result.stderr:
                self._output(result.stderr.rstrip())
        except FileNotFoundError:
            self._output(f"{cmd}: command not found")
        except OSError as exc:
            self._output(f"{cmd}: {exc.strerror}")
