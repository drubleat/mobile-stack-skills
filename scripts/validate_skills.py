#!/usr/bin/env python3
"""Validate skill metadata, local reference graph, and context budgets offline."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("mobile-stack-toolkit", "supabase-postgres-best-practices")
IMPACTS = {"CRITICAL", "HIGH", "MEDIUM-HIGH", "MEDIUM", "LOW-MEDIUM", "LOW"}


class UniqueLoader(yaml.SafeLoader):
    pass


def unique_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"Duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def frontmatter(text):
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("Missing frontmatter")
    data = yaml.load(match[1], Loader=UniqueLoader)
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a mapping")
    return data, text[match.end():]


def prose(text):
    """Exclude fenced examples, whose relative links are illustrative."""
    result, fence = [], None
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            continue
        if fence is None:
            result.append(line)
    return "\n".join(result)


def local_links(path, text):
    for target in re.findall(r"\[[^\]]*\]\(([^)\n]+)\)", prose(text)):
        target = target.strip().strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        yield (path.parent / unquote(parsed.path)).resolve()


def validate(root=ROOT):
    root = root.resolve()
    errors, metrics = [], {}
    documents = list(root.glob("*.md"))
    for name in SKILLS:
        directory = root / name
        documents.extend(directory.rglob("*.md"))
        entry = directory / "SKILL.md"
        try:
            data, body = frontmatter(entry.read_text())
            if data.get("name") != name or not re.fullmatch(r"[a-z0-9-]{1,64}", name):
                errors.append(f"{entry}: name must match skill directory")
            allowed = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
            if set(data) - allowed:
                errors.append(f"{entry}: unsupported frontmatter keys: {set(data) - allowed}")
            description = data.get("description")
            if not isinstance(description, str) or not description.strip() or len(description) > 300:
                errors.append(f"{entry}: description must contain 1–300 characters")
            if len(body.split()) > 650:
                errors.append(f"{entry}: entry exceeds the 650-word context budget")
            agent = yaml.load((directory / "agents/openai.yaml").read_text(), Loader=UniqueLoader)
            interface = agent["interface"]
            if not 25 <= len(interface["short_description"]) <= 64:
                errors.append(f"{entry}: UI description must contain 25–64 characters")
            if f"${name}" not in interface["default_prompt"]:
                errors.append(f"{entry}: default prompt must name the skill")
            metrics[name] = {
                "description_characters": len(description),
                "entry_words": len(body.split()),
                "entry_bytes": len(entry.read_bytes()),
                "reference_files": len(list((directory / ("references" if name == SKILLS[0] else "rules")).rglob("*.md"))),
            }
        except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
            errors.append(f"{entry}: {exc}")
    graph = {}
    for path in documents:
        text = path.read_text()
        if "references" in path.parts or "rules" in path.parts:
            try:
                data, _ = frontmatter(text)
                for key in ("title", "impactDescription", "tags"):
                    if not isinstance(data.get(key), str) or not data[key].strip():
                        errors.append(f"{path}: missing or invalid {key}")
                if data.get("impact") not in IMPACTS:
                    errors.append(f"{path}: invalid impact")
            except (ValueError, yaml.YAMLError) as exc:
                errors.append(f"{path}: {exc}")
        graph[path.resolve()] = set(local_links(path, text))
        for target in graph[path.resolve()]:
            if not target.is_relative_to(root):
                errors.append(f"{path}: link escapes repository: {target}")
            elif not target.exists():
                errors.append(f"{path}: broken local link: {target}")
    for name in SKILLS:
        directory = (root / name).resolve()
        pending = [directory / "SKILL.md"]
        visited = set()
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(p for p in graph.get(current, ()) if p.is_relative_to(directory))
        reference_root = directory / ("references" if name == SKILLS[0] else "rules")
        for path in reference_root.rglob("*.md"):
            if path not in visited:
                errors.append(f"{path}: unreachable from SKILL.md")
        for current in visited:
            for target in graph.get(current, ()):
                if target.is_relative_to(root) and not target.is_relative_to(directory):
                    errors.append(f"{current}: runtime reference requires another skill: {target}")
    return errors, metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    errors, metrics = validate(args.root)
    if args.json:
        print(json.dumps({"errors": errors, "metrics": metrics}, indent=2))
    else:
        for name, values in metrics.items():
            print(f"{name}: {values}")
        print("\n".join(errors) if errors else "All structural checks passed.")
    raise SystemExit(bool(errors))


if __name__ == "__main__":
    main()
