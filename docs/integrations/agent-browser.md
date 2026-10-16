# Compiling w2s skills with agent-browser

[agent-browser](https://github.com/vercel-labs/agent-browser) is the recommended tool for compiling w2s skills. Its accessibility-tree snapshots and element refs (`@eN`) are a natural fit for w2s's element inventory format.

This document covers how to use agent-browser during **compilation only**. The output of w2s is a comprehensive page reference — workflow generation is a separate downstream project.

---

## Why agent-browser for compilation

| | agent-browser | Generic headless browser |
|---|---|---|
| **Snapshot output** | Compact accessibility tree with `@eN` refs (~200-400 tokens) | Full DOM (~3000-5000 tokens) |
| **Element identification** | `role=button[name="New issue"]` semantics | CSS class names (often auto-generated) |
| **Token efficiency** | Designed for AI agents | Not optimized for agents |
| **Interactive snapshots** | `snapshot -i` shows refs inline | Manual DOM inspection |
| **Built-in screenshot annotation** | `screenshot --annotate` overlays refs | None |

The accessibility tree maps directly to w2s's element inventory format. What agent-browser calls `@e5` becomes a w2s element with a stable selector.

---

## Setup

```bash
npm i -g agent-browser
agent-browser install
```

`agent-browser install` downloads the Chromium binary. Run it once per machine.

---

## The compilation workflow

### 1. Open the URL

```bash
agent-browser open https://github.com/foo/bar
agent-browser snapshot -i
```

The `-i` flag gives you an **interactive snapshot** with numbered refs:

```
@e1  link    "Skip to content"
@e2  link    "Sign in"
@e3  link    "Sign up"
@e4  button  "Search"
@e5  link    "Pull requests"
@e6  link    "Issues"
@e7  link    "Codespaces"
@e8  link    "Marketplace"
@e9  link    "Explore"
@e10 link    "Pricing"
...
```

### 2. Click every interactive element

For each `@eN` in the snapshot, click it and snapshot again to capture the resulting state:

```bash
agent-browser click @e2          # Sign in
agent-browser snapshot -i        # Capture sign-in modal
# ... document modal state, fields, dismiss behavior ...

agent-browser press Escape       # Close modal

agent-browser click @e6          # Issues link → navigates
agent-browser snapshot -i        # Snapshot of /issues
# ... document new page state ...
```

**Skip destructive elements** — do not click submit, publish, push, delete, pay, send, post, etc. Document them in the inventory with their selector and label, mark them `destructive: true` in the output, and move on. See `w2s/SKILL.md` Step 2 for the full safety rule.

### 3. Hover over hover-revealed elements

```bash
agent-browser hover @e5          # Pull requests link
agent-browser snapshot -i        # Capture hover state (tooltip, dropdown)
```

### 4. Map `@eN` refs to w2s element refs

For each interactive element, note the `@eN` ref, label, role, and location. Write the w2s element entry with the stable selector and an `ab-ref` field recording the snapshot line:

```markdown
### `new-issue-btn`

- **type:** button
- **selector:** `a[href$="/issues/new"]`
- **fallback:** `role=button[name="New issue"]`
- **location:** top-right of main column, green
- **action:** navigates to `/owner/repo/issues/new`
- **ab-ref:** "@e8  link  "New issue""
```

The `ab-ref` field is optional metadata that records the exact snapshot line, useful for debugging and for any downstream tool that wants to map back to agent-browser's runtime refs.

### 5. Document forms

For every form you encounter, snapshot it and document every field with its label, type, validation rules, and required/optional status. See `w2s/format-spec.md` "Forms" section for the schema.

### 6. Document states (modals, dropdowns, toasts, etc.)

For every state triggered by a click/hover, record it as a `## States` entry in the output:

```markdown
### `sign-in-modal`

- **trigger:** `sign-in-btn`
- **dismiss:** Escape key, or click outside
- **contains:** `email-input`, `password-input`, `submit-btn`
- **notes:** traps focus; first input auto-focused
```

See `w2s/distillation.md` "Interaction states" section for the full taxonomy.

### 7. Write the comprehensive reference

For each route family, write one `SKILL.md` with all the elements, forms, states, and edge cases you observed. The schema is in `w2s/format-spec.md`.

---

## Useful agent-browser commands during compilation

| Goal | Command |
|---|---|
| Open URL | `agent-browser open <url>` |
| Interactive snapshot | `agent-browser snapshot -i` |
| JSON snapshot for parsing | `agent-browser snapshot -i --json` |
| Screenshot with numbered refs | `agent-browser screenshot --annotate` |
| Click element | `agent-browser click <@eN>` |
| Hover element | `agent-browser hover <@eN>` |
| Type into field | `agent-browser type <@eN> "<text>"` |
| Press key | `agent-browser press <@eN> <key>` |
| Get current URL | `agent-browser url` |
| Wait for element | `agent-browser wait <selector>` |
| Get CSS selector for an `@eN` | `agent-browser evaluate "document.querySelector('[aria-label=\"...\"]') ? '<selector>' : null"` |

See [agent-browser-commands.md](./agent-browser-commands.md) for the full command reference.

---

## Programmatic compilation

If you're building a tool that auto-generates w2s skills, use the JSON snapshot output:

```bash
agent-browser snapshot -i --json | jq '.data.refs'
```

Returns:

```json
{
  "e1": {"role": "link", "name": "Sign in", "selector": "a[href*='login']"},
  "e2": {"role": "button", "name": "Search", "selector": "button[aria-label='Search']"},
  ...
}
```

You can iterate through every ref, click it, snapshot the new state, and write the resulting markdown. The downstream workflow generator reads the markdown and figures out what to do at runtime.

---

## Common pitfalls

- **Auto-generated class names.** Sites like Notion, Figma, Linear use CSS-in-JS class hashes (`.css-1a2b3c`). agent-browser's accessibility tree resolves these for you — prefer the `role=` and `name=` selectors it surfaces over CSS class selectors.
- **iFrames.** If content lives in an iframe, you may need to switch contexts. agent-browser's `evaluate` command can do this with `document.querySelector('iframe').contentDocument`.
- **Shadow DOM.** Some sites use shadow DOM (Google, YouTube). agent-browser's accessibility tree flattens shadow DOM by default.
- **Token limits.** A full page snapshot can exceed your model's context window. Snapshot in sections (header, then main, then footer) and merge the results.
- **Destructive elements.** Never click submit/publish/delete during compilation. Document them with their selector and skip the click. See `w2s/SKILL.md` Step 2.

---

## See also

- [agent-browser README](https://github.com/vercel-labs/agent-browser)
- [w2s format spec](../../w2s/format-spec.md)
- [w2s distillation guide](../../w2s/distillation.md)
- [agent-browser commands reference](./agent-browser-commands.md)
- [`w2s/examples/web2skill-agent-browser/`](../../w2s/examples/web2skill-agent-browser/) — worked example of a comprehensive reference compiled using agent-browser
