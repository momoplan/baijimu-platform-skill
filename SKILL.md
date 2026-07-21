---
name: baijimu-platform
description: 通过 `baijimu` CLI 使用百积木企业 AI 操作系统。用于登录认证，管理工作区、项目文件和 Git、智能体会话、模型凭证、Bundle、模块、运行时服务与应用、托管服务、数据库配置、平台应用、本地 Connector 和发布流程，或通过公开 Partner API 补充 CLI 尚未封装的能力。适用于任何能够读取 SKILL.md 并执行本机命令的智能体平台。
---

# 百积木平台

通过本机 `baijimu` CLI 操作百积木。把 CLI 视为唯一执行入口；本技能只提供文本工作流，不包含凭证、平台专属工具或私有接口。

## 标准工作流

1. 运行 `baijimu --version` 和目标命令的 `--help`，确认本机安装及实际命令面。
2. 运行 `baijimu capabilities --json` 发现当前 CLI 和公共 Bundle；已知工作区时增加 `--workspace <ID或精确名称>`。
3. 运行 `baijimu auth status --verify`。未登录时运行 `baijimu auth login`，由用户在浏览器中完成授权。
4. 使用 `baijimu resource ...` 或命令自身的精确名称解析，把展示名解析为稳定 ID。零匹配或多匹配时停止并请求稳定 ID。
5. 写操作前读取当前状态，执行后用对应的 `get`、`list`、`status`、`messages`、`resources` 或审计命令回查。
6. 汇报业务结果、稳定 ID、验证证据和仍未解决的权限或版本问题。

如果 `baijimu` 不存在，告知用户先安装官方 CLI。不要静默下载二进制文件，也不要把 token 写进技能目录、命令历史、临时脚本或回复。

## 能力路由

- 认证与工作区：`auth`、`workspace`、`resource`。
- 可发现能力与安装：`capabilities`、`bundle`。
- 项目文件与 Git：`project file`、`project git`。
- 智能体与消息：`agent session`、`agent chat`、`llm-credential`。
- 模块和运行时：`module`、`runtime`。
- 托管服务和构建：`hosted-service`、`rust-build`、`db-profile`。
- 平台应用：`platform-app`。
- 本地 Connector：`local-app`；设备运行面仅在本机 CLI 的帮助或能力输出确认存在时使用。
- CLI 未封装的公开能力：`baijimu api <METHOD> <PATH>`。调用前必须确认 Partner API 路径、参数、权限和返回结构。

读取 `references/cli-and-runtime-entrypoints.md` 获取命令模式。处理桌面、本地 shell、设备或 Connector 时读取 `references/desktop-and-bridge-agent.md`。判断能力归属或排查顺序时读取 `references/platform-map.md`。

## 执行规则

- 不编造 workspaceId、projectId、businessId、method、connectorId、moduleId、versionId、sessionId 或发布 ID。
- 不把展示名、模糊搜索结果第一项或缓存状态当作协议标识。
- 不熟悉命令时先运行相应的 `--help`；帮助中不存在的命令不得执行。
- Runtime 调用先列服务，再读取方法定义，最后调用；所有业务参数放入 `--params` 对象，无参数也显式传 `{}`。
- 复杂 JSON 优先写入临时文件并使用 `@file`，完成后清理不含用户资产的临时文件。
- 不直接编辑 CLI 认证文件、Bridge Agent 配置、Connector 安装目录或 management token。
- 不输出 PAT、模型密钥、服务令牌、cookie 或完整认证响应。除非用户明确要求，不使用任何显示 secret 的选项。

## 风险与确认

查询、列表、帮助、状态和审计属于只读操作，可直接执行。

创建、更新、安装、升级、发布、提交审核和调用可能产生业务副作用的方法，必须确保目标与参数明确；执行后回查。

删除、卸载、回滚、重置、撤回发布、释放数据库、覆盖远端内容，以及可能产生费用或向外部发送消息的操作，必须获得用户对准确目标的明确授权。不要用临时兼容分支、缓存态或手工改服务器文件绕过失败。

## 完成标准

只有在目标操作成功且状态源回查一致时才报告完成。若失败，保留原始错误码和可公开的错误信息，区分 CLI 版本缺失、认证失败、权限不足、资源解析失败、平台业务错误和本地 Connector 不健康。
