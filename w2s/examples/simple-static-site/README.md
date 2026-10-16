# Example: simple static site

A worked end-to-end example of compiling a small, mostly-static
website into a w2s skill. Use this to learn what good output looks
like before compiling a real site.

## The site

A small marketing site for a fictional product. Four routes, all
served as static HTML. No login, no SPAs, no dynamic content. The
"simplest useful" case.

| Route | Purpose |
|-------|---------|
| `/` | Marketing homepage |
| `/pricing` | Pricing page with two plan cards |
| `/signup` | Email capture form |
| `/login` | Login form |

Fictional domain: `harvestgrove.com`. The site is rendered as plain
HTML with semantic markup (`<header>`, `<nav>`, `<main>`, `<footer>`)
and stable `data-testid` attributes on interactive elements.

## The user's request

> "Make a skill for harvestgrove.com so my agent can sign up new
> users and check pricing."

## The URLs the agent compiled

```text
https://harvestgrove.com/
https://harvestgrove.com/pricing
https://harvestgrove.com/signup
https://harvestgrove.com/login
```

## The grouping decision

| URL | Path shape | Family | Filename |
|-----|-----------|--------|----------|
| `harvestgrove.com/` | `/` | homepage | `home.md` |
| `harvestgrove.com/pricing` | `/pricing` | pricing | `pricing.md` |
| `harvestgrove.com/signup` | `/signup` | signup | `signup.md` |
| `harvestgrove.com/login` | `/login` | login | `login.md` |

Four families, four files, plus the overview.

## The output files

- [`overview.md`](./overview.md) — the site map
- [`home.md`](./home.md) — the homepage skill
- [`pricing.md`](./pricing.md) — the pricing page skill
- [`signup.md`](./signup.md) — the signup page skill
- [`login.md`](./login.md) — the login page skill

## What to learn from this example

1. **Selectors are simple.** Static sites with semantic HTML and
   test IDs make selector choice trivial. Real sites rarely do.
2. **Workflows are short.** 2-3 steps each. No complex
   multi-page workflows.
3. **Edge cases are minimal.** Static sites do not have modals,
   loading states, or auth walls. The "edge cases" section is
   short or empty.
4. **The overview is small.** Four routes fit on one page. Real
   sites need to be selective about which routes appear in the
   mermaid graph.

After studying this, look at `../complex-spa/` to see how the
same structure scales (or has to be adapted) for a single-page
application.