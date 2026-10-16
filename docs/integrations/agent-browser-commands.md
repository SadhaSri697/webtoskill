# agent-browser command reference for w2s compilation

Quick reference of agent-browser commands useful when compiling w2s skills. See the [full docs](https://github.com/vercel-labs/agent-browser) for complete details.

---

## Core navigation

### `open`
```
agent-browser open <url>
```
Opens a URL in the browser. If the browser is not running, it starts a new session.

```bash
agent-browser open https://github.com/foo/bar
agent-browser open https://github.com/foo/bar/issues
```

### `url`
```
agent-browser url
```
Prints the current URL. Use to confirm route in a workflow.

```bash
agent-browser url
# → https://github.com/foo/bar/issues
```

### `back`
```
agent-browser back
agent-browser forward
```
Go back or forward in navigation history.

### `reload`
```
agent-browser reload
```
Reloads the current page.

---

## Element interaction

### `click`
```
agent-browser click <@eN>
```
Clicks an element by its snapshot ref.

```bash
agent-browser click @e5       # Click the element with ref @e5
agent-browser click @e12       # Click submit button
```

### `double-click`
```
agent-browser double-click <@eN>
```

### `right-click`
```
agent-browser right-click <@eN>
```

### `hover`
```
agent-browser hover <@eN>
```
Hovers over an element. Use to trigger hover-revealed actions (tooltips, quick-action toolbars on rows).

```bash
agent-browser hover @e7       # Hover over an issue row
# Now the quick-action buttons @e8, @e9, @e10 are visible
agent-browser click @e8       # Click the checkmark (mark complete)
```

### `type`
```
agent-browser type <@eN> "<text>"
```
Types text into an input field. Clears the field first.

```bash
agent-browser type @e3 "Search query"
agent-browser type @e5 "issue title"
```

### `press`
```
agent-browser press <@eN> <key>
```
Presses a key on an element or globally. Keys: `Enter`, `Tab`, `Escape`, `ArrowDown`, `ArrowUp`, `ArrowLeft`, `ArrowRight`, `Backspace`, `Space`.

```bash
agent-browser press @e3 Enter    # Submit a search
agent-browser press @e2 Escape   # Close a modal
agent-browser press --key Escape  # Global: close modal from anywhere
```

### `select-option`
```
agent-browser select-option <@eN> <value>
```
Selects an option in a `<select>` dropdown.

```bash
agent-browser select-option @e4 "open"
```

### `check` / `uncheck`
```
agent-browser check <@eN>
agent-browser uncheck <@eN>
```
Checks or unchecks a checkbox.

---

## Finding elements

### `find`
```
agent-browser find <selector> [--first] [--timeout <ms>]
```
Finds elements by CSS selector. Returns the first match as a ref.

```bash
agent-browser find 'a[href$="/issues/new"]' --first
# → @e5

agent-browser find '[data-testid="issue-row"]' --first
```

Used by the w2s bridge to map w2s element refs to agent-browser refs.

### `find-all`
```
agent-browser find-all <selector>
```
Returns all matching elements as refs. Use for list iteration.

```bash
agent-browser find-all 'tr[data-testid="issue-row"]'
# → @e5, @e6, @e7, ... (list of issue rows)
```

---

## State and inspection

### `snapshot`
```
agent-browser snapshot [-i|--interactive]
```
Captures the accessibility tree. Use `-i` for numbered refs (`@e1`, `@e2`, ...).

```bash
agent-browser snapshot -i
# @e1  button  "Star"
# @e2  link    "Issues"
# @e3  link    "Pull requests"
# @e4  link    "Actions"
# ...

agent-browser snapshot -i --json
# {"success":true,"data":{"tree":"...","refs":{"e1":{"role":"button",...}}}}
```

### `wait`
```
agent-browser wait <selector> [--timeout <ms>]
```
Waits for an element to appear. Default timeout is 5000ms.

```bash
agent-browser wait '.issue-list'
agent-browser wait '@e12' --timeout 10000
```

### `scroll`
```
agent-browser scroll [--by <pixels>] [--to <selector>]
```
Scrolls the page.

```bash
agent-browser scroll --by 500           # Scroll down 500px
agent-browser scroll --to @e10          # Scroll to element @e10
agent-browser scroll --to bottom        # Scroll to bottom
```

### `evaluate`
```
agent-browser evaluate <js-expression>
```
Runs a JavaScript expression in the browser context. Returns the result.

```bash
agent-browser evaluate "document.title"
# → "foo/bar: Issues"

agent-browser evaluate "document.querySelector('.issue-row').textContent"
```

---

## Screenshot and visual

### `screenshot`
```
agent-browser screenshot [--path <file>] [--annotate]
```
Takes a screenshot.

```bash
agent-browser screenshot                              # Saves to default path
agent-browser screenshot --path ./screenshot.png
agent-browser screenshot --annotate                   # Numbered element labels
```

`--annotate` overlays the element refs on the screenshot. Use when mapping visual elements to w2s element inventory.

---

## Batch execution

### `batch`
```
agent-browser batch --json
```
Executes multiple commands from JSON stdin in one invocation. More efficient than running multiple CLI calls.

```bash
echo '[["open","https://github.com/foo/bar"],["snapshot","-i"],["click","@e5"]]' \
  | agent-browser batch --json
```

Useful for batch compilation — open a URL, snapshot, click several elements in sequence without re-spawning the CLI.

---

## Session management

### `session save`
```
agent-browser session save <name>
```
Saves the current browser session state (cookies, localStorage, etc.) to a named session.

```bash
agent-browser session save github-auth
```

### `session load`
```
agent-browser session load <name>
```
Restores a saved session.

```bash
agent-browser session load github-auth
```

Used for sites that require authentication — save the session after manually logging in once, then load it for subsequent compilations.

---

## Compilation example

A complete w2s compilation session using agent-browser commands:

```bash
# Open the repo
agent-browser open https://github.com/foo/bar

# Initial snapshot to discover the page
agent-browser snapshot -i
agent-browser url

# Click the Issues tab (@e2 from the snapshot) to navigate
agent-browser click @e2

# Wait for the issues list to load
agent-browser wait '[data-testid="issue-list"]'

# Snapshot to find the New issue button
agent-browser snapshot -i
# → @e5 is "New issue"

# Click New issue to discover the modal
agent-browser click @e5

# Wait for the modal to open
agent-browser wait @e8

# Snapshot the modal contents
agent-browser snapshot -i
# → @e10 is the title input, @e11 is the body, @e15 is submit

# Get the actual selectors for the w2s element inventory
agent-browser evaluate "document.querySelector('[data-testid=\"new-issue-title\"]') ? '[data-testid=\"new-issue-title\"]' : 'input[name=\"title\"]'"

# Close the modal (do not submit — destructive)
agent-browser press Escape
```

Note: do NOT click `@e15` (Submit) during compilation. Document it in the inventory with `destructive: true` and move on.

---

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Element not found |
| `2` | Navigation failed |
| `3` | Timeout |
| `4` | Invalid arguments |

Use exit codes in scripts to handle errors:

```bash
agent-browser click @e5
if [ $? -ne 0 ]; then
  echo "Click failed — element not found"
  agent-browser screenshot --path error.png
fi
```