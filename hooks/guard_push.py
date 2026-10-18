#!/usr/bin/env python3
"""ai-sdlc PreToolUse hook for Bash: block risky `git push` commands.

Blocks a push that (a) forces (--force, -f, --force-with-lease, --mirror,
+refspec), (b) names a protected branch as a destination (or pushes every
branch with --all/--branches), or (c) has no refspec, or a refspec the shell
has not expanded yet ($VAR, $(...), `...`), while the current branch is
protected. Any unexpected input or error -> allow (exit 0).
"""
import json
import os
import re
import shlex
import subprocess
import sys

PROTECTED = {"main", "master", "develop", "development", "staging", "trunk", "mainline",
             "integration"}
SEPARATORS = {";", "&&", "||", "|", "&", "|&", "(", ")", ";;"}
PUNCT = "();<>|&"
OPERATORS = {"&&", "||", "|&", ";;", ">>", "<<", ">&", "<&", "&>"}
GIT_OPTS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}
PUSH_OPTS_WITH_VALUE = {"-o", "--push-option", "--repo", "--receive-pack", "--exec"}
SHELLS = {"sh", "bash", "zsh", "dash", "fish"}
PREFIXES = {"sudo", "doas", "env", "command", "exec", "time", "nohup", "nice", "xargs",
            "if", "then", "else", "elif", "do", "while", "until", "!", "{"}


def is_protected(branch):
    branch = re.sub(r"^refs/heads/", "", branch.strip())
    return branch in PROTECTED or branch.startswith("release/")


def split_punct(token):
    """shlex glues adjacent punctuation (`);`, `))`); split it back into shell operators."""
    if not token or token.strip(PUNCT):
        return [token]
    pieces, i = [], 0
    while i < len(token):
        size = 2 if token[i:i + 2] in OPERATORS else 1
        pieces.append(token[i:i + size])
        i += size
    return pieces


def segments(command):
    """Yield each simple command's tokens. A `$(...)` (or backtick) body is its own
    command, and the outer command keeps its `$` token and resumes after the `)`."""
    command = re.sub(r"`([^`]*)`", r"$(\1)", command.replace("\n", " ; "))
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        tokens = [piece for token in lexer for piece in split_punct(token)]
    except ValueError:
        tokens = []
        for part in re.split(r"[;&|()]+", command):
            tokens.extend(part.split() + [";"])
    stack, current = [], []
    for token in tokens:
        if token == "(" and current and current[-1].endswith("$"):
            stack.append(current)
            current = []
            continue
        if token == "(":
            stack.append(None)
        elif token == ")" and stack:
            if current:
                yield current
            current = stack.pop() or []
            continue
        if token in SEPARATORS:
            if current:
                yield current
            current = []
        else:
            current.append(token)
    for rest in [current] + stack[::-1]:
        if rest:
            yield rest


def git_index(tokens):
    """Index of `git` in command position (after env vars, sudo, if, ...), else None."""
    for i, token in enumerate(tokens):
        if os.path.basename(token) == "git":
            return i
        if not (token in PREFIXES or token.startswith("-") or re.match(r"^\w+=", token)):
            return None
    return None


def parse_push(tokens):
    """Return (git_dir, push_args) if tokens hold a `git ... push` call, else None."""
    i = git_index(tokens)
    if i is not None:
        git_dir, j = None, i + 1
        while j < len(tokens) and tokens[j].startswith("-"):
            opt = tokens[j]
            if opt in GIT_OPTS_WITH_VALUE and j + 1 < len(tokens):
                if opt == "-C":
                    git_dir = tokens[j + 1] if git_dir is None else os.path.join(git_dir, tokens[j + 1])
                j += 2
            else:
                j += 1
        if j < len(tokens) and tokens[j] == "push":
            return git_dir, tokens[j + 1:]
    return None


def current_branch(cwd):
    try:
        out = subprocess.run(
            ["git", "branch", "--show-current"], cwd=cwd, capture_output=True,
            text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def check_push(args, cwd):
    positionals, tags_only, skip = [], False, False
    for k, arg in enumerate(args):
        if skip:
            skip = False
            continue
        if arg == "--":
            positionals.extend(args[k + 1:])
            break
        if arg.startswith("--"):
            name = arg.split("=", 1)[0]
            if name.startswith("--force") or name == "--mirror":
                return "it forces ({})".format(arg)
            if name in ("--all", "--branches"):
                return "{} pushes every branch, protected ones included".format(arg)
            if name == "--tags":
                tags_only = True
            if name in PUSH_OPTS_WITH_VALUE and "=" not in arg:
                skip = True
            continue
        if arg.startswith("-") and len(arg) > 1:
            if "f" in arg[1:]:
                return "it forces ({})".format(arg)
            if arg[-1] == "o":
                skip = True
            continue
        positionals.append(arg)

    refspecs = positionals[1:]
    for spec in refspecs:
        if spec.startswith("+"):
            return "refspec {} forces".format(spec)
        dest = spec.split(":", 1)[1] if ":" in spec else spec
        if "$" in dest or "`" in dest:
            branch = current_branch(cwd)
            if branch and is_protected(branch):
                return ("refspec {} is not expanded yet and the current branch '{}' "
                        "is protected".format(spec, branch))
            continue
        if dest in ("HEAD", "@", ""):
            dest = current_branch(cwd) if dest else ""
        if dest and is_protected(dest):
            return "it targets protected branch '{}'".format(dest)
    if not refspecs and not tags_only:
        branch = current_branch(cwd)
        if branch and is_protected(branch):
            return "no refspec given and the current branch '{}' is protected".format(branch)
    return None


def check_command(command, cwd, depth=0):
    """Return (push_args, reason) for the first blocked push in command, else None."""
    for tokens in segments(command):
        for k, token in enumerate(tokens[:-2]):
            if depth < 2 and os.path.basename(token) in SHELLS and tokens[k + 1] == "-c":
                nested = check_command(tokens[k + 2], cwd, depth + 1)
                if nested:
                    return nested
        found = parse_push(tokens)
        if not found:
            continue
        git_dir, args = found
        run_dir = os.path.join(cwd, os.path.expanduser(git_dir)) if git_dir else cwd
        reason = check_push(args, run_dir)
        if reason:
            return args, reason
    return None


def main():
    data = json.load(sys.stdin)
    command = (data.get("tool_input") or {}).get("command")
    if not isinstance(command, str) or "push" not in command:
        return 0
    cwd = data.get("cwd") or os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    blocked = check_command(command, cwd)
    if not blocked:
        return 0
    args, reason = blocked
    sys.stderr.write(
        "Blocked by ai-sdlc guard_push: `{}` — {}. Agents never force-push and "
        "never push protected branches (main, master, develop, development, "
        "staging, trunk, mainline, integration, release/*); /ship pushes feature "
        "branches only. Push to a feature branch instead, or run this push "
        "yourself in a terminal if you really intend it.\n".format(" ".join(["git push"] + args), reason)
    )
    return 2


if __name__ == "__main__":
    try:
        code = main()
    except Exception:
        code = 0
    sys.exit(code)
