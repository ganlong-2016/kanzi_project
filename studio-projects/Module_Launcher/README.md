# launcher — 首页模块

**工程名**:`launcher` · **产物**:`launcher.kzb` · 引用 `core`。

桌面首页:卡片入口、时间/天气、快捷功能、媒体小窗等。复制 `_ModuleTemplate` 起步。

## 结构

```text
launcher.kzproj  (引用 core)
└── Prefabs/Pages/LauncherPage   # 根 Prefab(下游加载入口)
    Prefabs/Widgets/             # HomeCard / QuickAction / MediaMiniPlayer ...
```

## 数据绑定

- 主要绑定 `kzb://core/Data Sources/VehicleData/System`(时间、日期、网络、蓝牙、车外温度)。
- 卡片可聚合展示 Charging / Interior 的关键字段(只读),如 SOC、续航。

## 注意

- 高频常驻,严控首帧资源与内存。
- 文案双语、样式走主题 token、信号处理故障态。
