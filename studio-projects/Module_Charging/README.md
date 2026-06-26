# charging — 充电模块

**工程名**:`charging` · **产物**:`charging.kzb` · 引用 `core`。

充电状态展示:SOC、充电状态/功率、剩余时间、续航、充电曲线、目标电量设置。复制 `_ModuleTemplate` 起步。

## 结构

```text
charging.kzproj  (引用 core)
└── Prefabs/Pages/ChargingPage   # 根 Prefab(下游加载入口)
    Prefabs/Widgets/             # SocRing / ChargeCurve / TargetSocSlider ...
```

## 数据绑定(契约分组 `Charging`)

| UI | 字段 | 故障态 |
|----|------|--------|
| 电量环 | `soc` / `socValid` | `socValid==false` → "--%" + Color/Error |
| 状态 | `chargeStatus`(枚举)/ `chargeStatusValid` | 同上,FAULT(4)用告警/错误色 |
| 功率 | `chargePower` / `chargePowerValid` | "--" |
| 剩余时间 | `remainingMinutes` / `remainingMinutesValid` | "--" |
| 续航 | `rangeKm` / `rangeKmValid` | "--" |
| 充电枪 | `plugConnected` | — |
| 目标电量(可调) | `targetSoc` | 写操作以回推为准 |

## 注意

- `chargeStatus` 枚举见契约 `enums.ChargeStatus`,`0=UNKNOWN` 视为无效。
- 文案双语、样式走主题 token。
