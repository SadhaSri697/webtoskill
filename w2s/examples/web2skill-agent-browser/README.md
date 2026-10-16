# Example: w2s reference compiled with agent-browser

A worked example of a w2s comprehensive page reference for a
fictional project management tool ("Harvest Grove"). The
reference was compiled using agent-browser's `snapshot -i`
and `click` commands.

---

## What's in this folder

```
w2s/examples/web2skill-agent-browser/
├── README.md     ← this file
├── overview.md   ← site map (one per domain)
├── home.md       ← comprehensive reference for the homepage
└── login.md      ← comprehensive reference for the login page
```

---

## What the reference contains

Each `*.md` file is a comprehensive page reference, not a
task manual. It documents:

- **Page architecture** — header, hero, footer, layout
- **Element inventory** — every button, link, input, with
  selector, type, location, and `action:` describing what
  activating it does
- **States** — modals, dropdowns, hover-revealed, accordions
- **Forms** — every field, validation, submit behavior
- **Edge cases** — empty states, errors, rate limits, auth
  walls

It does **not** contain workflows. Workflow generation is a
separate downstream project. The reference is a complete
description of what the page offers; the runtime decides what
to do with it.

---

## What the `ab-ref` field is

Some elements in the inventory have an `ab-ref:` line. This
records the exact line from the agent-browser snapshot that
was used during compilation:

```markdown
### `hero-cta-signup`

- **type:** link
- **selector:** `[data-testid="hero-cta-signup"]`
- **fallback:** `a:has-text("Get started")` in the hero section
- **location:** hero section, right side, primary button
- **action:** navigates to /signup
- **ab-ref:** "@e7  link  "Get started""
```

The `ab-ref` is optional metadata. It is useful for debugging
and for any downstream tool that wants to map back to
agent-browser's runtime refs.

---

## Compiling this example

To compile a similar reference for a real site:

1. Install agent-browser:
   ```bash
   npm i -g agent-browser
   agent-browser install
   ```

2. Open the site and snapshot:
   ```bash
   agent-browser open https://real-site.com/home
   agent-browser snapshot -i
   ```
   Note every `@eN` and what it points to.

3. Click every interactive element, snapshot the resulting
   state, and document the elements you find. Skip destructive
   buttons (submit, publish, delete, pay, send, post) — see
   `w2s/SKILL.md` Step 2.

4. For forms, snapshot the form fields, document each one with
   its type, label, validation rules, and required/optional
   status.

5. For modals/dropdowns, record the trigger, dismiss behavior,
   and what's inside.

6. Write the reference using the schema in `w2s/format-spec.md`.

7. Validate:
   ```bash
   python3 w2s/validate.py ~/.claude/skills/<domain> --warnings
   ```

---

## Reading this reference

The compiled reference is meant to be read by an agent (or a
downstream workflow generator) that needs to know what the
page offers. The agent looks up element refs in the inventory
to find selectors, types, and locations.

Example: an agent that needs to navigate to the signup page
finds `hero-cta-signup` in the home reference, reads its
selector (`[data-testid="hero-cta-signup"]`), and uses that
selector with whatever browser tool it has.

The reference makes no assumption about which browser tool
will execute the actions. It just describes the page
exhaustively.
