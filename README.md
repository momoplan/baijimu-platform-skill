# Baijimu Agent Skill Suite

一组平台无关的纯文本 Agent Skill，通过本机
[`baijimu`](https://www.npmjs.com/package/@baijimu/cli) CLI 使用百积木平台：

- `baijimu-platform`：认证、能力发现、工作区、Project/Git 和通用能力路由。
- `baijimu-bundle-development`：Bundle-first 的 Module、资源、审核、市场和 Runtime 安装生命周期。
- `baijimu-hosted-service-development`：后端 Project、BuildJob/Artifact、数据库迁移、Environment、
  Deployment 和 Endpoint。

技能只保存跨版本稳定边界。易变化的参数、命令结构和详细协议发布在
[百积木官方文档站](https://docs.baijimu.com/)中，并由 CLI 返回与本机版本严格绑定的地址。

## 内容源与发行物

三个 `SKILL.md` 都是人工维护的权威源：

```text
SKILL.md
skills/baijimu-bundle-development/SKILL.md
skills/baijimu-hosted-service-development/SKILL.md
```

构建为每个技能分别生成：

- `dist/<skill-name>.zip` 与对应 `.sha256`，ZIP 中只有 `<skill-name>/SKILL.md`。
- `marketplace/<skill-name>/SKILL.md`，正文与权威源一致，并增加统一版本、MIT-0 许可和运行要求。

这样支持只导入单个 Skill 的 Agent 平台，也允许 Codex 一次安装完整套件。不要手工编辑 `marketplace/`
或 `dist/`。

```bash
python3 tools/build.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_cli.py
```

## 安装前准备

```bash
npm install -g @baijimu/cli
baijimu auth login
baijimu auth status --verify
```

## Codex

```bash
python3 tools/install_codex.py
```

安装器会把三个技能安装到 `~/.agents/skills/`，把已存在的目标技能和旧 `baijimu-docs` 技能迁移到
`~/.agents/skill-backups/`。安装过程可重复执行；内容一致时不会生成新备份。

## WorkBuddy、SkillHub、钉钉悟空和 TRAE

从 [GitHub Releases](https://github.com/momoplan/baijimu-platform-skill/releases) 下载需要的独立 ZIP：

- 通用能力必须安装 `baijimu-platform.zip`。
- 开发 Bundle 时再安装 `baijimu-bundle-development.zip`。
- 开发后端时再安装 `baijimu-hosted-service-development.zip`。

WorkBuddy 和钉钉悟空使用各自技能中心上传 ZIP；TRAE 可导入 ZIP 或把对应 `SKILL.md` 放入项目的
`.trae/skills/<skill-name>/`。GitHub 发布不会自动等同于 SkillHub 或其他市场上架。

## OpenClaw 与 Hermes

市场发行目录分别位于 `marketplace/<skill-name>/`。ClawHub 可以逐个发布和搜索三个技能；Hermes 可通过
ClawHub 使用已公开版本。直接从 GitHub 安装时也应逐个选择对应的权威 `SKILL.md`，不要把多个技能正文
合并成一个文件。

## 发布

仓库版本记录在 `VERSION`。确认版本、生成文件和测试一致后创建同版本 `v*` 标签；`release` workflow
会重新构建并测试，再把三个 ZIP 与三个 SHA-256 文件发布到同一个 GitHub Release。

ClawHub 发布每个 `marketplace/<skill-name>/` 目录时使用相同 `VERSION`。真实发布前必须分别 dry-run，
核对发布者、版本、来源仓库、分类和文件清单。

## 源码布局

```text
SKILL.md                                      基础路由 Skill
skills/*/SKILL.md                             场景 Skill 权威源
VERSION                                       套件统一语义版本
LICENSE                                       MIT-0 许可
marketplace/<skill-name>/SKILL.md             自动生成的市场发行件
tools/                                        构建、CLI 冒烟和 Codex 安装工具
tests/                                        发行包、路由与跨平台元数据测试
dist/                                         可重复构建的 ZIP 与 SHA-256
```
