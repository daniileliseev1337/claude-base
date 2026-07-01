# rules.py
import re
import shlex

SAFE_TOOLS = {"Read", "Glob", "Grep", "WebSearch", "WebFetch", "TodoWrite",
              "TaskCreate", "TaskUpdate", "TaskList", "TaskGet", "NotebookRead"}
WRITE_TOOLS = {"Write", "Edit", "NotebookEdit"}

# опасное — эскалировать (никогда не тихий allow)
DENY_SUBSTR = ["rm -rf", "rm -fr", "mkfs", "dd if=", ":(){", "> /dev/sda"]
DENY_TOKENS = [("git", "push", "--force"), ("git", "push", "-f"),
               ("git", "reset", "--hard"), ("drop", "database"), ("drop", "table"),
               ("rm", "-r", "-f"), ("rm", "-f", "-r"), ("chmod", "777"), ("chmod", "-r", "777")]
WRAPPERS = {"bash", "sh", "zsh", "python", "python3", "node", "perl", "ruby", "eval",
            "powershell", "pwsh"}

def _analyze_bash(cmd: str) -> str:
    low = cmd.lower()
    for s in DENY_SUBSTR:
        if s in low:
            return "escalate"
    try:
        toks = [t.lower() for t in shlex.split(cmd)]
    except ValueError:
        return "escalate"  # неразбираемое — не рисковать
    # обёртки с -c/-e и пайп-в-шелл — не видим внутрь → эскалация
    if toks and toks[0] in WRAPPERS and any(t in ("-c", "-e", "-ce") for t in toks):
        return "escalate"
    # пайп-в-шелл: слово sh/bash/zsh целиком (\b), а не подстрока (не ловить push/ssh/share)
    if "|" in cmd and re.search(r"\b(?:sh|bash|zsh)\b", low):
        return "escalate"
    for combo in DENY_TOKENS:
        if all(t in toks for t in combo):
            return "escalate"
    return "allow"

def decide(tool_name: str, tool_input: dict) -> dict:
    if tool_name in SAFE_TOOLS:
        return {"action": "allow", "reason": "safe tool"}
    if tool_name in WRITE_TOOLS:
        return {"action": "allow", "reason": "file write (low risk)"}
    if tool_name == "Bash":
        a = _analyze_bash(str(tool_input.get("command", "")))
        return {"action": a, "reason": f"bash: {a}"}
    return {"action": "escalate", "reason": "unknown tool — no rule"}
