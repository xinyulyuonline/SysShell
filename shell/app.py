"""
shell/app.py
------------
Tkinter GUI for SysShell.

The window is split into two areas:
* A read-only scrollable Text widget that shows all output.
* A bottom bar with a coloured prompt label and an Entry widget for input.

Pressing <Return> submits the current line to CommandHandler.run().
"""

import tkinter as tk

from .commands import CommandHandler

# ── Visual theme ──────────────────────────────────────────────────────────────
_FONT = ("Courier", 12)
_BG = "#1e1e1e"
_FG = "#d4d4d4"
_PROMPT_COLOR = "#4ec9b0"
_CURSOR_COLOR = "#ffffff"


class SysShellApp:
    """Main application window."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SysShell")
        self.root.configure(bg=_BG)
        self.root.geometry("800x500")

        self._build_ui()
        self.handler = CommandHandler(
            output_callback=self._write,
            clear_callback=self._clear,
        )
        self._update_prompt()
        self._write("Welcome to SysShell. Type 'help' for available commands.")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # Scrollable output area
        self._output_text = tk.Text(
            self.root,
            bg=_BG,
            fg=_FG,
            font=_FONT,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            insertbackground=_CURSOR_COLOR,
            padx=6,
            pady=4,
        )
        scrollbar = tk.Scrollbar(self.root, command=self._output_text.yview)
        self._output_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._output_text.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Input bar
        input_frame = tk.Frame(self.root, bg=_BG)
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=4)

        self._prompt_label = tk.Label(
            input_frame,
            text="$ ",
            bg=_BG,
            fg=_PROMPT_COLOR,
            font=_FONT,
        )
        self._prompt_label.pack(side=tk.LEFT)

        self._entry = tk.Entry(
            input_frame,
            bg=_BG,
            fg=_FG,
            font=_FONT,
            relief=tk.FLAT,
            insertbackground=_CURSOR_COLOR,
        )
        self._entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._entry.bind("<Return>", self._on_enter)
        self._entry.focus_set()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _write(self, text):
        """Append *text* followed by a newline to the output area."""
        self._output_text.configure(state=tk.NORMAL)
        self._output_text.insert(tk.END, text + "\n")
        self._output_text.configure(state=tk.DISABLED)
        self._output_text.see(tk.END)

    def _clear(self):
        """Erase all output."""
        self._output_text.configure(state=tk.NORMAL)
        self._output_text.delete("1.0", tk.END)
        self._output_text.configure(state=tk.DISABLED)

    def _prompt_text(self):
        """Return the prompt string for the current working directory."""
        return f"{self.handler.cwd} $ "

    def _update_prompt(self):
        """Refresh the prompt label to show the current working directory."""
        self._prompt_label.configure(text=self._prompt_text())

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_enter(self, _event=None):
        line = self._entry.get().strip()
        self._entry.delete(0, tk.END)
        if not line:
            return
        # Echo the command in the output area
        self._write(f"{self._prompt_text()}{line}")
        try:
            self.handler.run(line)
        except SystemExit:
            self.root.destroy()
            return
        self._update_prompt()

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self):
        """Start the Tkinter event loop."""
        self.root.mainloop()
