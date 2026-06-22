# vehiclecontrol — 车控模块

**工程名**:`vehiclecontrol` · **产物**:`vehiclecontrol.kzb` · 引用 `core`。

车门 / 车窗 / 后备厢 / 车锁 / 灯光控制(含写操作交互)。复制 `_ModuleTemplate` 起步。

## 结构

```text
vehiclecontrol.kzproj  (引用 core)
└── Prefabs/Pages/VehicleControlPage   # 根 Prefab(下游加载入口)
    Prefabs/Widgets/                   # CarTopView / DoorItem / WindowSlider ...
```

## 数据绑定(契约分组 `VehicleControl`)

| UI | 字段 | 备注 |
|----|------|------|
| 落锁 | `locked` / `lockedValid` | 写操作 |
| 四门 | `doorFrontLeft/Right` `doorRearLeft/Right` / `doorValid` | true=开 |
| 四窗 | `windowFrontLeft/Right` `windowRearLeft/Right` / `windowValid` | 0-100 开度,可拖动 |
| 后备厢 | `trunkOpen` | 写操作 |
| 大灯 | `headlightOn` | 写操作 |

## 写操作纪律

- 开窗/落锁等写指令后,**以下游回推的真实状态刷新 UI**,谨慎使用乐观更新。
- 写失败走显式错误(对应 `Valid` 置 false 或错误反馈),不静默。
- `Valid==false` 显示故障态。
