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
- **contains:** `email-input`, `password-input`, `submit-btn`,
  `forgot-password-link`, `signup-link`
- **ab-ref:** "@e3  form  "Log in to your account""

### `email-input`

- **type:** input
- **selector:** `[data-testid="login-email"]`
- **fallback:** `input[type="email"]` inside `login-form`
- **location:** first field in the form
- **action:** accepts text input for user email
- **ab-ref:** "@e4  textbox  "Email""

### `password-input`

- **type:** input
- **selector:** `[data-testid="login-password"]`
- **fallback:** `input[type="password"]` inside `login-form`
- **location:** second field in the form, below email
- **action:** accepts masked text input for password
- **ab-ref:** "@e5  textbox  "Password""

### `submit-btn`

- **type:** button (submit)
- **selector:** `[data-testid="login-submit"]`
- **fallback:** `button[type="submit"]` inside `login-form`
- **location:** below the password field, full-width
- **action:** submits the login form; on success redirects to
  app.harvestgrove.com or to `?redirect=<path>` if specified
- **destructive:** true
- **ab-ref:** "@e6  button  "Log in""

### `forgot-password-link`

- **type:** link
- **selector:** `[data-testid="login-forgot-password"]`
- **fallback:** `a:has-text("Forgot password?")` inside `login-form`
- **location:** right-aligned, below the password field
- **action:** navigates to `/forgot-password` (out of scope for
  this skill)
- **ab-ref:** "@e7  link  "Forgot password?""

### `signup-link`

- **type:** link
- **selector:** `[data-testid="login-to-signup"]`
- **fallback:** `a:has-text("Sign up")` inside `login-form`
- **location:** below the submit button, small text
- **action:** navigates to `/signup`
- **ab-ref:** "@e8  link  "Sign up""

### `error-banner`

- **type:** static text (displayed conditionally)
- **selector:** `[data-testid="login-error"]`
- **fallback:** `.login-error` (when visible)
- **location:** above the form, red text
- **action:** read-only; displays error message
- **ab-ref:** "@e9  text  "Invalid email or password"" (when shown)

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

- **trigger:** more than 5 failed login attempts in a short window
- **dismiss:** wait for the rate limit window to expire
- **contains:** `error-banner` with "Too many attempts. Please
  try again later."
- **notes:** runtime agents should stop and report to the user
  when this state is detected

## Edge cases

- **Validation errors:** empty email → `email-input` shows
  "Email is required" below; empty password → `password-input`
  shows "Password is required" below
- **Wrong credentials:** `error-banner` shows "Invalid email or
  password" above the form
- **Rate limiting:** after 5 failed attempts, `error-banner`
  shows "Too many attempts. Please try again later." Stop and
  report to the user.
- **Redirect after login:** if URL has `?redirect=<path>`, user
  is sent there after successful login (out of scope).
- **Already-logged-in:** if user is already authenticated and
  visits `/login`, redirects to `app.harvestgrove.com` automatically.
