#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""
Translate rookie-marketplace skills (SKILL.md) to Cursor IDE rules (.mdc).

Usage:
    uv run scripts/translate-skills.py --output ./cursor-rules
    uv run scripts/translate-skills.py --output ./cursor-rules --filter chief-of-staff,rust-dev
    uv run scripts/translate-skills.py --dry-run

Examples:
    # Translate all skills
    uv run scripts/translate-skills.py

    # Only translate specific plugins
    uv run scripts/translate-skills.py --filter chief-of-staff

    # Preview without writing files
    uv run scripts/translate-skills.py --dry-run
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml


def parse_skill_md(path: Path) -> dict | None:
    """Extract YAML frontmatter and body from SKILL.md."""
    content = path.read_text(encoding="utf-8")
    skill_dir_name = path.parent.name

    # Match YAML frontmatter between --- delimiters
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if not match:
        # No frontmatter - use directory name and full content as body
        print(f"  Warning: No frontmatter in {path} - using directory name", file=sys.stderr)
        # Try to extract first heading as name
        heading_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        name = heading_match.group(1) if heading_match else skill_dir_name.replace("-", " ").title()
        return {
            "name": name,
            "description": f"This skill provides guidance for {name.lower()}",
            "version": None,
            "body": content.strip(),
            "path": path,
        }

    frontmatter_str, body = match.groups()

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        # YAML parse error - try manual extraction
        print(f"  Warning: YAML error in {path}, trying manual parse", file=sys.stderr)
        frontmatter = {}
        # Try to extract name manually
        name_match = re.search(r"^name:\s*(.+)$", frontmatter_str, re.MULTILINE)
        if name_match:
            frontmatter["name"] = name_match.group(1).strip()
        # Try to extract description (first line only to avoid colons)
        desc_match = re.search(r"^description:\s*(.+)$", frontmatter_str, re.MULTILINE)
        if desc_match:
            frontmatter["description"] = desc_match.group(1).strip()
        # Try to extract version
        ver_match = re.search(r"^version:\s*(.+)$", frontmatter_str, re.MULTILINE)
        if ver_match:
            frontmatter["version"] = ver_match.group(1).strip()

    return {
        "name": frontmatter.get("name", skill_dir_name.replace("-", " ").title()),
        "description": frontmatter.get("description", f"Skill for {skill_dir_name}"),
        "version": frontmatter.get("version"),
        "body": body.strip(),
        "path": path,
    }


def parse_reference_md(path: Path, skill_name: str, plugin_name: str) -> dict:
    """Parse a reference markdown file."""
    content = path.read_text(encoding="utf-8")
    ref_name = path.stem  # e.g., "cos-workflow" from "cos-workflow.md"

    # Check for YAML frontmatter
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", content, re.DOTALL)
    if match:
        frontmatter_str, body = match.groups()
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            description = frontmatter.get("description", "")
        except yaml.YAMLError:
            description = ""
            body = content
    else:
        description = ""
        body = content

    # Generate description from filename if not present
    if not description:
        # Convert "cos-workflow" to "Chief of Staff workflow reference"
        readable_name = ref_name.replace("-", " ").replace("_", " ")
        description = f"Detailed reference for {readable_name} ({skill_name} skill)"

    return {
        "name": ref_name,
        "skill_name": skill_name,
        "plugin_name": plugin_name,
        "description": description,
        "body": body.strip(),
        "path": path,
    }


def generate_mdc(skill_data: dict, plugin_name: str, examples: list[Path] | None = None, scripts: list[Path] | None = None) -> str:
    """Generate .mdc file content from skill data."""
    lines = [
        "---",
        f"description: {skill_data['description']}",
        "alwaysApply: false",
        "---",
        "",
        f"# {skill_data['name']}",
        "",
    ]

    # Add version comment if present
    if skill_data.get("version"):
        lines.append(f"<!-- Version: {skill_data['version']} -->")
        lines.append("")

    # Add main body
    lines.append(skill_data["body"])

    # Inline examples if present
    if examples:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Examples")
        lines.append("")
        for example_path in examples:
            example_content = example_path.read_text(encoding="utf-8").strip()
            example_name = example_path.stem.replace("-", " ").replace("_", " ").title()
            lines.append(f"### {example_name}")
            lines.append("")
            lines.append(example_content)
            lines.append("")

    # Document scripts if present
    if scripts:
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Available Scripts")
        lines.append("")
        lines.append("The following scripts are available in the marketplace but cannot be executed from Cursor rules:")
        lines.append("")
        for script_path in scripts:
            script_name = script_path.name
            # Read first docstring if present
            script_content = script_path.read_text(encoding="utf-8")
            docstring_match = re.search(r'"""(.*?)"""', script_content, re.DOTALL)
            if docstring_match:
                docstring = docstring_match.group(1).strip().split("\n")[0]  # First line only
            else:
                docstring = "No description available"
            lines.append(f"- `{script_name}`: {docstring}")
        lines.append("")
        lines.append("To use these scripts, run them via `uv run` from the marketplace directory.")

    return "\n".join(lines)


def generate_reference_mdc(ref_data: dict) -> str:
    """Generate .mdc file content for a reference document."""
    lines = [
        "---",
        f"description: {ref_data['description']}",
        "alwaysApply: false",
        "---",
        "",
        f"# {ref_data['name'].replace('-', ' ').replace('_', ' ').title()}",
        "",
        f"_Reference for {ref_data['skill_name']} skill ({ref_data['plugin_name']} plugin)_",
        "",
        ref_data["body"],
    ]
    return "\n".join(lines)


def to_kebab_case(name: str) -> str:
    """Convert a name to kebab-case."""
    # Replace & with "and"
    name = name.replace("&", "and")
    # Replace underscores and spaces with hyphens
    name = re.sub(r"[_\s]+", "-", name)
    # Remove any non-alphanumeric characters except hyphens
    name = re.sub(r"[^a-zA-Z0-9-]", "", name)
    # Insert hyphen before uppercase letters and lowercase them
    name = re.sub(r"([a-z])([A-Z])", r"\1-\2", name)
    # Collapse multiple hyphens
    name = re.sub(r"-+", "-", name)
    return name.lower().strip("-")


def translate_skill(
    skill_dir: Path,
    plugin_name: str,
    output_dir: Path,
    dry_run: bool = False,
) -> list[Path]:
    """Translate a single skill directory to .mdc files."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []

    skill_data = parse_skill_md(skill_md)
    if not skill_data:
        return []

    skill_name = to_kebab_case(skill_data["name"])
    plugin_kebab = to_kebab_case(plugin_name)
    output_files = []

    # Find examples and scripts
    examples_dir = skill_dir / "examples"
    scripts_dir = skill_dir / "scripts"
    refs_dir = skill_dir / "references"

    examples = list(examples_dir.glob("*.md")) if examples_dir.exists() else []
    scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []

    # Generate main skill .mdc
    mdc_content = generate_mdc(skill_data, plugin_name, examples, scripts)
    mdc_filename = f"{plugin_kebab}-{skill_name}.mdc"
    mdc_path = output_dir / mdc_filename

    print(f"  → {mdc_filename}")
    if not dry_run:
        mdc_path.write_text(mdc_content, encoding="utf-8")
    output_files.append(mdc_path)

    # Generate separate .mdc for each reference
    if refs_dir.exists():
        for ref_path in refs_dir.glob("*.md"):
            ref_data = parse_reference_md(ref_path, skill_data["name"], plugin_name)
            ref_mdc_content = generate_reference_mdc(ref_data)
            ref_name = to_kebab_case(ref_data["name"])
            ref_mdc_filename = f"{plugin_kebab}-{skill_name}--{ref_name}.mdc"
            ref_mdc_path = output_dir / ref_mdc_filename

            print(f"  → {ref_mdc_filename}")
            if not dry_run:
                ref_mdc_path.write_text(ref_mdc_content, encoding="utf-8")
            output_files.append(ref_mdc_path)

    return output_files


def translate_all(
    marketplace_path: Path,
    output_dir: Path,
    plugin_filter: list[str] | None = None,
    dry_run: bool = False,
) -> list[Path]:
    """Walk marketplace and translate all skills."""
    output_files = []

    # Find all plugin directories (those with .claude-plugin/plugin.json)
    for plugin_dir in marketplace_path.iterdir():
        if not plugin_dir.is_dir():
            continue
        if plugin_dir.name.startswith("."):
            continue

        plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            continue

        plugin_name = plugin_dir.name

        # Apply filter if specified
        if plugin_filter and plugin_name not in plugin_filter:
            continue

        print(f"Plugin: {plugin_name}")

        # Find skills directory
        skills_dir = plugin_dir / "skills"
        if not skills_dir.exists():
            print("  (no skills directory)")
            continue

        for skill_dir in skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            files = translate_skill(skill_dir, plugin_name, output_dir, dry_run)
            output_files.extend(files)

    return output_files


def main():
    parser = argparse.ArgumentParser(
        description="Translate rookie-marketplace skills to Cursor .mdc rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--marketplace",
        type=Path,
        default=Path(__file__).parent.parent,
        help="Path to rookie-marketplace (default: parent of scripts/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).parent.parent / "cursor-rules",
        help="Output directory for .mdc files (default: ./cursor-rules)",
    )
    parser.add_argument(
        "--filter",
        type=str,
        help="Comma-separated list of plugins to translate (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing files",
    )

    args = parser.parse_args()

    marketplace_path = args.marketplace.resolve()
    output_dir = args.output.resolve()
    plugin_filter = args.filter.split(",") if args.filter else None

    print(f"Marketplace: {marketplace_path}")
    print(f"Output: {output_dir}")
    if plugin_filter:
        print(f"Filter: {plugin_filter}")
    if args.dry_run:
        print("DRY RUN - no files will be written")
    print()

    # Create output directory
    if not args.dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

    # Translate all skills
    output_files = translate_all(
        marketplace_path,
        output_dir,
        plugin_filter,
        args.dry_run,
    )

    print()
    print(f"Generated {len(output_files)} .mdc files")

    if args.dry_run:
        print()
        print("Run without --dry-run to write files")


if __name__ == "__main__":
    main()
