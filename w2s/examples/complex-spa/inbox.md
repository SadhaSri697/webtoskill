---
name: trail-inbox
description: |
  The Trail notifications inbox. List of notifications grouped
  by date (Today, Yesterday, This week, Earlier). Click a
  notification to navigate to the related issue.
match:
  - /^https:\/\/app\.trail\.dev\/inbox\/?$/
requires:
  - trail
---

# Trail — Inbox

## Page architecture

- **Top bar (inherited from overview)**
- **Left rail (inherited from overview)**
- **Main column:**
  - Header row: "Inbox" title (left), filter dropdown
    (right: All / Unread / Mentions), "Mark all as read" link
  - Notification groups, ordered most-recent first:
    - **Today** section
    - **Yesterday** section
    - **This week** section
    - **Earlier** section
  - Each group is a list of notification-item rows

## Element inventory

### `inbox-header`

- **type:** container
- **selector:** `[data-testid="inbox-header"]`
- **location:** top of main column
- **contains:** `inbox-title`, `filter-dropdown`,
  `mark-all-read-link`

### `filter-dropdown`

- **type:** select
- **selector:** `button[aria-haspopup="listbox"]`
- **fallback:** `button:has-text("All")` next to the inbox
  title
- **location:** right side of `inbox-header`
- **note:** the button's text shows the current filter
  ("All" / "Unread" / "Mentions")

### `mark-all-read-link`

- **type:** link
- **selector:** `a:has-text("Mark all as read")`
- **fallback:** `[data-testid="mark-all-read"]`
- **location:** right side of `inbox-header`, right of the
  filter dropdown

### `notification-group`

- **type:** container (repeatable — one per time bucket)
- **selector:** `[data-testid^="inbox-group-"]` (e.g.
  `inbox-group-today`, `inbox-group-yesterday`,
  `inbox-group-this-week`, `inbox-group-earlier`)
- **location:** stacked vertically below `inbox-header`
- **contains:** `group-label` (static text), `notification-item`
  (repeatable, list)

### `notification-item` (repeatable)

- **type:** repeatable
- **selector:** `[data-testid="notification-item"]`
- **location:** rows within each `notification-group`
- **contains:**
  - `notification-icon` (small icon, type of notification)
  - `notification-text` (the message, may include links)
  - `notification-timestamp` (relative time, e.g. "2h ago")
  - `notification-unread-dot` (blue dot if unread; absent if
    read)
- **action:** clicking the row navigates to the related
  resource (issue, comment, etc.)

## Edge cases

- **Empty inbox:** "No notifications" message in the main
  column with a small illustration.
- **Loading state:** `notification-group` rows show skeleton
  loaders for 200-1500ms. Wait for real content.
- **Real-time updates:** new notifications appear at the top
  of the "Today" group as they arrive, with a brief slide-in
  animation. The agent may see rows that did not exist a
  moment ago — this is normal, not a bug.
- **Pagination:** if there are >100 notifications in
  "Earlier," a "Load more" button appears at the bottom of
  that group. Click to load the next 100.
