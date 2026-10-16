---
name: trail-issue
description: |
  The Trail single-issue view. Shows issue details, comments,
  and the actions available on an issue. Reached by clicking an
  issue row in the team view.
match:
  - /^https:\/\/app\.trail\.dev\/[^/]+\/issue\/[^/]+\/?$/
requires:
  - trail
---

# Trail — Issue Detail

## Page architecture

- **Top bar (inherited from overview)**
- **Left rail (inherited from overview)** — the current team
  is highlighted
- **Main column:**
  - **Issue header:** issue ID (e.g. "TRAIL-42") as breadcrumb,
    issue title (large, editable on click), status badge,
    priority badge, assignee avatar (clickable to reassign)
  - **Sub-header row:** "Back to <team>" link (left), action
    buttons (right): Subscribe, Share, More menu (...)
  - **Body (two-column layout on wide screens, stacked on
    narrow):**
    - **Left column (main):** description (markdown-rendered,
      editable), comments list
    - **Right column (sidebar, 280px):** properties panel
      (Status, Assignee, Priority, Labels, Due date,
      Estimate) — each is a clickable property that opens a
      popover to edit

## Element inventory

### `issue-header`

- **type:** container
- **selector:** `[data-testid="issue-header"]`
- **location:** top of main column
- **contains:** `issue-id`, `issue-title`, `issue-status`,
  `issue-priority`, `issue-assignee`

### `issue-id`

- **type:** static text
- **selector:** `[data-testid="issue-id"]`
- **location:** top-left of the issue header, small text,
  monospace font
- **note:** clicking copies the issue URL to clipboard

### `issue-title`

- **type:** static text (editable)
- **selector:** `[data-testid="issue-title"]`
- **fallback:** `h1` within `issue-header`
- **location:** large text, right of `issue-id`
- **note:** click to edit; an inline editor appears with
  autosave on blur

### `issue-status`

- **type:** badge
- **selector:** `[data-testid="issue-status"]`
- **fallback:** `role=status` within `issue-header`
- **location:** right side of the issue header
- **values:** "Backlog" / "Todo" / "In Progress" / "In Review"
  / "Done" / "Cancelled"

### `back-link`

- **type:** link
- **selector:** `[data-testid="back-to-team"]`
- **fallback:** `a:has-text("Back to")` below the issue
  header
- **location:** top of main column, below the header
- **note:** navigates to the team view (`/:team`)

### `subscribe-btn`

- **type:** button
- **selector:** `button[aria-label="Subscribe"]`
- **fallback:** `button:has-text("Subscribe")` in the
  sub-header
- **location:** right side of sub-header
- **note:** toggles; if subscribed, the icon is filled and the
  label reads "Unsubscribe"

### `more-menu`

- **type:** button (menu trigger)
- **selector:** `button[aria-label="More actions"]`
- **fallback:** `button:has-text("...")` in the sub-header
- **location:** far right of sub-header
- **note:** opens a dropdown with: Copy link, Duplicate,
  Archive, Delete (latter two require permissions)

### `description`

- **type:** static text (editable, markdown-rendered)
- **selector:** `[data-testid="issue-description"]`
- **fallback:** `.description` within main column
- **location:** left column, below sub-header
- **note:** click to edit; an inline markdown editor appears
  with a preview tab

### `comments-list`

- **type:** container
- **selector:** `[data-testid="comments-list"]`
- **location:** left column, below `description`
- **contains:** `comment` (repeatable, ordered oldest first)

### `comment` (repeatable)

- **type:** repeatable
- **selector:** `[data-testid="comment"]`
- **location:** list in left column
- **contains:** `comment-author` (avatar + name), `comment-
  body` (markdown-rendered), `comment-timestamp`, `comment-
  actions` (Edit, Delete — author only)

### `comment-input`

- **type:** textarea
- **selector:** `[data-testid="comment-input"]`
- **fallback:** `textarea` at the bottom of the comments list
- **location:** bottom of left column
- **note:** supports `@mentions` (type `@` to see a user list),
  markdown, file attachments (drag/drop or click the paperclip
  icon)

### `comment-submit`

- **type:** button
- **selector:** `button:has-text("Comment")` near
  `comment-input`
- **fallback:** `button[type="submit"]` for the comment form
- **location:** bottom-right of `comment-input`
- **note:** disabled when `comment-input` is empty

### `property-status`

- **type:** property (popover trigger)
- **selector:** `[data-testid="property-status"]`
- **fallback:** `[aria-label="Status"]` in the sidebar
- **location:** right column, first property
- **note:** click to open a popover with status options

### `property-assignee`

- **type:** property (popover trigger)
- **selector:** `[data-testid="property-assignee"]`
- **fallback:** `[aria-label="Assignee"]` in the sidebar
- **location:** right column, second property

### `property-priority`

- **type:** property (popover trigger)
- **selector:** `[data-testid="property-priority"]`
- **fallback:** `[aria-label="Priority"]` in the sidebar
- **location:** right column, third property
- **values:** "No priority" / "Urgent" / "High" / "Medium" /
  "Low"

### `property-labels`

- **type:** property (popover trigger)
- **selector:** `[data-testid="property-labels"]`
- **fallback:** `[aria-label="Labels"]` in the sidebar
- **location:** right column, fourth property

## Edge cases

- **Loading state:** the entire main column shows a skeleton
  for 200-1500ms. Wait for the issue header and properties
  to render before acting.
- **Archived issue:** if the issue is archived, the header
  shows a yellow "Archived" badge and most actions are
  disabled. The only available actions are: View history,
  Restore (admin only).
- **No description:** "Add a description..." placeholder text
  in `description`. Click to add.
- **No comments yet:** `comments-list` is empty; the input
  shows "Add a comment..." placeholder.
- **Permission denied:** if the user is a viewer (not a
  member) of the team, all edit affordances (title,
  description, properties, comment) are disabled with
  tooltips "You don't have permission to edit this issue."
- **Optimistic update failure:** if a property change (status,
  assignee, etc.) is rejected by the server, the property
  reverts to its previous value and a toast appears with the
  error message. Report to the user.
- **Conflicting edit:** if another user edited the issue
  while you were viewing it, a banner appears at the top of
  the page: "This issue was updated by <user> <time ago>.
  Reload to see the latest." Reload and re-read the issue
  before continuing.
