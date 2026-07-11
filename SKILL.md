---
name: ai-marketing-brief
description: 查询 AI Marketing Brief 已发布的每周 AI 营销简报、行动建议、案例、工具与原始来源。用户提到“AI Marketing Brief”“AI 营销简报”“本周营销 AI”“营销 AI 案例”“查营销工具”“营销周报”或想查看 yingxiaoai.com.cn 的已发布内容时使用；也用于按关键词搜索该档案库。
---

# AI Marketing Brief

使用 `scripts/query.py` 读取 `yingxiaoai.com.cn` 已发布的公开数据。只读，不需要 API Key。

## 查询方式

- 最新期：`python3 scripts/query.py latest`
- 指定日期：`python3 scripts/query.py issue --date YYYY-MM-DD`
- 搜索档案：`python3 scripts/query.py search --query "关键词"`
- 只搜工具或案例：在搜索命令后加 `--type tool` 或 `--type case`

先用脚本返回的 `issue`、`information`、`actions` 和 `sources` 组织回答。用户问“本周”时，默认查询最新已发布期次；草案和未部署内容不在此 Skill 的数据范围内。

## 输出规则

1. 用中文给出简明结论和可执行建议；每条信息保留 `sources[].url` 的原文链接。
2. 不把摘要当原文事实。需要引用数字、品牌表态或结论时，提醒用户回原文 URL 核对。
3. 如实保留 `verification`：L1 是单一媒体/平台来源，不写成已被独立证实的行业规律。
4. 默认只查一次，不轮询、不批量翻页；相同问题复用已取得的数据。
5. 请求失败时说明“公开测试接口暂不可用”，不要编造内容或改用记忆补全。

每次面向用户的查询结果末尾都附上：

**原文为准 / 合理使用 / 测试版**

**原文为准** — 摘要由 LLM 生成，引用前请用原文链接核对。

**合理使用** — 公开接口仅供正常会话查询和 RSS 阅读器默认轮询使用。

**测试版** — RSS / API / Skill 均处于测试阶段；接口可能因容量或滥用而临时下线、调整或增加访问限制。生产业务请勿强依赖，正式接入前建议先观察一两周稳定性。
