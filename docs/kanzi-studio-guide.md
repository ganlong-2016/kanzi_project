# Kanzi Studio 操作手册(手把手,3.9.15)

面向"照着做"的**具体操作**:先在 `common` 建共享资源,再在 `launcher` 建数据源,再搭 `demo`,最后在 launcher 挂载连线并导出。

> 基于 **Kanzi Studio 3.9.15** 官方文档核实。约定:**创建资源用 `Alt + 右键` 对应分类**(Kanzi 的习惯操作)。
> 相关:[architecture](architecture.md)、[conventions](conventions.md)、[data-source §3.5](data-source.md)、[demo 布局与连线表](demo-module.md)。

窗口:**Library**(资源库)、顶部 **Dictionaries**(字典/主题·语言预览)/**Pages**、**Node Tree**、**Properties**、**Prefabs**、**Binding Editor**、**Preview**。

---

# A. 在 `common` 里创建共享资源

打开 `IVI/common/common.kzproj`。common 提供:**颜色画刷/主题、字体与本地化样式、通用组件**。数据源不在 common(在 launcher,见 B)。

## A1. 颜色:Color Brush

Kanzi 里"颜色"是 **Color Brush**(在 `Materials and Textures > Brushes` 下),不是单独的 Colors 分类。

1. `Library` → **Alt + 右键 `Materials and Textures`** → **Color Brush** → 命名,如 `Brush_Accent`。
2. 选中该 Brush → `Properties` 设 **Brush Color**(H/S/L 或 RGBA)。
3. 用法:
   - 填充背景:节点 `Properties` → 添加 **Background Brush** → 选该 brush。
   - 文字颜色:Text Block 节点 → 添加 **Foreground Brush** → 选该 brush(或就地 `+ Color Brush`)。
4. 按需建一组:`Brush_Background`、`Brush_Surface`、`Brush_Accent`、`Brush_TextPrimary`、`Brush_Error` 等。

## A2. 主题(日/夜):Theme Group

3.9.15 用 **Theme(Theme Group)** 做主题切换,资源 ID 在各 Theme 下取不同 brush。

1. **先准备两套值的 brush**:如 `Brush_Bg_Day`(浅)与 `Brush_Bg_Night`(深),`Brush_Accent_Day` / `Brush_Accent_Night` 等。
2. **把节点资源加入 Theme Group**:在 `Node Tree` 选中用了这些 brush 的节点 → **右键 → Add Resources to a Theme Group**(新建一个 Theme Group)。Kanzi 会**自动为每个资源生成 resource ID**,并把节点改成用 resource ID。
3. **建主题并逐格指定**:`Library > Themes` 双击该 Theme Group → 打开 **Theme Editor** → **Create Theme** 建 `Day`、`Night` → 每一行 resource ID,在 `Day` / `Night` 列 double-click 选对应 brush(如背景行:Day=Brush_Bg_Day,Night=Brush_Bg_Night)。
4. **手动加资源(可选)**:Theme Editor → **+ Add Resource** → Create/Add Existing → 命名 resource ID;节点属性设为 `< Resource ID >` 并填该 ID。
5. **预览切换**:顶部 **Dictionaries** 窗口 → 点 **Locales and Themes** → 为该 Theme Group 选 `Day`/`Night`,Preview 立即变。

> 组件/页面里"用某颜色" = 用主题的 resource ID(经 Theme Group),而不是写死某个 brush,这样才可日夜切换。

## A3. 字体与多语言样式(Named Style)

你工程里的 `LocaleStyle` / `LocaleStyle_zh` 就是这套(按语言切字体):

1. **导入字体**:`File > Import`(或 `Font Families` 已有 `NotoSansCJKsc`)。
2. **建 Named Style**:打开 **Localization Editor**(双击 `Library > Localization > Localization Table`)→ **+ Add Resource** → **Create > Named Style** → 命名 `LocaleStyle`。
3. **复制出各语言版**:`Library > Styles` 右键 `LocaleStyle` → **Duplicate** → 命名 `LocaleStyle_zh` 等。
4. **各 style 设字体**:选中 style → `Properties` 添加并设 **Font Family**(`LocaleStyle`=拉丁字体,`LocaleStyle_zh`=Noto Sans CJK SC)。
5. **在本地化表按 locale 指定**:Localization Table 里 `LocaleStyle` 行,在各 locale 列 double-click 选对应 style。
6. **节点应用**:目标节点(如页面根)`Properties` → **移除 Font Family** → 添加 **Style** → 设 resource ID 为 `LocaleStyle`。切 locale 时字体随之切换。

## A4. 通用组件(Prefabs)

1. **搭结构**:`Node Tree` 里用 Kanzi 内置交互节点(如 **Button 2D / Toggle Button 2D / Slider**,或容器 + 视觉)搭一个控件,套好 A1/A2 的画刷、A3 的样式。
2. **做成 Prefab**:把该节点**拖进 `Prefabs` 窗口** → Kanzi 自动生成 prefab 模板,并把原节点替换为实例。命名如 `ToggleSwitch`、`Card`、`ListItem`。
3. **暴露对外属性(关键,自动生成 `##Template`)**:在 prefab 内部选中要对外的节点,`Properties` 里 **在该属性旁点"暴露(expose)"小图标** → Kanzi 自动:在 **prefab 根**建一个自定义属性,并在该节点建 `##Template` 绑定指向根属性。可重命名这个暴露出来的属性(如 `ToggleSwitch.IsChecked`)。
   - 命令行等价:`ExposePrefabProperty <节点> <属性类型> [属性名]`。
4. 使用方(demo/launcher)之后只需在实例上设这个暴露属性即可控制组件。

## A5. 设为 Public 并导出

- 单项:`Prefabs`/`Library` 选中 → 右键 **Make Public**(或 `Properties` 设 `Visibility Across Projects = Public`)。
- 整工程:`Project > Properties` → `Resource Visibility Across Projects = Public`。
- `File > Export > Export KZB` 导出 `common.kzb`。

---

# B. 数据源(在 `launcher` 创建)

打开 `IVI/launcher/Tool_project/launcher.kzproj`。

## B1. 导入并启用插件
1. `Library` → **右键 `Kanzi Engine Plugins`** → **Import Kanzi Engine Plugin** → 选 `plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`(Android 用 Java 插件)。
2. 选中插件 → `Properties` 确认 **Is Enabled** 打开。改过插件后用右键 **Update Kanzi Engine Plugin** 刷新元数据。

## B2. 建数据源并指向 XML
1. 打开 **Data Sources** 面板(`Window` 菜单)→ 右键 → 新建数据源,类型选插件的 **DroidDataSource** 类型,命名 `VehicleData`。
2. 在其属性里把 **XML 路径**指向 `assets/datasource.xml`(仓库根,单一契约)。
3. 右键数据源 → **Update Data Source Contents**,应出现 `System / Charging / VehicleControl / Interior / Demo` 分组字段。

## B3. 设 Data Context
- `Node Tree` 选 **Screen/RootPage 根** → `Properties` → **+ Add** → **Data Context** → 设为 `VehicleData`;子节点(含运行时挂入的子模块)继承。

---

# C. 搭 `demo` 样板

打开/新建 `IVI/demo/demo.kzproj`。目标见 [demo 布局与连线表](demo-module.md)。

## C1. 引用 common
- `Library` → **右键 `Project References`** → **Add** → **Existing Project** → 选 `IVI/common/common.kzproj`。可用 common 的画刷/主题/样式/组件。

## C2. 页面根 Prefab
- `Node Tree` 搭页面容器(用 Grid/Stack Layout 排卡片)→ 拖进 `Prefabs` 窗口 → 命名 `DemoPage`(放 `Prefabs/Pages/`)。

## C3. 每张卡片(用 common 组件 + 暴露属性)

> demo 内部**不直接绑数据源**(数据源在 launcher);它把要接收的值**暴露为 DemoPage 根属性**(A4 的 expose 机制),launcher 再把这些属性接到数据源(见 D)。

- **读·文本**:放 Text Block(Style=`LocaleStyle`,Foreground Brush 走主题)→ 选它的 `Text` 属性 → 点旁边 **expose 图标** → 在 DemoPage 根生成属性,重命名 `Demo.Title`。
- **读·进度**:放 ProgressBar/表盘 → expose 其 `Value` → `Demo.GaugeValue`;故障态用 State Manager:另 expose 一个 `Demo.GaugeValid`(Bool),false 时切到"--"+ 主题 `Error` 色状态。
- **写·开关**:放 Toggle Button/`ToggleSwitch` → expose 其选中属性 → `Demo.ToggleOn`。写回见 D(launcher 侧 To-Source)。
- **写·滑块**:放 Slider → expose `Value` → `Demo.SliderValue`。
- **写·颜色**:色块的 Color Brush 的颜色 → expose → `Demo.AccentColor`。
- **枚举·状态**:expose `Demo.StatusEnum`(Int)驱动 State Manager 切图标。
- **图片**:Image 节点 expose 其 `Image`/URI 来源 → `Demo.IconUri`。
- **列表**:List Box(`Items Source`)—— 建议由 launcher 侧绑数据源 `Demo/menu`,或用消息驱动。

## C4. 主题 / 本地化
- 颜色都走主题 resource ID(A2),文字都走 `LocaleStyle`(A3)/ 本地化,禁止写死。

## C5. Make Public + 导出
- 选 `DemoPage` → **Make Public**;`File > Export > Export KZB` 导出 `demo.kzb`。

---

# D. 在 `launcher` 挂载 demo 并连线

回到 `launcher`。

## D1. 引用并挂载
1. `Library > Project References > Add > Existing Project` → `IVI/demo/demo.kzproj`。
2. `Node Tree` 内容区 → **Alt + 右键** 目标节点 → **Prefab View** → 命名 `DemoView` → `Properties` 的 **Prefab Template** = `kzb://demo/Prefabs/Pages/DemoPage`。

## D2. 连线(在 DemoView 上,数据源 ↔ 暴露属性)
`DemoView` 带着 demo 暴露的 `Demo.*` 属性。按 [demo 连线对照表](demo-module.md#launcher-连线对照表核心):
- **读**:选中 `DemoView` → 某属性(如 `Demo.GaugeValue`)`+ Add Binding` → 表达式指向数据源 `VehicleData` 的 `Demo/gaugeValue`。其余读字段同理。
- **写**:对 `Demo.ToggleOn` / `Demo.SliderValue` / `Demo.AccentColor`,在 Binding Editor 加一条 **Binding Mode = To Source** 的绑定,Push Target = 数据源对应字段(`Demo/toggleOn` 等)。
  - 链路:demo 内控件改值 → DemoView 属性 → 该 To-Source → 数据源 → 插件下发。

## D3. 导航 + 导出
- 用 State Manager / 可见性从桌面切到 `DemoView`。
- 导出顺序:`common.kzb` → `demo.kzb` → `launcher.kzb`(见 [export-kzb](export-kzb.md))。

---

# E. 常见问题

| 现象 | 检查 |
|------|------|
| Library 里找不到 Colors / Resource Dictionaries | 没这分类:颜色=Color Brush(Materials and Textures>Brushes);主题=Themes;字典预览=顶部 Dictionaries |
| 创建资源找不到入口 | 用 **Alt + 右键** 对应分类(如 Alt+右键 Materials and Textures) |
| 主题切了不变 | 颜色写死了;应经 Theme Group 的 resource ID;预览用 Dictionaries>Locales and Themes |
| demo 里选不到数据源字段 | 正常:数据源在 launcher。demo 只 expose 属性;字段绑定在 launcher 的 DemoView 上做 |
| Update Data Source 后无字段 | XML 路径要指 `assets/datasource.xml`,插件 Is Enabled,再 Update |
| 开关点了不回写 | 补 To-Source(demo expose 属性 → launcher DemoView 上 To-Source 到数据源) |

---

# F. 各工程各建什么

| 工程 | 建什么(章节) |
|------|----------------|
| `common` | Color Brush(A1)、Theme Group 日/夜(A2)、Named Style 多语言字体(A3)、通用组件 Prefab+expose(A4)、Make Public+导出(A5) |
| `launcher` | 导入插件(B1)、建数据源指向 `assets/datasource.xml`(B2)、Screen 设 Data Context(B3)、挂载 Prefab View + 连线(D) |
| `demo`/各模块 | 引用 common(C1)、页面 Prefab(C2)、卡片用 common 组件并 **expose** 出 `Demo.*` 属性(C3)、主题/本地化(C4)、Make Public+导出(C5) |
