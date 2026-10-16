---
name: trail-team-view
description: |
  The Trail team view. Main workspace for a single team. Shows
  a list of issues with sub-tabs for Active, Backlog, and
  Completed. Includes the "New issue" trigger.
match:
  - /^https:\/\/app\.trail\.dev\/[^/]+\/?$/
  - /^https:\/\/app\.trail\.dev\/[^/]+\/(active|backlog|completed)\/?$/
requires:
  - trail
---

# Trail — Team View

This skill covers the team workspace and all three of its
sub-tabs. The sub-tabs (Active, Backlog, Completed) are
URL-driven but visually a single page — they share the same
layout, filters, and element inventory. They differ only in
which issues are listed.

## Page architecture

- **Top bar (inherited from overview)**
- **Left rail (inherited from overview)** — the current team
  is highlighted
- **Main column:**
  - **Team header:** team name (left), team avatar, member
    count, settings gear (right, only for admins)
  - **Tab bar:** Active / Backlog / Completed tabs (with
    counts on each), filter button (right), sort dropdown
    (right of filter), "New issue" button (right, primary)
  - **Issue list:** rows of issues, each showing title,
    status badge, priority, assignee avatar, labels, last-
    updated timestamp. Infinite scroll — more issues load as
    you scroll.

## Element inventory

### `team-header`

- **type:** container
- **selector:** `[data-testid="team-header"]`
- **location:** top of main column
- **contains:** `team-name`, `team-avatar`, `team-member-count`,
  `team-settings-link` (admin only)

### `tab-active`

- **type:** tab
- **selector:** `[data-testid="tab-active"]`
- **fallback:** `role=tab[name="Active"]`
- **location:** tab bar, first position
- **note:** URL is `/:team` or `/:team/active`; the count is
  shown to the right of the label

### `tab-backlog`

- **type:** tab
- **selector:** `[data-testid="tab-backlog"]`
- **fallback:** `role=tab[name="Backlog"]`
- **location:** tab bar, second position
- **note:** URL is `/:team/backlog`; the count is shown to the
  right of the label

### `tab-completed`

- **type:** tab
- **selector:** `[data-testid="tab-completed"]`
- **fallback:** `role=tab[name="Completed"]`
- **location:** tab bar, third position
- **note:** URL is `/:team/completed`; the count is shown to
  the right of the label

### `filter-button`

- **type:** button
- **selector:** `button[aria-label="Filter"]`
- **fallback:** `button:has-text("Filter")` in the tab bar
- **location:** right side of the tab bar
- **note:** opens a popover with assignee / label / priority
  filters; the button's badge shows the active filter count

### `sort-dropdown`

- **type:** select
- **selector:** `button[aria-haspopup="listbox"]` in the tab
  bar
- **fallback:** `button:has-text("Sort")` in the tab bar
- **location:** right of `filter-button`
- **note:** options are "Last updated," "Created," "Priority,"
  "Title"

### `new-issue-btn`

- **type:** button
- **selector:** `[data-testid="new-issue-btn"]`
- **fallback:** `button:has-text("New issue")` in the tab bar
- **location:** far right of the tab bar, primary color
- **note:** opens the new-issue modal (see `new-issue.md`)

### `issue-list`

- **type:** container
- **selector:** `[data-testid="issue-list"]`
- **location:** below the tab bar
- **contains:** `issue-row` (repeatable, up to 50 per page;
  more load on scroll)

### `issue-row` (repeatable)

- **type:** repeatable
- **selector:** `[data-testid="issue-row"]`
- **fallback:** `role=listitem` within `issue-list`
- **location:** vertical list, fills the main column
- **contains:**
  - `issue-id` (text, e.g. "TRAIL-42")
  - `issue-title` (link, opens the issue)
  - `issue-priority` (badge, color-coded)
  - `issue-status` (badge, color-coded)
  - `issue-assignee` (avatar)
  - `issue-labels` (list of label chips)
  - `issue-updated` (relative time, e.g. "2h ago")

## Edge cases

- **Empty state:** if the active sub-tab has no issues, the
  list area shows an illustration and a message ("No active
  issues — you're all caught up!" for Active, "Nothing in the
  backlog" for Backlog, "No completed issues yet" for
  Completed).
- **Loading state:** when switching tabs or scrolling, the
  list shows skeleton rows (gray boxes) for 200-1500ms. Do
  not act on the page until real rows appear.
- **Infinite scroll:** the list loads 50 issues at a time.
  When you scroll within 200px of the bottom, more rows are
  fetched. If the list does not contain the issue you are
  looking for, you may need to scroll. To know if you have
  reached the end, look for "No more issues" text at the
  bottom of the list.
- **Filter persists across tabs:** if you set a filter (e.g.
  "assignee: me"), it stays active when you switch tabs. The
  filter badge on `filter-button` shows the count.
- **Optimistic updates:** "mark complete" updates the UI
  immediately, but the server may reject the change (e.g.
  permissions, archived issue). If rejected, the row
  reappears and a toast reads "Couldn't mark TRAIL-42 as done"
  with a "Retry" button.
- **No permission to create:** if the user is a viewer (not
  a member) of the team, `new-issue-btn` is disabled with a
  tooltip "You don't have permission to create issues in this
  team."
