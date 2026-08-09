# baijimu-platform Skill

一个平台无关的纯文本 Agent Skill，通过本机 [`baijimu`](https://www.npmjs.com/package/@baijimu/cli) CLI 使用百积木平台。

同一份技能内容适用于能够读取 `SKILL.md` 并执行本机命令的 Agent，包括 Codex、Claude Code、WorkBuddy、钉钉悟空、OpenClaw、Hermes 和 TRAE。Skill 不携带 PAT、平台私有配置或可执行脚本；所有业务操作均由已安装并完成授权的 `baijimu` CLI 执行。跨版本稳定规则保存在 Skill，易变化的命令结构和详细说明发布在[百积木官方文档站](https://docs.baijimu.com/)中，并由 CLI 返回与本机版本严格绑定的地址。

## 唯一内容源与发行物

根目录 [`SKILL.md`](./SKILL.md) 是唯一人工维护的技能内容源。构建过程从它生成两类发行物：

- `dist/baijimu-platform.zip`：通用纯文本包，供 Codex、Claude Code、WorkBuddy、钉钉悟空和 TRAE 导入；ZIP 内只有 `baijimu-platform/SKILL.md`。
- `marketplace/baijimu-platform/SKILL.md`：自动生成的 OpenClaw/Hermes 市场版本，正文与根目录完全一致，并额外声明版本、MIT-0 许可、`baijimu` 可执行文件、npm 安装方式和 Hermes 终端工具要求。

不要手工编辑市场版本。修改根目录 Skill 或 `VERSION` 后运行构建脚本，并提交生成结果。

```bash
python3 tools/build.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_cli.py
```

通用 ZIP 和 SHA-256 发布到 [GitHub Releases](https://github.com/momoplan/baijimu-platform-skill/releases)。发布版本记录在根目录 `VERSION`。

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

安装器会把统一技能安装到 `~/.agents/skills/baijimu-platform/`，并把旧的 `baijimu-docs` 或 `~/.codex/skills/baijimu-platform` 迁移到 `~/.agents/skill-backups/`。备份不会留在技能发现目录中，因此不会被重复发现。

## WorkBuddy、SkillHub、钉钉悟空和 TRAE

下载 [GitHub 最新发行包](https://github.com/momoplan/baijimu-platform-skill/releases/latest/download/baijimu-platform.zip)：

- WorkBuddy：在「专家·技能·连接器」中上传 ZIP，或把本仓库单独提交到 SkillHub。GitHub 发布不会自动同步到 SkillHub。
- 钉钉悟空：在技能中心选择上传技能并导入 ZIP。
- TRAE：在「设置 → 技能与命令 → 创建」中导入 ZIP，或把 `SKILL.md` 放到项目的 `.trae/skills/baijimu-platform/`。当前仓库不假定存在可自动提交的 TRAE 公共市场接口。

千问办公目前单独管理自己的技能套件和上架渠道；在其开放标准 `SKILL.md` 导入或公开开发者提交流程前，不能把本仓库的 GitHub/ClawHub 发布等同于千问办公上架。

## OpenClaw

不经过市场时，可以直接从 GitHub 安装根目录 Skill：

```bash
openclaw skills install git:momoplan/baijimu-platform-skill --global
```

进入 ClawHub 后，也可以在 OpenClaw 中搜索并安装市场版本：

```bash
openclaw skills search baijimu
```

市场发布目录是 `marketplace/baijimu-platform/`。仓库提供 ClawHub 的 Pull Request 预检和手动发布工作流；真实发布前必须在 GitHub 仓库配置 `CLAWHUB_TOKEN`。

## Hermes

Hermes 可以直接安装公开的根目录 Skill：

```bash
hermes skills install https://raw.githubusercontent.com/momoplan/baijimu-platform-skill/main/SKILL.md
```

Hermes 也把 ClawHub 集成为社区来源。ClawHub 版本公开可见后，无需再复制一份技能到 Hermes 仓库：

```bash
hermes skills search baijimu --source clawhub
```

## 发布

### GitHub Release

确认 `VERSION`、生成文件和测试全部一致后创建同版本标签；标签推送会运行完整构建和测试，再发布通用 ZIP 与 SHA-256。

### ClawHub

ClawHub 上的技能统一采用 MIT-0 许可。本仓库已采用同一许可，市场发行目录只包含待发布的 `SKILL.md`，不会把测试、安装器或仓库配置误打进技能包。

本地首次发布或排查时先预检：

```bash
clawhub login
clawhub skill publish marketplace/baijimu-platform \
  --version "$(tr -d '\n' < VERSION)" \
  --categories productivity \
  --topics baijimu,lowcode,automation,cli \
  --dry-run
```

确认发布者、版本、来源仓库、分类和文件清单正确后，移除 `--dry-run` 完成发布。后续也可以在 GitHub Actions 中手动运行 `ClawHub` 工作流；该工作流需要仓库 Secret `CLAWHUB_TOKEN`。

## 源码布局

```text
SKILL.md                                  唯一人工维护的通用 Skill 内容
VERSION                                   统一语义版本
LICENSE                                   MIT-0 许可
marketplace/baijimu-platform/SKILL.md     自动生成的 OpenClaw/Hermes 市场发行件
tools/                                    构建、CLI 冒烟和 Codex 安装工具
tests/                                    发行包与跨平台元数据测试
dist/                                     可重复构建的 ZIP 与 SHA-256
```
