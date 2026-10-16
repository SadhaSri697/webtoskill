---
name: trail-settings
description: |
  The Trail user settings page. Left rail of settings categories
  (Profile, Account, Notifications, Appearance, Integrations),
  main column shows the selected category's settings.
match:
  - /^https:\/\/app\.trail\.dev\/settings\/?$/
  - /^https:\/\/app\.trail\.dev\/settings\/.*$/
requires:
  - trail
---

# Trail — Settings

## Page architecture

- **Top bar (inherited from overview)**
- **Left rail (inherited from overview)**
- **Settings rail (in main column, 240px):** vertical list of
  settings categories — Profile, Account, Notifications,
  Appearance, Integrations, Billing
- **Settings panel (right of the settings rail):** the
  selected category's settings form
- **No left rail navigation in the team sense** — the
  left rail is still present, but the user is in "settings
  context" and the team list is dimmed

## Element inventory

### `settings-rail`

- **type:** container
- **selector:** `[data-testid="settings-rail"]`
- **location:** main column, left
- **contains:** `settings-nav-item` (repeatable, one per
  category)

### `settings-nav-item` (repeatable)

- **type:** link
- **selector:** `[data-testid^="settings-nav-"]` (e.g.
  `settings-nav-profile`, `settings-nav-account`,
  `settings-nav-notifications`, `settings-nav-appearance`,
  `settings-nav-integrations`, `settings-nav-billing`)
- **fallback:** `a:has-text("<category>")` in `settings-rail`
- **location:** vertical list in `settings-rail`
- **note:** the active category is highlighted

### `settings-panel`

- **type:** container
- **selector:** `[data-testid="settings-panel"]`
- **location:** main column, right of `settings-rail`
- **contains:** category-specific fields, varies by route
- **note:** the URL determines which panel is shown
  (`/settings/profile` shows the Profile panel, etc.)

### `panel-header`

- **type:** container
- **selector:** `[data-testid="panel-header"]`
- **location:** top of `settings-panel`
- **contains:** `panel-title` (static text), `panel-save-status`
  (e.g. "Saved," "Unsaved changes," "Saving...")

### `panel-save-btn`

- **type:** button
- **selector:** `button:has-text("Save")` in the
  `settings-panel` header
- **fallback:** `[data-testid="panel-save"]`
- **location:** top-right of `settings-panel`
- **note:** only enabled if there are unsaved changes; some
  panels autosave (toggle switches)

## Edge cases

- **Unsaved changes warning:** if the user navigates away from
  a panel with unsaved changes, a browser confirm dialog
  appears: "You have unsaved changes. Leave anyway?" The
  agent should click "Cancel" to stay, save the changes, then
  navigate away.
- **Billing requires admin:** if the user is not a billing
  admin, `/settings/billing` shows a panel reading "You don't
  have permission to view billing settings." Click
  `settings-nav-billing` is still allowed (URL changes), but
  the panel content is restricted.
- **Integrations require team context:** some integrations
  (e.g. GitHub) require the user to be in at least one team
  and have admin permissions on it. The panel will say which
  team the integration applies to.
- **Account deletion:** the Account panel has a "Delete
  account" button at the bottom. This is irreversible and
  requires typing the user's email to confirm. The agent
  should NOT perform this action without explicit user
  confirmation, regardless of the task.
