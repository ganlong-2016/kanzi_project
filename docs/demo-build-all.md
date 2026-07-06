# demo 一站式搭建文档(v2 · 每步已对照 Kanzi Studio 3.9.15 官方文档核实)

本文是 demo 的**唯一施工文档**:按"先通用基础(主题 → 本地化 → 数据通信 → 组件库),再具体功能(页面 → 卡片 → 连线)"的顺序,把每一步写到可以照着点鼠标的程度。窗口名、菜单名、属性名均按 **Kanzi Studio 3.9.15 官方文档**(docs.kanzi.com/3.9.15)的原文写,未经官方核实的操作不会出现在本文里。

> **v2 相对 v1 的修正**(v1 里有几处在 Studio 中不存在或不可靠的写法,已删除):
>
> - ~~Factory Content 的圆形 Progress Indicator~~ → 改为用两个 Rectangle 2D + 绑定表达式实现的 **ProgressBar**(§5.4)。
> - ~~Alt+右键 → Empty Node From Items 替换预制体根节点~~ → 改为明确的手工重建步骤(§5.2)。
> - demo 内子页导航不用 Activity Host(官方:Activity Host 由 Activity Browser 创建、挂在 **Screen 节点**下,属于主工程级结构,不适合放进子工程的 prefab)→ 改用 **State Manager** 切换(§6.3),Activity 方案作为 launcher 级可选扩展(§12)。

## 图例(每一步的负责人)

| 标记 | 含义 |
|------|------|
| ✅ | **已完成**(已核实存在于当前工程文件中,只需检查) |
| 🔨 | **需要你在 Kanzi Studio 中手工操作**(kzproj 是工具序列化格式,文档无法代做) |
| 📁 | **仓库侧已完成**(XML/文档,已随本文档提交) |

---

## 0. 分工(必读)

| 工程 | 放什么 | 不放什么 |
|------|--------|----------|
| **common** | Color Brush、AppTheme、Font、Named Style | UI 组件 Prefab、页面、数据源 |
| **demo** | Card / LabelText 等组件、DemoPage、绑定示例 | 业务逻辑;不替代业务模块 kzb |
| **launcher** | Screen、数据源、本地化表、挂模块 | 业务 UI 细节 |
| **业务模块** | 本域 Prefab 与页面 | 复制 common 资源;不运行时依赖 demo |

> **组件在 demo**: `LabelText` / `Card` 等 UI Prefab 已在 `IVI/demo/demo.kzproj` 的 `Prefabs` 下;common 只提供 Brush / Theme / Font。业务模块对照 demo 自建,不运行时引用 demo kzb。

## 0.1 已完成的部分(经工程文件核实)

| 项 | 位置 | 状态 |
|----|------|------|
| 18 个颜色 Brush(`Brush_<角色>_<Day/Night>`) | common | ✅ |
| Theme Group `AppTheme`,含 `Day` / `Night` 两个 Theme,9 个 `Color/*` resource ID | common | ✅ |
| Named Style `LocaleStyle` / `LocaleStyle_zh`(另有 `LocaleStyle_en`) | common | ✅ |
| 组件 `LabelText` / `ToggleSwitch` / `Slider` / `Card` | **demo** `Prefabs/` | ✅(Card 结构待 §5.2 改造) |
| common 工程级 `Visibility Across Projects = Public` | common | ✅ |
| 数据源插件 `DroidDataSourceplugin` 已导入注册 | launcher | ✅ |
| 数据源实例已创建(名为 `Data source`) | launcher | ✅(File 路径需修正,见 §4.3) |
| launcher 引用全部子工程;demo/car/car_setting/environment 均已引用 common | 各工程 | ✅ |
| DemoPage 骨架(Grid Layout 2D + 7 张 Card 实例)与 4 个 `Demo.*` 属性类型 | demo | ✅ 部分(需按 §6/§7 补全) |

### 0.2 需要你在 Studio 完成的部分(本文正文)

1. §4 修正数据源 File 路径、把 Data Context 移到 RootPage 根。
2. §3 在 launcher 建本地化表(zh-CN / en)+ 语言切换。
3. §5 改造 Card,新建 Button / ProgressBar / StatusIcon / ImageBox / ListItem;删除试验品 `Card2`、`Slider 2D`。
4. §6–§7 补全 DemoPage(双子页 + 8+8 张卡)并暴露属性。
5. §8–§9 launcher 挂载 DemoView、连数据、做顶栏。
6. §10 子页 B 的 8 张进阶卡。
7. §11 Make Public 与导出。

### 0.3 仓库侧已完成

- 📁 `assets/datasource.xml`:契约字段(`System/Vehicle/Charging/VehicleControl/Interior/Demo`)已就绪,头部过时注释已修正(单一来源,无第二份副本)。本次 demo 不需要新增字段(子页 B 的卡片演示的是 UI 机制,复用现有字段)。
- 📁 本文档及 `demo-spec.md` / `demo-module.md` 的同步修订。

---

## 1. 全局设计值(照抄即可)

| 项 | 值 |
|----|----|
| Screen 分辨率 | 1920 × 1080 |
| 顶部安全边距(系统状态栏) | 80 px |
| 底部安全边距(系统导航栏) | 100 px |
| 安全内容区 | 1920 × 900(Y:80→980) |
| demo 顶栏 | 高 96(Y:80→176) |
| 卡片区 | 1920 × ~804(Y:176→980) |
| 卡片网格 | 4 列 × 2 行,卡片 440 × 360,间距 32 |
| 字号 | Title 40 / Body 28 / Caption 20 |
| 圆角 | 8 / 16 / 24;间距 8 / 16 / 32 |

颜色值(Day/Night 各 9 个)见 `demo-spec.md` §2,common 里已全部建好。

---

## 2. 通用基础一:主题(common)✅ 已建好,以下是检查方法与日常用法

### 2.1 机制(为什么这样做)

Kanzi 的主题 = **Theme Group** 里若干 **Theme**,每个 Theme 给同一批 **resource ID** 指定不同资源。节点永远只引用 resource ID(如 `Color/Accent`),切主题时 Kanzi 替换 resource ID 背后的资源。主题在 **Screen 节点**层解析,所以运行时的激活由含 Screen 的 launcher 控制;common 只负责定义。

### 2.2 检查现状(1 分钟)

1. 打开 `IVI/common/common.kzproj`。
2. `Library > Themes` 下应有 **AppTheme**;双击它打开 **Theme Editor**,应看到 `Day`、`Night` 两列和 9 行 `Color/*` resource ID,每格分别指向 `Brush_*_Day` / `Brush_*_Night`。
3. 预览切换:打开 **Dictionaries** 窗口 → 点 **Locales and Themes** → 给 AppTheme 选 `Day` 或 `Night`,Preview 应立即变色。

### 2.3 以后如何新增一个主题 token(官方流程,记住备用)

1. 方式一(推荐,自动):在 **Node Tree**(或 **Prefabs**)里**右键**用了某 brush 的节点 → **Add Resources to a Theme Group** → 窗口里把 **Theme Group** 设为 `AppTheme`,勾选要加的资源,可双击重命名 resource ID → **Add**。Kanzi 会自动生成 resource ID 并把节点改成引用该 ID。
2. 方式二(手动):`Library > Themes` 双击 `AppTheme` 打开 **Theme Editor** → **+ Add Resource** → **Create**(或 **Add Existing**)→ 命名 resource ID → 在 `Day` / `Night` 两列分别双击选择资源。
3. 节点侧使用:在节点 **Properties** 里把对应属性(如 Background Brush)设为 **< Resource ID >** 并填该 ID。

> 常见坑:节点上直接选了某个 `Brush_..._Day`(写死)会导致"切主题不变"。凡是要随主题变的颜色,一律走 resource ID。

---

## 3. 通用基础二:多语言本地化(launcher)🔨

### 3.1 机制(官方结论,决定了架构)

- 本地化表(**Localization Table**)按 **resource ID → 每个 locale 一列值** 存储;文本节点通过 resource ID 取当前语言的值。
- 官方明确:**多工程合并成一个应用时,本地化表必须对主工程(含 Screen 的 launcher)的 Screen 可见**——要么直接定义在主工程,要么合并进主工程(跨工程共享表需要向 Rightware 申请专用插件)。
- 因此本项目约定:**表建在 launcher**;demo 等子模块**不碰本地化表**,文案经"launcher 解析 → 属性下发"进入子模块(见 §3.5、§8)。

### 3.2 创建本地化表与 locale(launcher)🔨

1. 打开 `IVI/launcher/Tool_project/launcher.kzproj`。
2. `Library` 里按住 **Alt 右键点击 Localization** → 选 **Localization Table** → 命名 `AppStrings`。
   - 当前工程里已有一个名为 `Localization Table` 的表(只有 zh-CN 一个 locale、没有条目),可直接复用它:双击打开后继续下面步骤,不必新建。
3. 双击该表打开 **Localization Editor**。
4. 点 **+ Create Locale** → 输入 `zh-CN` → OK;再 **+ Create Locale** → 输入 `en` → OK。

### 3.3 添加文案条目 🔨

在 **Localization Editor** 里点 **+ Add Resource → Create → Text**(文本资源),逐条建下面的 key,并双击各 locale 单元格填译文:

| resource ID | zh-CN | en |
|-----|-------|----|
| `demo.title` | 演示 | Demo |
| `demo.gauge` | 进度 | Gauge |
| `demo.text` | 文本 | Text |
| `demo.switch` | 开关 | Switch |
| `demo.slider` | 滑块 | Slider |
| `demo.color` | 颜色 | Color |
| `demo.status` | 状态 | Status |
| `demo.image` | 图片 | Image |
| `demo.list` | 列表 | List |
| `common.unavailable` | 不可用 | Unavailable |

> 说明:如果是给**已有的 Text Block 节点**批量做本地化,官方更快的入口是:在 Node Tree 右键节点(或 Screen)→ **Add Resources to a Localization Table**,Kanzi 会为相同文本自动合并生成 resource ID。我们这里因为文案主要下发给 demo,所以直接在 Editor 里手建条目。

### 3.4 预览与切换语言 🔨

- **预览**:**Dictionaries** 窗口 → **Locales and Themes** → 选 locale,Preview 里凡是绑定了 resource ID 的文本立即切换。
- **运行时切换**(做成按钮,§9 会用到):切语言 = 改 **Screen 节点的 Locale 属性**。官方做法:
  1. 在语言按钮节点的 **Node Components** 里按住 **Alt 右键 Triggers** → **Message Trigger > Button > Click**(如果用 Toggle Button 则选 Toggled On)。
  2. 按住 **Alt 右键该触发器** → 选 **Set Property** 动作,设:
     - **Target Item** = Screen
     - **Target Property** = Locale
     - **Value From** = Fixed value
     - **Fixed Value** = 目标 locale(列表里选 `Chinese (Simplified, China) (zh-CN)` 或 `English`;默认语言选 Invariant Language)

### 3.5 demo 里的文案怎么办(本项目约定)

demo 设计期看不到 launcher 的表,所以:

- demo 内部所有要显示的文案一律走**暴露的 String 属性**(如 `Demo.Title`),设计期给默认值便于预览;
- launcher 侧在挂载 demo 的 Prefab View 上,把这些属性**绑定到本地化表**:`+ Add Binding` → Property 选对应属性 → **Expression** 填:

```text
string(acquire("demo.title"))
```

`acquire()` 是官方绑定函数,按 resource ID 取**当前 locale**的资源;切语言时绑定自动刷新,demo 对语言零感知。
- demo 卡片的 8 个小标题为避免 8 条属性连线,设计期先直接填占位文本(§7),量产模块再按上面的链路接;本 demo 用顶栏标题 + 卡 2 完整示范这条链路(§8/§9)。

---

## 4. 通用基础三:数据通信(launcher)🔨

### 4.1 机制

```text
assets/datasource.xml(契约) → DroidDataSourceplugin(Java 插件,解析 XML)
  → Data Sources 面板里的数据源实例 → 节点 Data Context → 绑定(读 / To-Source 写)
```

数据源也是 Screen 级资源:插件与数据源实例在 **launcher**;demo 只暴露属性,由 launcher 把数据源接到属性上(§8)。

### 4.2 检查插件 ✅

`Library > Kanzi Engine Plugins` 下应有 **DroidDataSourceplugin**;选中它,在 **Properties** 确认 **Is Enabled** 已勾选。若以后更新了 jar:右键插件 → **Update Kanzi Engine Plugin**。

### 4.3 修正数据源的 File 路径 🔨(当前配置有问题,必做)

现状:数据源实例 `Data source` 的 `DroidDataSource.File` 值是裸文件名 `datasource.xml`,而工程目录下并没有这个文件——**这是当前数据源不出字段的直接原因**。修正:

1. 菜单 **Window > Data Sources** 打开 **Data Sources** 窗口。
2. 找到 `Data source`(可顺手重命名为 `VehicleData`,后文按此名称写)。
3. 点它的属性设置图标,把 **File** 改为指向仓库根的契约文件。从 `IVI/launcher/Tool_project/` 出发的相对路径是:

```text
../../../assets/datasource.xml
```

   (若相对路径不生效,先用绝对路径验证,再和团队统一相对写法。)
4. 点该数据源旁的**更新**图标(官方:update data source contents)。
5. **验收**:Data Sources 窗口里展开后应出现 `System / Vehicle / Charging / VehicleControl / Interior / Demo` 六个分组;悬停任一数据对象可看到类型和当前值(来自 XML 里的默认值)。

### 4.4 设置 Data Context 🔨

现状:Data Context 设在 `RootPage/Controls` 节点上,只有 Controls 子树能继承。按官方建议挂到页面根:

1. **Node Tree** 选中 **RootPage**。
2. **Properties** → **+ Add** → 搜索 **Data Context** → 设为 `VehicleData`。
3. (可选清理)选中 `Controls` 节点,把它 Properties 里多余的 Data Context 删除(右键该属性 → Remove)。

> 规则:一个节点只有一个 Data Context,子节点自动继承;要换数据源就在子树上重设。**运行时挂到 RootPage 下的 demo 实例也会继承**——这正是 launcher 能替 demo 连数据的原因。

### 4.5 读绑定(官方拖拽法,最快)

- 单值属性:直接**从 Data Sources 窗口把数据对象拖到 Properties 里目标属性上**,Kanzi 自动生成绑定。
- 需要表达式时:**+ Add Binding** → **Binding Editor** 里设 **Property**(目标属性),再把数据对象**拖进 Expression 区**,在其外面套表达式,**Save**。

### 4.6 写绑定(To-Source,官方三要素)

在要回写的节点上 **+ Add Binding**,**Binding Editor** 里设:

| 字段 | 值 |
|------|----|
| **Binding Mode** | `To source` |
| **Push Target** | 要写入的目标(点选目标项 + 目标属性) |
| **Property** | 本节点被监听的属性(它一变就推送) |
| **Expression** | 计算要写出的值(可含类型转换,如 `{@./ToggleSwitch.State} != 0`) |

> 若 Push Target 无法直接选到数据源的数据对象(插件版本差异),写回退路是**消息方案**:demo 内控件变化 → launcher 用 Message Trigger 拦截 → Android 侧写数据。先试 To-Source,不行再退。

### 4.7 常见坑

| 现象 | 处理 |
|------|------|
| Update 后没有字段 | File 路径不对(§4.3);插件未 Enabled;XML 语法错误(看 Log 窗口) |
| 绑定后值不变 | 节点不在 Data Context 生效子树内;字段名大小写不一致 |
| 回写无效 | 只做了读绑定,补 To-Source(§4.6);或改消息方案 |
| 字段改名后绑定失效 | 契约冻结:`datasource.xml` 交付后只追加不改名 |

---

## 5. 通用基础四:组件库(demo)🔨

> **在 `IVI/demo/demo.kzproj` 里操作**(已引用 common,可直接用 `<Resource ID>` `Color/*` 与 `LocaleStyle`)。**不要在 common 建 UI Prefab。**

### 5.1 总表

| 组件 | 状态 | 根节点 | 暴露属性 |
|------|------|--------|----------|
| `LabelText` | ✅ 已有 | Text Block 2D | `LabelText.Text`(String) |
| `ToggleSwitch` | ✅ 已有 | Toggle Button 2D | `ToggleSwitch.State`(Int,即 Toggle State) |
| `Slider` | ✅ 已有 | Slider 2D(轨道+手柄) | `Slider.Value` |
| `Card` | 🔨 改造(§5.2) | Empty Node 2D | (可选)`Card.Title` |
| `Button` | 🔨 新建(§5.3) | Button 2D | `Button.Label`(String) |
| `ProgressBar` | 🔨 新建(§5.4) | Empty Node 2D | `ProgressBar.Value`(Float 0–100) |
| `StatusIcon` | 🔨 新建(§5.5) | Empty Node 2D | `StatusIcon.Status`(Int 0–4) |
| `ImageBox` | 🔨 新建(§5.6) | Image | `ImageBox.Image`(Image 资源) |
| `ListItem` | 🔨 新建(§5.7) | Empty Node 2D | `ListItem.Title`(String) |
**通用手法(下面每个组件都用到,先记住):**

- **建节点**:在 **Node Tree** 按住 **Alt 右键**父节点 → 选节点类型。
- **做成 Prefab**:把搭好的节点**拖进 Prefabs 窗口**,Kanzi 自动生成模板并把原节点替换为实例。
- **暴露属性**(官方 expose 机制):在 **Prefabs** 里选中预制体**内部**的节点 → **Properties** 里点目标属性**右侧的 expose 小图标** → Kanzi 自动在预制体根创建同类型自定义属性,并在该节点生成 `##Template` 绑定指向根属性。
- **重命名暴露出的属性**:`Library > Property Types` 里找到新属性 → F2 改名(如 `ProgressBar.Value`)。
- **Make Public**:右键 Prefab → **Make Public**(demo 工程级 Public 已设,单个新资源仍建议确认一次)。
- **Prefab View 不能展开**:Node Tree 里 **Prefab View 2D 实例不可展开**编辑内部;要改结构请双击 **Prefabs** 里的模板,或在页面用 **Prefab Placeholder** 拖入(设计期可编辑)。实例侧主要通过 expose + `##Template` 改属性。

### 5.2 Card 改造 🔨(修复"卡片里加内容看不见")

目标结构(根必须是**容器**,不能是 Rectangle 2D):

```text
Card (Empty Node 2D,Layout Width=440, Layout Height=360)
├── Background (Rectangle 2D,440×360,Background Brush=<Resource ID> Color/Surface)
└── Content (Stack Layout 2D,440×360,内边距 16,竖排) ← 卡片内容一律加在这里
```

步骤:

1. `Prefabs` 双击打开 **Card**,看根节点类型:
   - 若根已是 Empty Node 2D(或"组件节点"),跳到第 3 步补子节点;
   - 若根是 Rectangle 2D,执行第 2 步重建。
2. **重建**(替换根节点没有可靠的一键操作,手工做):
   1. 在 **Node Tree** 任意处 Alt+右键 → **Empty Node 2D**,命名 `Card`,Properties 设 **Layout Width=440、Layout Height=360**。
   2. Alt+右键这个新 `Card` → **Rectangle 2D**,命名 `Background`:Layout Width=440、Layout Height=360;**Background Brush** 设为 **< Resource ID >** → 填 `Color/Surface`。
   3. Alt+右键 `Card` → **Stack Layout 2D**,命名 `Content`:Layout Width=440、Layout Height=360;Direction=Vertical;四边 Padding/Margin 16。
   4. 确认 Node Tree 里 `Background` 排在 `Content` **前面**(先画背景后画内容)。
   5. 把 `Card` 拖进 **Prefabs** 窗口生成新模板;删除旧 Card 模板,把新模板改名为 `Card`。
3. 若只缺子节点:按 2-ii、2-iii 在根下补 `Background` 和 `Content`。
4. **Make Public**。

### 5.3 Button 🔨(新建;交互/触发器示例都靠它)

1. Node Tree 里 Alt+右键 → **Button 2D**,命名 `Button`:Layout Width=180、Layout Height=72;**Background Brush** = `<Resource ID>` `Color/Accent`。
2. Alt+右键该 Button → **Text Block 2D**,命名 `Label`:Text=`Button`;**Style** = `LocaleStyle`;**Foreground Brush** = `<Resource ID>` `Color/Surface`(深色底白字);水平/垂直 Alignment=Center。
3. (可选,按压反馈)选中 Button → **State Tools** 点 **Create State Manager** → **Create State** 两次,命名 `Up`/`Down` → controller property 下拉选 **Button > Is Down**,`Up`=false、`Down`=true → 在 `Down` 状态里把背景换成略深色并保存该状态外观 → **Edit State Manager** 退出编辑。
4. 拖进 **Prefabs** 命名 `Button` → 选中内部 `Label` → expose 它的 **Text** → 在 Property Types 里改名 `Button.Label` → **Make Public**。

### 5.4 ProgressBar 🔨(新建;替代 v1 的"ProgressRing")

原理:前景条宽度 = 值/100 × 总宽,一条绑定表达式完成,全部用官方机制。

1. Alt+右键 → **Empty Node 2D**,命名 `ProgressBar`:Layout Width=360、Layout Height=24。
2. Alt+右键 `ProgressBar` → **Rectangle 2D**,命名 `Track`:360×24;Background Brush = `<Resource ID>` `Color/Divider`。
3. Alt+右键 `ProgressBar` → **Rectangle 2D**,命名 `Fill`:Layout Height=24;**Horizontal Alignment=Left**;Background Brush = `<Resource ID>` `Color/Accent`。
4. 拖进 **Prefabs** 命名 `ProgressBar`。
5. 在 Prefabs 里选中 `ProgressBar` 根 → **Properties → + Add** 一个自定义属性:先去 `Library > Property Types` Alt+右键 → **Property Type**,Name=`ProgressBar.Value`,Data Type=Float,默认值 62,Upper Bound 100;回到根节点 **+ Add** 该属性。
6. 选中 `Fill` → **+ Add Binding**:Property=**Layout Width**,Expression:

```text
{##Template/ProgressBar.Value} / 100.0 * 360.0
```

7. **Make Public**。预览:改根上 `ProgressBar.Value`,进度条应跟着变。

### 5.5 StatusIcon 🔨(新建;枚举 → State Manager)

1. Alt+右键 → **Empty Node 2D**,命名 `StatusIcon`:96×96。
2. Alt+右键它 → **Rectangle 2D**,命名 `Dot`:64×64,居中;Background Brush 先设 `<Resource ID>` `Color/Success`。
3. 建属性类型 `StatusIcon.Status`(Int,默认 1,0–4),加到 `StatusIcon` 根上(方法同 §5.4 第 5 步)。
4. 选中 `StatusIcon` 根 → **State Tools → Create State Manager** → **Create State** 5 次,命名 `Unknown/Charging/Done/Paused/Fault`。
5. controller property 下拉选 **StatusIcon.Status**,给 5 个状态分别设值 0/1/2/3/4。
6. 逐状态点选,把 `Dot` 的 Background Brush 分别设为:`Color/TextSecondary` / `Color/Accent` / `Color/Success` / `Color/Warning` / `Color/Error`,每设完在该状态上保存外观。
7. **Edit State Manager** 退出;拖进 **Prefabs**;**Make Public**。预览:改 `StatusIcon.Status` 值,颜色应切换。

### 5.6 ImageBox 🔨(新建)

1. Alt+右键 → **Image**,命名 `ImageBox`:Layout Width=200、Layout Height=200;**Image** 属性先选工程里任一占位图(如 `DefaultTextureImage`)。
2. 拖进 **Prefabs**;选中根 → expose 它的 **Image** 属性 → Property Types 里改名 `ImageBox.Image`;**Make Public**。

> 说明:数据契约里的 `Demo/iconUri` 是字符串 URI,由 Java 插件的内容加载器在**运行时**解析成图片,Studio 预览里不会显示真图。设计期用 `ImageBox.Image` 直接换占位图演示;URI 链路在 Android 侧联调时验证。

### 5.7 ListItem 🔨(新建;列表行模板)

1. Alt+右键 → **Empty Node 2D**,命名 `ListItem`:400×72。
2. 其下 Alt+右键 → **Image**,命名 `Icon`:48×48,Horizontal Alignment=Left,左边距 12,占位图任选。
3. 其下 Alt+右键 → **Text Block 2D**,命名 `Title`:Style=`LocaleStyle`,Foreground Brush=`<Resource ID>` `Color/TextPrimary`,靠左,左边距 72。
4. 拖进 **Prefabs**;expose `Title` 的 **Text** → 改名 `ListItem.Title`;**Make Public**。

### 5.8 导出

1. demo:新建/改动的组件 Prefab 全部 **Make Public** → `File > Export > Export KZB` 导出 `demo.kzb`。
2. common:若只改了 Brush/Theme/Font,单独重导 `common.kzb`;与组件无关时不必因 demo 组件变更而重导 common。

---

## 6. demo 页面骨架 🔨(DemoPage + 双子页)

打开 `IVI/demo/demo.kzproj`(已引用 common ✅)。

### 6.1 统一 DemoPage 位置与尺寸

现状:已有 `Prefabs/DemoPage/DemoPage`(Grid Layout 2D + 7 张 Card 实例)。约定最终路径为 **`Prefabs/Pages/DemoPage`**(与规范一致、供 launcher 挂载):在 **Prefabs** 里建文件夹 `Pages`,把 `DemoPage` 拖进去(或重建后迁移内容)。

DemoPage 根(Empty Node 2D 或现有根):**Layout Width=1920、Layout Height=900**(这是安全内容区尺寸;顶部 80/底部 100 的安全边距由 launcher 摆放时保证)。

### 6.2 页内结构

```text
DemoPage (根,1920×900)
├── TopBar (Stack Layout 2D,横向,1920×96)
│   ├── TitleText (Text Block 2D ← 之后绑 {##Template/Demo.Title})
│   ├── BtnPageA / BtnPageB (demo `Button` 实例,子页切换)
│   └── (日/夜、中/EN 切换在 launcher 顶栏做,见 §9)
├── PageA (Grid Layout 2D,1920×804) ← 数据绑定八卡(§7)
└── PageB (Grid Layout 2D,1920×804) ← 交互与视觉八卡(§10)
```

搭建步骤:

1. 在 DemoPage 根下 Alt+右键 → **Stack Layout 2D**,命名 `TopBar`:1920×96,Direction=Horizontal。
2. 现有的 Grid Layout 2D 重命名为 `PageA`,Properties 设 **Column Definitions / Row Definitions** 为 4 列 × 2 行(每列 472、每行 396 左右,含间距;Grid 放在 Y=96 处,1920×804)。
3. 复制 `PageA` 得到 `PageB`(右键 → Copy/Paste),先清空其子节点。

### 6.3 子页切换(State Manager,已核实的官方流程)

1. **Node Tree** 选中 **DemoPage 根** → **State Tools** 点 **Create State Manager**(窗口进入橙色 Edit 模式)。
2. 点 **Create State** 两次,双击重命名为 `ShowA`、`ShowB`。
3. 点选 `ShowA` 状态:把 `PageA` 的 **Visible**=true、`PageB` 的 **Visible**=false,保存该状态外观;点选 `ShowB` 反过来设一遍。
4. (可选转场)在 State Tools 点 **Any -> Any** 过渡 → **State Transition Settings** 里设 Duration=200ms(对齐规范档位)。
5. 点 **Edit State Manager** 退出编辑模式。
6. 给 TopBar 的两个按钮接切换动作:
   1. 从 **Prefabs** 把 `Button` 拖两个到 `TopBar` 下,实例上分别设 `Button.Label` = `Page A` / `Page B`。
   2. 选中 `BtnPageA` 实例 → **Node Components** 按住 **Alt 右键 Triggers** → **Message Trigger > Button > Click**。
   3. Alt+右键该 **Button: Click** 触发器 → **Dispatch Message Action > State Manager > Go to State**,动作里设 **State** = `ShowA`、**Target Item** = DemoPage 根。
   4. `BtnPageB` 同理指向 `ShowB`。
7. **验收**:Preview 里点两个按钮,两页互切,带 200ms 过渡。

> 这一张"骨架"本身就覆盖了三个官方特性:State Manager 状态切换、状态过渡动画、Button Click 触发器 + Go to State 动作。

---

## 7. 子页 A:数据绑定八卡 🔨(逐卡步骤)

先建齐 DemoPage 的暴露属性(demo 现有 4 个 ✅,补 4 个):

| 属性(Property Types 里建/核对) | 类型 | 默认值 | 状态 |
|------|------|--------|------|
| `Demo.Title` | String | `Demo` | ✅ 已有 |
| `Demo.GaugeValue` | Float | 62 | ✅ 已有 |
| `Demo.ToggleOn` | Int(0/1) | 0 | ✅ 已有(注意类型应为 Int,对应 Toggle State) |
| `Demo.SliderValue` | Int | 30 | ✅ 已有 |
| `Demo.GaugeValid` | Bool | true | 🔨 新建 |
| `Demo.AccentColor` | Color | #1E6BFF | 🔨 新建 |
| `Demo.StatusEnum` | Int | 1 | 🔨 新建 |
| `Demo.ActivePage` | Int | 0 | 🔨 可选(若想让 launcher 控制子页) |

建法:`Library > Property Types` Alt+右键 → **Property Type**,填 Name/Data Type/Default Value;然后**选中 DemoPage 根 → Properties → + Add** 把这些属性逐个加到根节点上(加上才能被外部赋值/被 `##Template` 引用)。

**每张卡的通用三步**(以下不再重复):

1. `PageA` 下放一个 **Card 实例**(从 Prefabs 拖 `Card` 进 Grid,或复用已有 7 个实例,补齐到 8 个)。
2. **展开** Card 实例 → 找到内部 `Content`(Stack Layout 2D)→ 内容一律 Alt+右键加在 **Content 下**(先放一个 `LabelText` 实例当卡片小标题,设占位文字)。
3. 组件属性绑定到 `{##Template/Demo.Xxx}`:选中组件实例 → **+ Add Binding** → Property 选组件的暴露属性 → Expression 填 `{##Template/Demo.Xxx}` → Save。

| 卡 | Content 下放 | 绑定/逻辑 |
|----|--------------|-----------|
| **卡1 读·进度** | LabelText(`进度`)+ `ProgressBar` 实例 | `ProgressBar.Value` ← `{##Template/Demo.GaugeValue}` |
| **卡2 读·文本** | LabelText(`文本`)+ LabelText | 第二个 LabelText 的 `LabelText.Text` ← `{##Template/Demo.Title}` |
| **卡3 写·开关** | LabelText(`开关`)+ `ToggleSwitch` 实例 | 读:`ToggleSwitch.State` ← `{##Template/Demo.ToggleOn}`;写:同一实例再加一条绑定,**Binding Mode=To source**,Property=`ToggleSwitch.State`,**Push Target**=DemoPage 根的 `Demo.ToggleOn`。若读写绑定互相打架(点击被读绑定覆盖),删掉读绑定改用 **Binding Mode=Two way**(官方支持),Source=`{##Template/Demo.ToggleOn}` |
| **卡4 写·滑块** | LabelText(`滑块`)+ `Slider` 实例 | 同卡3 手法:读 `{##Template/Demo.SliderValue}` + To-Source 回 `Demo.SliderValue`(或 Two way) |
| **卡5 写·颜色** | LabelText(`颜色`)+ Rectangle 2D 色块 160×160 | 色块 **+ Add Binding**:Property=Background Brush 的 **Brush Color**(在 Binding Editor 用 **Property Field** 选 Color 字段),Expression=`{##Template/Demo.AccentColor}` |
| **卡6 枚举·状态** | LabelText(`状态`)+ `StatusIcon` 实例 | `StatusIcon.Status` ← `{##Template/Demo.StatusEnum}`(0–4 五色切换,内部 State Manager 已做) |
| **卡7 图片** | LabelText(`图片`)+ `ImageBox` 实例 | 设计期直接换 `ImageBox.Image` 占位图;URI 链路运行时联调(§5.6 说明) |
| **卡8 列表** | LabelText(`列表`)+ **Grid List Box 2D**(Alt+右键 Content → Grid List Box 2D,400×480) | ① **Item Template** 属性设为 demo 的 `ListItem`;② 列表数据在 **launcher 侧**绑(数据源 `Demo/menu` → 拖到 **Items Source**,见 §8);③ 选中列表 → Node Components → Alt+右键 Triggers → **Message Trigger > List Box > Item Selected** → 其下加 **Write Log** 动作(输出选中项,演示选中事件) |
| **故障态(卡1 加强)** | 在卡1 的 Content 里再放一个 LabelText,Text 固定 `--`,Foreground = `<Resource ID>` `Color/Error` | 给它加绑定:Property=**Visible**,Expression=`!{##Template/Demo.GaugeValid}`;再给 ProgressBar 实例加绑定 Property=Visible,Expression=`{##Template/Demo.GaugeValid}` —— Valid=false 时进度隐藏、`--` 变红显示 |

**独立验收**(不接 launcher 就能测):选中 Node Tree 里挂 DemoPage 的实例(demo 自己的 Screen/RootPage 下放一个 Prefab View 指向 DemoPage),在实例 Properties 上改 `Demo.GaugeValue`、`Demo.StatusEnum`、`Demo.GaugeValid` 等值,Preview 应实时响应。

最后:右键 `Pages/DemoPage` → **Make Public**;`File > Export > Export KZB`。

---

## 8. launcher:挂载 DemoView 与数据连线 🔨

打开 launcher(已引用 demo ✅)。

### 8.1 挂载

1. Node Tree 在内容区(RootPage 下)Alt+右键 → **Prefab View**(2D),命名 `DemoView`。
2. Properties 里 **Prefab Template** = `kzb://demo/Prefabs/Pages/DemoPage`(demo 必须已 Make Public 并保存)。
3. 摆放:X=0、**Y=80**、宽 1920、高 900(顶部让出 80 状态栏;底部 100 导航栏自然空出)。

### 8.2 连线(逐条,读=拖拽,写=To-Source)

选中 `DemoView`,它的 Properties 里会出现 demo 暴露的 `Demo.*` 属性(frequently used 区)。

**读(6 条,直接拖)**:Data Sources 窗口里把数据对象**拖到对应属性上**:

| 数据对象 | → DemoView 属性 |
|----------|----------------|
| `Demo/titleText` | `Demo.Title`(或改用本地化:删除该绑定,+ Add Binding,Expression=`string(acquire("demo.title"))`,演示 §3.5 链路) |
| `Demo/gaugeValue` | `Demo.GaugeValue` |
| `Demo/gaugeValid` | `Demo.GaugeValid` |
| `Demo/statusEnum` | `Demo.StatusEnum` |
| `Demo/sliderValue` | `Demo.SliderValue` |
| `Demo/toggleOn` | `Demo.ToggleOn` —— bool→Int 需表达式:改用 + Add Binding,Expression=`{DataContext.Demo.toggleOn} ? 1 : 0`(把数据对象拖进 Expression 生成引用后再套三元) |

**写(3 条,To-Source)**:在 `DemoView` 上逐条 **+ Add Binding**:

| Property(监听) | Push Target | Expression |
|------------------|-------------|------------|
| `Demo.ToggleOn` | 数据源 `Demo/toggleOn` | `{@./Demo.ToggleOn} != 0`(Int→bool) |
| `Demo.SliderValue` | 数据源 `Demo/sliderValue` | `{@./Demo.SliderValue}` |
| `Demo.AccentColor` | 数据源 `Demo/accentColor` | 颜色→字符串按项目约定转换 |

**列表**:选中 demo 里那张卡 8 的 Grid List Box(在 DemoView 下展开实例树),把 `Demo/menu` 拖到它的 **Items Source**;再打开 demo 的 `ListItem` 模板,把 `Title` 的 Text 绑 `{DataContext.title}`、`Icon` 留占位(列表行的 Data Context 自动指向行数据)。

### 8.3 验收

Preview 里:改 `assets/datasource.xml` 里 `Demo` 组的默认值并保存 → Data Sources 面板点更新 → 卡 1/2/6 应变化;点 demo 里的开关/滑块 → Data Sources 面板里悬停 `toggleOn`/`sliderValue` 应看到值被写回。

---

## 9. launcher 顶栏:时间 / 日夜 / 中英 🔨

1. **时间**:顶栏放 Text Block 2D,从 Data Sources 把 `System/timeText` 拖到它的 **Text**。
2. **日/夜切换**(官方 Theme: Activate Theme 动作):
   1. 顶栏放一个 demo `Button` 实例(`Button.Label`=`日/夜`)。
   2. Node Components → Alt+右键 Triggers → **Message Trigger > Button > Click**。
   3. Alt+右键该触发器 → **Theme 动作 > Activate Theme**,选 `AppTheme` 的 `Night`。
   4. 再放一个按钮指向 `Day`(先用两个按钮,最稳;想做单键轮换再用 Toggle Button + 两条带 Condition 的动作)。
3. **中/EN 切换**:两个按钮,各接 **Set Property** 动作:Target Item=**Screen**,Target Property=**Locale**,Fixed Value 分别选 `zh-CN` 与 `en`(§3.4 详细步骤)。
4. **验收**:点日/夜按钮,凡走 `Color/*` resource ID 的颜色全部切换;点中/EN,凡经 `acquire()` 的文案切换。

---

## 10. 子页 B:交互与视觉八卡 🔨(逐卡步骤)

每张卡在 **DemoPage 模板**里用 Card 的 **Prefab View 2D** 实例组合;要往卡里塞演示内容,请在 **Prefabs 里编辑 Card 模板**的 `Content` 槽(§5.2),或在页面层用 expose/`##Template` 驱动子 Prefab——**不要**指望在 Node Tree 展开 Prefab View 往里拖节点。

### 卡 9:触发器与动作(Trigger / Action / 消息)

1. Content 下放 LabelText(`触发器`)+ 一个 demo `Button` 实例(`Button.Label`=`点我`)+ 一个 Rectangle 2D `Target`(120×120,Background Brush=`<Resource ID>` `Color/Divider`)。
2. 选中 Button 实例 → Node Components → Alt+右键 Triggers → **Message Trigger > Button > Click**。
3. 给该触发器加两个动作(Alt+右键触发器逐个加):
   - **Set Property**:Target Item=`Target` 色块,Target Property=**Opacity**,Value From=Fixed value,Fixed Value=0.3(每次点击半透明,肉眼可见)。
   - **Write Log**:Message 填 `demo card9 clicked`(打开 **Log** 窗口看输出——团队以后排查交互就靠它)。
4. (消息冒泡演示)把同样的 **Button: Click** 触发器加在**卡 9 的 Card 实例**上(父节点),动作用 Write Log 输出 `bubbled to card`。Preview 点按钮,两条日志都出现;在按钮那条触发器里勾选 **Set Message Handled** 后,父节点不再收到——这就是官方的 tunneling/bubbling 机制。

### 卡 10:动画(关键帧 + 平滑插值)

**A. 关键帧动画(Animation Clip + Animation Player)**

1. Content 下放 Rectangle 2D `Ball`(64×64,`Color/Accent`)。
2. `Library` Alt+右键 **Animations > Animation Clips** → 新建 **Animation Clip**,双击打开 **Animation Clip Editor**。
3. **Current Time** 设 0 → Node Tree 选中 `Ball` → 从 **Properties 把 Render Transformation 属性拖进 Animation Clip Editor**(生成第 0 帧)。
4. Current Time 设 0.4 → Properties 里把 `Ball` 的 Render Transformation Translation X 改到 240 → 再拖一次 Render Transformation 进编辑器(生成第二帧)。
5. 清理:右键该 Clip → **Delete Animations with One or Zero Effective Keyframes**;选中 Translation X 的两帧,左侧 **Easing** 设 `Smooth Step`。
6. 选中 `Ball` → **Node Components** Alt+右键 **Animation** → **Animation Player**:**Target Animation Timeline**=该 Clip,**Autoplay Enabled**=先开着验证,验证后关掉。
7. 用触发器播放:卡内再放一个 Button(`播放`),其 **Button: Click** 触发器下 Alt+右键 → **Dispatch Message Action > Animation Player > Start**,**Target Item**=`Ball`。(Pause/Resume/Stop 动作同一菜单,可各加一个按钮体验。)

**B. 平滑插值(Property Target Interpolator,仪表指针标准做法)**

1. 卡内放一个 `ProgressBar` 实例 + 一个 Button(`+20`)。
2. 选中 ProgressBar 实例 → **Node Components** Alt+右键 **Animation** → **Property Target Interpolator**,对话框里 **Interpolated Property Type** 选 `ProgressBar.Value`(Float,可直接插值)。
3. 在 Interpolator 上设 **Acceleration=5、Drag=2**。
4. Button 的 Click 触发器 → **Set Property**:Target=ProgressBar 实例,Property=`ProgressBar.Value`,Fixed Value=90。
5. **验收**:点按钮,进度不是跳变而是平滑逼近 90(弹簧-阻尼模型,永不超调)。

### 卡 11:手势(长按)

> 官方限制:**Long-Press Manipulator 触发器不能加在 Button/Toggle Button 上**(它们自带输入处理),要加在普通可命中节点上。

1. Content 下放 Rectangle 2D `Pad`(200×120,`Color/Divider`),Properties 确认 **Hit Testable** 开启。
2. 选中 `Pad` → Node Components → Alt+右键 Triggers → **Message Trigger > Long Press > Long Press**(默认按住 500ms 触发,可在 Long-Press Manipulator 的 Long Press Duration 上改)。
3. 触发器下加 **Set Property** 动作:把 `Pad` 的 Background Brush 换成 `Color/Warning`(或 Write Log)。
4. **验收**:短点无反应,按住半秒变色——和 Button: Click 形成对照(Button 的长按对应 **Button: Long Press** 触发器 + Hold Interval 属性,可在卡 9 的按钮上顺手试)。

### 卡 12:滚动(Scroll View)

1. Content 下 Alt+右键 → **Scroll View 2D**,命名 `Scroller`:400×240。
2. 其下 Alt+右键 → **Stack Layout 2D**(竖排),放 6 个 LabelText 实例(`行1`…`行6`,各高 64,总高超出 240 才有得滚)。
3. 选中 `Scroller` → Node Components → Alt+右键 Triggers → **Message Trigger > Scroll View > Scroll Started**(和 **Scroll Finished** 各一条),各加一条 **Write Log**(演示滚动事件)。
4. **验收**:Preview 里拖动列表上下滚,松手有惯性,Log 出现开始/结束。

### 卡 13:Data Trigger(数据驱动,与绑定法对照)

> 官方:**Data Trigger** 监听属性/数据源值变化,配 **Apply Property Action** 施加属性值——和"绑定"不同,它是**事件式**的,适合"值到了某条件才动作"。

1. Content 下放 Rectangle 2D `Alarm`(120×120,`Color/Success`)。
2. 选中 `Alarm` → Node Components → Alt+右键 Triggers → **Data Trigger**。
3. Data Trigger 里:监听源选 DemoPage 的 `Demo.StatusEnum`(`##Template` 场景下若选不到,退一步在 launcher 侧对数据源字段建同样的 Data Trigger,效果一致);**Condition** 设 `== 4`(故障)。
4. 其下加 **Apply Property Action**:Target=`Alarm`,Property=Background Brush,值=`Color/Error`。
5. **验收**:把 `Demo.StatusEnum`(或数据源 `Demo/statusEnum`)改成 4,色块变红;改回 1 恢复(Apply 型动作在条件不满足时自动撤销施加值——这正是它与 Set Property 的区别)。

### 卡 14:2D 特效(Shadow / Blur / 毛玻璃)

1. **卡片投影(推荐直接给 Card 组件加,所有卡片同时生效)**:在 **demo** 工程 `Library` Alt+右键 **Effects > 2D Effects** → **Shadow Effect 2D**;从 Library 把它**拖到 Prefabs 里 Card 的 `Background` 节点上**;选中该 Effect 调 **Shadow Blur Radius**(默认 8,试 16)。注意:2D 特效不参与布局计算,卡片四周要留够 Margin 否则阴影被裁。
2. **本卡演示模糊**:demo 里 Content 下放一个 `ImageBox` 实例;`Library` Alt+右键 **Effects > 2D Effects** → **Blur Effect 2D**,拖到该实例上;选中 Effect 调 **Blur Radius**。
3. (进阶,可选)**Effect Stack 2D** 毛玻璃:Library 里创建 **Effect Stack 2D**,在其内 Alt+右键分别加 Blur Effect 2D 与 Shadow Effect 2D,拖到目标节点——官方"frosted glass"做法。
4. **验收**:Preview 中肉眼可见投影/模糊;调属性实时变。

### 卡 15:3D 视口(2D/3D 混合最小示例)

1. Content 下 Alt+右键 → **Viewport 2D**,命名 `Mini3D`:400×260。
2. 在 `Mini3D` 下 Alt+右键 → **Scene**。检查 Scene 内是否自动带 **Camera** 和光源;缺什么就 Alt+右键 Scene 补:**Camera**、**Directional Light**。
3. Scene 下 Alt+右键 → 选一个内置几何体(**Sphere / Box / Plane** 均可),命名 `Model`,调整位置到相机可见(Translation Z 拉开距离)。
4. 卡内放一个 `Slider` 实例,给 `Model` 加绑定:**+ Add Binding** → Property=**Render Transformation**,**Property Field**=Rotation 的 Y 分量 → Expression:

```text
{@../../Slider/Slider.Value} / 100.0 * 6.28
```

   (相对路径按你的实际节点层级用 Binding Editor 的拾取器选,别手拼。)
5. **验收**:拖滑块,3D 模型绕 Y 轴旋转——一张卡覆盖 Viewport/Scene/Camera/Light/3D 变换绑定五个概念。

### 卡 16:动态换 Prefab(Prefab View 热切换)

> 官方:**Prefab View 持续监听 Prefab Template 属性**,值一变就替换实例——这是动态加载/换装的基础。

1. 在 demo 的 **Prefabs** 里做两个小内容 Prefab:`SwapA`(Rectangle 2D,`Color/Success`,120×120)、`SwapB`(Rectangle 2D,`Color/Warning`,120×120)。
2. Content 下 Alt+右键 → **Prefab View**(2D),命名 `SwapHost`,**Prefab Template**=`SwapA`。
3. 放两个 Button(`A`/`B`),Click 触发器各接 **Set Property**:Target=`SwapHost`,Target Property=**Prefab Template**,Fixed Value 分别选 `SwapA`/`SwapB`。
4. **验收**:点 A/B,内容热替换,不重启 Preview。

---

## 11. Make Public 与导出顺序

1. common:仅资源(Brush/Theme/Font)有变更时 Export KZB。
2. demo:组件 Prefab + `Pages/DemoPage` 全部 **Make Public** → Export KZB。
3. launcher:Export KZB。
4. 顺序永远是 **common → demo(各模块)→ launcher**;运行时 Android 侧**先加载 `common.kzb`** 再加载模块 kzb。业务模块**不**依赖 `demo.kzb`,只依赖 `common.kzb` + 自身 kzb。

---

## 12. 可选扩展(不在必做清单,官方入口备查)

| 主题 | 说明 | 官方文档入口(3.9.15) |
|------|------|------------------------|
| Activity 导航 | Screen 级导航体系(Exclusive/Parallel/Data-Driven Host),在 **launcher** 用 **Activity Browser** 创建(根 Host 自动挂 Screen 下),支持虚拟化与转场;适合 launcher 重构导航时引入 | Working with… > Activities |
| Text Box 输入 | Text Box 2D 单行输入 + IME + Maximum Text Length | Working with… > Text nodes > Using the Text Box nodes |
| 焦点/按键导航 | Focusable、焦点链,配硬键/旋钮 | Working with… > Focus |
| Trajectory Layout | 弧形/路径布局菜单 | Working with… > Trajectories |
| Instantiator | 一份内容多处镜像 | Working with… > Instantiator node |
| 性能分析 | Preview 的 Analyze 工具、Performance HUD | Working with… > Performance profiling |

---

## 13. 常见问题(v2 更新)

| 现象 | 处理 |
|------|------|
| 数据源 Update 后没字段 | File 路径不对(§4.3 用 `../../../assets/datasource.xml`);插件未 Enabled |
| 卡片里加了内容看不见 | ① Card 结构不对(§5.2);② 内容没加在 `Content` 下;③ `Background` 挡住了 `Content`(顺序);④ 2D 节点没设 Layout Width/Height(无尺寸=0×0) |
| 用主题色的文字在 demo 预览里不显示 | demo 预览需激活主题:Dictionaries → Locales and Themes 选 Day/Night;排查时可临时把 Foreground 换成具体 Brush |
| 切主题不变色 | 颜色写死了,改走 `<Resource ID>` `Color/*`(§2.3) |
| 切语言文字不变 | 文本没经 resource ID/`acquire()`;或 locale 名不一致(zh-CN/en) |
| 开关点了被弹回 | 读写绑定打架:删读绑定改 **Two way**,或只留 To-Source(§7 卡3) |
| 长按触发器加不上按钮 | 官方限制:Long-Press Manipulator 不能用于 Button/Toggle Button;普通节点才行(§10 卡11),按钮用 **Button: Long Press** |
| 动画不播 | Animation Player 的 Target Animation Timeline 没指到 Clip;或 Autoplay 关了又没接 Start 动作 |
| 阴影被裁掉 | 2D 特效不参与布局,给节点加 Margin(§10 卡14) |
| demo 里 Data Trigger 选不到数据源 | 正常(数据源在 launcher):监听 `##Template` 属性,或把该 Data Trigger 建在 launcher 侧(§10 卡13) |
| 改了没进 git | Studio 里 **Ctrl+S** 保存(autosave 不算);提交前关 Studio 再 pull/reset |
