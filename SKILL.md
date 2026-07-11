---
name: ai-marketing-brief
description: 查询 AI Marketing Brief 已发布的营销 AI 周刊、最近更新、案例、工具与原文来源。用户提到“AI Marketing Brief”“AI 营销简报”“营销 AI 简报”“今天营销 AI”“最近营销 AI”“营销 AI 案例”“AI 营销工具”“营销周报”“GEO”“AIGC 创意”或“营销自动化”时使用；也用于检索 yingxiaoai.com.cn 的已发布营销 AI 档案库。
---

# AI Marketing Brief

使用 `query.py` 查询 `yingxiaoai.com.cn` 的已发布公开数据。只读、无需 API Key；候选、草稿与未部署期次不在结果范围内。

## 路由

- “本周 / 本期 / 周报 / 该知道什么 / 可以做什么” → `latest`。
- “今天 / 最近 N 天 / 最近更新 / 新内容” → `feed --days N`；未写天数时默认 7 天。
- “全部 / 档案库 / 历史案例 / 工具目录” → `archive`；仅当用户明确要全量时使用。
- 品牌、行业、工具、渠道、GEO、AIGC 创意、营销自动化等具体问题 → `search`，并按用户条件加筛选。

不要把“来源数量”“验证等级”或“更新时间”称作热度。这里提供的是本期编辑精选和最近已审核更新，不是算法热搜榜。

## 命令

```bash
python3 query.py latest
python3 query.py issue --number 2
python3 query.py issue --date 2026-07-13
python3 query.py feed --days 3 --category aigc-creative
python3 query.py archive --type case --market CN --min-verification L2
python3 query.py search --query "小红书" --type intel
```

可用于 `feed`、`archive`、`search` 的筛选：`--type`（intel / case / tool / all）、`--category`（五大分类）、`--market`、`--min-verification`（L1–L4）和 `--take`。`search` 额外需要 `--query`。

## 输出规则

1. 用直接、业务人员看得懂的中文作答；不要展示 API 路径、参数、缓存或内部实现。
2. 每条信息保留 `sources[].url` 原文链接和 `verification`。数字、品牌表态与结论引用前必须回原文核对。
3. L1 是单一媒体、平台自述或服务商来源，不写成已被独立证实的行业规律；L0 不进入“最近已审核更新”。
4. 用户问当天而滚动流没有内容时，如实说明“暂无新的已审核更新”，可补充最新周刊，不拿旧条目凑数。
5. 每会话首次查询时，读取结果中的 `skill_update`；只有 `available: true` 才在最终回答末尾提示一次更新。查询失败时说明“公开测试接口暂不可用”，不要用记忆补全。

每次面向用户的查询结果末尾都附上：

**原文为准 / 合理使用 / 测试版**

**原文为准** — 摘要由 LLM 生成，引用前请用原文链接核对。

**合理使用** — 公开接口仅供正常会话查询和 RSS 阅读器默认轮询使用。

**测试版** — RSS / API / Skill 均处于测试阶段；接口可能因容量或滥用而临时下线、调整或增加访问限制。生产业务请勿强依赖，正式接入前建议先观察一两周稳定性。
