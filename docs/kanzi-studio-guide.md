# Kanzi Studio 操作手册(手把手,3.9.15)

面向"照着做"的**具体操作**:先在 `common` 建共享资源,再在 `launcher` 建数据源,再搭 `demo`,最后在 launcher 挂载连线并导出。

> 基于 **Kanzi Studio 3.9.15** 官方文档核实。约定:**创建资源用 `Alt + 右键` 对应分类**(Kanzi 的习惯操作)。
> 相关:[architecture](architecture.md)、[conventions](conventions.md)、[data-source §3.5](data-source.md)、[demo 布局与连线表](demo-module.md)。

窗口:**Library**(资源库)、顶部 **Dictionaries**(字典/主题·语言预览)/**Pages**、**Node Tree**、**Properties**、**Prefabs**、**Binding Editor**、**Preview**。

---

# A. 在 `common` 里创建共享资源

打开 `IVI/KanziProject/Shared/common/v101_sedan/common.kzproj`。common **只提供资源**:颜色画刷、主题、字体与 Named Style。**不放 UI 组件 Prefab**(组件在 `demo` 或各业务模块)。数据源不在 common(在 launcher,见 B)。

## A1. 颜色:Color Brush

Kanzi 里"颜色"是 **Color Brush**(在 `Materials and Textures > Brushes` 下),不是单独的 Colors 分类。

1. `Library` → **Alt + 右键 `Materials and Textures`** → **Color Brush** → 命名,如 `Brush_Accent`。
2. 选中该 Brush → `Properties` 设 **Brush Color**(H/S/L 或 RGBA)。
3. 用法:
   - 填充背景:节点 `Properties` → 添加 **Background Brush** → 选该 brush。
   - 文字颜色:Text Block 节点 → 添加 **Foreground Brush** → 选该 brush(或就地 `+ Color Brush`)。
4. 按需建一组:`Brush_Background`、`Brush_Surface`、`Brush_Accent`、`Brush_TextPrimary`、`Brush_Error` 等。

## A2. 主题(日/夜):Theme Group

> ⚠️ **勘误(官方多工程规则)**:Theme Group **必须建在 launcher(含 Screen 的主工程)**,不能建在 common——定义在被引用工程里的 Theme Group,其他工程经 resource ID 找不到(官方 [Using Themes](https://docs.kanzi.com/3.9.15/en/working-with/themes/using-themes.html) "Using themes in multiple Kanzi Studio projects" 一节)。common 只放各主题用的 **brush(值资源,Public)**;Theme Editor 的格子用 Add Existing / `< URL >` 指向 common 的 brush。迁移与完整方案见 [architecture/localization-theme-design.md](architecture/localization-theme-design.md)。下述操作流程本身不变,只是**建组的工程换成 launcher**。

3.9.15 用 **Theme(Theme Group)** 做主题切换,资源 ID 在各 Theme 下取不同 brush。

1. **先准备两套值的 brush**:如 `Brush_Bg_Day`(浅)与 `Brush_Bg_Night`(深),`Brush_Accent_Day` / `Brush_Accent_Night` 等。
2. **把节点资源加入 Theme Group**:在 `Node Tree` 选中用了这些 brush 的节点 → **右键 → Add Resources to a Theme Group**(新建一个 Theme Group)。Kanzi 会**自动为每个资源生成 resource ID**,并把节点改成用 resource ID。
3. **建主题并逐格指定**:`Library > Themes` 双击该 Theme Group → 打开 **Theme Editor** → **Create Theme** 建 `Day`、`Night` → 每一行 resource ID,在 `Day` / `Night` 列 double-click 选对应 brush(如背景行:Day=Brush_Bg_Day,Night=Brush_Bg_Night)。
4. **手动加资源(可选)**:Theme Editor → **+ Add Resource** → Create/Add Existing → 命名 resource ID;节点属性设为 `< Resource ID >` 并填该 ID。
5. **预览切换**:顶部 **Dictionaries** 窗口 → 点 **Locales and Themes** → 为该 Theme Group 选 `Day`/`Night`,Preview 立即变。

> 组件/页面里"用某颜色" = 用主题的 resource ID(经 Theme Group),而不是写死某个 brush,这样才可日夜切换。

## A3. 字体与多语言样式(Named Style)

> ⚠️ **勘误(官方多工程规则)**:**Localization Table 必须建在 launcher**,理由同 A2(官方 [Localizing applications](https://docs.kanzi.com/3.9.15/en/working-with/localization/localizing-applications.html) "Using localization in multiple Kanzi Studio projects" 一节)。common 只放 **Named Style 与字体(值资源,Public)**;launcher 表的各 locale 列指向 `kzb://common/Styles/LocaleStyle_zh` 等(launcher 现有表已是这种写法)。见 [architecture/localization-theme-design.md](architecture/localization-theme-design.md)。

你工程里的 `LocaleStyle` / `LocaleStyle_zh` 就是这套(按语言切字体):

1. **导入字体**:`File > Import`(或 `Font Families` 已有 `NotoSansCJKsc`)。
2. **建 Named Style**:打开 **Localization Editor**(双击 `Library > Localization > Localization Table`)→ **+ Add Resource** → **Create > Named Style** → 命名 `LocaleStyle`。
3. **复制出各语言版**:`Library > Styles` 右键 `LocaleStyle` → **Duplicate** → 命名 `LocaleStyle_zh` 等。
4. **各 style 设字体**:选中 style → `Properties` 添加并设 **Font Family**(`LocaleStyle`=拉丁字体,`LocaleStyle_zh`=Noto Sans CJK SC)。
5. **在本地化表按 locale 指定**:Localization Table 里 `LocaleStyle` 行,在各 locale 列 double-click 选对应 style。
6. **节点应用**:目标节点(如页面根)`Properties` → **移除 Font Family** → 添加 **Style** → 设 resource ID 为 `LocaleStyle`。切 locale 时字体随之切换。

## A4. 设为 Public 并导出(common 仅资源)

- `Library` 里 Brush / Theme / Style / Font 等资源 → 右键 **Make Public**。
- 整工程:`Project > Properties` → `Resource Visibility Across Projects = Public`。
- `File > Export > Export KZB` 导出 `common.kzb`。

> **不要在 common 建 Card / Button 等 UI Prefab。** 组件搭建见下文 C 节(demo)。

---

# B. 数据源(在 `launcher` 创建)

打开 `IVI/KanziProject/launcher/Tool_project/launcher.kzproj`。

## B1. 导入并启用插件
1. `Library` → **右键 `Kanzi Engine Plugins`** → **Import Kanzi Engine Plugin** → 选 `IVI/plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`(Android 用 Java 插件)。
2. 选中插件 → `Properties` 确认 **Is Enabled** 打开。改过插件后用右键 **Update Kanzi Engine Plugin** 刷新元数据。

## B2. 建数据源并指向 XML
1. 打开 **Data Sources** 面板(`Window` 菜单)→ 右键 → 新建数据源,类型选插件的 **DroidDataSource** 类型,命名 `VehicleData`。
2. 在其属性里把 **XML 路径**指向 `IVI/assets/xml/datasource.xml`(单一契约)。
3. 右键数据源 → **Update Data Source Contents**,应出现 `System / Charging / VehicleControl / Interior / Demo` 分组字段。

## B3. 设 Data Context
- `Node Tree` 选 **Screen/RootPage 根** → `Properties` → **+ Add** → **Data Context** → 设为 `VehicleData`;子节点(含运行时挂入的子模块)继承。

---

# C. 搭 `demo` 样板(组件 + 页面)

打开 `IVI/KanziProject/demo/demo.kzproj`。demo 是**完整参考实现**:UI 组件、DemoPage、绑定示例都在这里。业务模块**对照 demo 学**,运行时**不依赖** demo kzb(除非 launcher 要挂 Demo 页)。

## C0. 若组件仍在 common(历史遗留)

按 [migrate-components-to-demo.md](migrate-components-to-demo.md) 先迁到 demo,再继续下面步骤。

## C1. 引用 common

- `Library` → **右键 `Project References`** → **Add** → **Existing Project** → `IVI/KanziProject/Shared/common/v101_sedan/common.kzproj`。
- 组件里颜色用 `< Resource ID >` → `Color/Surface` 等;文字用 `LocaleStyle`。

## C2. UI 组件(Prefab,建在 demo)

1. **搭结构**:`Node Tree` 用 Kanzi 内置节点(Button 2D / Toggle Button 2D / Slider / Rectangle 2D 等),样式引用 common 的 theme token 与 Named Style。
2. **做成 Prefab**:拖进 `Prefabs` 窗口 → 命名 `Card`、`LabelText`、`ToggleSwitch` 等。
3. **暴露属性**:在 prefab 内对要对外的属性点 expose(+)→ 根节点生成自定义属性 + 内部 `##Template` 绑定。
4. **Card 建议**:在 demo 内用 **Prefab Placeholder** 从 Prefabs 拖入页面(可展开编辑内部);launcher 挂模块时用 **Prefab View** + `kzb://`。Card 壳 + 页面内组合内容,详见 [demo-build-all.md](demo-build-all.md) §5。

## C3. 页面根 Prefab
- `Node Tree` 搭页面容器(用 Grid/Stack Layout 排卡片)→ 拖进 `Prefabs` 窗口 → 命名 `DemoPage`(放 `Prefabs/Pages/`)。

## C4. 每张卡片(用 demo 内组件 + 暴露属性)

> demo 内部**不直接绑数据源**(数据源在 launcher);它把要接收的值**暴露为 DemoPage 根属性**(A4 的 expose 机制),launcher 再把这些属性接到数据源(见 D)。

- **读·文本**:放 Text Block(Style=`LocaleStyle`,Foreground Brush 走主题)→ 选它的 `Text` 属性 → 点旁边 **expose 图标** → 在 DemoPage 根生成属性,重命名 `Demo.Title`。
- **读·进度**:放 ProgressBar/表盘 → expose 其 `Value` → `Demo.GaugeValue`;故障态用 State Manager:另 expose 一个 `Demo.GaugeValid`(Bool),false 时切到"--"+ 主题 `Error` 色状态。
- **写·开关**:放 Toggle Button/`ToggleSwitch` → expose 其选中属性 → `Demo.ToggleOn`。写回见 D(launcher 侧 To-Source)。
- **写·滑块**:放 Slider → expose `Value` → `Demo.SliderValue`。
- **写·颜色**:色块的 Color Brush 的颜色 → expose → `Demo.AccentColor`。
- **枚举·状态**:expose `Demo.StatusEnum`(Int)驱动 State Manager 切图标。
- **图片**:Image 节点 expose 其 `Image`/URI 来源 → `Demo.IconUri`。
- **列表**:List Box(`Items Source`)—— 建议由 launcher 侧绑数据源 `Demo/menu`,或用消息驱动。

## C5. 主题 / 本地化
- 颜色都走主题 resource ID(A2),文字都走 `LocaleStyle`(A3)/ 本地化,禁止写死。

## C6. Make Public + 导出
- 选 `DemoPage` → **Make Public**;`File > Export > Export KZB` 导出 `demo.kzb`。

---

# D. 在 `launcher` 挂载 demo 并连线

回到 `launcher`。

## D1. 引用并挂载
1. `Library > Project References > Add > Existing Project` → `IVI/KanziProject/demo/demo.kzproj`。
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
| Update Data Source 后无字段 | XML 路径要指 `IVI/assets/xml/datasource.xml`,插件 Is Enabled,再 Update |
| 开关点了不回写 | 补 To-Source(demo expose 属性 → launcher DemoView 上 To-Source 到数据源) |

---

# F. 各工程各建什么

| 工程 | 建什么(章节) |
|------|----------------|
| `common` | Color Brush(A1)、Theme Group(A2)、Named Style(A3)、Make Public+导出(A4) — **仅资源** |
| `launcher` | 导入插件(B1)、建数据源指向 `IVI/assets/xml/datasource.xml`(B2)、Screen 设 Data Context(B3)、挂载 Prefab View + 连线(D) |
| `demo` | 引用 common(C1)、UI 组件(C2)、页面(C3)、卡片 expose(C4)、Make Public+导出(C6) |
| 业务模块 | 引用 common、**参照 demo** 自建 Prefab,expose 本模块属性,Make Public+导出 |
