# demo 一站式搭建文档(只看这一份,3.9.15)

在 Kanzi Studio 里从零搭出 demo 所需的**全部值 + 操作 + 逐组件配方 + 卡片 + 连线 + 本地化 + 导出**,都在这一份里,开发时不用切换其它文档。

> 基于 Kanzi Studio **3.9.15**。约定:**创建资源用 `Alt + 右键` 对应分类**。已完成的可跳过(截至目前:18 个颜色 Brush 已建好)。

## 目录
1. 画布 · 2. 创建顺序 · 3. common 颜色 · 4. common 主题 · 5. common 字体样式 · 6. common 组件配方 · 7. Make Public/导出 · 8. launcher 数据源 · 9. demo 页面与卡片 · 10. 本地化 · 11. launcher 连线 · 12. 导出顺序 · 13. 常见问题

---

## 1. 画布(中控 1920×1080 + 安全区)
| 项 | 值 |
|----|----|
| Screen 分辨率 | 1920 × 1080 |
| 顶部安全边距(状态栏) | 80 px |
| 底部安全边距(导航栏) | 100 px |
| 安全内容区 | 1920 × 900(Y:80→980) |
| demo 顶栏 | 高 96(Y:80→176) |
| 卡片区 | 1920 × ~804(Y:176→980) |
| 卡片网格 | 4 列 × 2 行,卡片约 440 × 360,间距 32 |

做法:根节点铺满 Screen;内部放"内容容器",Y=80、高=900(上下留出安全边距);所有顶栏/卡片放内容容器内,不越过上下边距。

## 2. 创建顺序
`common`(颜色→主题→字体样式→组件→Make Public→导出)→ `launcher`(插件→数据源→Data Context)→ `demo`(引用 common→页面/卡片→本地化→Make Public→导出)→ `launcher`(挂 DemoView→连线→导航→导出)。

---

## 3. common — 颜色(Color Brush)✅ 已建
每个角色 × 主题一个 Color Brush,命名 `Brush_<角色>_<Day/Night>`,Alpha=255。
建法:`Library` → **Alt+右键 `Materials and Textures`** → **Color Brush** → 命名 → `Properties` 设 Brush Color(RGBA 0–255)。

**Day**:Background `#F5F6F8`(245,246,248) · Surface `#FFFFFF`(255,255,255) · Accent `#1E6BFF`(30,107,255) · TextPrimary `#1A1D21`(26,29,33) · TextSecondary `#5A626B`(90,98,107) · Divider `#E2E5EA`(226,229,234) · Success `#1FAE6C`(31,174,108) · Warning `#E8A317`(232,163,23) · Error `#E5484D`(229,72,77)

**Night**:Background `#0E1116`(14,17,22) · Surface `#1A1F26`(26,31,38) · Accent `#4D8BFF`(77,139,255) · TextPrimary `#F2F4F7`(242,244,247) · TextSecondary `#A2ABB5`(162,171,181) · Divider `#2A313A`(42,49,58) · Success `#3DDC97`(61,220,151) · Warning `#FFC453`(255,196,83) · Error `#FF6B70`(255,107,112)

## 4. common — 主题(Theme Group `AppTheme`)
建法:`Node Tree` 选用了 brush 的节点 → **右键 → Add Resources to a Theme Group**(建 `AppTheme`),自动生成 resource ID;`Library > Themes` 双击 `AppTheme` → **Create Theme** 建 `Day`、`Night` → 每行两格选对应 brush。预览:顶部 **Dictionaries → Locales and Themes** 选主题。

**9 个 resource ID 逐行分配(Day / Night):**
| Resource ID | Day | Night |
|----|----|----|
| `Color/Background` | Brush_Background_Day | Brush_Background_Night |
| `Color/Surface` | Brush_Surface_Day | Brush_Surface_Night |
| `Color/Accent` | Brush_Accent_Day | Brush_Accent_Night |
| `Color/TextPrimary` | Brush_TextPrimary_Day | Brush_TextPrimary_Night |
| `Color/TextSecondary` | Brush_TextSecondary_Day | Brush_TextSecondary_Night |
| `Color/Divider` | Brush_Divider_Day | Brush_Divider_Night |
| `Color/Success` | Brush_Success_Day | Brush_Success_Night |
| `Color/Warning` | Brush_Warning_Day | Brush_Warning_Night |
| `Color/Error` | Brush_Error_Day | Brush_Error_Night |
> 之后节点用颜色一律选 resource ID(如 `Color/Accent`),不直接选 brush。

## 5. common — 字体样式(Named Style)
建法:双击 `Library > Localization > Localization Table` 打开 Localization Editor → **+ Add Resource → Create → Named Style** 命名 `LocaleStyle` → `Library > Styles` 右键 Duplicate 出 `LocaleStyle_zh` → 各 style `Properties` 设 **Font Family**(均用 `NotoSansCJKsc`)→ 本地化表 `LocaleStyle` 行:`en`列=LocaleStyle、`zh-CN`列=LocaleStyle_zh。
用法:文本节点用 **Style = LocaleStyle**(不直接设 Font Family)。

字号档位:Title 40/Bold · Body 28 · Caption 20。圆角:8/16/24。间距:8/16/32(偶数)。

---

## 6. common — 8 个通用组件(逐组件配方)

> 通用步骤:搭好节点 → 套主题 brush / LocaleStyle → **拖进 `Prefabs` 窗口**成为 Prefab → 在内部节点属性旁点 **expose 图标**,自动在 Prefab 根生成自定义属性 + `##Template` 绑定,重命名成下表属性名 → Make Public。
> 交互控件:Button 2D / Toggle Button 2D 用 `Alt+右键` 创建;Slider / Progress 用 **Factory Content**(工厂组件)添加。属性名以你版本为准,不确定时在 Properties 里核对。

| 组件 | 用什么节点 | 样式 | 暴露属性(默认) |
|------|-----------|------|------------------|
| **Card** | Empty Node 2D(或 **Rectangle 2D**,自带宽高更直观) | Background Brush = `Color/Surface`;**必须设 Layout Width/Height(否则 2D 节点塌成 0×0 完全看不见)**,如 440×360;圆角用带圆角九宫格图作底 | (可选)`Card.Title`(String)—— 内含 Text 子节点 |
| **LabelText** | Text Block 2D | Style=`LocaleStyle`;Foreground Brush=`Color/TextPrimary` | `LabelText.Text`(String,"Text") |
| **ToggleSwitch** | Toggle Button 2D(+State Manager,见 §6.1) | Background=`Color/Surface`;On/Off 视觉用 State Manager(On=`Color/Accent`) | `ToggleSwitch.State`(**Int**,0,expose 其 **Toggle State**);`ToggleSwitch.Label`(String,来自子 Text Block 2D) |
| **Slider** | Factory Content 的 **Slider**(或按滑块教程:轨道+手柄) | 轨道=`Color/Divider`;已滑=`Color/Accent`;手柄=`Color/Surface` | `Slider.Value`(Int/Float,30,expose 其 **Value**) |
| **ProgressRing** | Factory Content 的 **Progress Indicator**(圆形)/ Progress Bar | 进度色=`Color/Accent`;底=`Color/Divider` | `ProgressRing.Value`(Float,62,expose 其 **Value**,0–100) |
| **StatusIcon** | Image 2D + **State Manager** | 颜色/图标按状态切 | `StatusIcon.Status`(Int,1,驱动 State Manager) |
| **ImageBox** | Image 2D | — | `ImageBox.Uri`(String,expose 其图片来源)—— URI 由数据源插件加载 |
| **ListItem** | Empty Node 2D(行)+ Image(图标)+ Text(标题,Style=LocaleStyle) | Foreground=`Color/TextPrimary` | `ListItem.Title`(String);`ListItem.IconUri`(String) |

### 6.1 ToggleSwitch 详细(Toggle Button 2D 用法,重点)

要点:**Toggle Button 2D 的 `Toggle State` 是整数**(不是 bool),状态个数由 **`Toggle State Count`** 决定;做开关取 2 个状态(Off=0、On=1)。**它没有内置 Label**,标签要自己加一个 **Text Block 2D 子节点**。On/Off 的视觉差异用 **State Manager** 实现。

1. `Node Tree` **Alt+右键 → Toggle Button 2D**,命名 `ToggleSwitch`(也可从 **Asset Packages > Factory Content** 拖 Toggle Button 进来)。
2. `Properties`:设 **`Toggle State Count = 2`**;设 Layout Width/Height;Background Brush = `Color/Surface`(圆角可用带圆角九宫格图作底)。
3. **加子节点**:
   - 一个 Image 2D / Empty Node 2D 作"指示/圆点";
   - 一个 **Text Block 2D** 作标签(Style=`LocaleStyle`,Foreground Brush=`Color/TextPrimary`)。
4. **State Manager 做 On/Off**:选中 `ToggleSwitch` → **State Tools** → **Create State Manager** → **Create State ×2** 命名 `Off`/`On` → 分别摆好指示位置/颜色(On 用 `Color/Accent`),点各状态上方保存外观 → **Controller Property** 选 **Toggle Button > Toggle State** → `Off` 值设 **0**、`On` 值设 **1** → **Edit State Manager** 退出。
5. **拖进 `Prefabs`** 命名 `ToggleSwitch`。
6. **暴露属性**:选 `ToggleSwitch` 根 → 在 **Toggle State** 属性旁点 **expose** → 重命名 `ToggleSwitch.State`(Int);选那个 Text Block → expose 其 `Text` → `ToggleSwitch.Label`(String)。**Make Public**。

> 写回:Toggle State 支持 **To-Source / 双向**绑定(注意:**单向绑定会被点击覆盖**)。demo/launcher 侧的映射见 §9 卡3 与 §11(数据源里 `toggleOn` 是 bool,与 Int 用 `? 1 : 0` / `!= 0` 互转)。

## 7. common — Make Public + 导出
- 选中每个组件/brush/style → 右键 **Make Public**(或 `Properties` 设 `Visibility Across Projects = Public`);或 `Project > Properties` 设 `Resource Visibility Across Projects = Public` 一次性全公开。
- `File > Export > Export KZB` 导出 `common.kzb`。

---

## 8. launcher — 数据源
1. `Library` → 右键 **Kanzi Engine Plugins** → **Import Kanzi Engine Plugin** → 选 `plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`;`Properties` 确认 **Is Enabled**。
2. **Data Sources** 面板(`Window` 菜单)→ 新建数据源类型 DroidDataSource,命名 `VehicleData`,XML 路径指向 `assets/datasource.xml` → 右键 **Update Data Source Contents**。
3. `Node Tree` 选 Screen/RootPage 根 → `Properties` **+ Add → Data Context** → 设为 `VehicleData`。

数据字段(demo 用):`Demo/titleText`(string)、`gaugeValue`(float)、`gaugeValid`(bool)、`toggleOn`(bool)、`sliderValue`(int)、`accentColor`(string)、`statusEnum`(int)、`iconUri`(string)、`menu`(list: index/title/icon)。完整见 `assets/datasource.xml`。

---

## 9. demo — 页面与卡片
1. 引用 common:`Library` 右键 **Project References → Add → Existing Project** → `IVI/common/common.kzproj`。
2. 建页面:`Node Tree` 用 Grid Layout 2D 排 4×2,拖进 `Prefabs` 命名 `DemoPage`(放 `Prefabs/Pages/`)。按 §1 放进"内容容器"。

**DemoPage 暴露属性(在卡片组件上 expose 后重命名):**
| 属性 | 类型 | 默认 |
|----|----|----|
| `Demo.Title` | String | Demo |
| `Demo.GaugeValue` | Float | 62 |
| `Demo.GaugeValid` | Bool | true |
| `Demo.ToggleOn` | **Int**(0=关/1=开) | 0 |
| `Demo.SliderValue` | Int | 30 |
| `Demo.AccentColor` | Color | #1E6BFF |
| `Demo.StatusEnum` | Int | 1 |
| `Demo.IconUri` | String | (空) |

**8 张卡片(每张=一个 Card 实例内放对应组件,组件属性绑到 DemoPage 根属性):**
| 卡 | 标题(本地化键) | 组件 | 绑定 |
|----|------|------|------|
| 1 读·进度 | `demo.gauge` | ProgressRing | `Value` ← `{##Template/Demo.GaugeValue}`;`Demo.GaugeValid`=false→"--"+`Color/Error` |
| 2 读·文本 | `demo.text` | LabelText | `Text` ← `{##Template/Demo.Title}` |
| 3 写·开关 | `demo.switch` | ToggleSwitch | `ToggleSwitch.State`(Int)读 ← `{##Template/Demo.ToggleOn}`,并 To-Source 写回同属性;`ToggleSwitch.Label` ← 本地化 `demo.switch` |
| 4 写·滑块 | `demo.slider` | Slider | `Value` 读 ← `{##Template/Demo.SliderValue}` + To-Source 写回 |
| 5 写·颜色 | `demo.color` | 色块(Color Brush) | 颜色 ↔ `{##Template/Demo.AccentColor}`(读+To-Source) |
| 6 枚举·状态 | `demo.status` | StatusIcon | `Status` ← `{##Template/Demo.StatusEnum}` |
| 7 图片 | `demo.image` | ImageBox | `Uri` ← `{##Template/Demo.IconUri}` |
| 8 列表 | `demo.list` | Grid List Box + ListItem | Items ← 由 launcher 绑 `Demo/menu` |

> demo 内部只绑 `##Template/Demo.*`(自己的属性);把属性接到数据源在 launcher 做(§11)。

## 10. demo — 本地化键
Localization Editor 里加下列 key,填中/英:
| key | zh-CN | en |
|----|----|----|
| `demo.gauge` | 进度 | Gauge |
| `demo.text` | 文本 | Text |
| `demo.switch` | 开关 | Switch |
| `demo.slider` | 滑块 | Slider |
| `demo.color` | 颜色 | Color |
| `demo.status` | 状态 | Status |
| `demo.image` | 图片 | Image |
| `demo.list` | 列表 | List |
| `common.unavailable` | 不可用 | Unavailable |
卡片标题的 Text 绑定到对应 key(经本地化);切 locale 时随之变。Make Public `DemoPage` → 导出 `demo.kzb`。

---

## 11. launcher — 挂载 DemoView + 连线
1. `Library` 引用 `IVI/demo/demo.kzproj`;`Node Tree` 内容区 `Alt+右键 → Prefab View` 命名 `DemoView`,`Prefab Template` = `kzb://demo/Prefabs/Pages/DemoPage`。
2. 选中 `DemoView`,按下表逐条绑定(读=普通 Binding;写=再加一条 `Mode=To Source`,Push Target 指字段):

| DemoView 属性 | 方向 | 数据源字段 |
|----|----|----|
| `Demo.Title` | 读 | `Demo/titleText` |
| `Demo.GaugeValue` | 读 | `Demo/gaugeValue` |
| `Demo.GaugeValid` | 读 | `Demo/gaugeValid` |
| `Demo.ToggleOn`(Int) | 读写 | `Demo/toggleOn`(bool) |
| `Demo.SliderValue` | 读写 | `Demo/sliderValue` |
| `Demo.AccentColor` | 读写 | `Demo/accentColor` |
| `Demo.StatusEnum` | 读 | `Demo/statusEnum` |
| `Demo.IconUri` | 读 | `Demo/iconUri` |
| List Box Items | 读 | `Demo/menu` |

> **开关的 Int↔bool 转换**(Toggle State 是 Int,`toggleOn` 是 bool):读绑定表达式 `{@datasource Demo/toggleOn} ? 1 : 0`;写用 To-Source,Push Target=`Demo/toggleOn`,表达式 `{... Demo.ToggleOn} != 0`。(参考官方 Toggle Button 文档的绑定示例。)

3. 顶栏:时间 Text ← `System/timeText`;日/夜按钮切 AppTheme;中/EN 按钮切 Screen 的 Locale。导航用 State Manager 切换显示 `DemoView`。

## 12. 导出顺序
`common.kzb` → `demo.kzb` → `launcher.kzb`。运行时先加载 `common.kzb`。

## 13. 常见问题
| 现象 | 处理 |
|----|----|
| Card/卡片完全看不到 | 2D 节点没尺寸=0×0。给 `Layout Width/Height`(如 440×360);背景走主题 `Color/Surface` 时预览要在 Dictionaries 里激活主题,或临时用直接 Color Brush 验证 |
| 找不到 Colors/Resource Dictionaries 分类 | 颜色=Color Brush(Materials and Textures);主题=Themes;预览=顶部 Dictionaries |
| 创建资源没入口 | 用 **Alt+右键** 分类 |
| 改了没进 git | Kanzi 里 **Ctrl+S 保存**(autosave 不算);确认编辑的是仓库里那份工程 |
| demo 选不到数据源字段 | 正常:数据源在 launcher;demo 只绑 `##Template/Demo.*`,字段绑定在 launcher 的 DemoView |
| 开关点了不回写 | 补 To-Source(demo 属性 → launcher DemoView 上 To-Source 到字段) |
| 主题切了不变 | 颜色写死了;要经 AppTheme 的 `Color/*` resource ID |
| Slider/Progress 找不到节点 | 它们是 Factory Content 工厂组件,从工厂内容添加;Value 属性名以版本为准 |

> 值的来源与更详细拆分说明另见 `demo-spec.md` / `kanzi-studio-guide.md`(与本文一致,本文已够开发用)。
