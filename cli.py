# src/cli.py
import readline
from terminal_core import Terminal, TerminalError
import os

# enable simple history file
HISTFILE = os.path.expanduser("~/.codemate_terminal_history")
try:
    readline.read_history_file(HISTFILE)
except FileNotFoundError:
    pass

def save_history():
    try:
        readline.write_history_file(HISTFILE)
    except Exception:
        pass

def completer(text, state):
    # basic completion: commands + files in cwd
    commands = ["ls","pwd","cd","mkdir","rm","touch","cat","mv","cp","stat","sysinfo","ps","help","exit"]
    options = [c for c in commands if c.startswith(text)]
    try:
        return options[state]
    except IndexError:
        return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

def main():
    term = Terminal(root_dir="sandbox")
    print("CodeMate Terminal - type 'help' for commands. 'exit' to quit.")
    try:
        while True:
            try:
                prompt = f"{term.pwd()}> "
                line = input(prompt)
                if not line.strip():
                    continue
                out = term.run(line)
                if out == "exit":
                    break
                print(out)
            except TerminalError as e:
                print("Error:", e)
            except KeyboardInterrupt:
                print("")  # newline
    finally:
        save_history()

if __name__ == "__main__":
    main()