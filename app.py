"""
WebToSkill Studio - Fullstack Application
Backend powered by Flask, providing:
1. Live Website-to-Skill Compiler (DOM Scraping & SKILL.md Generator)
2. Skill Specification Explorer & Reader
3. w2s Format Lint Validator (via w2s/validate.py)
4. AI Agent Automation Simulator
"""

import os
import re
import sys
import json
import traceback
from pathlib import Path
from urllib.parse import urlparse, urljoin
from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
from bs4 import BeautifulSoup

# Ensure current directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from w2s.validate import lint, Errors, parse_frontmatter
except ImportError:
    lint = None
    Errors = list
    parse_frontmatter = None

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

COMPILED_DIR = BASE_DIR / "compiled_skills"
COMPILED_DIR.mkdir(exist_ok=True)
EXAMPLES_DIR = BASE_DIR / "w2s" / "examples"


def sanitize_ref_name(text: str) -> str:
    """Produce clean kebab-case identifier for element inventory refs."""
    cleaned = re.sub(r"[^a-zA-Z0-9\s_-]", "", text.strip())
    kebab = re.sub(r"[\s_]+", "-", cleaned).lower().strip("-")
    if not kebab or not kebab[0].isalpha():
        kebab = "el-" + (kebab or "item")
    return kebab[:32]


def build_stable_selector(tag, tag_type="element") -> str:
    """Generate a clean, resilient selector (avoiding fragile deep DOM chains)."""
    if tag.get("data-testid"):
        return f'[data-testid="{tag["data-testid"]}"]'
    if tag.get("id"):
        return f'#{tag["id"]}'
    if tag.get("name"):
        return f'{tag.name}[name="{tag["name"]}"]'
    if tag.get("aria-label"):
        return f'{tag.name}[aria-label="{tag["aria-label"]}"]'
    if tag.name == "button" and tag.get_text(strip=True):
        text = tag.get_text(strip=True)[:25].replace('"', '\\"')
        return f'button:has-text("{text}")'
    if tag.name == "a" and tag.get("href"):
        href = tag.get("href")
        if href.startswith("/") or href.startswith("#"):
            return f'a[href="{href}"]'
    classes = [c for c in tag.get("class", []) if not re.search(r"(css-|jsx-|\d{5,})", c)]
    if classes:
        return f"{tag.name}.{classes[0]}"
    return tag.name


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def status():
    """Return backend health and capability metadata."""
    examples = []
    if EXAMPLES_DIR.exists():
        examples = [d.name for d in EXAMPLES_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]
    
    compiled = []
    if COMPILED_DIR.exists():
        compiled = [d.name for d in COMPILED_DIR.iterdir() if d.is_dir() and not d.name.startswith(".")]

    return jsonify({
        "status": "online",
        "service": "WebToSkill Studio API",
        "version": "1.0.0",
        "validator_ready": lint is not None,
        "sample_skills_count": len(examples),
        "compiled_skills_count": len(compiled),
        "examples": examples,
        "compiled": compiled
    })


@app.route("/api/skills")
def list_skills():
    """List all available skills (both built-in examples and user compiled)."""
    skills = []

    # Built-in examples
    if EXAMPLES_DIR.exists():
        for d in sorted(EXAMPLES_DIR.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            readme = d / "README.md"
            overview = d / "overview.md"
            desc = "Precompiled w2s reference specification"
            if overview.exists():
                text = overview.read_text(encoding="utf-8", errors="replace")
                data, _ = parse_frontmatter(text) if parse_frontmatter else ({}, "")
                if data and data.get("description"):
                    desc = data["description"]
            elif readme.exists():
                lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
                for line in lines:
                    if line.strip() and not line.startswith("#"):
                        desc = line.strip()[:140]
                        break

            file_count = len(list(d.glob("*.md")))
            skills.append({
                "id": d.name,
                "name": d.name.replace("-", " ").title(),
                "type": "example",
                "folder": str(d.relative_to(BASE_DIR)).replace("\\", "/"),
                "file_count": file_count,
                "description": desc
            })

    # User compiled skills
    if COMPILED_DIR.exists():
        for d in sorted(COMPILED_DIR.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            overview = d / "overview.md"
            desc = "Compiled live website skill"
            if overview.exists():
                text = overview.read_text(encoding="utf-8", errors="replace")
                data, _ = parse_frontmatter(text) if parse_frontmatter else ({}, "")
                if data and data.get("description"):
                    desc = data["description"]
            file_count = len(list(d.glob("*.md")))
            skills.append({
                "id": d.name,
                "name": d.name,
                "type": "compiled",
                "folder": str(d.relative_to(BASE_DIR)).replace("\\", "/"),
                "file_count": file_count,
                "description": desc
            })

    return jsonify({"skills": skills})


@app.route("/api/skills/<path:skill_id>")
def get_skill_details(skill_id):
    """Retrieve full file contents and element inventory of a skill."""
    target_dir = None
    if (EXAMPLES_DIR / skill_id).exists():
        target_dir = EXAMPLES_DIR / skill_id
    elif (COMPILED_DIR / skill_id).exists():
        target_dir = COMPILED_DIR / skill_id
    elif (BASE_DIR / skill_id).exists():
        target_dir = BASE_DIR / skill_id

    if not target_dir or not target_dir.is_dir():
        return jsonify({"error": f"Skill directory '{skill_id}' not found"}), 404

    files = {}
    elements = []
    for f in sorted(target_dir.glob("*.md")):
        content = f.read_text(encoding="utf-8", errors="replace")
        files[f.name] = content

        # Parse element inventory refs
        for match in re.finditer(r"^###\s+`([^`]+)`\s*\n([\s\S]*?)(?=\n###|\n##|\Z)", content, re.MULTILINE):
            ref_name = match.group(1).strip()
            block = match.group(2)
            selector_match = re.search(r"-\s+\*\*selector:\*\*\s*`?([^`\n]+)`?", block)
            type_match = re.search(r"-\s+\*\*type:\*\*\s*([^\n]+)", block)
            purpose_match = re.search(r"-\s+\*\*purpose:\*\*\s*([^\n]+)", block)
            elements.append({
                "file": f.name,
                "ref": ref_name,
                "selector": selector_match.group(1).strip() if selector_match else "unknown",
                "type": type_match.group(1).strip() if type_match else "element",
                "purpose": purpose_match.group(1).strip() if purpose_match else ""
            })

    return jsonify({
        "id": skill_id,
        "path": str(target_dir.relative_to(BASE_DIR)).replace("\\", "/"),
        "files": files,
        "elements": elements
    })


@app.route("/api/compile", methods=["POST"])
def compile_website():
    """
    Compile a live website into a w2s-standard skill package.
    Parses the target URL, extracts elements, builds overview.md & route.md,
    and runs the format validator.
    """
    data = request.get_json() or {}
    url = data.get("url", "").strip()

    if not url:
        return jsonify({"error": "URL parameter is required"}), 400

    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    if not domain:
        return jsonify({"error": "Invalid website URL format"}), 400

    clean_domain_name = re.sub(r"^www\.", "", domain)
    skill_slug = re.sub(r"[^a-z0-9]+", "-", clean_domain_name.lower()).strip("-")
    if not skill_slug or not skill_slug[0].isalpha():
        skill_slug = "site-" + (skill_slug or "web")
    route_skill_name = f"{skill_slug}-home"

    skill_output_dir = COMPILED_DIR / skill_slug
    skill_output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch live page HTML
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    fetch_success = False
    html_content = ""
    error_msg = None

    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        html_content = resp.text
        fetch_success = True
    except Exception as e:
        error_msg = str(e)
        # Fallback to simulated HTML structure if offline or host blocked
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{clean_domain_name.capitalize()} Portal</title>
            <meta name="description" content="Official website and portal for {clean_domain_name}.">
        </head>
        <body>
            <header>
                <nav>
                    <a href="/" data-testid="nav-home">Home</a>
                    <a href="/features" data-testid="nav-features">Features</a>
                    <a href="/pricing" data-testid="nav-pricing">Pricing</a>
                    <a href="/login" data-testid="nav-login">Sign In</a>
                </nav>
            </header>
            <main>
                <h1>Welcome to {clean_domain_name}</h1>
                <p>Build better AI agent workflows with automated page references.</p>
                <form id="search-form" action="/search" method="get">
                    <input type="text" name="q" placeholder="Search documentation..." data-testid="search-input" />
                    <button type="submit" data-testid="search-submit">Search</button>
                </form>
                <div class="actions">
                    <button data-testid="get-started-btn">Get Started Free</button>
                    <button data-testid="demo-modal-btn">Watch Live Demo</button>
                </div>
            </main>
        </body>
        </html>
        """

    soup = BeautifulSoup(html_content, "html.parser")

    # Extract Meta & Titles
    page_title = soup.title.string.strip() if soup.title and soup.title.string else f"{clean_domain_name.capitalize()} Home"
    meta_desc = ""
    meta_tag = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    if meta_tag and meta_tag.get("content"):
        meta_desc = meta_tag["content"].strip()
    if not meta_desc or len(meta_desc) < 10:
        meta_desc = f"Comprehensive element, state, and interaction reference for {clean_domain_name}."

    # Extract Interactive Elements
    elements_found = []
    seen_refs = set()

    def add_element(ref_candidate, selector, el_type, purpose):
        base_ref = sanitize_ref_name(ref_candidate)
        ref = base_ref
        idx = 1
        while ref in seen_refs:
            ref = f"{base_ref}-{idx}"
            idx += 1
        seen_refs.add(ref)
        elements_found.append({
            "ref": ref,
            "selector": selector,
            "type": el_type,
            "purpose": purpose
        })

    # Buttons
    for btn in soup.find_all(["button", "input"], limit=20):
        if btn.name == "input" and btn.get("type") not in ("button", "submit", "reset"):
            continue
        text = btn.get_text(strip=True) or btn.get("value") or btn.get("aria-label") or btn.get("name") or "button"
        selector = build_stable_selector(btn, "button")
        add_element(f"btn-{text[:16]}", selector, "button", f"Triggers {text.strip()} action")

    # Input Fields
    for inp in soup.find_all(["input", "textarea", "select"], limit=15):
        if inp.name == "input" and inp.get("type") in ("hidden", "button", "submit"):
            continue
        name = inp.get("name") or inp.get("id") or inp.get("placeholder") or "field"
        selector = build_stable_selector(inp, "input")
        inp_type = inp.get("type", "text") if inp.name == "input" else inp.name
        add_element(f"input-{name[:16]}", selector, f"input", f"Captures {name} input value")

    # Navigation Links
    for a in soup.find_all("a", href=True, limit=15):
        href = a["href"].strip()
        text = a.get_text(strip=True) or href
        if not text or len(text) > 40:
            continue
        selector = build_stable_selector(a, "link")
        add_element(f"link-{text[:16]}", selector, "link", f"Navigates to {href}")

    # Ensure minimal elements if sparse page
    if not elements_found:
        add_element("main-container", "body", "container", "Primary document body")

    # 2. Generate overview.md
    overview_content = f"""---
name: {skill_slug}
domain: {clean_domain_name}
description: {meta_desc}
match:
  - {clean_domain_name}
  - {clean_domain_name}/*
---

# {clean_domain_name} Reference

Comprehensive site reference for AI agents interacting with `{clean_domain_name}`.

## Route Map

| Route Family | URL Pattern | Description | Skill File |
| :--- | :--- | :--- | :--- |
| Home & Portal | `^https?://(www\\.)?{clean_domain_name}/?$` | Main entry point and dashboard | `home.md` |

## Sub-Skills

- `home.md` — Complete element inventory, form behaviors, and state definitions for `{clean_domain_name}`.
""".strip() + "\n"

    with open(skill_output_dir / "overview.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(overview_content)

    # 3. Generate home.md
    home_elements_md = []
    for el in elements_found:
        home_elements_md.append(f"""### `{el['ref']}`
- **selector:** `{el['selector']}`
- **type:** {el['type']}
- **purpose:** {el['purpose']}
""")

    elements_block = "\n".join(home_elements_md)

    home_content = f"""---
name: {route_skill_name}
description: Home page element inventory and interaction patterns for {clean_domain_name}.
match:
  - {clean_domain_name}
requires:
  - {skill_slug}
---

# {clean_domain_name} — Home

Reference for the primary landing page and interface of `{clean_domain_name}`.

## Page Architecture

- **Canonical URL:** `{url}`
- **Page Title:** {page_title}
- **Authentication Required:** No
- **Primary Layout:** Standard web application view with navigation header and main content block.

## Element Inventory

{elements_block}

## Forms

### Standard Form Handling
- Inputs validate according to client-side constraints.
- Form submissions perform navigation or API query dispatch.

## States

- Default State: Initial document view loaded.
- Active State: Interactive triggers display hover / focus indicators.

## Edge Cases

- Network latency: Show inline spinner or wait for response.
- Empty search: Displays prompt to enter valid query.
""".strip() + "\n"

    with open(skill_output_dir / "home.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(home_content)

    # 4. Validate output using w2s validator
    validation_passed = True
    validation_errors = []
    validation_warnings = []

    if lint and Errors:
        errs = Errors()
        lint(skill_output_dir, errs)
        validation_errors = errs.errors()
        validation_warnings = errs.warnings()
        validation_passed = len(validation_errors) == 0

    return jsonify({
        "success": True,
        "target_url": url,
        "domain": clean_domain_name,
        "title": page_title,
        "skill_id": skill_slug,
        "live_fetch": fetch_success,
        "fetch_note": None if fetch_success else f"Live fetch fallback applied: {error_msg}",
        "elements_count": len(elements_found),
        "files_created": ["overview.md", "home.md"],
        "validation": {
            "passed": validation_passed,
            "errors": validation_errors,
            "warnings": validation_warnings
        },
        "overview_preview": overview_content,
        "home_preview": home_content,
        "elements": elements_found
    })


@app.route("/api/validate", methods=["POST"])
def validate_skill():
    """Run w2s/validate.py format linting on a skill folder."""
    data = request.get_json() or {}
    skill_path_str = data.get("skill_path", "").strip()

    if not skill_path_str:
        return jsonify({"error": "skill_path parameter is required"}), 400

    target = BASE_DIR / skill_path_str
    if not target.exists():
        # Check inside w2s/examples or compiled_skills
        if (EXAMPLES_DIR / skill_path_str).exists():
            target = EXAMPLES_DIR / skill_path_str
        elif (COMPILED_DIR / skill_path_str).exists():
            target = COMPILED_DIR / skill_path_str
        else:
            return jsonify({"error": f"Path '{skill_path_str}' does not exist"}), 404

    if not lint or not Errors:
        return jsonify({"error": "w2s.validate module is not loaded"}), 500

    errs = Errors()
    lint(target, errs)

    return jsonify({
        "path": str(target.relative_to(BASE_DIR)).replace("\\", "/"),
        "passed": len(errs.errors()) == 0,
        "errors": errs.errors(),
        "warnings": errs.warnings(),
        "summary": f"{len(errs.errors())} errors, {len(errs.warnings())} warnings"
    })


@app.route("/api/simulate", methods=["POST"])
def simulate_agent():
    """
    AI Agent Execution Simulator.
    Given a task query and a skill reference, identifies the target DOM element
    and generates an automated Browser-Use / Playwright execution plan.
    """
    data = request.get_json() or {}
    task = data.get("task", "").strip()
    skill_id = data.get("skill_id", "").strip()

    if not task:
        return jsonify({"error": "task parameter is required"}), 400

    # Retrieve skill elements
    details_resp = get_skill_details(skill_id)
    if isinstance(details_resp, tuple) and details_resp[1] == 404:
        return jsonify({"error": f"Skill '{skill_id}' not found"}), 404

    elements = details_resp.json.get("elements", [])
    task_lower = task.lower()

    # Score and rank elements based on semantic match
    ranked = []
    for el in elements:
        score = 0
        ref_words = el["ref"].lower().replace("-", " ").split()
        purpose_words = el["purpose"].lower().split()
        selector_words = el["selector"].lower().split()

        for word in task_lower.split():
            if len(word) < 3:
                continue
            if word in ref_words:
                score += 5
            if word in purpose_words:
                score += 3
            if word in selector_words:
                score += 2

        if score > 0:
            ranked.append((score, el))

    ranked.sort(key=lambda x: x[0], reverse=True)
    best_matches = [r[1] for r in ranked[:3]] if ranked else (elements[:2] if elements else [])

    target_element = best_matches[0] if best_matches else {
        "ref": "primary-action",
        "selector": "button, a",
        "type": "button",
        "purpose": "Default page interaction"
    }

    # Generate step-by-step action plan
    actions = [
        {
            "step": 1,
            "action": "Load Reference",
            "detail": f"Consulted `{skill_id}` element inventory for matching intent: '{task}'."
        },
        {
            "step": 2,
            "action": "Resolve Selector",
            "detail": f"Matched ref `{target_element['ref']}` with selector `{target_element['selector']}`.",
            "selector": target_element['selector']
        },
        {
            "step": 3,
            "action": "Execute Action",
            "detail": f"Simulating {'click' if 'btn' in target_element['ref'] or 'link' in target_element['ref'] else 'input'} on {target_element['selector']}.",
            "code": f"await page.locator('{target_element['selector']}').click();"
        },
        {
            "step": 4,
            "action": "State Verification",
            "detail": "Verified DOM mutation, waiting for network response or state transition."
        }
    ]

    playwright_code = f"""# Playwright Agent Script using w2s reference
from playwright.async_api import async_playwright

async def run(playwright):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()
    await page.goto("https://{skill_id}/")
    
    # Target element resolved from {skill_id} SKILL.md
    target = page.locator('{target_element["selector"]}')
    await target.wait_for(state="visible")
    await target.click()
    
    await browser.close()
"""

    return jsonify({
        "task": task,
        "skill_id": skill_id,
        "matched_ref": target_element["ref"],
        "target_selector": target_element["selector"],
        "actions": actions,
        "playwright_code": playwright_code
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=======================================================")
    print(f" WebToSkill Studio running on http://127.0.0.1:{port}")
    print(f"=======================================================\n")
    app.run(host="0.0.0.0", port=port, debug=False)
