---
name: trail-new-issue
description: |
  The Trail new-issue modal. Opens on top of the team view when
  the "New issue" button is clicked. Used to create a new issue
  in the current team.
match:
  - /^https:\/\/app\.trail\.dev\/[^/]+\/issue\/new\/?$/
requires:
  - trail
---

# Trail — New Issue (Modal)

## Important: this is a modal

The new-issue "page" is not a standalone page. It is a modal that
overlays the team view. The URL changes to
`/:team/issue/new` (so the agent can match against it), but the
team view is still partially visible behind a dim overlay.

**You reach this state by:** clicking `new-issue-btn` in the team
view (see `team-view.md`).

**To leave this state:** either submit a new issue (it becomes a
real issue, you navigate to `/:team/issue/<new-id>`) or press
Escape / click outside the modal / click the close button to
dismiss.

## Page architecture

- **Modal overlay (full-screen, dimmed background)**
- **Modal container (centered, 600px wide):**
  - **Header:** "New issue" title (left), close button (X,
    right)
  - **Form:**
    - Title input (large, autofocus)
    - Description textarea (markdown editor with preview tab)
    - Properties row (inline, not in a sidebar): Status
      dropdown, Priority dropdown, Assignee dropdown, Labels
      selector
  - **Footer:** "Cancel" button (left), "Create issue" button
    (right, primary)

## Element inventory

### `modal-overlay`

- **type:** container
- **selector:** `[data-testid="modal-overlay"]`
- **location:** full-screen, fixed position
- **note:** clicking outside the modal container (i.e. on the
  overlay) dismisses the modal

### `modal-container`

- **type:** container
- **selector:** `[data-testid="new-issue-modal"]`
- **location:** centered
- **note:** focus is trapped within the modal; Tab cycles
  through its elements

### `modal-close`

- **type:** button
- **selector:** `button[aria-label="Close"]`
- **fallback:** `button:has-text("×")` in the modal header
- **location:** top-right of the modal
- **note:** clicking dismisses the modal without creating an
  issue

### `title-input`

- **type:** input
- **selector:** `input[name="title"]`
- **fallback:** `input[placeholder*="title" i]` in the modal
- **location:** top of the form, autofocus
- **note:** required; "Create issue" is disabled if empty

### `description-input`

- **type:** textarea
- **selector:** `textarea[name="description"]`
- **fallback:** `textarea` in the modal
- **location:** below `title-input`
- **note:** supports markdown; tab to switch between "Write"
  and "Preview"

### `status-select`

- **type:** select
- **selector:** `[data-testid="new-issue-status"]`
- **fallback:** `button:has-text("Backlog")` in the properties
  row
- **location:** properties row, first
- **note:** default is "Backlog" for new issues; options are
  the standard status values (see `issue.md`)

### `priority-select`

- **type:** select
- **selector:** `[data-testid="new-issue-priority"]`
- **fallback:** `button:has-text("No priority")` in the
  properties row
- **location:** properties row, second

### `assignee-select`

- **type:** select (with typeahead)
- **selector:** `[data-testid="new-issue-assignee"]`
- **fallback:** `button:has-text("Unassigned")` in the
  properties row
- **location:** properties row, third

### `labels-select`

- **type:** select (multi-select)
- **selector:** `[data-testid="new-issue-labels"]`
- **fallback:** `button:has-text("Add labels")` in the
  properties row
- **location:** properties row, fourth

### `cancel-btn`

- **type:** button
- **selector:** `button:has-text("Cancel")` in the modal
  footer
- **fallback:** `[data-testid="new-issue-cancel"]`
- **location:** bottom-left of the modal
- **note:** dismisses the modal without creating an issue

### `create-btn`

- **type:** button
- **selector:** `button:has-text("Create issue")` in the modal
  footer
- **fallback:** `[data-testid="new-issue-create"]`
- **location:** bottom-right of the modal, primary color
- **note:** disabled if `title-input` is empty

## Edge cases

- **Empty title:** "Create issue" is disabled. The agent
  cannot submit until a title is entered.
- **Modal loses focus:** if the user clicks outside the
  modal, it does NOT close (the click is captured by the
  overlay to dismiss, but the agent using a headless browser
  may experience this differently — see below).
- **Submit while typing:** the agent must wait for the title
  to be entered before clicking create. A common bug is
  clicking create before the input is focused, which causes
  the title to be entered into nothing.
- **Network failure on create:** if the create request fails,
  the modal stays open, a toast appears with "Couldn't create
  issue. Try again." and the title/description are preserved.
  Click `create-btn` again to retry.
- **Slow create (server is slow):** the button shows a
  spinner. The agent must wait for the spinner to complete
  before assuming the issue was created.
- **Modal opened from a filtered list:** if the team view was
  filtered when the modal was opened, the filter is
  preserved when the modal closes. The agent does not need
  to re-apply filters.
