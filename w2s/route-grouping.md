# route-grouping.md

How to group a list of compiled URLs into route families, where
each family gets its own `SKILL.md`. Load this file before grouping
URLs in Step 3 of the methodology.

The goal: each `SKILL.md` describes ONE page structure. URLs that
render the same structure (with different data) belong to the same
family. URLs that render a structurally different page belong to
different families.

## The basic rule

Two URLs belong to the same family if they have the same path SHAPE
after collapsing dynamic segments.

A "dynamic segment" is a path component that varies per-resource
(owner name, repo name, user ID, issue number, etc.). Replace each
dynamic segment with a typed placeholder:

- `:owner` — username or org name (e.g. `foo`, `bar`)
- `:name` — repo name, project name, etc.
- `:id` — numeric ID (issue number, user ID, etc.)
- `:slug` — human-readable slug (post slug, article slug)

After replacement, URLs that have the same path belong to the same
family.

## Worked examples

### github.com

| URL | Path shape | Family |
|-----|-----------|--------|
| `github.com/foo` | `/foo` | `org` |
| `github.com/foo/bar` | `/:owner/:name` | `repo` |
| `github.com/baz/qux` | `/:owner/:name` | `repo` |
| `github.com/foo/bar/issues` | `/:owner/:name/issues` | `issues` |
| `github.com/foo/bar/issues/42` | `/:owner/:name/issues/:id` | `issues` |
| `github.com/foo/bar/pulls` | `/:owner/:name/pulls` | `pulls` |
| `github.com/foo/bar/pull/123` | `/:owner/:name/pull/:id` | `pulls` |
| `github.com/foo/bar/settings` | `/:owner/:name/settings` | `settings` |
| `github.com/foo/bar/settings/branches` | `/:owner/:name/settings/branches` | `settings` |
| `github.com/settings/profile` | `/settings/profile` | `user-settings` |

`/:owner/:name/issues` and `/:owner/:name/issues/:id` are the same
family — the list view and detail view share a structure, with the
detail view just being the list view with one item focused.

### app.linear.app

| URL | Path shape | Family |
|-----|-----------|--------|
| `linear.app` | `/` | `home` |
| `linear.app/inbox` | `/inbox` | `inbox` |
| `linear.app/foo` | `/:team` | `team` |
| `linear.app/foo/active` | `/:team/active` | `team-view` |
| `linear.app/foo/issue/BAR-123` | `/:team/issue/:id` | `issue` |
| `linear.app/foo/cycles` | `/:team/cycles` | `cycles` |
| `linear.app/settings` | `/settings` | `settings` |

`/foo/active`, `/foo/backlog`, `/foo/completed` all map to
`team-view` — they share structure, only the filter tab differs.

## Naming files

For each family, pick a short, kebab-case filename that describes
the family. The filename becomes the skill name. Conventions:

- Use the most natural name for the family
- Prefer a single word when possible (`repo`, `issues`, `pulls`,
  `settings`, `home`, `inbox`)
- Use hyphens for multi-word (`user-settings`, `team-view`)
- For parameterized views, the name is the noun
  (`issue`, not `issue-detail` or `issue-view`)

Good names: `repo`, `issues`, `pulls`, `settings`, `home`, `inbox`,
`issue`, `cycle`, `user-settings`, `org-settings`, `team-view`.

Bad names: `repo-main-page`, `issues-list-and-detail-combined`,
`page-1`, `route-family-A`.

## Query parameters, hashes, and fragments

**Query parameters** (`?tab=open&assignee=foo`): Ignore them for
grouping purposes. They are filters/state, not routes. If the page
has fundamentally different layouts based on a query param
(some sites do), treat each layout as a separate family.

**Hash fragments** (`#issuecomment-1234`): Ignore them. They scroll
the page but do not change the structure.

**Trailing slashes** (`/foo/` vs `/foo`): Treat as the same family.
Most servers normalize this.

## When to split

Split a family into multiple `SKILL.md` files when:

- The page structure is genuinely different. Example: a list view
  and a detail view are usually the same family (the detail view
  is just the list view with focus), but a list view and an edit
  view are usually different families.
- The element inventory would be >2x larger if combined. If
  splitting keeps each file under ~150 lines, split.
- The workflows have nothing in common. If the list view and
  detail view have entirely different tasks, they probably want
  different files.

When in doubt, start with the broader grouping. Splitting later is
easier than merging.

## When to merge

Merge two families into one `SKILL.md` when:

- They share a header, footer, and 80%+ of the layout
- The only differences are a few sub-tabs or filters
- The workflows share setup steps (e.g. "navigate to the repo,
  then...")

The `team-view` example above is a merge — `/:team/active`,
`/:team/backlog`, and `/:team/completed` all share a structure and
differ only in the active tab.

## Special cases

### The homepage

The homepage is always its own family, named `home` (or `homepage`
if it is long-form). The homepage often has a very different
structure from the rest of the site.

### Authentication pages

`/login`, `/signup`, `/forgot-password`, `/logout` are usually
distinct families from each other, but separate from the main
app. Consider whether to compile them — most agents do not need
a skill to log in (the user does it manually first). If you do
compile them, name them `login`, `signup`, etc.

### Settings pages

`/settings`, `/settings/profile`, `/settings/account`,
`/settings/security` are usually the same family (`settings`) if
they share a left-rail navigation pattern. They are different
families if each is a standalone page with no shared chrome.

### 404 / error pages

If you encounter a 404 while distilling, that is a real
observation — record it as a "broken URL" edge case in the
relevant skill and move on. Do not compile a separate `404.md`
unless the user specifically asks for error handling.

### Redirects

If a URL redirects to another URL, follow the redirect and use
the destination's structure. Note the redirect in the source
URL's "Edge cases" section.

## The output

After grouping, you should have a list of families, each with:

- A name (kebab-case filename)
- A list of URLs that belong to it
- The path shape (e.g. `/:owner/:name/issues/:id`)

This list is the input to Step 4 of the methodology, where you
write one `SKILL.md` per family.