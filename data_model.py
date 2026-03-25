import os

class Terminal:
    def __init__(self):
        self.path = os.getcwd()
        self.commands = {"cd": self.cmd_cd, 
                         "ls": self.cmd_ls, 
                         "pwd": self.cmd_pwd, 
                         "clear": self.cmd_clear
                         }
        self.history = []

    def run_command(self, text) -> str:
        text = text.strip()
        if not text:
            return f""

        parts = text.split()
        name = parts[0].lower()
        args = parts[1:]

        command = self.commands.get(name)


        if command is None:
            return f"Unknown command: {name}"

        self.history.append(text)
        return command(args)
    
    def cmd_cd(self, args):
        """
        Wechselt in ein anderes Verzeichnis
        """
        if not args:
            return "Usage: cd <path>"

        path = args[0]

        if not os.path.isabs(path):
            path = os.path.join(self.path, path)

        new_path = os.path.abspath(path)

        if not os.path.exists(new_path):
            return f"Path not found: {new_path}"

        if not os.path.isdir(new_path):
            return f"Not a directory: {new_path}"

        os.chdir(new_path)
        self.path = os.getcwd()

        return f"Changed directory to: {self.path}"
    
    def cmd_ls(self, args):

        """
        Listet die Dateien und Verzeichnisse im aktuellen Verzeichnis auf
        """
        entries = os.listdir(self.path)
        ls = "\n".join(entries)
        if not ls:
            return "<empty>"
        return ls
    
    def cmd_pwd(self, args):
        """
        Zeigt den aktuellen Pfad an
        """
        return self.path
    
    def cmd_clear(self, args):
        """
        Löscht den Terminal-Bildschirm
        """
        self.history.clear()
        return ""