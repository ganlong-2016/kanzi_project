# shell — 主工程

**工程名**:`shell` · **产物**:`shell.kzb` · **角色**:桌面框架 / 状态栏 / 全局导航与转场 / 模块加载占位点。

引用 `core`。在 Kanzi Studio 于本目录创建 `shell.kzproj`。

## 必须包含

```text
shell.kzproj   (引用 core)
├── Screens/                 # 完整 Screen 根节点 / 视口
├── Prefabs/
│   ├── Pages/
│   │   └── LauncherShell    # 桌面外壳(状态栏 + 内容区 + 导航)
│   └── Widgets/
│       └── StatusBar        # 实例化 core 的 StatusBar,绑定 System 数据
└── State Managers / Animations/   # 全局转场/导航动效模板
```

## 约束

- **不在设计期硬连任何 module 内部节点**;只放占位/加载点,模块 kzb 由下游运行时加载。
- 状态栏、主题切换入口、语言切换入口等全局元素放这里,数据绑定到 `kzb://core/Data Sources/VehicleData/System`。
- 视觉一律引用 `core` 的 token / 组件 / 字体,不写死样式。
