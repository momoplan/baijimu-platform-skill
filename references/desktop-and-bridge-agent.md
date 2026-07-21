# 百积木本地端与 Connector

处理桌面控制、本地 shell、本地 HTTP 服务、设备授权、本地应用和 Connector 时读取本参考。

## 角色与边界

- 百积木本地端在用户机器上管理本地应用、服务和授权。
- Bridge Agent 负责本机 Connector 生命周期和能力上报。
- Relay 负责鉴权与转发，不执行本地命令。
- 外部调用方只能使用用户已授权的 `service.method`。

不要假设本地 shell、截图、桌面控制或本地服务天然可用。先确认本地端已安装、运行并完成授权。

## 术语

- 本地应用：用户在桌面 UI 中管理的对象。
- Connector：包含 `connector.json` 和服务注册文件的可安装本地应用包。
- 服务：协议能力组，例如 `computer`、`shell` 或某个 Connector 注册的服务。
- 方法：可调用动作，例如 `computer.screenshot` 或 `shell.exec`。
- 事件：Connector 上报的异步事件。

对用户沟通时使用“本地应用”；排查协议时使用稳定的 `service.method`。

## 授权流程

1. 用户安装并启动百积木本地端。
2. 用户在平台授权页面授权设备和工作区。
3. 本地端取得设备侧凭证并连接 Relay。
4. 用户授权指定本地应用或服务能力。
5. 调用方经 Relay 使用已授权的 `service.method`。

不要混淆设备侧凭证与调用方凭证，不要读取或打印任一 token。

## CLI 管理

先检查本机命令面：

```bash
baijimu local-app --help
```

如果帮助中存在设备运行面，再按帮助使用以下能力：

```bash
baijimu local-app device status
baijimu local-app device market
baijimu local-app install <marketAppId> --market
baijimu local-app install <source> --accept-untrusted
baijimu local-app device list
baijimu local-app device get <connectorId>
baijimu local-app device start <connectorId>
baijimu local-app device stop <connectorId>
baijimu local-app device sync <connectorId>
baijimu local-app device invoke <connectorId> <operation> --params <json|@file>
baijimu local-app device uninstall <connectorId> --yes
```

- 市场安装先读取市场记录取得真实 appId。
- 本地目录、Git 或 URL 属于用户信任来源，检查来源后才可接受非市场安装风险。
- `device invoke` 只能调用清单声明的 management operation。
- 安装、同步、启停或设置后用 `device get/list` 回查；远程调用还要确认 Relay 上报的服务和方法。
- 不直接编辑 Bridge Agent 配置、Connector 目录、发现文件或 management token。

如果本机 CLI 不提供设备运行面，明确报告版本/能力缺失，不要用手工改配置替代。

## 排查顺序

1. 本地端已安装、运行并授权。
2. Relay 连接正常。
3. Connector 已安装并启用。
4. 本地健康检查通过。
5. Relay 可见预期的服务、方法或事件。
6. 调用方具有目标能力权限。
7. 本地日志、Relay 记录和平台审计相互印证。
