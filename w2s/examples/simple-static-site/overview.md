---
name: harvestgrove
domain: harvestgrove.com
description: |
  Use harvestgrove.com to view the marketing site, check pricing,
  sign up for an account, and log in. Static HTML site, no SPA,
  no dynamic content beyond standard form submissions.
match:
  - harvestgrove.com
  - harvestgrove.com/*
---

# Harvest Grove — Site Map

## How to navigate

Harvest Grove is a four-page marketing site. The homepage is the
entry point; pricing, signup, and login are top-level routes
reached from the global nav. There is no logged-in dashboard —
once a user signs up, they are redirected to a separate app at
`app.harvestgrove.com` (out of scope for this skill).

## Route map

```mermaid
graph TD
    Home[harvestgrove.com/] -->|click Pricing in nav| Pricing[/pricing]
    Home -->|click Sign up in nav| Signup[/signup]
    Home -->|click Log in in nav| Login[/login]
    Pricing -->|click Get started| Signup
    Pricing -->|click Log in| Login
```

## Sub-skills

- `home.md` — matches `/` (the homepage)
- `pricing.md` — matches `/pricing`
- `signup.md` — matches `/signup`
- `login.md` — matches `/login`

## Site-wide patterns

- **Header (every page):** logo top-left links to home; nav links
  for "Pricing," "Sign up," and "Log in" top-right
- **Footer (every page):** copyright text, links to "Privacy" and
  "Terms" (external, do not compile)
- **No modals, banners, or overlays.** Static site.
- **No authentication state on marketing pages.** All four routes
  are public.

## Identity model

There is no logged-in state on the marketing site. If the user
arrives at `app.harvestgrove.com` (the post-login app), this skill
does not apply — the app is a separate domain and out of scope.

## Global edge cases

- None. The site is fully static. Forms submit to a separate
  endpoint and the user is redirected externally.
