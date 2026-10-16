#!/usr/bin/env python3
"""
w2s validator — lint a compiled w2s skill directory against the format spec.

Usage:
    python3 w2s/validate.py <skill-dir> [--warnings] [--fix]

Exit codes:
    0 — skill is valid
    1 — skill has errors
    2 — invalid arguments / missing PyYAML
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

if sys.platform == "win32" and sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

REQUIRED_OVERVIEW_FIELDS = ["name", "domain", "description", "match"]
REQUIRED_SKILL_FIELDS = ["name", "description", "match"]

FORBIDDEN_SELECTOR_PATTERNS = [
    (re.compile(r"\.css-\w{8,}"), "random CSS hash"),
    (re.compile(r"\.jsx-\w+"), "JSX hash"),
    (re.compile(r">\s*\w+\s*>\s*\w+\s*>\s*\w+"), "deep nested descendant chain (>3 levels)"),
    (re.compile(r":nth-child\s*\(\s*[0-9]+\s*\)"), "nth-child positional selector"),
    (re.compile(r"\[\s*class\s*=\s*[\"'][^\"']*[\"'][^\]]*\]"), "class attribute (fragile)"),
]


# ---------------------------------------------------------------------------
# Errors collector
# ---------------------------------------------------------------------------

class Errors(list):
    def add(self, file: str, line: int | None, message: str, severity: str = "ERROR"):
        loc = f"{file}" + (f":{line}" if line else "")
        super().append(f"[{severity}] {loc}: {message}")

    def errors(self):
        return [m for m in self if "[ERROR]" in m]

    def warnings(self):
        return [m for m in self if "[WARNING]" in m]


# ---------------------------------------------------------------------------
# Parsing helpers
# ---------------------------------------------------------------------------

def parse_frontmatter(text: str):
    """Return (frontmatter_dict, body) or (None, full_text) if no frontmatter."""
    text = text.replace("\r\n", "\n")
    if yaml is None:
        return None, text
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        return None, text
    try:
        data = yaml.safe_load(match.group(1))
        body = text[match.end():]
        return data or {}, body
    except yaml.YAMLError:
        return None, text


def extract_sections(body: str) -> dict[str, str]:
    """Return {'section name': 'section content'} for markdown sections."""
    sections = {}
    current = "_preamble"
    lines = body.splitlines(keepends=True)
    buf = []

    for line in lines:
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            if buf:
                sections[current] = "".join(buf).strip()
                buf = []
            current = m.group(2).strip().lower()
        buf.append(line)

    if buf:
        sections[current] = "".join(buf).strip()

    return sections


def extract_element_refs(body: str) -> set[str]:
    """Find all top-level element ref names (### `ref-name`)."""
    return {m.group(1) for m in re.finditer(r"^###\s+`([^`]+)`", body, re.MULTILINE)}


def extract_child_refs(body: str) -> set[str]:
    """Find child refs defined inside element entries (contains: ...)."""
    refs = set()
    in_inventory = False
    for line in body.splitlines():
        if re.match(r"^##\s+element inventory", line, re.IGNORECASE):
            in_inventory = True
        if in_inventory and re.match(r"^##\s+", line):
            in_inventory = False
        m = re.search(r"- \*\*contains:\*\*\s*(.+)", line)
        if m:
            for child in re.split(r",\s*", m.group(1)):
                refs.add(child.strip().rstrip("."))
    return refs


def _is_element_ref(text: str) -> bool:
    """Return True if text looks like an element ref (kebab-case identifier)."""
    return bool(re.match(r"^[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*$", text.strip()))


def extract_inventory_refs(body: str) -> set[str]:
    """Find element refs used anywhere in the body (prose and inventory).

    Excludes refs that appear inside a `contains:` line, since those are
    declared as child refs of a container and don't need to also be
    top-level elements.
    """
    refs = set()
    for line in body.splitlines():
        if re.search(r"- \*\*contains:\*\*", line):
            # Skip refs in contains: lines — those are child declarations
            continue
        for m in re.finditer(r"`([^`]+)`", line):
            ref = m.group(1).strip()
            if _is_element_ref(ref):
                refs.add(ref)
    return refs


def check_selectors(body: str, errors: Errors, file: str):
    """Check element selectors for forbidden patterns."""
    for line_no, line in enumerate(body.splitlines(), 1):
        for pattern, description in FORBIDDEN_SELECTOR_PATTERNS:
            if pattern.search(line):
                errors.add(file, line_no, f"selector appears fragile ({description}): {line.strip()}", "WARNING")


# ---------------------------------------------------------------------------
# Per-file linting
# ---------------------------------------------------------------------------

def lint_overview(file_path: Path, errors: Errors, known_skills: dict):
    text = file_path.read_text()
    data, body = parse_frontmatter(text)

    if data is None:
        errors.add(str(file_path), None, "missing YAML frontmatter (file should start with '---')", "ERROR")
        return

    missing = [f for f in REQUIRED_OVERVIEW_FIELDS if f not in data]
    if missing:
        errors.add(str(file_path), None, f"missing frontmatter fields: {', '.join(missing)}", "ERROR")

    match_patterns = data.get("match", [])
    if not match_patterns:
        errors.add(str(file_path), None, "missing 'match' field in frontmatter", "ERROR")
    else:
        for p in match_patterns:
            try:
                re.compile(p)
            except re.error as e:
                errors.add(str(file_path), None, f"invalid regex in 'match': '{p}' — {e}", "ERROR")

    desc = data.get("description", "")
    if not desc or len(desc.strip()) < 10:
        errors.add(str(file_path), None, "'description' too short (need at least 10 chars)", "WARNING")

    sections = extract_sections(body)
    for sec in ("route map", "sub-skills"):
        if sec not in sections:
            errors.add(str(file_path), None, f"missing section: '## {sec}'", "ERROR")

    # Check sub-skill file references are real
    sub_skills_section = sections.get("sub-skills", "")
    for m in re.finditer(r"`([a-z0-9_-]+\.md)`", sub_skills_section):
        if not (file_path.parent / m.group(1)).exists():
            errors.add(str(file_path), None, f"sub-skill listed but not found: '{m.group(1)}'", "ERROR")

    domain = data.get("domain", "")
    if domain:
        first_match = str(match_patterns[0]) if match_patterns else ""
        if first_match and domain not in first_match:
            errors.add(str(file_path), None, f"first match ('{first_match}') does not include domain '{domain}'", "WARNING")

    check_selectors(body, errors, str(file_path))


def lint_skill(file_path: Path, errors: Errors, known_skills: dict):
    text = file_path.read_text()
    data, body = parse_frontmatter(text)

    if data is None:
        errors.add(str(file_path), None, "missing YAML frontmatter", "ERROR")
        return

    missing = [f for f in REQUIRED_SKILL_FIELDS if f not in data]
    if missing:
        errors.add(str(file_path), None, f"missing frontmatter fields: {', '.join(missing)}", "ERROR")

    match_patterns = data.get("match", [])
    if match_patterns:
        for p in match_patterns:
            try:
                re.compile(p)
            except re.error as e:
                errors.add(str(file_path), None, f"invalid regex in 'match': '{p}' — {e}", "ERROR")

    desc = data.get("description", "")
    if not desc or len(desc.strip()) < 10:
        errors.add(str(file_path), None, "'description' too short", "WARNING")

    sections = extract_sections(body)
    for sec in ("page architecture", "element inventory"):
        if sec not in sections:
            errors.add(str(file_path), None, f"missing section: '## {sec}'", "ERROR")

    # v2: forms and states are recommended only when relevant
    has_form_elements = bool(re.search(r"\*\*type:\*\*\s*(input|textarea|select|button|checkbox|radio)", body))
    has_modal_triggers = bool(re.search(r"\*\*type:\*\*\s*(modal|dropdown|popover|menu)", body, re.IGNORECASE))
    if "forms" not in sections and has_form_elements:
        errors.add(str(file_path), None, "missing section: '## Forms' (page has form-like elements)", "WARNING")
    if "states" not in sections and has_modal_triggers:
        errors.add(str(file_path), None, "missing section: '## States' (page has modal/dropdown triggers)", "WARNING")

    # Check name is kebab-case
    name = data.get("name", "")
    if name and not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", name):
        errors.add(str(file_path), None, f"'name: {name}' is not kebab-case", "ERROR")

    # Check requires references exist
    for req in data.get("requires", []):
        if req not in known_skills:
            errors.add(str(file_path), None, f"'requires: [{req}]' — no skill with that name found", "ERROR")

    # Duplicate refs
    top_refs = re.findall(r"^###\s+`([^`]+)`", body, re.MULTILINE)
    if len(top_refs) != len(set(top_refs)):
        seen = {}
        for ref in top_refs:
            if ref in seen:
                errors.add(str(file_path), None, f"duplicate element ref: '{ref}'", "ERROR")
            seen[ref] = True

    # Ref coverage: all backticked refs should exist as top-level or child
    all_refs = extract_element_refs(body)
    child_refs = extract_child_refs(body)
    inventory_refs = extract_inventory_refs(body)
    known = all_refs | child_refs

    for ref in sorted(inventory_refs):
        if ref not in known:
            errors.add(str(file_path), None, f"references '{ref}' but it is not in the element inventory", "WARNING")

    check_selectors(body, errors, str(file_path))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def lint(skill_dir: Path, errors: Errors):
    skill_dir = skill_dir.expanduser().resolve()

    if not skill_dir.is_dir():
        errors.add(str(skill_dir), None, f"not a directory: {skill_dir}", "ERROR")
        return

    # Build skill name -> filename map (across ALL .md files in dir)
    known_skills = {}
    for f in sorted(skill_dir.glob("*.md")):
        if f.name.startswith("_") or f.name.lower() == "readme.md":
            continue
        data, _ = parse_frontmatter(f.read_text())
        if data and data.get("name"):
            known_skills[data["name"]] = f.name

    # overview.md
    overview = skill_dir / "overview.md"
    if overview.exists():
        lint_overview(overview, errors, known_skills)
    else:
        errors.add(str(skill_dir), None, "overview.md not found — every skill needs one", "ERROR")

    # Per-route skill files
    skill_files = [
        f for f in sorted(skill_dir.glob("*.md"))
        if f.name not in ("overview.md",) and not f.name.lower().startswith("readme") and not f.name.startswith("_")
    ]
    if not skill_files:
        errors.add(str(skill_dir), None, "no SKILL.md files found — skill directory is empty", "ERROR")
    else:
        for f in skill_files:
            lint_skill(f, errors, known_skills)


def main():
    parser = argparse.ArgumentParser(description="Lint a w2s compiled skill directory.")
    parser.add_argument("skill_dir", help="Path to the compiled skill directory")
    parser.add_argument("--warnings", action="store_true", help="Include warnings in output")
    args = parser.parse_args()

    if yaml is None:
        print("error: PyYAML is required. Install with: pip install pyyaml", file=sys.stderr)
        sys.exit(2)

    errors = Errors()
    lint(Path(args.skill_dir), errors)

    error_msgs = errors.errors()
    warning_msgs = errors.warnings() if args.warnings else []
    all_msgs = error_msgs + warning_msgs

    if all_msgs:
        for m in all_msgs:
            print(m)
        print(f"\n{len(error_msgs)} error(s), {len(warning_msgs)} warning(s).")
        sys.exit(1)
    else:
        print(f"✓ {args.skill_dir} — skill is valid.")
        sys.exit(0)


if __name__ == "__main__":
    main()