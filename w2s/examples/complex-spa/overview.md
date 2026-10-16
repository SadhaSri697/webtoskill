---
name: trail
domain: app.trail.dev
description: |
  Use app.trail.dev (Trail) to manage issues across teams, view
  notifications, and configure user settings. SPA — most routes
  require authentication, content is dynamic, and "New issue" is
  a modal that overlays the team view rather than a separate
  page.
match:
  - app.trail.dev
  - app.trail.dev/*
---

# Trail — Site Map

## How to navigate

Trail is a single-page application. The URL changes as the user
clicks around, but the page never fully reloads — only the main
column and (sometimes) the URL change. Authentication is required
for everything except `/login` and `/signup`. After logging in, the
default landing page is `/home`.

The app is organized around **teams**. Every team has its own
workspace at `/<team>`, with sub-views for Active issues, Backlog,
and Completed issues. Issues live at `/<team>/issue/<id>`.

## Route map

```mermaid
graph TD
    Login[/login] -->|submit credentials| Home[/home]
    Signup[/signup] -->|create account| Home
    Home -->|click Inbox| Inbox[/inbox]
    Home -->|click team name| TeamView[/:team]
    TeamView -->|click Active tab| Active[/:team/active]
    TeamView -->|click Backlog tab| Backlog[/:team/backlog]
    TeamView -->|click Completed tab| Completed[/:team/completed]
    TeamView -->|click issue title| Issue[/:team/issue/:id]
    TeamView -->|click New issue button| NewIssue[/:team/issue/new modal]
    NewIssue -.->|submit| Issue
    Home -->|click avatar menu| Settings[/settings]
```

## Sub-skills

- `login.md` — matches `/login`
- `signup.md` — matches `/signup`
- `home.md` — matches `/home`
- `inbox.md` — matches `/inbox`
- `team-view.md` — matches `/:team`, `/:team/active`,
  `/:team/backlog`, `/:team/completed`
- `issue.md` — matches `/:team/issue/:id`
- `new-issue.md` — matches `/:team/issue/new` (modal state)
- `settings.md` — matches `/settings`

## Site-wide patterns

- **Top bar (every authenticated page):** logo (left), team
  switcher (center-left), global search (center-right), inbox
  icon, notifications icon, avatar menu (right)
- **Left rail (every authenticated page except login/signup):**
  list of teams the user belongs to, "Add team" button at bottom
- **Main column:** page-specific content
- **No footer in the app.** Marketing/legal links live in a
  separate marketing site at `trail.dev` (out of scope).
- **Modals overlay the main column.** When a modal is open, the
  background page is dimmed but still partially visible.
- **Toasts (bottom-right, ephemeral):** appear for ~5 seconds to
  confirm actions. Do not interact with them — they are
  informational.

## Identity model

- **Logged out:** any route except `/login` and `/signup`
  redirects to `/login` with a `?next=<original-url>` query param.
- **Logged in:** avatar (top-right) shows the user's profile
  picture. Click for menu (Settings, Help, Log out).
- **Session expiry:** after 30 days of inactivity, the session
  expires and the next request redirects to `/login`.

## Global edge cases

- **Auth redirect:** if the agent is not logged in and tries to
  access a protected route, it will be redirected to
  `/login?next=<url>`. The agent should log in first, then
  retry the original URL. (The `login.md` skill documents how.)
- **Loading state:** every authenticated page shows a skeleton
  loader for 200-1500ms while data is fetched. Do not act on the
  page until the skeleton is replaced with real content.
- **Offline state:** if the network drops, a banner appears at
  the top of the page reading "You're offline. Changes will sync
  when you reconnect." The agent should stop and report.
- **Toasts vs persistent notifications:** ephemeral toasts (5s)
  are not the same as inbox notifications. Toasts confirm an
  action; the inbox is the persistent log of notifications.
