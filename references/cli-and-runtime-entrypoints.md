# `baijimu` CLI 命令入口

本参考给出稳定的命令模式。具体子命令和参数以本机 `baijimu capabilities --json` 与 `--help` 为准。

## 起步与认证

```bash
baijimu --version
baijimu capabilities --json
baijimu auth status --verify
baijimu workspace list
```

未登录时：

```bash
baijimu auth login
```

只有用户明确提供 PAT 并要求非交互配置时才使用 `auth token set`。不要把 token 放进回复或可提交文件。

## 工作区与稳定 ID

```bash
baijimu workspace list
baijimu workspace get <workspaceId>
baijimu resource workspace <ID或精确名称>
baijimu resource bundle-market <listingId|bundleId|精确名称>
baijimu resource bundle-install <workspace> <installId|bundleId|精确名称>
baijimu resource bundle-definition <workspace> <id|bundleId|精确名称>
```

名称解析只接受大小写不敏感的精确匹配。零匹配或多匹配时改用稳定 ID。

## 项目文件与 Git

```bash
baijimu project file list <projectId> [path]
baijimu project file read <projectId> <path>
baijimu project file grep <projectId> <query> [path]
baijimu project file write <projectId> <path> --content-file <file>
baijimu project file download <projectId> [path]
baijimu project file import-url <projectId> <targetPath> --source-url <url>

baijimu project git status <projectId>
baijimu project git head <projectId>
baijimu project git log <projectId>
baijimu project git diff <projectId> <filePath>
baijimu project git commit <projectId> --message <message> --file <path>
baijimu project git pull <projectId>
baijimu project git push <projectId>
```

`rollback` 和 `reset` 是破坏性操作，只能在用户明确授权准确目标时执行。

## 智能体会话

```bash
baijimu agent session create <projectId> --agent-config-id <id>
baijimu agent session list <projectId>
baijimu agent session recent
baijimu agent session get <projectId> <sessionId>
baijimu agent session messages <projectId> <sessionId>
baijimu agent session audit <projectId> <sessionId>
baijimu agent chat <projectId> <sessionId> --message <text>
```

创建模型凭证前先查看帮助并确认作用域。除非用户明确需要，不使用 `--show-secret`。

## Bundle

先发现市场和当前安装状态：

```bash
baijimu bundle market list --workspace <workspace>
baijimu bundle market get <listingId|bundleId|精确名称> --workspace <workspace>
baijimu bundle list <workspace>
baijimu bundle get <workspace> <installId|bundleId|精确名称>
```

安装、升级和查询资源：

```bash
baijimu bundle install <workspace> <listingId|bundleId|精确名称>
baijimu bundle upgrade <workspace> <installId|bundleId|精确名称> [--version-id <id>]
baijimu bundle resources <workspace> <installId|bundleId|精确名称>
baijimu bundle uninstall <workspace> <installId|bundleId|精确名称> --yes
```

Bundle 定义、版本、审核和市场发布使用 `bundle create|update|definition|version|review|market`。这些写操作的参数随 CLI 版本演进，执行前必须读取对应 `--help`，发布后回查版本、审核和市场记录。

## Runtime 服务

```bash
baijimu runtime services list <workspaceId>
baijimu runtime service get <workspaceId> <businessId> --method <method>
baijimu runtime service call <workspaceId> <businessId> <method> --params <json|@file>
```

顺序固定为：列服务、读取方法定义、调用。不得猜 businessId、method 或字段结构。无参数方法也传 `--params '{}'`。

部分 CLI 版本把运行时应用安装能力放在 Bundle 或平台应用命令中。不要假设存在 `runtime app`；以本机帮助和能力输出为准。

## 模块、托管服务和平台应用

```bash
baijimu module --help
baijimu hosted-service --help
baijimu rust-build --help
baijimu db-profile --help
baijimu platform-app --help
```

这些命令覆盖模块项目/定义/方法/版本、托管服务及环境、Rust 构建产物、数据库分配、平台应用版本/市场/工作区安装。先读取目标对象，再执行写操作，最后读取同一状态源验证。

释放数据库、撤回发布、卸载应用、删除或覆盖版本必须取得明确授权。

## 本地 Connector

开发者发布记录使用：

```bash
baijimu local-app list
baijimu local-app get <appId>
baijimu local-app create --data @app.json
baijimu local-app update <appId> --data @app.json
baijimu local-app version create <appId> --data @version.json
baijimu local-app submit <appId> <version>
baijimu local-app publications
baijimu local-app withdraw <publicationId>
```

较新 CLI 可能提供 `local-app install` 和 `local-app device ...` 设备运行面。只有 `baijimu local-app --help` 明确列出时才能使用；详情见 `desktop-and-bridge-agent.md`。

## Partner API 兜底

CLI 未封装但已有正式 Partner API 文档或已确认路径时：

```bash
baijimu api <METHOD> <PATH> [--data <json|@file>] [--query k=v]
```

不得猜测内部接口、绕过公开权限或直接访问内部网关。调用前确认路径、参数、权限和返回结构，调用后用公开查询接口回查。
