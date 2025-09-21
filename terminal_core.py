# src/terminal_core.py
import os
import shlex
import shutil
from pathlib import Path
from typing import Optional
import psutil

class TerminalError(Exception):
    pass

class Terminal:

    def __init__(self, root_dir: Optional[str] = None):
        self.root = Path(root_dir or Path.cwd()).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.cwd = self.root

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            new = p.resolve()
        else:
            new = (self.cwd / p).resolve()
        # Prevent escaping root
        try:
            new.relative_to(self.root)
        except Exception:
            raise TerminalError(f"Path outside sandbox: {path}")
        return new

    def ls(self, path: str = ".") -> str:
        p = self._resolve_path(path)
        if not p.exists():
            raise TerminalError("No such file or directory")
        out = []
        for e in sorted(p.iterdir()):
            out.append(e.name + ("/" if e.is_dir() else ""))
        return "\n".join(out)

    def pwd(self) -> str:
        # return path relative to root with leading /
        rel = "/" if self.cwd == self.root else f"/{self.cwd.relative_to(self.root)}"
        return rel

    def cd(self, path: str) -> str:
        new = self._resolve_path(path)
        if not new.is_dir():
            raise TerminalError("Not a directory")
        self.cwd = new
        return self.pwd()

    def mkdir(self, path: str) -> str:
        p = self._resolve_path(path)
        p.mkdir(parents=True, exist_ok=True)
        return f"Created: {p.relative_to(self.root)}"

    def rm(self, path: str, recursive: bool = False) -> str:
        p = self._resolve_path(path)
        if not p.exists():
            raise TerminalError("No such file or directory")
        if p.is_dir():
            if recursive:
                shutil.rmtree(p)
                return f"Removed directory tree: {p.relative_to(self.root)}"
            else:
                p.rmdir()
                return f"Removed directory: {p.relative_to(self.root)}"
        else:
            p.unlink()
            return f"Removed file: {p.relative_to(self.root)}"

    def touch(self, path: str) -> str:
        p = self._resolve_path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch(exist_ok=True)
        return f"Touched: {p.relative_to(self.root)}"

    def cat(self, path: str) -> str:
        p = self._resolve_path(path)
        if not p.exists() or p.is_dir():
            raise TerminalError("No such file or file is a directory")
        return p.read_text()

    def mv(self, src: str, dst: str) -> str:
        s = self._resolve_path(src)
        d = self._resolve_path(dst)
        d_parent = d.parent
        d_parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(s), str(d))
        return f"Moved {s.relative_to(self.root)} -> {d.relative_to(self.root)}"

    def cp(self, src: str, dst: str) -> str:
        s = self._resolve_path(src)
        d = self._resolve_path(dst)
        d_parent = d.parent
        d_parent.mkdir(parents=True, exist_ok=True)
        if s.is_dir():
            shutil.copytree(str(s), str(d))
        else:
            shutil.copy2(str(s), str(d))
        return f"Copied {s.relative_to(self.root)} -> {d.relative_to(self.root)}"

    def stat(self, path: str) -> str:
        p = self._resolve_path(path)
        if not p.exists():
            raise TerminalError("No such file or directory")
        st = p.stat()
        return (
            f"size: {st.st_size} bytes\n"
            f"mode: {oct(st.st_mode)}\n"
            f"mtime: {st.st_mtime}"
        )

    def sysinfo(self) -> str:
        vm = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        return f"CPU: {cpu}%\nMemory: {vm.percent}% ({vm.used // (1024**2)}MB used)"

    def ps(self, limit: int = 10) -> str:
        procs = []
        for p in psutil.process_iter(attrs=["pid", "name", "username", "cpu_percent", "memory_percent"]):
            info = p.info
            procs.append((info["cpu_percent"] or 0.0, info))
        procs.sort(reverse=True, key=lambda x: x[0])
        lines = []
        for cpu, info in procs[:limit]:
            lines.append(f"{info['pid']:>6} {info['name'][:25]:25} user={info['username'] or 'N/A'} cpu={cpu:.1f}% mem={info['memory_percent'] or 0:.1f}%")
        return "\n".join(lines)

    def run(self, cmdline: str) -> str:
        """Parse and execute a high-level command line."""
        tokens = shlex.split(cmdline)
        if not tokens:
            return ""
        cmd = tokens[0]
        args = tokens[1:]

        try:
            if cmd in ("ls", "dir"):
                return self.ls(args[0] if args else ".")
            if cmd == "pwd":
                return self.pwd()
            if cmd == "cd":
                return self.cd(args[0] if args else ".")
            if cmd == "mkdir":
                if not args:
                    raise TerminalError("mkdir: missing operand")
                return self.mkdir(args[0])
            if cmd in ("rm", "del"):
                if not args:
                    raise TerminalError("rm: missing operand")
                recursive = False
                if args[0] == "-r":
                    recursive = True
                    target = args[1] if len(args) > 1 else None
                else:
                    target = args[0]
                if not target:
                    raise TerminalError("rm: missing operand")
                return self.rm(target, recursive=recursive)
            if cmd == "touch":
                if not args:
                    raise TerminalError("touch: missing operand")
                return self.touch(args[0])
            if cmd == "cat":
                if not args:
                    raise TerminalError("cat: missing operand")
                return self.cat(args[0])
            if cmd == "mv":
                if len(args) < 2:
                    raise TerminalError("mv: missing operands")
                return self.mv(args[0], args[1])
            if cmd == "cp":
                if len(args) < 2:
                    raise TerminalError("cp: missing operands")
                return self.cp(args[0], args[1])
            if cmd == "stat":
                if not args:
                    raise TerminalError("stat: missing operand")
                return self.stat(args[0])
            if cmd == "sysinfo":
                return self.sysinfo()
            if cmd == "ps":
                n = int(args[0]) if args else 10
                return self.ps(limit=n)
            if cmd in ("help", "?"):
                return "Commands: ls pwd cd mkdir rm touch cat mv cp stat sysinfo ps help exit"
            if cmd in ("exit", "quit"):
                return "exit"
            # Default: unsupported
            raise TerminalError(f"Unsupported command: {cmd}")
        except TerminalError:
            raise
        except Exception as e:
            raise TerminalError(str(e))
