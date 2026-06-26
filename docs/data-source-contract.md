# Data Source 数据契约说明

## 1. 它是什么

- Kanzi Studio 侧虽然不接真值,但**必须在 `core` 工程的 `Data Sources/VehicleData` 中按契约建好数据结构**(配 stub 默认值),否则 UI 无法用 Binding 开发/预览。
- 这份数据结构(字段名/类型/层级/枚举)**就是交给 Android 侧 Java Plugin 的接口契约**。两侧必须逐字段对齐,否则 kzb 进到 Android 后 Binding 全部失效。
- 契约文件:[`contracts/vehicle-data.schema.json`](../contracts/vehicle-data.schema.json)。

> 一句话:**数据是假的(stub),结构是真的、冻结的。**

## 2. 在 Studio 中怎么建

1. 在 `core` 建一个 Data Source `VehicleData`,按契约的 `groups`(System / Charging / VehicleControl / Interior)建分组与字段。
2. 每个字段类型对应 Kanzi 的 DataObject 类型:
   - `bool` → DataObjectBool
   - `int` / `enum` → DataObjectInt
   - `real` → DataObjectReal
   - `string` → DataObjectString
   - `list` → DataObjectList
3. 用契约里的 `stub` 值作为默认值,便于在 Studio 预览各种状态(含故障态)。
4. 各模块工程引用 core 后,UI 节点绑定到 `kzb://core/Data Sources/VehicleData/<分组>/<字段>`。

## 3. 有效性 / 故障字段(强约束)

- 每个关键信号都有 `<signal>Valid`(bool)。无效/超时/故障时为 `false`。
- UI 绑定规则:
  - `<signal>Valid == false` → 显示故障态:文案用本地化 `common.unavailable`,颜色用主题 `Color/Error`。
  - **严禁**用默认值 / 0 / 空字符串伪装成正常数据。
- 例:`Charging.socValid == false` 时,SOC 显示 "--%" 并置错误色,而不是显示 0%。

## 4. 写操作(车控/内饰交互)

- 开窗、落锁、调氛围灯等写操作由下游执行;**UI 以下游回推的真实状态刷新**(谨慎使用乐观更新)。
- 写失败必须走显式错误路径(对应信号 `Valid` 置 false 或专门的错误反馈),不得静默。

## 5. 变更流程

- 字段**只允许追加**;改名/改类型/删除/改枚举值都属破坏性变更,需变更评审并通知 Android 组同步。
- 契约文件 `version` 在每次结构变更时升级,并在 CI 中与各工程 Data Source 做一致性校验(见 export-kzb.md 质量门)。

## 6. 分组速览

| 分组 | 用途 | 主要字段 |
|------|------|----------|
| `System` | 状态栏/全局 | 时间、日期、locale、theme、网络、蓝牙、车外温度 |
| `Charging` | 充电模块 | soc、chargeStatus、chargePower、remainingMinutes、rangeKm、plugConnected、targetSoc |
| `VehicleControl` | 车控模块 | locked、四门、四窗开度、trunk、headlight |
| `Interior` | 内饰模块 | 氛围灯(开关/颜色/亮度)、香氛、座椅加热、天窗 |

> 字段明细与 stub 值、枚举定义见契约 JSON。
