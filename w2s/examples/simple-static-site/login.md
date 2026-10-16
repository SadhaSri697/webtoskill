---
name: harvestgrove-login
description: |
  The Harvest Grove login page. Email and password form that
  authenticates and redirects to app.harvestgrove.com.
match:
  - /^https:\/\/harvestgrove\.com\/login(\?.*)?$/
requires:
  - harvestgrove
---

# Harvest Grove — Login Page

## Page architecture

- **Header (inherited from overview):** logo + nav
- **Form container (centered, ~400px wide):**
  - Heading: "Log in to your account"
  - Email field
  - Password field
  - "Log in" submit button
  - "Forgot password?" link
  - Link to "/signup" for new users
- **Footer (inherited from overview)**

## Element inventory

### `login-form`

- **type:** form
- **selector:** `[data-testid="login-form"]`
- **location:** centered in main column
- **contains:** `email-input`, `password-input`, `submit-btn`

### `email-input`

- **type:** input
- **selector:** `[data-testid="login-email"]`
- **fallback:** `input[type="email"]` inside `login-form`
- **location:** first field in the form

### `password-input`

- **type:** input
- **selector:** `[data-testid="login-password"]`
- **fallback:** `input[type="password"]` inside `login-form`
- **location:** second field in the form, below email

### `submit-btn`

- **type:** button (submit)
- **selector:** `[data-testid="login-submit"]`
- **fallback:** `button[type="submit"]` inside `login-form`
- **location:** below the password field, full-width

### `forgot-password-link`

- **type:** link
- **selector:** `[data-testid="login-forgot-password"]`
- **fallback:** `a:has-text("Forgot password?")` inside
  `login-form`
- **location:** right-aligned, below the password field

### `signup-link`

- **type:** link
- **selector:** `[data-testid="login-to-signup"]`
- **fallback:** `a:has-text("Sign up")` inside `login-form`
- **location:** below the submit button, small text
- **action:** navigates to `/signup`

### `error-banner`

- **type:** static text (displayed conditionally)
- **selector:** `[data-testid="login-error"]`
- **location:** above the form, red text
- **action:** read-only; displays error message

## Forms

**`login-form`** (defined in Element inventory)

- **trigger:** page load (login form is the only thing on the page)
- **submit-btn:** `submit-btn` (destructive)
- **fields:**
  - `email-input` — text, required, accepts email format
  - `password-input` — password, required, min 8 chars
- **validation:**
  - Empty email shows "Email is required" below `email-input`
  - Empty password shows "Password is required" below
    `password-input`
  - Invalid email format shows "Please enter a valid email"
- **on success:** redirects to `app.harvestgrove.com` (or to
  `?redirect=<path>` if specified in the URL)
- **on error:** stays on `/login`, shows `error-banner` above
  the form with text "Invalid email or password"

## States

### `error-state`

- **trigger:** invalid credentials submission
- **dismiss:** correct credentials OR navigate away
- **contains:** `error-banner` with the error message
- **notes:** page does NOT distinguish "no such user" from
  "wrong password"

### `rate-limited-state`

- **trigger:** more than 5 failed login attempts in 10 minutes
- **dismiss:** wait for the rate limit window to expire
- **contains:** `error-banner` with "Too many attempts. Please
  try again later."
- **notes:** runtime agents should stop and report to the user
  when this state is detected

## Edge cases

- **Validation errors:**
  - Empty email: error "Email is required" below `email-input`
  - Empty password: error "Password is required"
- **Wrong credentials:** error "Invalid email or password" above
  the form. The page does NOT distinguish between "no such user"
  and "wrong password" (good security practice).
- **Rate limiting:** after 5 failed attempts in 10 minutes, the
  form is disabled with "Too many attempts. Please try again
  later." Stop and report.
- **Redirect after login:** if the URL has `?redirect=<path>`,
  the user is sent to `<path>` after a successful login
  (otherwise they go to the app home).
