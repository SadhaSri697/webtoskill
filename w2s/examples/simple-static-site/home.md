---
name: harvestgrove-home
description: |
  The Harvest Grove marketing homepage. Hero section, three
  feature blocks, and a call-to-action at the bottom.
match:
  - /^https:\/\/harvestgrove\.com\/?$/
requires:
  - harvestgrove
---

# Harvest Grove — Homepage

## Page architecture

- **Header (inherited from overview):** logo + nav (Pricing, Sign
  up, Log in)
- **Hero (top of main column):** headline, subhead, two CTAs
  ("Get started" → `/signup`, "View pricing" → `/pricing`)
- **Features section:** three feature blocks in a row, each with
  an icon, title, and short description
- **Testimonial section:** a single pull quote from a customer
- **Final CTA (bottom of main column):** "Ready to get started?"
  with a "Sign up free" button
- **Footer (inherited from overview)**

## Element inventory

### `hero-cta-signup`

- **type:** link
- **selector:** `[data-testid="hero-cta-signup"]`
- **fallback:** `a:has-text("Get started")` in the hero section
- **location:** hero section, right side, primary button

### `hero-cta-pricing`

- **type:** link
- **selector:** `[data-testid="hero-cta-pricing"]`
- **fallback:** `a:has-text("View pricing")` in the hero section
- **location:** hero section, right side, secondary button (left
  of `hero-cta-signup`)

### `feature-block` (repeatable)

- **type:** repeatable
- **selector:** `[data-testid="feature-block"]`
- **location:** three blocks in a horizontal row, middle of page
- **contains:** `feature-icon`, `feature-title`, `feature-body`

### `testimonial-quote`

- **type:** static text
- **selector:** `[data-testid="testimonial-quote"]`
- **location:** centered in the testimonial section

### `final-cta-signup`

- **type:** link
- **selector:** `[data-testid="final-cta-signup"]`
- **fallback:** `a:has-text("Sign up free")`
- **location:** bottom CTA section, centered

### `nav-pricing`

- **type:** link
- **selector:** `nav [data-testid="nav-pricing"]`
- **fallback:** `nav a:has-text("Pricing")`
- **location:** header, right side

### `nav-signup`

- **type:** link
- **selector:** `nav [data-testid="nav-signup"]`
- **fallback:** `nav a:has-text("Sign up")`
- **location:** header, right side

### `nav-login`

- **type:** link
- **selector:** `nav [data-testid="nav-login"]`
- **fallback:** `nav a:has-text("Log in")`
- **location:** header, right side

## Edge cases

- None. Static site with no dynamic state.
