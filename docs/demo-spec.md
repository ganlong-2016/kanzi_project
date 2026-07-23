# demo 定义清单(照着直接创建)

本文给出 demo 的**全部具体定义**:颜色(日/夜)、主题、字体样式、字号/圆角/间距、通用组件、DemoPage 暴露属性、卡片布局、连线与数据字段。**这是 demo 示例的设定值,直接在 Kanzi Studio 里录入即可**。

> ⭐ **逐步操作以 [demo-build-all.md](demo-build-all.md)(v2)为准**:该文档已按 Kanzi Studio 3.9.15 官方文档逐步核实,并把 demo 扩展为**双子页**(子页 A=数据绑定八卡,即本文 §8;子页 B=交互与视觉八卡:触发器/动画/手势/滚动/Data Trigger/2D 特效/3D 视口/动态换 Prefab)。本文与其不一致处以 demo-build-all 为准(已知差异:ProgressRing 改为 ProgressBar、组件清单增加 Button、DemoPage 统一放 `Prefabs/Pages/`)。

---

## 1. 画布(中控 1920×1080,预留安全区)

| 项 | 值 | 说明 |
|----|----|----|
| Screen 分辨率 | **1920 × 1080** | 中控主屏 |
| 顶部安全边距 | **80 px** | 预留给系统**状态栏**,内容不进此区 |
| 底部安全边距 | **100 px** | 预留给系统**导航栏**,内容不进此区 |
| 安全内容区 | 1920 × **900**(Y: 80 → 980) | 所有 UI 放这里 |
| demo 顶栏 | 高 96 px(在安全区内,Y: 80 → 176) | 标题 + 日夜/中英切换 |
| 卡片区 | 1920 × ~804(Y: 176 → 980) | |
| 卡片网格 | 4 列 × 2 行,卡片约 **440 × 360**,间距 32 | 四周留 32 边距 |

**做法**:根容器用一个铺满 Screen 的节点,再放一个**内容容器**,其 `Layout` 上下留边(Top Margin=80、Bottom Margin=100)或直接把内容容器摆在 Y=80、高=900;所有卡片、顶栏都放内容容器内,**不要越过上下安全边距**,以免被状态栏/导航栏遮挡。左右可按需再留边距(如各 32)。

---

## 2. 颜色(Color Brush)

在 `common` 里为**每个角色 × 每个主题**各建一个 Color Brush(共 9 角色 × 2 = 18 个),命名 `Brush_<角色>_Day` / `Brush_<角色>_Night`。Alpha 均为 255(不透明)。

### Day(白天)
| 角色 | Brush 名 | HEX | RGBA(0–255) |
|------|----------|-----|-------------|
| Background | `Brush_Background_Day` | `#F5F6F8` | 245, 246, 248, 255 |
| Surface(卡片) | `Brush_Surface_Day` | `#FFFFFF` | 255, 255, 255, 255 |
| Accent(强调) | `Brush_Accent_Day` | `#1E6BFF` | 30, 107, 255, 255 |
| TextPrimary | `Brush_TextPrimary_Day` | `#1A1D21` | 26, 29, 33, 255 |
| TextSecondary | `Brush_TextSecondary_Day` | `#5A626B` | 90, 98, 107, 255 |
| Divider(分隔) | `Brush_Divider_Day` | `#E2E5EA` | 226, 229, 234, 255 |
| Success | `Brush_Success_Day` | `#1FAE6C` | 31, 174, 108, 255 |
| Warning | `Brush_Warning_Day` | `#E8A317` | 232, 163, 23, 255 |
| Error | `Brush_Error_Day` | `#E5484D` | 229, 72, 77, 255 |

### Night(夜间,对应示意图深色)
| 角色 | Brush 名 | HEX | RGBA(0–255) |
|------|----------|-----|-------------|
| Background | `Brush_Background_Night` | `#0E1116` | 14, 17, 22, 255 |
| Surface(卡片) | `Brush_Surface_Night` | `#1A1F26` | 26, 31, 38, 255 |
| Accent(强调) | `Brush_Accent_Night` | `#4D8BFF` | 77, 139, 255, 255 |
| TextPrimary | `Brush_TextPrimary_Night` | `#F2F4F7` | 242, 244, 247, 255 |
| TextSecondary | `Brush_TextSecondary_Night` | `#A2ABB5` | 162, 171, 181, 255 |
| Divider | `Brush_Divider_Night` | `#2A313A` | 42, 49, 58, 255 |
| Success | `Brush_Success_Night` | `#3DDC97` | 61, 220, 151, 255 |
| Warning | `Brush_Warning_Night` | `#FFC453` | 255, 196, 83, 255 |
| Error | `Brush_Error_Night` | `#FF6B70` | 255, 107, 112, 255 |

> Kanzi Color Brush 的 Brush Color 可用 RGBA 直接填(0–255 或 0–1)。0–1 = 每个分量 ÷ 255。

---

## 3. 主题(Theme Group)

新建 Theme Group 命名 **`AppTheme`**,含两个 Theme:**`Day`**、**`Night`**。资源 ID 与各主题取值:

| Resource ID | Day 列 | Night 列 |
|-------------|--------|----------|
| `Color/Background` | `Brush_Background_Day` | `Brush_Background_Night` |
| `Color/Surface` | `Brush_Surface_Day` | `Brush_Surface_Night` |
| `Color/Accent` | `Brush_Accent_Day` | `Brush_Accent_Night` |
| `Color/TextPrimary` | `Brush_TextPrimary_Day` | `Brush_TextPrimary_Night` |
| `Color/TextSecondary` | `Brush_TextSecondary_Day` | `Brush_TextSecondary_Night` |
| `Color/Divider` | `Brush_Divider_Day` | `Brush_Divider_Night` |
| `Color/Success` | `Brush_Success_Day` | `Brush_Success_Night` |
| `Color/Warning` | `Brush_Warning_Day` | `Brush_Warning_Night` |
| `Color/Error` | `Brush_Error_Day` | `Brush_Error_Night` |

- 节点用颜色时一律引用左列 **Resource ID**(经 AppTheme),不直接选某个 brush。
- 预览:顶部 **Dictionaries** → Locales and Themes → AppTheme 选 Day/Night。

---

## 4. 字体与样式(Named Style)

字体已有 `NotoSansCJKsc-Regular.otf`(覆盖中英)。建 2 个 Named Style:

| Style 名 | Font Family | 用于 locale |
|----------|-------------|-------------|
| `LocaleStyle` | NotoSansCJKsc | `en`(默认) |
| `LocaleStyle_zh` | NotoSansCJKsc | `zh-CN` |

- 本地化表 `LocaleStyle` 行:`en` 列=LocaleStyle,`zh-CN` 列=LocaleStyle_zh。
- 文本节点用 **Style = LocaleStyle**(而非直接 Font Family)。

---

## 5. 字号 / 圆角 / 间距(固定档位)

| token | 值(px) | 用途 |
|-------|---------|------|
| Font/Title | 40,Bold | 卡片/页面标题 |
| Font/Body | 28,Regular | 正文/数值 |
| Font/Caption | 20,Regular | 说明(≥18,满足车载可读) |
| Size/RadiusS | 8 | 小圆角 |
| Size/RadiusM | 16 | 卡片圆角 |
| Size/RadiusL | 24 | 大圆角 |
| Size/SpacingS | 8 | 紧密间距 |
| Size/SpacingM | 16 | 常规间距 |
| Size/SpacingL | 32 | 卡片间距 |

> 字号在 Text Block/Style 上设;圆角/间距 Kanzi 无数值资源,按上表在组件里填固定值(偶数,符合 conventions)。

---

## 6. 样板组件(demo 工程,Prefab + 暴露属性)

> **不在 common。** 路径 `kzb://demo/Prefabs/...`。业务模块对照此表自建,不引用 demo 的 Card。

| 组件 Prefab | 说明 | 暴露属性(类型) |
|-------------|------|-----------------|
| `Card` | 卡片容器(Empty Node 2D 根 + Background Rectangle + Content Stack Layout;**内容加在 Content 下**) | `Card.Title`(String,可选) |
| `LabelText` | 文本(Style=LocaleStyle,Foreground=TextPrimary) | `LabelText.Text`(String) |
| `Button` | 按钮(Button 2D + Label 子 Text Block;触发器/动作示例的载体) | `Button.Label`(String) |
| `ToggleSwitch` | 开关(Toggle Button 2D + State Manager;Toggle State Count=2) | `ToggleSwitch.State`(**Int**,expose Toggle State)、`ToggleSwitch.Label`(String,子 Text Block 2D) |
| `Slider` | 滑块(0–100) | `Slider.Value`(Int) |
| `ProgressBar` | 条形进度 0–100(两个 Rectangle + 宽度绑定表达式;原 ProgressRing 方案依赖不存在的工厂组件,已废弃) | `ProgressBar.Value`(Float) |
| `StatusIcon` | 状态图标(Int 枚举驱动内部 State Manager,0–4 五态) | `StatusIcon.Status`(Int) |
| `ImageBox` | 图片(设计期换 Image 资源;URI 链路由插件在运行时解析) | `ImageBox.Image`(Image) |
| `ListItem` | 列表项(图标+标题,作 List Box 的 Item Template) | `ListItem.Title`(String) |

> 组件逐步搭建配方见 [demo-build-all.md](demo-build-all.md) §5。

- 组件颜色全走主题 `Color/*`;文字走 `LocaleStyle`;全部 Make Public。

---

## 7. DemoPage 暴露属性(`Demo.*`)

`demo` 的 `DemoPage` 根 Prefab 暴露以下属性(用第 6 步组件搭好后,expose 对应属性并重命名):

| 属性 | 类型 | 默认值 | 对应卡片 |
|------|------|--------|----------|
| `Demo.Title` | String | `Demo` | 顶栏/卡2 |
| `Demo.GaugeValue` | Float | 62 | 卡1 进度 |
| `Demo.GaugeValid` | Bool | true | 卡1 故障态 |
| `Demo.ToggleOn` | **Int**(0/1) | 0 | 卡3 开关(Toggle State) |
| `Demo.SliderValue` | Int | 30 | 卡4 滑块 |
| `Demo.AccentColor` | Color | `#1E6BFF` | 卡5 颜色 |
| `Demo.StatusEnum` | Int | 1 | 卡6 状态 |
| `Demo.IconUri` | String | (空) | 卡7 图片 |

---

## 8. 卡片布局与内容(4×2)

| 卡片 | 标题(本地化键) | 内容组件 | 绑定(demo 内 `##Template`) |
|------|------------------|----------|------------------------------|
| 1 读·进度 | `demo.gauge` | ProgressRing | `Value` ← `Demo.GaugeValue`;`Demo.GaugeValid`=false→"--"+Error |
| 2 读·文本 | `demo.text` | LabelText | `Text` ← `Demo.Title` |
| 3 写·开关 | `demo.switch` | ToggleSwitch | `IsChecked` ↔ `Demo.ToggleOn` |
| 4 写·滑块 | `demo.slider` | Slider | `Value` ↔ `Demo.SliderValue` |
| 5 写·颜色 | `demo.color` | 色块(Color Brush) | 颜色 ↔ `Demo.AccentColor` |
| 6 枚举·状态 | `demo.status` | StatusIcon | `Status` ← `Demo.StatusEnum` |
| 7 图片 | `demo.image` | ImageBox | `Uri` ← `Demo.IconUri` |
| 8 列表 | `demo.list` | List Box + ListItem | Items ← `Demo/menu`(launcher 侧) |

顶栏:左 时间(`System/timeText`,launcher 侧)、中 标题、右 两个切换(日/夜、中/EN)。

---

## 9. launcher `DemoView` 连线(数据源 ↔ 暴露属性)

| DemoView 属性 | 方向 | 数据源字段 | Binding |
|---------------|------|-----------|---------|
| `Demo.Title` | 读 | `Demo/titleText` | 普通 |
| `Demo.GaugeValue` | 读 | `Demo/gaugeValue` | 普通 |
| `Demo.GaugeValid` | 读 | `Demo/gaugeValid` | 普通 |
| `Demo.ToggleOn` | 读写 | `Demo/toggleOn` | 读普通 + 写 To-Source |
| `Demo.SliderValue` | 读写 | `Demo/sliderValue` | 读普通 + 写 To-Source |
| `Demo.AccentColor` | 读写 | `Demo/accentColor` | 读普通 + 写 To-Source |
| `Demo.StatusEnum` | 读 | `Demo/statusEnum` | 普通 |
| `Demo.IconUri` | 读 | `Demo/iconUri` | 普通 |
| List Box Items | 读 | `Demo/menu` | 普通 |

数据字段定义见 [`IVI/assets/datasource.xml`](../IVI/assets/datasource.xml) 的 `Demo` 分组。

---

## 10. 本地化键(中/英)

| key | zh-CN | en |
|-----|-------|----|
| `demo.gauge` | 进度 | Gauge |
| `demo.text` | 文本 | Text |
| `demo.switch` | 开关 | Switch |
| `demo.slider` | 滑块 | Slider |
| `demo.color` | 颜色 | Color |
| `demo.status` | 状态 | Status |
| `demo.image` | 图片 | Image |
| `demo.list` | 列表 | List |
| `common.unavailable` | 不可用 | Unavailable |

---

## 创建顺序
1. `common`:建 18 个 Color Brush(§2)→ AppTheme 主题(§3)→ LocaleStyle/_zh(§4)→ Make Public → 导出。
2. `demo`:按 §6 建 Card / LabelText 等组件与 DemoPage → Make Public → 导出(业务模块对照 demo,不引用 demo kzb)。
2. `launcher`:导入插件 → 数据源指向 `IVI/assets/datasource.xml` → Screen 设 Data Context。
3. `demo`:引用 common → DemoPage → 按 §8 搭卡片、expose §7 属性 → 本地化(§10)→ Make Public → 导出。
4. `launcher`:Prefab View 挂 DemoView → 按 §9 连线 → 导航 → 导出。
