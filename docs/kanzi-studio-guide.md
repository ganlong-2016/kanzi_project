# Kanzi Studio 操作手册(手把手)

面向"照着做"的**具体操作步骤**:先在 `common` 建好共享资源,再建数据源(launcher),再搭 `demo` 样板,最后在 launcher 挂载连线并导出。

> 版本说明:本项目使用 **Kanzi Studio 3.9.15**。不同版本菜单名可能略有差异,遇到名称对不上时按同义项找即可。
> 前置概念见 [architecture](architecture.md)、[conventions](conventions.md)、[data-source §3.5](data-source.md)、[demo 布局与连线表](demo-module.md)。

窗口速查:**Library**(资源库)、**Node Tree**(节点树)、**Prefabs**(预制件)、**Properties**(属性)、**Node Components**、**Binding Editor**(绑定编辑器)、**Preview**(预览)。

---

# A. 在 `common` 里创建共享资源

打开 `IVI/common/common.kzproj`。common 提供:主题 token、字体、通用组件。**数据源不在 common**(在 launcher,见 B)。

## A1. 主题 token(Resource Dictionary + 日/夜)

目标:颜色/字号/尺寸集中成"有名字的资源",供全项目引用、可切日夜。

1. **建资源字典**:`Library` 面板 → 右键 **Resource Dictionaries** → **Create Resource Dictionary** → 命名 `Theme_Day`;再建一个 `Theme_Night`。
2. **建颜色资源**:`Library` → 右键 **Colors**(或 Materials and Textures 下的 Color)→ **Create Color** → 设 RGBA;命名如 `Color_Background`、`Color_Accent`、`Color_TextPrimary`、`Color_Error` 等(对照 [conventions](conventions.md) 的 token 表)。
3. **把颜色加进字典并起别名(resource ID)**:双击 `Theme_Day` 打开字典编辑器 → **Add** → 选颜色资源 → 设 **Resource ID** 如 `Color/Accent`。`Theme_Night` 里用**同样的 Resource ID**,但指向夜间取值的颜色。
4. **字号/尺寸**:字号通过 Font(见 A2)与 Text Block 属性;间距/圆角这类纯数值 Kanzi 无"数值资源",按约定在组件里用固定档位(见 conventions 第 8/9 节)。
5. **激活/切换**:主题切换 = 运行时切换激活的字典;设计期可在 **Dictionaries** 窗口切 Day/Night 预览。

> 之后组件里"用某颜色"= 引用 `Color/Accent` 这个 Resource ID,而不是直接填色值。

## A2. 字体

1. 字体文件已在 `IVI/common/Fonts/NotoSansCJKsc-Regular.otf`。
2. **导入为字体资源**:`Library` → 右键 **Font Families**(或 Fonts)→ **Import Font** → 选该 otf → 生成字体资源,命名 `Font_CJK`。
3. 用法:Text Block 节点 `Properties` 的 **Font** 属性设为 `Font_CJK`。
4. 设 Public(见 A4),供各工程 `kzb://common/...` 引用。

## A3. 通用组件(Prefabs)

以 **Button**、**ToggleSwitch**、**Card**、**Slider**、**ProgressBar**、**ListItem** 为例。每个组件都做成 Prefab 并**暴露对外属性**。

以 **ToggleSwitch** 为例(其它同理):
1. **搭结构**:`Node Tree` 里建一个容器(Empty Node 2D)+ 背景 + 滑块圆点 + 状态视觉。
2. **做成 Prefab**:选中容器根 → 右键 → **Create Prefab**(或拖到 `Prefabs` 面板)→ 命名 `ToggleSwitch`。
3. **对外属性**:给 Prefab 根节点加自定义属性(见 C3 建 Property Type 的方法)`Switch.IsChecked`(Bool)、`Switch.Label`(String)。
4. **内部绑定到根属性**:内部"开/关视觉"节点的相关属性 `+ Add Binding` → 表达式 `{##Template/Switch.IsChecked}`;标签 Text 绑 `{##Template/Switch.Label}`。
   - 也可用快捷法:在 Prefab 根选中该属性,`Properties` 里属性旁的小图标点一下,Kanzi 会自动生成 control property + `##Template` 绑定。
5. **样式引用 token**:背景/圆点颜色引用 `Color/*`(A1),不写死。
6. **交互**:用 Trigger(点击)切换 `Switch.IsChecked`(或留给使用方绑定)。
7. **设默认值**便于预览。

> 组件的原则:**内部只认自己的对外属性**(`##Template/...`),使用方(demo/launcher)只设这些属性。这与数据源解耦。

## A4. 设为 Public(跨工程可用)

- 单项:在 `Prefabs`/`Library` 选中组件/字体/颜色 → 右键 **Make Public**(或 `Properties` 设 `Visibility Across Projects = Public`),public 项左上角有绿标。
- 整工程:`Project > Properties` → `Resource Visibility Across Projects = Public`。
- 导出一次 `common.kzb`(`File > Export > Export KZB`)。

---

# B. 数据源(在 `launcher` 创建)

打开 `IVI/launcher/Tool_project/launcher.kzproj`。

## B1. 注册插件

1. `Library` → 右键 **Kanzi Engine Plugins** → **Import Plugin**(或 Add)→ 选 `plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`。
2. 确认插件加载成功(Log 窗口无报错);插件路径要对 Studio 预览可达。

## B2. 建数据源并指向 XML

1. 打开 **Data Sources** 窗口(`Window` 菜单里找 Data Sources)→ 右键 → **Create Data Source** → 类型选插件提供的 **DroidDataSource** 类型 → 命名 `VehicleData`。
2. 在数据源属性里把 **XML/文件路径**指向 `assets/datasource.xml`(仓库根的单一契约)。
3. 右键数据源 → **Update Data Source Contents**(刷新),此时应能看到 `System / Charging / VehicleControl / Interior / Demo` 分组和字段。

## B3. 设 Data Context(Screen 级)

1. `Node Tree` 选 **Screen**(或 RootPage 根)→ `Properties` → **+ Add** → 添加 **Data Context** 属性 → 设为 `VehicleData`。
2. 之后 launcher 内节点、以及运行时挂到其下的子模块都继承这个数据上下文。

---

# C. 搭 `demo` 样板模块

打开/新建 `IVI/demo/demo.kzproj`。目标见 [demo 布局与连线表](demo-module.md)。

## C1. 引用 common

1. `Library` → 右键 **Project References** → **Add** → **Existing Project** → 选 `IVI/common/common.kzproj`。
2. 现在能用 common 的 `Font_CJK`、`Color/*`、`ToggleSwitch/Slider/...` 组件。

## C2. 建页面根 Prefab

1. `Node Tree` 建根容器(Empty Node 2D / 用布局如 Grid/Stack)→ 命名 `DemoPage`。
2. 选中 → 右键 → **Create Prefab** → 命名 `DemoPage`,放 `Prefabs/Pages/`。

## C3. 建对外输入属性(Property Types)

对每个要从 launcher 接收的数据建一个属性类型:
1. `Library` → 右键 **Property Types** → **Create Property Type**。
2. 依次建(名字 / 数据类型 / 默认值):
   - `Demo.Title`(String,默认 "Demo")
   - `Demo.GaugeValue`(Float,默认 62)
   - `Demo.GaugeValid`(Bool,默认 true)
   - `Demo.ToggleOn`(Bool,默认 false)
   - `Demo.SliderValue`(Int,默认 30)
   - `Demo.AccentColor`(Color,默认蓝)
   - `Demo.StatusEnum`(Int,默认 1)
   - `Demo.IconUri`(String,默认空)
3. 选中 `DemoPage` 根节点 → `Properties` → **+ Add** → 把上面这些属性都加到根节点(给设计期默认值,便于独立预览)。

## C4. 逐个卡片(用 common 组件 + 绑 `##Template`)

> 每张卡片都用 `Card` 组件做外框,内部放对应控件。控件属性绑定到 `DemoPage` 根的对应属性(`##Template`)。

- **卡片2 读·文本**:放 Text Block → `Text` `+ Add Binding` → `{##Template/Demo.Title}`;`Font` = `Font_CJK`。
- **卡片1 读·进度**:放 common 的 ProgressBar(或环形表盘)→ 其 `Value` 绑 `{##Template/Demo.GaugeValue}`;
  - **故障态**:给数值区加一条绑定/状态:当 `{##Template/Demo.GaugeValid}` 为 false → 显示 "--" 且颜色用 `Color/Error`(可用 State Manager 或表达式)。
- **卡片3 写·开关**:放 `ToggleSwitch` 实例 → 其 `Switch.IsChecked`:
  - 读:`+ Add Binding` ← `{##Template/Demo.ToggleOn}`;
  - 写:再加一条 **To-Source** 绑定,Push Target = `{##Template/Demo.ToggleOn}`(即写回 DemoPage 根属性)。
- **卡片4 写·滑块**:放 `Slider` → `Value` 读 ← `{##Template/Demo.SliderValue}`,并加 To-Source 写回同属性(int 0–100)。
- **卡片5 写·颜色**:色块的颜色属性 ↔ `{##Template/Demo.AccentColor}`(读 + To-Source);调色控件同理。
- **卡片6 枚举·状态**:用 `{##Template/Demo.StatusEnum}` 驱动 **State Manager**(0/1/2/3/4 各一个状态,切换图标/文字)。
- **卡片7 图片**:Image 节点的图片来源绑 `{##Template/Demo.IconUri}`;给占位图。
- **卡片8 列表**:见 [demo-module.md](demo-module.md);列表建议放 launcher 侧或用消息驱动(数据源 list 由 Android 侧填充)。

## C5. 主题与本地化(demo 内)

- **主题**:卡片里所有颜色引用 `Color/*`(A1),不写死 → 日/夜切换自动生效。
- **本地化**:卡片里固定文案(标题/单位)不要硬编码;用本地化(见 [localization-and-theme](localization-and-theme.md) 的 DataLayer,由 launcher 下发字符串;demo 内绑到普通 string 属性)。

## C6. 暴露与导出

1. 选 `DemoPage` → **Make Public**。
2. `File > Export > Export KZB` 导出 `demo.kzb`。

---

# D. 在 `launcher` 挂载 demo 并连线

回到 `launcher`。

## D1. 引用并挂载

1. `Library > Project References > Add > Existing Project` → `IVI/demo/demo.kzproj`。
2. `Node Tree` 内容区 → 右键 → 添加 **Prefab View 2D** → 命名 `DemoView` → `Properties` 的 **Prefab Template** 设为 `kzb://demo/Prefabs/Pages/DemoPage`。

## D2. 连线(数据源 ↔ Prefab View 属性)

选中 `DemoView`(它就是 demo 实例根,带着 `Demo.*` 属性),按 [demo-module 连线对照表](demo-module.md#launcher-连线对照表核心) 逐条绑:
- **读**:`Demo.Title` `+ Add Binding` ← 数据源 `VehicleData` 的 `Demo/titleText`;`Demo.GaugeValue` ← `Demo/gaugeValue` … 依此类推。
- **写**:对 `Demo.ToggleOn`/`Demo.SliderValue`/`Demo.AccentColor` 再各加一条 **To-Source**,Push Target = 数据源对应字段(`Demo/toggleOn` 等)。
  - 链路:demo 内控件写 → DemoView 的属性 → 这条 To-Source → 数据源 → 插件下发。

## D3. 导航

- 在桌面/标签上加入口 → 用 State Manager / 可见性切换显示 `DemoView`。
- (可选)在 `DemoView` 上设 `Demo.AccentColor` 演示从外部控制 demo 主色。

## D4. 导出

- 依次导出:`common.kzb`(先)→ `demo.kzb` → `launcher.kzb`。见 [export-kzb](export-kzb.md)。

---

# E. 验证与常见问题

| 现象 | 检查 |
|------|------|
| demo 里选不到数据源字段 | 正常:数据源在 launcher。demo 只绑 `##Template/Demo.*`;字段绑定在 launcher 的 DemoView 上做 |
| Update Data Source 后没新字段 | 确认 XML 路径指向 `assets/datasource.xml`,插件已加载,再 Update |
| 开关点了不回写 | 只做了读绑定;补一条 To-Source(demo 内 → 根属性;launcher 上 → 数据源) |
| 组件颜色不随日夜变 | 颜色写死了;改成引用 `Color/*` Resource ID |
| 引用 common 后看不到组件 | 组件没 Make Public;或 common 未先导出 |
| 预览无数据 | 给 `Demo.*` 属性设计期默认值 |

---

# F. 小结:各工程各建什么

| 工程 | 建什么(操作章节) |
|------|--------------------|
| `common` | 主题字典 Day/Night + 颜色 token(A1)、字体资源(A2)、通用组件 Prefab(A3)、全部 Make Public(A4) |
| `launcher` | 注册插件(B1)、建数据源指向 `assets/datasource.xml`(B2)、Screen 设 Data Context(B3)、挂载各模块 Prefab View + 连线(D) |
| `demo`/各模块 | 引用 common(C1)、页面 Prefab(C2)、对外属性(C3)、用 common 组件搭 UI + 绑 `##Template`(C4)、主题/本地化(C5)、Make Public + 导出(C6) |
