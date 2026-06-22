# interior — 内饰模块

**工程名**:`interior` · **产物**:`interior.kzb` · 引用 `core`。

内饰控制与展示:氛围灯(颜色/亮度)、香氛、座椅加热、天窗。常含 3D / 动效。复制 `_ModuleTemplate` 起步。

## 结构

```text
interior.kzproj  (引用 core)
├── Prefabs/Pages/InteriorPage   # 根 Prefab(下游加载入口)
│   Prefabs/Widgets/             # AmbientColorPicker / SeatControl / FragranceControl ...
├── Meshes / 3D/                 # 内饰 3D 模型(若有)
└── Materials & Textures/
```

## 数据绑定(契约分组 `Interior`)

| UI | 字段 | 备注 |
|----|------|------|
| 氛围灯开关 | `ambientOn` / `ambientValid` | 写操作 |
| 氛围灯颜色 | `ambientColor`(#RRGGBBAA) | 写操作 |
| 氛围灯亮度 | `ambientBrightness`(0-100) | 写操作 |
| 香氛 | `fragranceOn` / `fragranceLevel`(0-3) | |
| 座椅加热 | `seatHeatLevel`(0-3) | |
| 天窗 | `sunroofPosition`(0-100) | |

## 注意

- 3D 资源注意面数 / 纹理预算(见 export-kzb.md)。
- 文案双语、样式走主题 token、信号处理故障态。
