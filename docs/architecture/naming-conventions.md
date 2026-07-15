# 命名规范(Kanzi IVI 工程)

> 清单产物 1/9。本文是**可直接执行/评审用**的命名规范单页;工程结构、资源、3D 等完整规范见 [conventions.md](conventions.md)。
>
> 铁律:**命名交付后冻结,只追加不改名**;禁止中文、空格、特殊字符;kzb URL 与工程名**全小写**。

## 1. 总览:哪类东西用哪种命名

| 对象 | 规则 | 示例 | 反例 |
|------|------|------|------|
| 工程 / kzb | 全小写 + 下划线 | `launcher` `car_setting` | `Car.kzproj`(现存遗留,待改) |
| 节点 / Prefab | PascalCase,语义清晰 | `CarSettingPage` `ToggleSwitch` | `test` `Node01` |
| 模块根 Prefab | `<域>Page`,唯一入口 | `CarPage` `HvacPage` | `main` `root2` |
| 自定义属性 | `<命名空间>.<属性>`,空间=模块名 | `Car.DoorFrontLeftOpen` | `myProp` |
| 数据字段(XML) | camelCase,分组分层 | `Charging/chargeStatus` | `Charge_Status` |
| 有效性字段 | `<signal>Valid`(bool) | `socValid` `tiresValid` | 缺失(用默认值掩盖故障) |
| 本地化 key | `<模块>.<语义>` | `charging.title` `common.ok` | 直接写中文字面量 |
| 主题 token | `<类别>/<语义>` | `Color/Accent` `Font/Body` | 节点写死 `#1E6BFF` |
| 2D 切图 | `模块_组件_状态_尺寸_分辨率.png` | `hvac_btn_fan_press_48px_1920x720.png` | `图标 1.png` |
| 3D 部件 | `内外饰_部件_功能_材质` | `ext_door_fl_hinge_metal` | `Cube.161`(Blender 默认名) |

## 2. 状态机(State Manager)命名 ★

状态机相关对象在 Studio 里分四层,各层规则:

| 层 | 规则 | 示例(充电状态机) |
|----|------|--------------------|
| State Manager | `SM_<域><主题>` | `SM_ChargingStatus` |
| State Group | `SG_<关注面>`;一个 Group 管一组互斥状态 | `SG_Status`、`SG_Motion` |
| State | PascalCase 名词/形容词,与契约枚举一一对应 | `Unknown / Charging / Complete / Paused / Fault` |
| Controller Property | 复用暴露属性名 | `Charging.ChargeStatus`(Int) |

规则:

- **State 名与 `datasource.xml` 枚举注释一一对应**(如 `chargeStatus`:0=Unknown…4=Fault),三端(XML/Studio/Android)同名同义。
- 一个 State Manager 内多个关注面(如底盘"高度"与"是否升降中")拆成**多个 State Group**,不要把组合状态摊平成 `LowMoving/HighMoving...`。
- 过渡动画(Transition)命名 `TR_<From>_<To>`(Studio 内备注用)。

## 3. Trigger / Action / 消息命名 ★

| 对象 | 规则 | 示例 |
|------|------|------|
| 自定义 Message | `Msg_<域>_<动词短语>` | `Msg_Hvac_SetMode` |
| Message 参数 | 同自定义属性 | `Hvac.TargetMode`(Int) |
| Trigger(Studio 内固定名) | 用官方类型名,不改 | `On Property Change` `Button: Click` `Data Trigger` |
| 带条件的 Trigger 备注 | `<条件>-><动作>` 写进 Comment | `chargeStatus==4 -> ShowFault` |

## 4. 数据字段命名细则(XML 契约)

- 分组节点(无 `type`)用 PascalCase:`System / Vehicle / Charging / VehicleControl / Interior / Chassis / Tires / Hvac / Demo`。
- 字段 camelCase;枚举字段用 `int` 并**在注释里写全枚举表**;可写字段(UI 可设置)在注释标注"可设置"。
- 四轮同构信号用后缀 `FL/FR/RL/RR`:`statusFL` `pressureRR`(与 3D 节点 `Wheel_FL`、`Door_FL` 的后缀一致)。
- 交付后**只追加不改名**;废弃字段保留并注释 `@deprecated`。

## 5. 3D 节点分组命名(car 模块现行)

```text
car (EmptyNode)
├── Body                 # 非轮非门
├── Wheels
│   ├── Wheel_FL  Wheel_FR  Wheel_RL  Wheel_RR
└── Doors
    ├── Door_FL   Door_FR   Door_RL   Door_RR
```

- 组名 PascalCase + `_位置后缀`;与数据字段后缀(§4)对齐,绑定时可直读。
- 网格(mesh)最终应按 `内外饰_部件_功能_材质` 在 DCC 侧改名后再导入;Blender 默认名(`Circle.076`)只允许过渡期存在。

## 6. 自检清单(评审用)

- [ ] 新增工程/文件名全小写;无空格、中文
- [ ] 新增 State/枚举与 `datasource.xml` 注释一一对应
- [ ] 状态机对象带 `SM_/SG_` 前缀;消息带 `Msg_` 前缀
- [ ] 文案走本地化 key、颜色走主题 token,无字面量
- [ ] 关键信号有 `<signal>Valid` 配套字段
- [ ] 未改动任何已冻结命名(只追加)
