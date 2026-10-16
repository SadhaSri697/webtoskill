---
name: trail-signup
description: |
  The Trail signup page. Email, password, and team name fields.
  Creates a new account and a new team, then redirects to /home.
match:
  - /^https:\/\/app\.trail\.dev\/signup(\?.*)?$/
requires:
  - trail
---

# Trail — Signup Page

## Page architecture

- **No top bar, no left rail** (public page)
- **Centered card (480px wide):**
  - Trail logo at the top
  - Heading: "Create your Trail account"
  - Subheading: "Start a free 14-day trial. No credit card
    required."
  - Email input
  - Password input (with strength meter)
  - Team name input
  - "Create account" submit button
  - "Already have an account? Log in" link
- **Background:** solid dark color, no images

## Element inventory

### `email-input`

- **type:** input
- **selector:** `input[name="email"]`
- **fallback:** `input[type="email"]` in the signup card
- **location:** first field, below the heading

### `password-input`

- **type:** input
- **selector:** `input[name="password"]`
- **fallback:** `input[type="password"]` in the signup card
- **location:** second field, below email
- **note:** a strength meter appears below the field; the submit
  button is disabled if the password is "weak"

### `password-strength`

- **type:** static text (informational)
- **selector:** `[data-testid="password-strength"]`
- **location:** directly below `password-input`
- **values:** "Weak" / "Fair" / "Good" / "Strong" — the input
  border color also changes (red/orange/yellow/green)

### `team-name-input`

- **type:** input
- **selector:** `input[name="teamName"]`
- **fallback:** `input[placeholder*="team" i]` in the signup
  card
- **location:** third field, below password

### `submit-btn`

- **type:** button
- **selector:** `button[type="submit"]`
- **fallback:** `button:has-text("Create account")` in the
  signup card
- **location:** below the team name field, full-width
- **note:** disabled if password is "weak" or any field is
  empty

### `login-link`

- **type:** link
- **selector:** `a[href="/login"]`
- **fallback:** `a:has-text("Log in")` in the signup card
- **location:** below the submit button, centered

## Edge cases

- **Email already in use:** inline error below `email-input`:
  "An account with this email already exists. Log in instead."
  The agent should suggest logging in.
- **Weak password:** `password-strength` reads "Weak"; the
  submit button is disabled with a tooltip "Choose a stronger
  password." The agent must add complexity.
- **Team name taken:** inline error below `team-name-input`:
  "This team name is already taken." The agent must choose
  another.
- **Rate limiting:** same as login (5 attempts / 10 min).
- **Trial exhausted:** if a free trial is created from a domain
  that has already had a trial, signup succeeds but a banner
  appears: "You've already used your free trial on this domain."
