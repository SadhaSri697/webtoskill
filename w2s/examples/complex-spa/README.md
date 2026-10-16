# Example: complex SPA

A worked end-to-end example of compiling a single-page application
(SPA) into a w2s skill. Use this after studying
`../simple-static-site/` to see how the same structure adapts to
dynamic, authenticated, content-heavy apps.

## The site

A fictional project management tool — "Trail." SPA built on a
modern frontend framework. Client-side routing. Authenticated.
Dynamic content. Modals. Infinite scroll. The realistic case.

| Route | Purpose |
|-------|---------|
| `/login` | Login form (public) |
| `/signup` | Signup form (public) |
| `/home` | Dashboard with recent activity |
| `/inbox` | Notifications inbox |
| `/<team>` | Team view with sub-tabs (Active, Backlog, Completed) |
| `/<team>/issue/<id>` | Single issue view |
| `/<team>/issue/new` | Create-issue modal-trigger |
| `/settings` | User settings (profile, account, notifications) |

Fictional domain: `app.trail.dev`.

## What makes this harder than the static example

1. **Authentication.** Most routes require login. The agent must
   detect logged-in vs logged-out state and bail out (or sign in)
   before acting.
2. **Modals and overlays.** "New issue" opens as a modal on top of
   the team view, not as a separate route. The skill must describe
   the modal state, the trigger, and how to dismiss it.
3. **Dynamic content.** The team view loads more issues as you
   scroll. The skill must warn the agent not to act until
   scrolling has finished.
4. **Sub-navigation.** `/<team>` has sub-tabs (Active, Backlog,
   Completed) that are URL-driven but visually a single page. The
   agent must know that the URL pattern covers all three tabs.
5. **Asynchronous state changes.** Marking an issue "complete" is
   optimistic — the UI updates before the server confirms. The
   skill must tell the agent to wait for server confirmation
   before assuming the change persisted.

## The user's request

> "Make a skill for app.trail.dev so my agent can manage issues in
> my team. I want it to be able to read the team backlog, create
> new issues, and mark issues as done."

## The URLs the agent compiled

```text
https://app.trail.dev/login
https://app.trail.dev/signup
https://app.trail.dev/home
https://app.trail.dev/inbox
https://app.trail.dev/acme
https://app.trail.dev/acme/backlog
https://app.trail.dev/acme/active
https://app.trail.dev/acme/completed
https://app.trail.dev/acme/issue/TRAIL-42
https://app.trail.dev/acme/issue/new
https://app.trail.dev/settings
```

## The grouping decision

| URL | Path shape | Family | Filename |
|-----|-----------|--------|----------|
| `app.trail.dev/login` | `/login` | login | `login.md` |
| `app.trail.dev/signup` | `/signup` | signup | `signup.md` |
| `app.trail.dev/home` | `/home` | dashboard | `home.md` |
| `app.trail.dev/inbox` | `/inbox` | inbox | `inbox.md` |
| `app.trail.dev/<team>` | `/:team` | team view | `team-view.md` |
| `app.trail.dev/<team>/active` | `/:team/active` | team view | `team-view.md` |
| `app.trail.dev/<team>/backlog` | `/:team/backlog` | team view | `team-view.md` |
| `app.trail.dev/<team>/completed` | `/:team/completed` | team view | `team-view.md` |
| `app.trail.dev/<team>/issue/<id>` | `/:team/issue/:id` | issue detail | `issue.md` |
| `app.trail.dev/<team>/issue/new` | `/:team/issue/new` | new issue | `new-issue.md` |
| `app.trail.dev/settings` | `/settings` | settings | `settings.md` |

Seven families (login, signup, dashboard, inbox, team-view, issue,
new-issue, settings), but only seven `SKILL.md` files because
multiple URLs share families.

## The output files

- [`overview.md`](./overview.md)
- [`login.md`](./login.md)
- [`signup.md`](./signup.md)
- [`home.md`](./home.md)
- [`inbox.md`](./inbox.md)
- [`team-view.md`](./team-view.md)
- [`issue.md`](./issue.md)
- [`new-issue.md`](./new-issue.md)
- [`settings.md`](./settings.md)

## What to learn from this example

1. **Group aggressively when structure is shared.** The four
   `team-view` URLs all share the same page chrome, layout, and
   elements. One skill file covers all four.
2. **Distinguish "page" from "modal" carefully.** "New issue" is
   a modal that overlays the team view, not a separate page. The
   URL changes but the user never navigates away. The
   `new-issue.md` skill documents the modal state, not a
   standalone page.
3. **Document loading and async states explicitly.** Dynamic SPAs
   need explicit "wait for X" steps in workflows. Static sites
   do not.
4. **Be honest about the auth wall.** The `team-view` skill says
   "if you are not logged in, the page redirects to `/login`"
   and the agent is expected to handle that.
5. **Selectors get weaker on SPAs.** Many SPAs use framework-
   generated class names. The example uses `data-testid` where
   the site provides them, `aria-label` as fallback, and
   occasionally `role=` selectors when test IDs are absent.
6. **Workflows span multiple files.** "Mark an issue complete"
   starts in `team-view.md` (find the issue), jumps to
   `issue.md` (open it), and uses the `mark-complete` action
   documented in `issue.md`. The skills compose.
