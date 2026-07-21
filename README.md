# baijimu-platform Skill

一个平台无关的纯文本 Agent Skill，通过本机 [`baijimu`](https://www.npmjs.com/package/@baijimu/cli) CLI 使用百积木平台。

同一份发行包适用于能够读取 `SKILL.md` 并执行本机命令的 Agent，包括 Codex、WorkBuddy 和钉钉悟空。Skill 不携带 PAT、平台私有配置或可执行脚本；所有业务操作均由已安装的 `baijimu` CLI 完成。

## 构建

```bash
python3 tools/build.py
python3 -m unittest discover -s tests -v
python3 tools/smoke_cli.py
```

产物：

- `dist/baijimu-platform.zip`
- `dist/baijimu-platform.zip.sha256`

ZIP 内只有 `SKILL.md` 和 `references/*.md` 文本文件。

## 安装

先安装并登录 CLI：

```bash
npm install -g @baijimu/cli
baijimu auth login
```

Codex：

```bash
python3 tools/install_codex.py
```

安装器会先备份已有的同名技能，再从发行 ZIP 安装并验证内容。

WorkBuddy：在技能页面上传 `dist/baijimu-platform.zip`，或把仓库导入 SkillHub 后安装。

钉钉悟空：打开技能中心，选择“上传技能”，上传 `dist/baijimu-platform.zip`。

## 源码布局

```text
SKILL.md + references/    通用 Skill 唯一源码
tools/                    构建、CLI 冒烟和 Codex 安装工具
tests/                    发行包兼容性测试
dist/                     可重复构建的 ZIP 与 SHA-256
```

发布版本记录在根目录 `VERSION`。修改 Skill 后必须重新构建并运行全部测试；不要手工修改 `dist/`。
