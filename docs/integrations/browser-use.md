# Using w2s skills with browser-use

[w2s](../../README.md) generates skills. [browser-use](https://github.com/browser-use/browser-use) is the agent that runs them. This document shows you how to plug the two together using browser-use's existing capabilities — no custom runner, no extra framework.

The short version: **a w2s skill is just markdown with a YAML frontmatter. browser-use accepts a custom system prompt. You read the skill, pass it as the system prompt, and the agent uses it.** That's the whole integration.

---

## Installation

```bash
pip install browser-use
playwright install chromium
```

You also need an LLM. browser-use works with any LangChain-compatible chat model. Pick one:

```bash
# OpenAI
pip install langchain-openai
export OPENAI_API_KEY=sk-...

# Anthropic
pip install langchain-anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Google
pip install langchain-google-genai
export GOOGLE_API_KEY=...
```

---

## The 30-second version

You have a w2s skill at `~/.claude/skills/github.com/`. You want to use it with browser-use. The minimum viable code is:

```python
import asyncio
from pathlib import Path
from browser_use import Agent
from langchain_openai import ChatOpenAI

async def main():
    skill = Path("~/.claude/skills/github.com").expanduser().read_text()
    agent = Agent(
        task="Star the web2skill repo on GitHub",
        llm=ChatOpenAI(model="gpt-4o"),
        extend_system_message=skill,
    )
    result = await agent.run()
    print(result)

asyncio.run(main())
```

That's it. browser-use opens a real Chrome window (headed mode is the default for `Agent.run()`), reads the reference, and the agent uses the element refs from the skill instead of improvising.

---

## Loading a skill properly

The snippet above reads an entire skill directory as one blob. That works for small skills but breaks down for big ones (multi-route sites have several `SKILL.md` files plus an `overview.md`). You want to load only the **relevant** skill for the current task.

A skill directory looks like this:

```
github.com/
├── overview.md         # site map (load only as fallback)
├── repo.md             # matches /:owner/:repo
├── issues.md           # matches /:owner/:repo/issues/*
├── pulls.md            # matches /:owner/:repo/pull/:n
└── settings.md         # matches /:owner/:repo/settings/*
```

Each file has YAML frontmatter with a `match` field (URL patterns or regexes) and a `description` field. The pattern for using the right one is:

1. Read `overview.md` first. It describes the site at a high level.
2. Look at the user's task. Decide which route family is most relevant.
3. Read the matching `SKILL.md` and append it to the system prompt.
4. If unsure, include `overview.md` so the agent has at least the site map.

Here is a helper that does that:

```python
import re
from pathlib import Path
import yaml

def load_skill(skill_dir: str | Path, task: str) -> str:
    """
    Read a w2s skill directory and return a system-prompt-ready
    string containing the overview + the most relevant SKILL.md
    for the given task.
    """
    skill_dir = Path(skill_dir).expanduser()
    parts: list[str] = []

    # 1. Always include the overview if present
    overview = skill_dir / "overview.md"
    if overview.exists():
        parts.append(overview.read_text())

    # 2. Score each SKILL.md by how well it matches the task
    best_file = None
    best_score = 0
    for skill_file in skill_dir.glob("*.md"):
        if skill_file.name == "overview.md":
            continue
        text = skill_file.read_text()
        # Parse frontmatter
        match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not match:
            continue
        meta = yaml.safe_load(match.group(1))
        score = _score_skill(meta, task, text)
        if score > best_score:
            best_score = score
            best_file = skill_file

    # 3. Append the most relevant SKILL.md
    if best_file:
        parts.append(best_file.read_text())

    return "\n\n---\n\n".join(parts)

def _score_skill(meta: dict, task: str, text: str) -> int:
    """Score a skill by how relevant it is to the task."""
    score = 0
    description = (meta.get("description") or "").lower()
    task_lower = task.lower()
    # Words in the description that also appear in the task
    for word in re.findall(r"\w+", description):
        if len(word) > 3 and word in task_lower:
            score += 2
    # Match patterns (if any are URL-shaped) — bonus if the task
    # mentions a route keyword
    for pattern in meta.get("match", []):
        if isinstance(pattern, str) and pattern.lower() in task_lower:
            score += 3
    return score
```

Use it like this:

```python
skill = load_skill("~/.claude/skills/github.com", "close issue #42 on foo/bar")
agent = Agent(
    task="Close issue #42 on foo/bar",
    llm=llm,
    extend_system_message=skill,
)
```

---

## A complete, working example

This script picks the right skill, runs the agent in headed mode, and prints what happened:

```python
import asyncio
from pathlib import Path
from browser_use import Agent, Browser
from browser_use.browser.browser import BrowserConfig
from langchain_anthropic import ChatAnthropic

# 1. Where your w2s skills live
SKILLS_DIR = Path("~/.claude/skills").expanduser()

# 2. Pick the skill directory for the site you want to use
SKILL_DIR = SKILLS_DIR / "github.com"

# 3. The user's request
TASK = "Star the web2skill repo on GitHub"

# 4. Load the right skill
skill = load_skill(SKILL_DIR, TASK)

# 5. Configure browser-use to run with a visible window
browser = Browser(
    config=BrowserConfig(
        headless=False,           # show the Chrome window
        disable_security=True,    # less friction on real sites
    )
)

# 6. Build the agent
agent = Agent(
    task=TASK,
    llm=ChatAnthropic(model="claude-sonnet-4-5"),
    browser=browser,
    extend_system_message=skill,
)

# 7. Run it
async def main():
    history = await agent.run()
    # history is a list of steps; print what happened
    for step in history:
        print(f"[{step.url}] {step.action}")

asyncio.run(main())
```

Save this as `run.py` and:

```bash
python run.py
```

You will see Chrome open, the agent navigate, and the actions stream to your terminal.

---

## What the agent actually sees

When you pass a w2s skill as `extend_system_message`, browser-use prepends it to the agent's system prompt. The agent's full context looks roughly like:

```
SYSTEM PROMPT (from browser-use defaults)
---
<your w2s skill content here>
---

USER: Star the web2skill repo on GitHub
```

The agent reads the reference, sees the element inventory and edge cases, and uses them. When it needs to click a button, it does not "look at the page" from scratch — it looks up the element ref in the inventory and uses the selector recorded there.

This is what makes w2s skills valuable: the agent skips the expensive "figure out the website" phase and goes straight to execution.

---

## Tips and gotchas

**Headless vs headed.** `headless=False` shows the browser window. Use it during development. For production automation, set `headless=True` and use a video recording if you need to debug.

**Token cost.** A multi-route w2s skill can be 5,000-15,000 tokens. That is the upfront cost; subsequent runs of the same skill amortize it. The trade-off vs raw browser-use is: pay more per turn for context, pay less per turn for reasoning (the agent does not need to "discover" the site).

**Reference freshness.** Sites change. If a selector error occurs, the reference is stale. Re-run w2s on the same URLs to refresh it. browser-use does not auto-heal references — that is a future feature.

**Multiple skills at once.** If the user's task spans multiple sites (e.g. "copy this GitHub issue to Linear"), load both skills. Concatenate them in `extend_system_message`, separated by a clear header:

```python
skill = (
    "## SKILL: github.com\n\n"
    + load_skill("~/.claude/skills/github.com", task)
    + "\n\n## SKILL: linear.app\n\n"
    + load_skill("~/.claude/skills/linear.app", task)
)
```

**Don't load every skill.** If the user has 50 w2s skills, do not load all 50. Pick the ones relevant to the task. Otherwise you blow the context window.

**Logging.** Pass a `logger` or wrap `agent.run()` in your own logging to capture what the agent did. browser-use's `history` object has the full action log.

---

## See also

- [browser-use documentation](https://docs.browser-use.com)
- [w2s format spec](../../w2s/format-spec.md) — what the agent is reading
- [w2s examples](../../w2s/examples/) — fully worked skills you can plug in to test
