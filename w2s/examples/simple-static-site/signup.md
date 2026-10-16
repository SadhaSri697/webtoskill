---
name: harvestgrove-signup
description: |
  The Harvest Grove signup page. Email capture form that creates
  a new account and redirects to app.harvestgrove.com.
match:
  - /^https:\/\/harvestgrove\.com\/signup(\?.*)?$/
requires:
  - harvestgrove
---

# Harvest Grove — Signup Page

## Page architecture

- **Header (inherited from overview):** logo + nav
- **Form container (centered, ~400px wide):**
  - Heading: "Create your account"
  - Subheading (if `?plan=pro` or `?plan=free` in URL): shows
    selected plan ("You selected: Pro" or "You selected: Free")
  - Email field
  - Password field
  - "Create account" submit button
  - Link to "/login" for existing users
- **Footer (inherited from overview)**

## Element inventory

### `signup-form`

- **type:** form
- **selector:** `[data-testid="signup-form"]`
- **location:** centered in main column
- **contains:** `email-input`, `password-input`, `submit-btn`

### `email-input`

- **type:** input
- **selector:** `[data-testid="signup-email"]`
- **fallback:** `input[type="email"]` inside `signup-form`
- **location:** first field in the form

### `password-input`

- **type:** input
- **selector:** `[data-testid="signup-password"]`
- **fallback:** `input[type="password"]` inside `signup-form`
- **location:** second field in the form, below email

### `submit-btn`

- **type:** button (submit)
- **selector:** `[data-testid="signup-submit"]`
- **fallback:** `button[type="submit"]` inside `signup-form`
- **location:** below the password field, full-width

### `login-link`

- **type:** link
- **selector:** `[data-testid="signup-to-login"]`
- **fallback:** `a:has-text("Log in")` inside `signup-form`
- **location:** below the submit button, small text

### `plan-indicator`

- **type:** static text (only present if URL has `?plan=...`)
- **selector:** `[data-testid="signup-plan-indicator"]`
- **location:** below the heading, above the form fields
- **action:** read-only; shows selected plan ("You selected:
  Pro" or "You selected: Free")

### `error-banner`

- **type:** static text (displayed conditionally)
- **selector:** `[data-testid="signup-error"]`
- **location:** above the form, red text
- **action:** read-only; displays error message

## Forms

**`signup-form`** (defined in Element inventory)

- **trigger:** page load (signup form is the only thing on the page)
- **submit-btn:** `submit-btn` (destructive)
- **fields:**
  - `email-input` — text, required, accepts email format
  - `password-input` — password, required, min 8 chars
- **validation:**
  - Empty email shows "Email is required" below `email-input`
  - Invalid email format shows "Please enter a valid email"
  - Empty password shows "Password is required" below
    `password-input`
  - Password < 8 chars shows "Password must be at least 8
    characters"
- **on success:** redirects to `app.harvestgrove.com/onboarding`
  (out of scope for this skill)
- **on error:** stays on `/signup`, shows `error-banner` above
  the form

## States

### `plan-pre-selected`

- **trigger:** URL contains `?plan=pro` or `?plan=free`
- **dismiss:** N/A — persists for the duration of the page
- **contains:** `plan-indicator` showing the selected plan
- **notes:** the new account inherits the selected plan

### `error-state`

- **trigger:** validation error on submit (e.g. duplicate email)
- **dismiss:** correct the field OR navigate away
- **contains:** `error-banner` with the error message
- **notes:** "An account with this email already exists" is
  shown for duplicate emails

### `rate-limited-state`

- **trigger:** more than 5 failed attempts from same IP in 10
  minutes
- **dismiss:** wait for the rate limit window to expire
- **contains:** `error-banner` with "Too many attempts. Please
  try again later."
- **notes:** runtime agents should stop and report to the user
  when this state is detected

## Edge cases

- **Validation errors:**
  - Empty email: error "Email is required" below `email-input`
  - Invalid email format: error "Please enter a valid email"
  - Empty password: error "Password is required"
  - Password too short: error "Password must be at least 8
    characters"
- **Plan pre-selected via URL:** if `?plan=pro` is in the URL,
  `plan-indicator` reads "You selected: Pro" and the new account
  will be created on the Pro plan. Same for `?plan=free`.
- **Rate limiting:** after 5 failed attempts from the same IP
  in 10 minutes, the form is temporarily disabled and shows
  "Too many attempts. Please try again later." Stop and report
  to the user.
