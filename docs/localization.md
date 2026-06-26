# 多语言(中 / 英)方案

## 1. 目标

- 支持 **中文 `zh-CN`** 与 **英文 `en`** 运行时切换。
- 字符串集中管理在 **core 的 Localization**,所有工程引用,**禁止在节点里硬编码文字**。

## 2. 在 Kanzi Studio 中的做法

1. 在 `core` 工程的 `Localization/` 中建立字符串表(String / Localization Resource),locale 列:`zh-CN`、`en`。
2. TextBlock 等文本节点的内容**绑定到本地化键**(`kzb://core/Localization/<key>`),不直接填字面文字。
3. 语言切换:运行时切换当前 locale,所有绑定文本自动刷新。
4. 模块工程引用 core 后,直接使用同一套键。

## 3. 键命名约定

- 形如 `<模块>.<语义>`,语义段 snake_case。

| Key | zh-CN | en |
|-----|-------|----|
| `common.ok` | 确定 | OK |
| `common.cancel` | 取消 | Cancel |
| `common.unavailable` | 不可用 | Unavailable |
| `launcher.greeting` | 你好 | Hello |
| `charging.title` | 充电 | Charging |
| `charging.remaining_time` | 剩余时间 | Time remaining |
| `charging.power` | 充电功率 | Charging power |
| `vehicle_control.title` | 车控 | Vehicle Control |
| `vehicle_control.door_locked` | 已锁车 | Locked |
| `vehicle_control.window` | 车窗 | Window |
| `interior.title` | 内饰 | Interior |
| `interior.ambient_light` | 氛围灯 | Ambient Light |
| `interior.fragrance` | 香氛 | Fragrance |

> 完整键表随开发增量维护。新增文案先加键,再在两种 locale 各补译文,缺译文视为缺陷。

## 4. 布局弹性

- 英文文案普遍比中文长,**文本容器用自适应 Layout**,预留扩展空间,避免截断或溢出。
- 关键标签做长文本(英文)与短文本(中文)两种 locale 下的走查。

## 5. 字体

- 中文需覆盖 CJK 字符集;英文用拉丁字体。建议:
  - `font_cjk`:中文(含标点),按**实际用字子集化**控制体积。
  - `font_latin`:英文/数字。
- 字体放在 `core` 的 `Fonts/`;字号/字重通过主题 token(`Font/*`)引用,不在节点写死。

## 6. 数字 / 单位 / 时间格式

- 单位(km、kW、%、kPa)与数值格式应可随 locale 调整(如需要)。
- 时间/日期格式按 locale 决定(12/24 小时、年月日顺序)。
- 这类格式化逻辑若依赖真值,由下游数据侧提供已格式化字段或在绑定层处理;**契约中数值字段保持原始数值 + 单位元数据**(见 data-source-contract.md)。

## 7. 反模式(严禁)

- TextBlock 直接填中文/英文字面量。
- 用图片承载可翻译文字(无法切换语言)。
- 漏译时回退成 key 名或空字符串而不报缺陷。
