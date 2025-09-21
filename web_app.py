# src/web_app.py
from flask import Flask, request, render_template_string
from terminal_core import Terminal, TerminalError

app = Flask(__name__)
term = Terminal(root_dir="sandbox_web")

PAGE = """
<!doctype html>
<title>CodeMate Terminal (web)</title>
<h2>CodeMate Terminal (web)</h2>
<form method=post>
  <input name=cmd style="width:70%" autofocus placeholder="Type command like: ls, pwd, mkdir test">
  <input type=submit value="Run">
</form>
<pre>{{output}}</pre>
"""

@app.route("/", methods=["GET","POST"])
def index():
    out = ""
    if request.method == "POST":
        cmd = request.form.get("cmd","")
        try:
            out = term.run(cmd)
        except TerminalError as e:
            out = f"Error: {e}"
    return render_template_string(PAGE, output=out)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
