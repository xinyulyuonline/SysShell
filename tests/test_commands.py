"""
tests/test_commands.py
-----------------------
Unit tests for CommandHandler (no GUI required).
"""

import os
import sys
import tempfile
import unittest

# Allow running from repo root without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from shell.commands import CommandHandler


class TestCommandHandler(unittest.TestCase):
    def setUp(self):
        self.output = []
        self.cleared = False
        self.handler = CommandHandler(
            output_callback=self.output.append,
            clear_callback=self._on_clear,
        )

    def _on_clear(self):
        self.cleared = True

    # ------------------------------------------------------------------
    # echo
    # ------------------------------------------------------------------

    def test_echo(self):
        self.handler.run("echo hello world")
        self.assertEqual(self.output, ["hello world"])

    def test_echo_empty(self):
        self.handler.run("echo")
        self.assertEqual(self.output, [""])

    # ------------------------------------------------------------------
    # help
    # ------------------------------------------------------------------

    def test_help_lists_builtins(self):
        self.handler.run("help")
        self.assertEqual(len(self.output), 1)
        for cmd in ("help", "echo", "clear", "exit", "ls", "cd", "cat"):
            self.assertIn(cmd, self.output[0])

    # ------------------------------------------------------------------
    # clear
    # ------------------------------------------------------------------

    def test_clear(self):
        self.handler.run("clear")
        self.assertTrue(self.cleared)

    # ------------------------------------------------------------------
    # ls
    # ------------------------------------------------------------------

    def test_ls_lists_files(self):
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "a.txt"), "w"):
                pass
            with open(os.path.join(d, "b.txt"), "w"):
                pass
            self.handler.run(f"ls {d}")
        self.assertIn("a.txt", self.output[0])
        self.assertIn("b.txt", self.output[0])

    def test_ls_empty_dir(self):
        with tempfile.TemporaryDirectory() as d:
            self.handler.run(f"ls {d}")
        self.assertEqual(self.output, ["(empty)"])

    def test_ls_invalid_path(self):
        self.handler.run("ls /nonexistent_path_xyz_abc")
        self.assertTrue(self.output[0].startswith("ls:"))

    # ------------------------------------------------------------------
    # cd
    # ------------------------------------------------------------------

    def test_cd_changes_cwd(self):
        original = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as d:
                self.handler.run(f"cd {d}")
                self.assertEqual(self.handler.cwd, os.path.realpath(d))
        finally:
            os.chdir(original)

    def test_cd_invalid_path(self):
        self.handler.run("cd /nonexistent_path_xyz_abc")
        self.assertTrue(self.output[0].startswith("cd:"))

    # ------------------------------------------------------------------
    # cat
    # ------------------------------------------------------------------

    def test_cat_reads_file(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as fh:
            fh.write("hello")
            name = fh.name
        try:
            self.handler.run(f"cat {name}")
            self.assertEqual(self.output, ["hello"])
        finally:
            os.unlink(name)

    def test_cat_missing_operand(self):
        self.handler.run("cat")
        self.assertTrue(self.output[0].startswith("cat:"))

    def test_cat_invalid_path(self):
        self.handler.run("cat /nonexistent_path_xyz_abc.txt")
        self.assertTrue(self.output[0].startswith("cat:"))

    # ------------------------------------------------------------------
    # exit
    # ------------------------------------------------------------------

    def test_exit_raises_system_exit(self):
        with self.assertRaises(SystemExit):
            self.handler.run("exit")

    # ------------------------------------------------------------------
    # system command fallback
    # ------------------------------------------------------------------

    def test_unknown_command_not_found(self):
        self.handler.run("__not_a_real_cmd_xyz__")
        self.assertIn("command not found", self.output[0])

    # ------------------------------------------------------------------
    # register
    # ------------------------------------------------------------------

    def test_register_custom_command(self):
        def _my_cmd(args):
            self.output.append("custom:" + " ".join(args))

        self.handler.register("mycmd", _my_cmd)
        self.handler.run("mycmd foo bar")
        self.assertEqual(self.output, ["custom:foo bar"])

    def test_register_overrides_builtin(self):
        self.handler.register("echo", lambda args: self.output.append("overridden"))
        self.handler.run("echo hello")
        self.assertEqual(self.output, ["overridden"])

    # ------------------------------------------------------------------
    # empty line
    # ------------------------------------------------------------------

    def test_empty_line_does_nothing(self):
        self.handler.run("   ")
        self.assertEqual(self.output, [])
        self.assertFalse(self.cleared)


if __name__ == "__main__":
    unittest.main()
