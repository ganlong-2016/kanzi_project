# nextrea — Kanzi Studio 工程基线

本仓库是 **nextrea** 车机 HMI 的 **Kanzi Studio 侧**工程基线与规范集合。
产物边界:**只负责到导出 kzb 为止**;导出的 kzb 交由 Android 渲染 Service 加载、各 Client 显示(不在本仓库范围内)。

## 架构一句话

> 多工程模块化、多 kzb 产物:**Core 共享资源工程(被所有人单向引用)+ Shell 主工程 + 各功能域子工程**;每个工程独立导出一个 kzb;跨工程靠 `kzb://` URL 引用;运行时加载任意模块 kzb 前必须先加载 `core.kzb`。

```text
                 core (共享资源, 导出 core.kzb)
                  ▲      ▲      ▲      ▲
        ┌─────────┘      │      │      └─────────┐
   shell(主工程)   launcher   charging  vehiclecontrol  interior ...
   shell.kzb      launcher.kzb charging.kzb vehiclecontrol.kzb interior.kzb
```

## 关键参数

| 项 | 值 |
|----|----|
| 项目名 | `nextrea` |
| 多语言 | 中文(`zh-CN`)/ 英文(`en`)切换 |
| 主题 | 白天(`Day`)/ 夜间(`Night`) |
| 初期模块 | Launcher 首页、充电、车控、内饰(可扩展:胎压、设置…) |
| 导出 | 多 kzb,每个 `.kzproj` 一个 kzb |

## 工程清单

| Kanzi 工程名 | 角色 | 产物 | 目录 |
|--------------|------|------|------|
| `core` | 共享资源(token/主题/组件库/字体/数据契约) | `core.kzb` | `studio-projects/Core/` |
| `shell` | 主工程:桌面框架/状态栏/导航 | `shell.kzb` | `studio-projects/Shell/` |
| `launcher` | 首页 | `launcher.kzb` | `studio-projects/Module_Launcher/` |
| `charging` | 充电 | `charging.kzb` | `studio-projects/Module_Charging/` |
| `vehiclecontrol` | 车控(门窗/锁/灯…) | `vehiclecontrol.kzb` | `studio-projects/Module_VehicleControl/` |
| `interior` | 内饰(氛围灯/座椅/香氛…) | `interior.kzb` | `studio-projects/Module_Interior/` |
| `_template` | 模块模板(复制即用) | — | `studio-projects/_ModuleTemplate/` |

## 文档索引

- [在 Kanzi Studio 中建工程操作手册](docs/setup-in-studio.md)
- [架构总览](docs/architecture.md)
- [工程引用与依赖规范](docs/project-references.md)
- [命名规范](docs/naming-conventions.md)
- [导出与 kzb 依赖规范](docs/export-kzb.md)
- [多语言(中/英)方案](docs/localization.md)
- [主题(日/夜)方案](docs/theming.md)
- [Data Source 数据契约说明](docs/data-source-contract.md)
- 数据契约文件:[`contracts/vehicle-data.schema.json`](contracts/vehicle-data.schema.json)
- 设计 token:[`design-tokens/tokens.json`](design-tokens/tokens.json)

## 说明:为什么仓库里没有 `.kzproj`

`.kzproj` 及其资源由 **Kanzi Studio 创建并维护**,属于工具私有格式。本仓库提供:
- 各工程的**目录占位与 README**(规定每个工程里该放什么、引用谁);
- 全套**规范文档**(架构/引用/命名/导出/多语言/主题);
- **数据契约**与**设计 token** 源文件(供 Studio 内建 Data Source / Resource Dictionary 时逐字段对齐)。

各组在 Kanzi Studio 中按对应目录的 README 建立 `.kzproj`,并把工程文件提交回该目录。

### Tool_project vs Application(kzb-only 工作流)

Kanzi Studio 新建工程会生成两个文件夹:
- **`Tool_project/`**:`.kzproj` + 资源,**kzb 从这里导出 —— 只需要它**,提交进 Git。
- **`Application/`**:C++ 运行时/各平台构建脚手架。本项目由 Android 加载 kzb,**不编译它**;已在 `.gitignore` 忽略 `studio-projects/**/Application/`,本地保留不碍事,**不必每次手删**。

建议把 kzb 的导出输出路径显式设到独立的 `out/` 目录,避免依赖 `Application/` 下的默认路径。

## 开工顺序(摘要)

1. 先建 `core` 并导出 `core.kzb`(token + 日/夜主题 + 通用组件库 + 冻结的 Data Source stub)。
2. 建 `shell`,引用 `core`,搭桌面/状态栏/导航 + 模块加载占位点。
3. 用 `_ModuleTemplate` 复制出一个示例模块,跑通 `core + shell + 1 模块` 的最小链路(引用/URL/导出/命名全部验证)。
4. 并行铺开 launcher / charging / vehiclecontrol / interior。

详见各文档。
