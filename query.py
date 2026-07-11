#!/usr/bin/env python3
"""只读查询 AI Marketing Brief 已发布的公开 JSON 数据。"""
import argparse
import json
import os
import sys
from datetime import date, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

VERSION = "0.2.0"
BASE = os.environ.get("AI_MARKETING_BRIEF_API_BASE", "https://yingxiaoai.com.cn/api").rstrip("/")
USER_AGENT = f"AI-Marketing-Brief-Skill/{VERSION} (+https://yingxiaoai.com.cn)"
LEVELS = {"L0": 0, "L1": 1, "L2": 2, "L3": 3, "L4": 4}
TYPE_FILES = {"intel": "intel", "case": "cases", "tool": "tools"}
TYPE_ALIASES = {"intel": "intel", "case": "case", "cases": "case", "tool": "tool", "tools": "tool", "all": "all"}


def fetch(name):
    request = Request(f"{BASE}/{name}.json", headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"公开数据暂不可用：{error}") from error


def optional_manifest():
    try:
        return fetch("agent-manifest")
    except RuntimeError:
        return None


def version_tuple(value):
    try:
        return tuple(int(part) for part in str(value).split("."))
    except ValueError:
        return ()


def update_notice(manifest):
    remote = ((manifest or {}).get("skill") or {}).get("version")
    if remote and version_tuple(remote) > version_tuple(VERSION):
        return {"available": True, "version": str(remote), "install_url": (manifest.get("skill") or {}).get("install_url")}
    return {"available": False}


def normalize_type(value):
    return TYPE_ALIASES.get(value, value)


def item_date(item):
    return str(item.get("released_at") or item.get("created") or item.get("updated") or "")


def sort_items(items):
    return sorted(items, key=lambda item: (item_date(item), item.get("id", "")), reverse=True)


def keep(item, args):
    wanted_type = normalize_type(getattr(args, "kind", "all"))
    if wanted_type != "all" and item.get("type") != wanted_type:
        return False
    category = getattr(args, "category", None)
    if category and item.get("category") != category:
        return False
    market = getattr(args, "market", None)
    if market and item.get("market") != market:
        return False
    minimum = getattr(args, "min_verification", None)
    if minimum and LEVELS.get(item.get("verification"), -1) < LEVELS[minimum]:
        return False
    return True


def clamp_take(value):
    return max(1, min(int(value), 50))


def all_archive_items(args):
    kind = normalize_type(args.kind)
    groups = TYPE_FILES if kind == "all" else {kind: TYPE_FILES[kind]}
    items = []
    for object_type, filename in groups.items():
        for item in fetch(filename):
            item = dict(item)
            item.setdefault("type", object_type)
            item.setdefault("released_at", item_date(item))
            if keep(item, args):
                items.append(item)
    return sort_items(items)


def archive_items(args):
    return all_archive_items(args)[:clamp_take(args.take)]


def latest_issue(issues):
    if not issues:
        raise RuntimeError("公开数据中没有已发布期次")
    return max(issues, key=lambda issue: (issue.get("number", 0), str(issue.get("date", ""))))


def issue_payload(issue):
    intel = {item["id"]: item for item in fetch("intel")}
    cases = {item["id"]: item for item in fetch("cases")}
    actions = {item["id"]: item for item in fetch("actions")}
    objects = {**intel, **cases}
    return {
        "issue": issue,
        "information": [objects[item_id] for item_id in issue.get("information", []) if item_id in objects],
        "actions": [actions[item_id] for item_id in issue.get("actions", []) if item_id in actions],
    }


def feed_payload(args):
    cutoff = date.today() - timedelta(days=max(0, min(args.days, 365)))
    items = [item for item in fetch("agent-feed") if keep(item, args) and item_date(item) >= cutoff.isoformat()]
    return {"window": {"days": args.days, "since": cutoff.isoformat()}, "items": sort_items(items)[:clamp_take(args.take)]}


def search_payload(args):
    needle = args.query.casefold()
    items = []
    for item in all_archive_items(args):
        haystack = json.dumps(item, ensure_ascii=False).casefold()
        if needle in haystack:
            items.append(item)
    return {"query": args.query, "results": items[:clamp_take(args.take)]}


def parser():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base-url", default=BASE, help=argparse.SUPPRESS)
    sub = ap.add_subparsers(dest="command", required=True)
    sub.add_parser("latest")
    issue = sub.add_parser("issue")
    group = issue.add_mutually_exclusive_group(required=True)
    group.add_argument("--date")
    group.add_argument("--number", type=int)
    for name in ("feed", "archive", "search"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--type", dest="kind", choices=tuple(TYPE_ALIASES), default="all")
        cmd.add_argument("--category")
        cmd.add_argument("--market")
        cmd.add_argument("--min-verification", choices=("L1", "L2", "L3", "L4"))
        cmd.add_argument("--take", type=int, default=10)
        if name == "feed":
            cmd.add_argument("--days", type=int, default=7)
        if name == "search":
            cmd.add_argument("--query", required=True)
    return ap


def main():
    global BASE
    args = parser().parse_args()
    BASE = args.base_url.rstrip("/")
    manifest = optional_manifest()
    try:
        if args.command == "latest":
            output = issue_payload(latest_issue(fetch("issues")))
        elif args.command == "issue":
            issues = fetch("issues")
            matched = next((item for item in issues if str(item.get("date")) == args.date), None) if args.date else next((item for item in issues if item.get("number") == args.number), None)
            if not matched:
                target = args.date or f"第 {args.number} 期"
                raise RuntimeError(f"未找到已发布的 {target}")
            output = issue_payload(matched)
        elif args.command == "feed":
            output = feed_payload(args)
        elif args.command == "archive":
            output = {"items": archive_items(args)}
        else:
            output = search_payload(args)
        output["skill_update"] = update_notice(manifest)
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
