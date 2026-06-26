# 命名规范

统一命名是多工程协作与下游(Android)按名加载的前提。**交付后命名一律冻结,只允许追加。**

## 1. 工程名(Kanzi 工程名 / kzb 文件名)

- 全小写,无空格,与 kzb 文件名一致。

| 工程 | 工程名 / kzb |
|------|--------------|
| 共享资源 | `core` → `core.kzb` |
| 主工程 | `shell` → `shell.kzb` |
| 首页 | `launcher` → `launcher.kzb` |
| 充电 | `charging` → `charging.kzb` |
| 车控 | `vehiclecontrol` → `vehiclecontrol.kzb` |
| 内饰 | `interior` → `interior.kzb` |

## 2. 节点 / Prefab 命名

- **PascalCase**(大驼峰),语义清晰。
- Prefab 模板分类:
  - 通用组件(core):`Button`、`ToggleSwitch`、`Card`、`ListItem`、`Popup`、`Toast`、`Slider`、`ProgressBar`、`StatusBar`
  - 组合控件(Widgets):`TirePressureGauge`、`DoorItem`、`ChargeCurve`、`AmbientColorPicker`
  - 页面(Pages,模块根 Prefab):`<域>Page`,如 `LauncherPage`、`ChargingPage`、`VehicleControlPage`、`InteriorPage`
- **页面根 Prefab 名是下游加载入口,务必稳定。**

## 3. 属性(Property)命名

- 自定义属性别名:`<Namespace>.<PropertyName>`,如 `Nextrea.IsActive`、`Nextrea.AccentColor`。
- 组件对外属性用 PascalCase:`Title`、`Value`、`IsChecked`、`IconUrl`。

## 4. Data Source 字段命名

- 字段 **camelCase**(小驼峰),与契约 JSON、与 Android 侧 DataObject **逐字段一致**。
- 分组用层级:`Vehicle`、`Charging`、`VehicleControl`、`Interior`、`System`。
- 每个信号配一个有效性字段:`<signal>Valid`(Bool),例如 `socValid`、`tirePressureFlValid`。
- 示例:`Charging.soc`、`Charging.socValid`、`VehicleControl.doorFrontLeft`、`Interior.ambientBrightness`。

## 5. 资源命名

- 纹理 / 图标:`ic_<语义>_<状态>`,如 `ic_charging_active`、`ic_door_open`。snake_case。
- 字体:`font_<语言/用途>`,如 `font_cjk`、`font_latin`。
- 材质 / 网格:PascalCase,如 `AmbientLightMaterial`、`SeatMesh`。

## 6. 本地化键(Localization Key)

- 形如 `<模块>.<语义>`,snake_case 语义段:`launcher.greeting`、`charging.remaining_time`、`vehicle_control.door_locked`、`common.ok`、`common.cancel`。
- 见 [localization.md](localization.md)。

## 7. 主题资源键(Resource Dictionary)

- 主题:`Theme_Day`、`Theme_Night`。
- token 键:`<类别>/<语义>`,如 `Color/Background`、`Color/Accent`、`Color/TextPrimary`、`Font/Title`、`Size/RadiusM`。
- 见 [theming.md](theming.md)。

## 8. 目录命名

- 仓库内子工程目录:`Core/`、`Shell/`、`Module_<英文域名>/`(PascalCase 域名),如 `Module_VehicleControl/`。
