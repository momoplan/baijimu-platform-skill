---
name: baijimu-platform
description: 使用百积木构建、分发和运行业务包（Bundle），将专业知识、业务流程和工具能力交付给团队或企业。平台提供企业级 AI Coding 能力和办公基础设施，支撑业务包的构建、交付与协作使用。通过官方文档理解流程，通过本机 baijimu CLI 执行。
version: 2.0.7
author: Baijimu
license: MIT-0
platforms: [openclaw, hermes]
metadata:
  openclaw:
    requires:
      bins: [baijimu]
    install:
      - kind: node
        package: "@baijimu/cli"
        bins: [baijimu]
    homepage: https://github.com/momoplan/baijimu-platform-skill
  hermes:
    tags: [baijimu, lowcode, automation, cli]
    requires_toolsets: [terminal]
---

# 百积木平台

百积木是业务包（Bundle）的构建、分发与运行平台。通过提供企业级 AI Coding 能力和办公基础设施，帮助个人和团队将专业知识、业务流程及工具能力封装成可安装的业务包，交付给团队或企业使用，并管理授权、版本与升级。本技能提供能力概览和操作入口，详细流程、接口与示例由官方文档维护。

## 平台能做什么

- 构建业务包：用智能体、工作流、定时任务、业务模块与应用组合 Bundle，按需通过 AI Coding 开发配套网站、工具和后端服务。
- 分发业务包：发布 Bundle，向指定工作区交付，或通过市场公开分发。
- 运行与协作：依托工作区、成员、权限、模型和消息渠道等办公基础设施使用专业能力，通过公开 API 与本地 Connector 接入外部系统和用户设备。
- 持续维护：管理源码、版本、授权、安装与升级，查询部署、执行状态和日志，验证业务结果。

Bundle 不声明其他 Bundle 的安装依赖，资源之间通过运行时引用和配置协作。语义校验在开发和创建版本时完成，安装交付已验证的资源与执行产物；安装、绑定生效和实际调用分别确认。Workflow、Timer 和 Event Trigger 的外部服务通过本包 Module 属性绑定，直接资源引用限定本包，不新增独立启用流程。执行主体首次安装默认安装人，后续配置和升级保留该主体；Timer 沿用自身启停与调度设置。具体规则见官方文档的 Bundle 开发章节。

## 如何开展任务

1. 根据用户目标按需读取 <https://docs.baijimu.com/>。不知道页面路径时，从 <https://docs.baijimu.com/llms.txt> 或 <https://docs.baijimu.com/docs-manifest.json> 定位相关 Markdown、Schema 和示例。
2. 运行 `baijimu --version` 和 `baijimu --help`，再沿当前任务所需的命令路径逐级读取 `--help`，确认实际命令与参数。CLI 不在 `PATH` 时，检查官方安装位置：Windows 为 `$env:LOCALAPPDATA\Baijimu\bin\baijimu.exe`，macOS/Linux 为 `~/.local/bin/baijimu`。未安装时提示用户安装，不静默下载。
3. 访问工作区资源前运行 `baijimu auth status --verify`；未登录时使用 `baijimu auth login`。从当前平台查询准确目标、权限与状态；项目源码按官方 Git 流程检出和修改，遵守项目实际分支策略；Runtime 调用参数从当前方法定义读取。
4. 在用户授权范围内执行，并回查结果。开发任务包含相应的验证、交付与正式入口验证，不能把提交、构建或版本创建成功当作完整任务完成。

## 工作区上下文与项目文件

工作区选择按“命令显式参数 → 本次任务的 `BAIJIMU_CURRENT_WORKSPACE_ID` → 用户默认工作区”解析。未指定目标时使用默认；用户已明确其他工作区时，把权威解析出的工作区 ID 传给本次任务的全部相关命令，或只在任务进程设置该环境变量。一次 `--workspace-id` 不改变默认，也不会让下一条命令自动继承；只有用户明确要求切换默认时才运行 `workspace use`，不要为某个并行任务改共享默认。

项目列表、详情、文件与 Git 使用同一目标工作区。先读取目标子命令帮助；文件的 `list/read/grep/download` 支持 `--workspace-id` 时显式传入，不支持时只为该次命令设置任务环境变量。Git 检出使用 `project checkout`，后续 Git 使用检出时绑定的工作区；旧检出尚未绑定时在任务进程明确工作区。不得遍历其他工作区凭据来尝试成功。

`FORBIDDEN` 不足以证明账号没有项目权限。保留服务端原始错误码，并核对 CLI 实际使用的工作区、任务上下文和目标项目；本地缺少目标凭据、工作区范围不符和项目授权失败分别说明。CLI JSON 的标准输出保留 Owner 错误，标准错误中的请求上下文用于诊断，二者都应读取；不输出凭据。

## 执行边界

官方文档定义产品流程，本机 CLI 帮助定义执行参数，平台实时查询定义资源身份和状态。三者不一致时保留实际错误并说明缺口，不猜测标识或参数，不通过内部 API、手工数据库或服务器修改绕过产品流程。

不输出或直接编辑认证凭据。删除、卸载、回滚、重置、覆盖远端内容、产生费用或向外部发送消息前，确认用户已明确授权准确目标与操作。
