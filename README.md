# Baijimu Platform Skill

一个平台无关的纯文本 Agent Skill，通过本机
[`baijimu`](https://www.npmjs.com/package/@baijimu/cli) CLI 使用百积木平台。

`baijimu-platform` 是唯一公开技能入口。它负责发现当前 CLI 能力、定位官方文档、执行安全边界和结果回查；
Bundle、Module、Hosted Service、事件、工作流、数据库等产品与架构契约统一维护在
[百积木官方文档站](https://docs.baijimu.com/)，不在技能中复制。

## 权威源与发行物

根目录的 `SKILL.md` 是唯一人工维护的技能源。构建生成：

- `dist/baijimu-platform.zip` 与对应 `.sha256`；ZIP 中只有 `baijimu-platform/SKILL.md`。
- `marketplace/baijimu-platform/SKILL.md`；正文与权威源一致，并增加统一版本、许可和运行要求。

不要手工编辑 `marketplace/` 或 `dist/`。

```bash
python3 tools/build.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_cli.py
```

## 安装

先安装并登录 CLI：

```bash
npm install -g @baijimu/cli
baijimu auth login
baijimu auth status --verify
```

Codex：

```bash
python3 tools/install_codex.py
```

安装器把技能安装到 `~/.agents/skills/baijimu-platform/`。已有版本和旧的 `baijimu-docs`、
`baijimu-bundle-development`、`baijimu-hosted-service-development` 会迁移到
`~/.agents/skill-backups/`，避免多个百积木技能同时被发现。

WorkBuddy、SkillHub、钉钉悟空、TRAE、OpenClaw 和 Hermes 均使用同一个
`baijimu-platform` 发行内容。支持 ZIP 的平台从
[GitHub Releases](https://github.com/momoplan/baijimu-platform-skill/releases) 导入
`baijimu-platform.zip`；市场发布使用 `marketplace/baijimu-platform/`。
GitHub Release 不会自动完成 SkillHub 或其他市场上架，市场版本需要分别发布和验证。

## 发布

仓库版本记录在 `VERSION`。确认版本、生成文件和测试一致后创建同版本 `v*` 标签；`release` workflow
会重新构建并测试，再把 ZIP 和 SHA-256 文件发布到 GitHub Release。

ClawHub 发布 `marketplace/baijimu-platform/` 时使用同一 `VERSION`。真实发布前必须 dry-run，核对发布者、
版本、来源仓库、分类和文件清单。

## 源码布局

```text
SKILL.md                              唯一技能权威源
VERSION                               语义版本
LICENSE                               MIT-0 许可
marketplace/baijimu-platform/SKILL.md 自动生成的市场发行件
tools/                                构建、CLI 冒烟和 Codex 安装工具
tests/                                发行包与迁移测试
dist/                                 可重复构建的 ZIP 与 SHA-256
```
