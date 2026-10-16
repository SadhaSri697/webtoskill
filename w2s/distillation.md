# distillation.md

How to turn a live web page into a compact, token-efficient
representation suitable for the compiler. Load this file before
distilling any URL.

The goal: from a page that may be 50K+ tokens of raw HTML, produce a
distilled view under 5,000 tokens that still contains everything an
agent needs to navigate the page later.

## The principle

Distillation is lossy by design. We are NOT trying to preserve the
page. We are trying to preserve the parts of the page an agent needs
to (a) find elements, (b) decide what to click, and (c) recognize
state.

The agent will use the output of distillation to write a `SKILL.md`.
That `SKILL.md` is what other agents will read at runtime. So the
distilled view only needs to support the writing of the skill — it
does not need to be readable on its own.

## What to keep

### Interactive elements

Every interactive element gets recorded. By "interactive," we mean
elements the user (or agent) can act on:

- Buttons (`<button>`, `role=button`)
- Links (`<a>` with meaningful `href`)
- Form fields (`<input>`, `<textarea>`, `<select>`)
- Checkboxes, radios, switches
- Tabs, accordions, disclosure widgets
- Dropdown menu triggers
- Sliders, draggable items
- File upload zones
- Search inputs (even if just a plain `<input type="search">`)

For each, record:

- **`ref`** — a stable, descriptive name (kebab-case). The agent
  uses this in the skill. Example: `new-issue-btn`,
  `search-input`, `filter-open-closed`.
- **`type`** — button, link, input, etc.
- **`label`** — what the element says. Prefer the visible text
  label; fall back to `aria-label`; fall back to
  `placeholder`/`title`/`value`.
- **`role`** — the accessibility role, if non-obvious
  (`button`, `link`, `menuitem`, `tab`, `option`, etc.)
- **`selector`** — the most stable CSS selector you can find (see
  Selector quality below).
- **`location`** — short prose describing where on the page
  ("top-right of main column, green button").

### Layout regions

The high-level structure of the page: header, sub-header, left
rail, main column, right rail, footer, modal, banner. For each
region, a one-sentence description of what is in it. Reference
elements by `ref` where appropriate.

### Visible text content

The text that an agent would need to recognize the page state:
headings, section titles, status messages, error messages, empty
state copy. Do NOT preserve paragraphs of body text, marketing
copy, legal text, or anything that is not load-bearing for
navigation.

### Modals, banners, and overlays (initially visible only)

Anything that is layered on top of the page and partially obscures
it, **as it appears on first load**: cookie banners, "sign up for
our newsletter" modals, "your trial ends in N days" banners,
"install our app" prompts, etc. For each, record: what it says,
where it is, and how to dismiss it (which element ref).

Modals and overlays that appear only AFTER clicking a trigger
are covered in the **Interaction states** section below — do not
document them here.

### Form structures

For forms, record every field and its label, even if all fields are
just text inputs. The skill writer needs to be able to write
workflows like "fill in the email field, fill in the password
field, click submit."

### Repeated patterns

If a list of items appears (issue rows, search results, file tree
nodes), record ONE element ref for the row template and one for
each significant child. Do not enumerate every row.

Example:

```markdown
### `issue-row`

- **type:** repeatable
- **selector:** `[data-testid="issue-row"]`
- **location:** each row in main column
- **contains:** `issue-title`, `issue-number`, `issue-labels`,
  `issue-author`, `issue-timestamp`
```

This is the single biggest token saver on list-heavy pages.

## Interaction states

A static snapshot of the page misses everything that only appears
AFTER a user interacts. Modals, dropdown menus, hover-revealed
actions, expanded accordions, toasts, lightboxes, and inline
editing states are all invisible until something is clicked,
hovered, or focused. **The compiler must trigger every interactive
element and document the resulting state.** This section is the
rules for doing that.

For every interactive state you encounter, record four things:

1. **`trigger`** — the element ref whose click/hover/focus opens
   the state. If the trigger is conditional (the state only opens
   sometimes), document the condition.
2. **`state`** — a short description of what appears, the element
   refs of the new content (or a sub-inventory of just the
   state-specific elements), and where on screen it lives
   (centered modal? bottom-right toast? inline below the
   trigger?).
3. **`dismiss`** — how to close the state. Common dismiss
   actions: clicking a close (X) button, pressing Escape,
   clicking outside the state, submitting a form, navigating
   away. If more than one dismiss path exists, document each.
4. **`persistence`** — does the state survive across page
   navigations? Most modals do not; some banners (cookie consent)
   do. Mention this if it matters for the workflow.

### Modals and dialogs

Modals are the most important interaction state. They frequently
contain their own forms and workflows (the "new issue" modal is a
textbook case — see `../examples/complex-spa/new-issue.md`).

```markdown
### `new-issue-modal` (triggered by `new-issue-btn`)

- **type:** modal
- **trigger:** `new-issue-btn` (button in the team-view tab bar)
- **state container:** `[data-testid="new-issue-modal"]`
- **location:** centered, 600px wide, with a dimmed full-screen
  overlay behind it
- **contains:** `title-input`, `description-input`, `status-select`,
  `priority-select`, `assignee-select`, `labels-select`,
  `cancel-btn`, `create-btn`, `modal-close`
- **dismiss:** click `modal-close`, click `cancel-btn`, press
  Escape, or click on the dimmed overlay
- **persistence:** dismissed on any navigation; reopening
  `new-issue-btn` starts a fresh modal
```

Decide whether a modal deserves its own `SKILL.md` or lives
inside the parent page's skill. Rule of thumb: if the modal has
its own multi-step workflow (form fields, validation, submit),
give it its own file. If it is a simple confirmation
("Are you sure?") it stays as an interaction state in the
parent skill.

### Dropdown menus and popovers

Menus that open on click, kebab (...) buttons, filter popovers,
sort dropdowns. They overlay the page in a small region, usually
anchored to the trigger.

```markdown
### `status-filter-menu` (triggered by `filter-button`)

- **type:** popover
- **trigger:** `filter-button` (right side of the tab bar)
- **state container:** `[data-testid="status-filter-menu"]`
- **location:** anchored below `filter-button`, ~240px wide
- **contains:** `filter-option-assignee`, `filter-option-label`,
  `filter-option-priority`, `filter-clear-all`
- **dismiss:** click outside the popover, press Escape, or click
  a filter option (which both applies the filter AND dismisses)
- **persistence:** dismissed on any click outside; the filter
  itself persists across the session
```

### Hover-revealed actions and tooltips

Some elements (table rows, list items, cards) reveal additional
actions only on hover: a quick-actions toolbar, a "more" menu, a
"delete" button. These are easy to miss in a static snapshot
because the trigger is just "hover anywhere on the row."

For each hover-revealed action:

- Record the parent element ref (`issue-row`)
- Record the hover-revealed element ref (`issue-quick-actions`)
- Note the action each child performs
- Note whether the action is also accessible without hover (a
  common pattern is "hover on desktop, always visible on
  touch/mobile")

```markdown
### `issue-quick-actions` (hover-revealed on `issue-row`)

- **type:** hover-revealed
- **trigger:** hover anywhere on `issue-row`
- **state container:** inside `issue-row`, right side
- **contains:** `issue-quick-complete` (checkmark), `issue-quick-
  assign` (avatar+), `issue-quick-more` (kebab menu)
- **note:** always visible on touch devices; on desktop, fades
  in over 100ms on hover
```

Tooltips (the small text labels that appear when you hover an
icon for 1+ seconds) are usually NOT worth documenting unless
they reveal information the agent cannot get elsewhere.

### Accordions and expand-collapse sections

Collapsible content blocks: FAQ items, "Show more" sections,
tree-view nodes. The state change is "expanded" or "collapsed."

```markdown
### `faq-item-expanded` (triggered by clicking `faq-question`)

- **type:** expand-collapse
- **trigger:** `faq-question` (the question text in any
  `faq-item`)
- **state change:** the `faq-answer` for that item becomes
  visible; the chevron icon rotates 180deg
- **dismiss:** click `faq-question` again, or click another
  `faq-question` to collapse this one (depending on whether
  the accordion is single-open or multi-open)
- **persistence:** collapsed/expanded state typically does NOT
  persist across page reloads
```

### Tabs (in-page, no URL change)

In-page tabs that swap content without changing the URL. (URL-
changing tabs are covered as separate route families in
`route-grouping.md`.)

```markdown
### `tab-content-active` (triggered by `tab-active`)

- **type:** in-page tab
- **trigger:** `tab-active` (or `tab-backlog` /
  `tab-completed` for other tabs)
- **state change:** `issue-list` content is replaced with the
  selected tab's issues
- **dismiss:** N/A (selecting another tab replaces it)
- **persistence:** the selected tab is reflected in the URL on
  some sites — check the URL after clicking; if the URL changed,
  this is actually a separate route family
```

### Toasts and ephemeral notifications

Short-lived confirmations and error messages that appear (usually
bottom-right) and disappear after a few seconds. Toasts are
almost never worth documenting as interaction states — they
require no action from the agent. **Mention them in the
parent page's "Edge cases" section only if** the agent might
mistake them for persistent state, or if the toast blocks
interaction with the underlying page (rare).

### Lightboxes and image zoom

Click-to-zoom image viewers, full-screen video players, PDF
viewers. The state is a full-screen overlay with media controls.

```markdown
### `image-lightbox` (triggered by clicking any `product-image`)

- **type:** lightbox
- **trigger:** click on any `product-image` thumbnail
- **state container:** `[data-testid="image-lightbox"]`
- **location:** full-screen, centered image, controls overlay
  bottom
- **contains:** `lightbox-image`, `lightbox-prev`,
  `lightbox-next`, `lightbox-close`
- **dismiss:** click `lightbox-close`, press Escape, or click
  outside the image
```

### Inline editing states

Form fields that are read-only until clicked (the user clicks
the field, it becomes editable, blur or Enter commits the
change). Common for issue titles, descriptions, comments.

```markdown
### `title-editor` (triggered by clicking `issue-title`)

- **type:** inline editor
- **trigger:** click on `issue-title`
- **state change:** `issue-title` is replaced by `title-input`
  (a text input) with the current value pre-filled and focused
- **dismiss / commit:** blur (clicking outside) saves, Escape
  cancels and reverts, Enter saves
- **persistence:** the saved value persists; the editor is only
  re-triggered by another click on the title
```

### State hygiene

While interacting, **close each state before opening the next**.
If you click `new-issue-btn` and then click `filter-button`
without first closing the modal, you will get confused about
which state is "on top" and the resulting documentation will
be wrong. Click `modal-close` (or press Escape) between
triggered states.

Also: some sites let you stack modals (a modal that opens
another modal). If you encounter this, document each level of
the stack as a separate interaction state, with the lower
modal dimmed more heavily than the upper one.

## What to ignore

- **Scripts, styles, JSON-LD, embeds.** All `<script>`, `<style>`,
  `<link rel="stylesheet">`, `<noscript>`, `<iframe>` (unless
  visibly interactive and important), `<object>`, `<embed>`.
- **Hidden elements.** Anything with `display: none`,
  `visibility: hidden`, `hidden` attribute, `aria-hidden="true"`,
  `tabindex="-1"` and not currently focused, or zero size
  (`width: 0` and `height: 0`).
- **Decorative images and SVGs.** `<img>` that is purely visual
  (logos, illustrations, avatars shown as decoration). KEEP
  `<img>` if it is the only representation of meaningful content
  (a product photo, a user-uploaded screenshot, etc.).
- **Ads and trackers.** Anything in an iframe, anything with
  classes/ids suggesting ads (`ad-`, `ads-`, `analytics-`,
  `tracking-`, `pixel-`), anything from a third-party domain.
- **Marketing chrome.** Footer links to "About us," "Careers,"
  "Press," "Terms of service," "Privacy policy" — UNLESS those are
  the actual routes the agent needs to navigate to.
- **Decorative repetition.** A long list of identical footer
  links, a sidebar of related-content links, a "you might also
  like" carousel. One representative example is enough; the rest
  is noise.
- **Empty containers.** `<div>`s with no content, no children of
  interest, and no semantic purpose.
- **Form helpers.** Hidden inputs (`<input type="hidden">`),
  CSRF tokens, tracking fields.
- **Repeated identical structures.** If a list has 50 items, do
  not list all 50. List the structure once, with `repeatable`
  semantics.

## Selector quality

The selectors you record determine whether the skill will keep
working when the site is redesigned. Use this priority order:

1. **`[data-testid="<name>"]`** — best. Designed to be stable.
2. **`#<stable-id>`** — good. The element has a real, semantic ID.
3. **`[aria-label="<exact>"]`** — good. Semantic and stable.
4. **`[name="<form-field-name>"]`** — good for form fields.
5. **`[role="<role>"][aria-label="<exact>"]`** — good. The
   combination is more specific than either alone.
6. **Semantic CSS:** `nav a[href="/pricing"]`,
   `form input[type="email"]` — acceptable. Tied to structure.
7. **Text-based:** `button:has-text("Sign in")`,
   `a:has-text("Pricing")` — last resort. Text can change with
   copy updates.
8. **FORBIDDEN:** auto-generated class hashes
   (`.css-1a2b3c`, `.jsx-abc123`), positional selectors
   (`div > div:nth-child(2) > a`), and deeply nested descendant
   chains with no semantic anchor. If the only selector you can
   produce is one of these, do not record the element.

When you record a `selector` field, also record a `fallback`
selector one level down the priority list. The agent will try the
primary first, then the fallback.

## Tool-specific guidance

Different agents have different browser tools. Adapt the
distillation method to your tool, but the OUTPUT FORMAT must match
what `format-spec.md` expects.

### If you have a real browser (Playwright, Puppeteer, browser-use)

- Open the page
- Wait for `networkidle` (no requests in flight for 500ms)
- Use the accessibility tree (`page.accessibility.snapshot()` in
  Playwright) as your starting point — it gives you roles, names,
  and properties for free
- Cross-reference with the live DOM for selectors and locations
- Take a screenshot for layout reference (don't put the screenshot
  in the output, just use it to write the page architecture
  section)

### If you have a "fetch and parse" tool (curl, web fetch)

- Fetch the HTML
- Strip `<script>`, `<style>`, `<noscript>`, hidden elements
- For each remaining element, extract label, role, attributes that
  would be a stable selector
- You will NOT get layout information (positions, sidebars) — say
  so in the page architecture section ("layout inferred from HTML
  structure, not from rendering")
- You will NOT see modals or dynamic content — flag this in the
  edge cases section

### If you have computer use (vision-based browser)

- Open the page
- Look at it
- For each visible interactive element, describe what you see: the
  label, its position, its appearance
- This is the most expensive option in tokens but the most
  reliable for SPAs that don't expose semantic HTML
- The selectors you record will be weaker (often text-based only)

## Output format

The distilled view is your working scratchpad — it does not get
saved as a file. It is the structured notes you take while
inspecting the page, and the source material you use to write the
`SKILL.md`. Organize it in roughly the same structure as the final
skill (architecture, elements, workflows, edge cases) but at lower
fidelity.

## Anti-patterns

- Do not record every link in a footer. Record the footer as a
  region, mention "30+ footer links present," and move on.
- Do not record every CSS class. Classes are implementation
  detail; refs and roles are what matter.
- Do not describe the page in human prose ("a beautiful clean
  layout with a blue header"). That belongs in a marketing
  brochure, not a skill.
- Do not record decorative content (avatar images, brand logos)
  as elements. They are not interactive.
- Do not record dynamic content that you only saw once and that
  will not be present on the next load (toast notifications,
  "welcome back" modals). Mention them in edge cases instead.