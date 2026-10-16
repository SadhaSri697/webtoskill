---
name: web2skill
description: |
  USE THIS SKILL WHEN the user wants to turn a website into a
  comprehensive page reference. Triggers: "compile <url>",
  "document <url>", "extract <url>", "turn <url> into a reference",
  "snapshot <url>", "make a reference for <website>", "w2s <url>",
  "I want my agent to know what <website> offers".

  DO NOT USE for: actually performing actions on a website
  (workflow generation is a separate downstream project), scraping
  data, or static documentation that is not an interactive
  website.
---

# web2skill (w2s)

You turn websites into comprehensive page references. A
"reference" is a structured folder of markdown files
(`overview.md` plus one `SKILL.md` per route family) that an
agent — or a downstream workflow generator — can load to
understand exactly what a specific website offers, element by
element, state by state.

w2s is the **compile-time** step. It clicks, hovers, opens, and
documents. The downstream project reads the resulting reference
and generates workflows at runtime.

## The mission

Given a URL, produce a markdown reference that fully describes
the page:

- Every element (button, link, input, tab, menu item, toggle,
  accordion, dropdown trigger)
- Every state (modals, dropdowns, hover-revealed, accordions,
  in-page tabs, toasts, lightboxes, inline editing)
- Every form (fields, validation, submit behavior)
- Every edge case (empty states, loading states, auth walls,
  errors, rate limits)

The output is **exhaustive reference**, not a recipe. Workflows
are not generated. The downstream project decides which elements
participate in workflows and how.

## What you produce

For every site you compile, produce a folder like this:

```
<skills-dir>/<domain>/
├── overview.md        # site map + route index
├── <route-1>.md       # comprehensive reference for route family 1
├── <route-2>.md       # comprehensive reference for route family 2
└── ...
```

`<domain>` is the registrable domain (e.g. `github.com`,
`app.linear.app`). `<route-N>.md` is one file per route family,
named after the route (e.g. `repo.md`, `issues.md`,
`pulls.md`).

The exact schema is in `format-spec.md`. The route-family naming
rules are in `route-grouping.md`. The interaction-state taxonomy
(modals, dropdowns, hover, etc.) is in `distillation.md`. Load
those files before writing any output.

## Methodology

Follow these steps IN ORDER. Skip none.

### Step 1 — Extract the URL list

Parse the user's request into a list of URLs to compile.

- If the user gave you URLs, use them.
- If the user gave only a domain, ASK for specific URLs. Suggest
  3-5 representative URLs that would let you identify the major
  route families (e.g. homepage, a list view, a detail view, a
  settings page).
- If the user gave a goal ("document linear so my agent can
  manage issues"), reverse-engineer the URLs that page would
  need (e.g. `linear.app/inbox`, `linear.app/<team>/active`,
  `linear.app/<team>/issue/<id>`). Confirm with the user
  before compiling.

A useful reference needs at least 2-3 URLs that share a
structure, plus 1-2 URLs for sibling routes. If the user gives
you only one URL, push back: "I need at least 2-3 URLs to
identify a route family. Can you share a few more?"

### Step 2 — For each URL, distill the page (observe AND interact)

A static snapshot misses half the page. Modals, dropdown menus,
popovers, hover-revealed actions, expanded accordions, and
toasts only exist AFTER something is clicked or hovered. The
compiler must interact with the page, not just observe it.

For each URL in the list, use your browser tool to:

1. Navigate to the URL
2. Wait for the page to be fully loaded (network idle, no
   visible loading spinners)
3. Extract a COMPACT representation of the page in its initial
   state (layout, visible elements, currently-visible modals
   or banners)
4. **Click every interactive element on the page** (buttons,
   tabs, dropdown triggers, menu items, accordions, "more"
   links) and document the resulting state
5. **Hover over interactive elements that have hover-only
   behavior** (tooltips, hover menus, action buttons that appear
   on row hover) and document what appears
6. For each triggered modal/popover/menu: record it as a
   distinct interaction state, with its own element inventory,
   and dismiss behavior
7. Close each opened state before moving to the next, so you
   do not stack modals
8. **Document every form** you encounter — every field, every
   validation rule, the submit button, the success/error
   outcomes

What to extract (and how to identify stable selectors) is
specified in `distillation.md`. The rules for documenting
interaction states (modals, dropdowns, hover menus, accordions,
toasts, lightboxes, inline editing) are in the **Interaction
states** section of `distillation.md`.

In short: every interactive element with its label, role,
stable selector, and location on the page, plus the high-level
layout (header, sidebars, main column, footer), plus every
modal, banner, or overlay that can be triggered on this page,
plus every form with its fields and validation.

What to ignore: scripts, styles, decorative SVGs, hidden
elements, tracking pixels, ads, analytics. The page must be
readable in under 5,000 tokens after distillation.

**Destructive actions are EXCLUDED from this click-everything
rule.**

Do NOT click buttons that mutate external state or have
irreversible side effects. This includes (but is not limited
to):

- **Submit / publish / push** — "Submit", "Save", "Publish",
  "Push changes", "Deploy", "Send", "Post", "Tweet", "Reply",
  "Confirm delete"
- **Destructive operations** — "Delete", "Remove", "Destroy",
  "Drop", "Purge", "Trash", "Archive" (when irreversible)
- **Payments / transfers** — "Pay", "Charge", "Transfer",
  "Buy", "Subscribe", "Purchase"
- **Account changes** — "Cancel subscription", "Close
  account", "Revoke", "Disable 2FA", "Reset password" (when
  the reset actually triggers an email)
- **External actions** — anything that posts to social media,
  sends an email, fires a webhook, or modifies a third-party
  system

For these elements, document them as **observable but not
exercised**:

- Record the element in the inventory with its selector,
  label, and location
- Do NOT click it during compilation
- Mark it with a `destructive: true` flag in the element
  inventory
- Describe the action in the `action:` field — what would
  happen if it were clicked

The reference must capture these elements so the downstream
workflow generator knows they exist, but compilation itself
must not trigger them. A reference that accidentally pushed
real changes during compilation would be catastrophic.

### Step 3 — Group URLs into route families

URLs that share a structural pattern get one `SKILL.md` each.
The exact grouping rules are in `route-grouping.md`. Summary:

- `github.com/foo/bar` and `github.com/baz/qux` are the same
  family (one SKILL.md, named `repo.md`)
- `github.com/foo/bar/issues` and `github.com/foo/bar/issues/42`
  are the same family (`issues.md`)
- `github.com/foo` (org view) is a DIFFERENT family from
  `github.com/foo/bar` (repo view)

Pick a stable, descriptive name per family (kebab-case). The
name becomes the filename and the `name:` field in the skill's
frontmatter.

### Step 4 — Write one SKILL.md per route family

For each family, produce a `SKILL.md` using the schema in
`format-spec.md`. The file must contain:

- **Frontmatter** (YAML): `name`, `description`, `match` (URL
  patterns), `requires` (other references this one depends on)
- **Page architecture**: header, sidebar, main, footer, with
  what's in each
- **Element inventory**: every interactive element, with a
  stable `ref` name, type, primary selector, fallback
  selector, location, and `action:` describing what activating
  it does
- **Forms**: every form on the page, with fields, validation,
  and submit behavior
- **States**: every modal, dropdown, hover-revealed element,
  accordion, in-page tab, toast, lightbox — with trigger and
  dismiss
- **Edge cases**: empty states, auth walls, loading states,
  errors, rate limits

### Step 5 — Write the overview.md

For each unique domain, produce an `overview.md` containing:

- **Frontmatter** (YAML): `name`, `domain`, `description`,
  `match`
- **Site map**: a mermaid graph showing how routes connect
- **Route index**: a bullet list of routes and which
  sub-reference handles each
- **Site-wide patterns**: persistent header, footer, global
  nav
- **Identity model**: how to detect logged-in vs logged-out
  state
- **Global edge cases**: cookie banners, marketing modals,
  etc.

### Step 6 — Save the skills

Save the output to the user's skills directory. For Claude
Code, that is `~/.claude/skills/<domain>/`. For other agents,
ask the user for the path or check the agent's docs.

If the directory already exists with a reference for the same
domain:

- If a route family is new: ADD the new file. Do not overwrite.
- If a route family exists: ASK the user whether to overwrite,
  merge, or skip.

Never save references to `/tmp` or any non-persistent
location.

### Step 7 — Self-check

Before declaring done, verify the reference by reading the
files back and checking:

- [ ] Every `ref` used anywhere exists in the element
      inventory
- [ ] Every `match` pattern in frontmatter actually matches a
      real URL the user gave
- [ ] The mermaid graph in `overview.md` references real
      route names
- [ ] Element selectors are stable (no random CSS hashes like
      `.css-1a2b3c`)
- [ ] Edge cases mentioned in element inventory are
      documented in the "Edge cases" section
- [ ] The `requires` field in sub-skills references the
      overview (`github`, not `github.com`)
- [ ] Every form has a corresponding `## Forms` section
- [ ] Every modal/dropdown/hover-state has a corresponding
      `## States` entry
- [ ] No destructive element was clicked during compilation

If any check fails, go back and fix it. Do not ship a broken
reference.

## Asking the user

The user is non-technical by default. Optimize for clarity over
cleverness. Use plain language. Don't ask them to write URL
patterns or selectors — that is your job.

Good questions:

- "Which URLs do you want compiled? I need at least 2-3 to
  identify the route family."
- "What's the goal — what should the agent be able to DO on
  this site once the reference is ready?"
- "Will you be logged in when using this reference? Auth
  walls change the available features."
- "This reference already exists at `<path>`. Do you want to
  overwrite it, or just add the new routes?"

Bad questions (do not ask):

- "What CSS selectors should I use for the buttons?"
- "Can you give me a URL pattern regex?"
- "What is the element taxonomy you prefer?"

## What NOT to do

- Do not compile a single URL and call it done. A single URL
  is evidence, not a reference.
- Do not include selectors that are obviously brittle
  (`.css-1a2b3c`, deep descendant chains with class names
  that look generated, positional selectors like `div:nth-child(3)
  > a`).
- Do not hallucinate elements you did not observe. If you
  cannot see it, do not document it.
- Do not save references to a non-persistent directory.
- Do not skip the self-check. A broken reference is worse
  than no reference.
- **Do not click destructive buttons during compilation.**
  Submit, publish, push, delete, pay, send, post — any
  button with irreversible side effects must be observed,
  documented, and flagged `destructive: true`, but NEVER
  clicked. See Step 2.
- **Do not generate workflows.** Workflows are the
  responsibility of a separate downstream project. The w2s
  output is a reference, not a recipe.

## Reference files

- `format-spec.md` — exact schema for `overview.md` and
  per-route `SKILL.md` files. Load before writing any output.
- `distillation.md` — rules for converting a live page into
  a compact representation. Load before distilling any URL.
- `route-grouping.md` — how to identify route families from
  a list of URLs. Load before grouping.
- `examples/` — worked end-to-end examples. Read at least one
  before compiling a real site for the first time.
