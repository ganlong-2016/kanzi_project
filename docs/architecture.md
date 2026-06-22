# 架构总览(多工程 + 多 kzb)

## 1. 目标与边界

- **范围**:仅 Kanzi Studio 侧,产物到 **kzb** 为止。
- **形态**:多个 `.kzproj`,各自导出一个 kzb;由下游 Android 渲染 Service 按需加载、Client 显示。
- **诉求**:多人并行开发、按需加载、独立迭代、按车型裁剪、视觉统一。

## 2. 工程分层

```text
┌──────────────────────────────────────────────────────────┐
│  core  (共享资源工程, 单向被引用, 自己不引用任何人)             │
│   - Resource Dictionaries: Design Token + Theme_Day/Night  │
│   - Prefabs/Components: 通用组件库(Button/Switch/Card…)     │
│   - Localization: 中/英字符串表                              │
│   - Fonts / Icons(Atlas)                                   │
│   - Data Sources: VehicleData(stub, 即数据契约)            │
│   → core.kzb                                               │
└──────▲────────────▲────────────▲────────────▲──────────────┘
       │ 引用         │ 引用         │ 引用         │ 引用
  ┌────┴────┐  ┌──────┴────┐  ┌─────┴──────┐  ┌──┴───────────┐
  │  shell  │  │ launcher  │  │  charging  │  │ vehiclecontrol│  interior ...
  │ 主工程   │  │  首页      │  │   充电      │  │    车控        │   内饰
  └─────────┘  └───────────┘  └────────────┘  └──────────────┘
```

- **core**:地基。所有视觉 token、主题、通用组件、字体、数据契约都在这里。**只被引用,不引用别人。**
- **shell**:主工程。桌面、状态栏、全局导航/转场框架、模块加载占位点。引用 core。
- **module**(launcher / charging / vehiclecontrol / interior / …):每个功能域一个工程,引用 core,内含本模块页面 Prefab。

## 3. 依赖规则(铁律)

1. 依赖**单向、无环**:`shell → core`、`module → core`。
2. **core 不得反向引用** shell 或任何 module。
3. **module 之间不得互相引用**;任何被多个模块需要的东西,一律下沉到 core。
4. **shell 不在设计期硬连 module 内部节点**;模块装载交给运行时加载 kzb,shell 只放占位/加载点。

> 详见 [project-references.md](project-references.md)。

## 4. 跨工程引用机制

Kanzi 资源以 URL 引用,跨工程引用形如:

```text
kzb://core/Prefabs/Components/Button
kzb://core/Resource Dictionaries/Theme_Day
kzb://core/Data Sources/VehicleData
```

含义:模块页面里用到的按钮、颜色、字体、数据字段,实际都指向 `kzb://core/...`。
**因此运行时加载某个 module.kzb 时,必须保证 core.kzb 已加载**,否则这些 URL 解析失败、UI 缺资源。

## 5. 每个工程内部结构(Studio 工程树)

统一采用下述分组(各模块保持一致,便于协作与复制):

```text
<project>.kzproj
├── Screens/                 # 仅 shell 有完整 Screen 根;模块以页面 Prefab 为主
├── Prefabs/
│   ├── Components/          # 仅 core 放通用组件;模块只实例化
│   ├── Widgets/             # 本工程内的组合控件
│   └── Pages/               # 本模块的页面(根 Prefab, 命名稳定供下游加载)
├── Resource Dictionaries/   # 仅 core 定义主题;其他工程引用 core 的
├── Data Sources/            # 仅 core 定义 VehicleData;其他工程绑定 core 的
├── Localization/            # 仅 core 维护字符串表
├── Materials & Textures/
├── Meshes / 3D/             # interior 等含 3D 的模块用
├── Fonts/                   # 仅 core
└── State Managers / Animations/
```

## 6. 模块职责简述

| 模块 | 主要内容 | 备注 |
|------|----------|------|
| `launcher` 首页 | 桌面卡片、时间/天气、快捷入口、媒体小窗 | 高频常驻 |
| `charging` 充电 | SOC、充电状态/功率/剩余时间、续航、充电曲线 | 纯电核心 |
| `vehiclecontrol` 车控 | 车门/车窗/后备厢/车锁/灯光 | 含写指令交互 |
| `interior` 内饰 | 氛围灯(颜色/亮度)、座椅、香氛、天窗 | 常含 3D / 动效 |
| (扩展) 胎压/设置… | 复制 `_ModuleTemplate` 起步 | 见模板 |

## 7. 最小链路验证(开工前)

先只做 `core + shell + 1 个示例模块`,跑通:
- 模块对 core 的引用与 `kzb://` URL 解析;
- 主题切换(Day/Night)与中英文切换在跨工程下生效;
- 各工程独立导出 kzb,且导出顺序/依赖正确;
- 命名约定(根 Prefab、Data 字段)稳定可被下游使用。

验证通过后再并行铺开所有功能模块。
