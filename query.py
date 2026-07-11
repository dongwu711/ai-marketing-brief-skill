#!/usr/bin/env python3
"""只读查询 AI Marketing Brief 已发布的公开 JSON 数据。"""
import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = "https://yingxiaoai.com.cn/api"
USER_AGENT = "AI-Marketing-Brief-Skill/0.1 (+https://yingxiaoai.com.cn)"


def fetch(name):
    request = Request(f"{BASE}/{name}.json", headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=15) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RuntimeError(f"公开数据暂不可用：{error}") from error


def latest_issue(issues):
    if not issues:
        raise RuntimeError("公开数据中没有已发布期次")
    return max(issues, key=lambda issue: (issue.get("number", 0), issue.get("date", "")))


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


def search_payload(query, kind, take):
    groups = ("intel", "cases", "tools") if kind == "all" else (kind,)
    matches = []
    needle = query.casefold()
    for group in groups:
        for item in fetch(group):
            haystack = json.dumps(item, ensure_ascii=False).casefold()
            if needle in haystack:
                matches.append(item)
    matches.sort(key=lambda item: (str(item.get("updated", "")), item.get("id", "")), reverse=True)
    return {"query": query, "results": matches[:take]}


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("latest")
    issue = sub.add_parser("issue")
    issue.add_argument("--date", required=True)
    search = sub.add_parser("search")
    search.add_argument("--query", required=True)
    search.add_argument("--type", choices=("all", "intel", "cases", "tools"), default="all")
    search.add_argument("--take", type=int, default=10)
    args = parser.parse_args()

    try:
        if args.command == "latest":
            output = issue_payload(latest_issue(fetch("issues")))
        elif args.command == "issue":
            matched = next((item for item in fetch("issues") if str(item.get("date")) == args.date), None)
            if not matched:
                raise RuntimeError(f"未找到已发布的 {args.date} 期次")
            output = issue_payload(matched)
        else:
            output = search_payload(args.query, args.type, max(1, min(args.take, 30)))
        print(json.dumps(output, ensure_ascii=False, indent=2))
    except RuntimeError as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
