# 多语言与多主题 — 设计架构方案

> 依据 **Kanzi 3.9.15 官方文档** + 本仓库**当前实际资产**给出的落地架构。原则速查见 [localization-and-theme.md](../localization-and-theme.md);Trigger/Action 白名单见 [trigger-guide.md](trigger-guide.md)。
>
> 本文所有"现状"均核对自工程文件(`launcher.kzproj` / `common.kzproj` / `demo.kzproj` / `datasource.xml`),所有机制均标注官方出处,无推测性设计。

## 1. 结论速览

| 关注点 | 结论 |
|--------|------|
| 谁决定语言/主题 | **Android 侧**,经数据契约 `System/locale`(string)、`System/theme`(int)下发——两个字段**契约里已预留** |
| 谁执行切换 | **只有 launcher**(Screen 级资源,与 trigger 白名单"Activate Theme / Set Locale 只允许 launcher 用"一致) |
| token/字体唯一源 | **common**(现状已是:`AppTheme` Theme Group + `LocaleStyle` 字体样式) |
| 业务模块感知什么 | **零感知**:颜色用 `<Resource ID>` token、字体用 `LocaleStyle`、文案用本地化 key;切换时自动刷新 |
| 3D 场景日夜 | 不走 UI 主题,**同一个 `System/theme` 字段**由 environment/car 模块用 State Manager / Data Trigger 自行消费 |

## 2. 官方机制依据(Kanzi 3.9.15)

### 2.1 本地化(Localization)

出处:[Localization](https://docs.kanzi.com/3.9.15/en/working-with/localization/localization.html)、[Using locales](https://docs.kanzi.com/3.9.15/en/working-with/localization/using-locales.html)、[Localizing applications](https://docs.kanzi.com/3.9.15/en/working-with/localization/localizing-applications.html)

- **Locale 是资源选择 ID**:Kanzi 用 locale 名(如 `zh-CN`)选择资源;可本地化的不只文本,还有字体、贴图、Style、材质等。
- **Localization Table + resource ID 间接寻址**:节点不直接持有文案/资源,持有 resource ID;表记录"哪个 locale 用哪个资源"。**未定义的 locale 回退到默认 locale**(表中 `neutral` 列)。
- **切换语言 = 改 Screen 节点的 `Locale` 属性**:官方明确"To set a locale using a control, use any trigger and the **Set Property** action to set the value of the **Locale** property in the **Screen** node";侦听变化用 On Property Change trigger。
- **PO 文件**可导入/导出,导入时自动补建 locale——译文可在外部统一管理。
- **Locale pack**:可把某 locale 的资源拆成独立 kzb,导出到 `<BinaryExportDirectory>/Locale_packs/`(目录名 Studio 固定),运行时用 Engine API 按需加载——主 kzb 不含这些资源,体积减小。

### 2.2 主题(Themes)

出处:[Using Themes](https://docs.kanzi.com/3.9.15/en/working-with/themes/using-themes.html)、[Theming applications](https://docs.kanzi.com/3.9.15/en/working-with/themes/theming-applications.html)、[Setting the Screen node](https://docs.kanzi.com/3.9.15/en/working-with/screens/screens.html)

- **Theme Group = 一组 Theme**;同一时刻每个 Theme Group 只有一个 Theme 激活;某 resource ID 在当前 Theme 未定义时**回退到该组默认值**(`DefaultValues`)。
- **可以有多个 Theme Group**(官方示例:一组管车型、一组管界面风格)——为将来"车型主题 × 日夜主题"留了正交扩展位。
- **切换主题的三种官方方式**:
  1. Studio 设计期:Library > Themes 的 **Selected Theme** / Dictionaries 窗口 **Locales and Themes**(仅预览);
  2. Trigger + **Activate Theme** action;
  3. C++:`screen->activateTheme("kzb://<project>/Themes/<ThemeGroup>/<Theme>")`——URL 含工程名,**跨 kzb 寻址是官方形态**。
- Locale 与 Theme 都在 **Screen 节点**上解析生效 → 都是**应用级**开关,归含 Screen 的 launcher 管。

## 3. 项目现状盘点(2026-07 核对)

### 3.1 已有资产

| 位置 | 资产 | 明细 |
|------|------|------|
| `IVI/assets/datasource.xml` | **契约字段已预留** | `System/locale`(string,默认 `zh-CN`,注释写 "zh-CN / en")、`System/theme`(int,0 Day / 1 Night) |
| `IVI/common/common.kzproj` | **Localization Table** | locale 列:`neutral` / `en-US` / `zh-CN`;key:`LocaleStyle`(按语言切字体的 Named Style) |
| | **Theme Group `AppTheme`** | Theme:`DefaultValues` / `Day` / `Night`;token:`Color/Accent`、`Color/Divider`、`Color/Error`、`Color/Success`、`Color/Surface`、`Color/TextPrimary`、`Color/TextSecondary`、`Color/Warning`(共 8 个) |
| | **字体** | `NotoSansCJKsc` + `LocaleStyle` / `LocaleStyle_zh` Named Style |
| `IVI/launcher/Tool_project/launcher.kzproj` | Screen | `Locale` 属性**写死 `zh-CN`** |
| | Localization Table | locale 列仅 `neutral` / `zh-CN`;key:`LocaleStyle`(neutral/zh 列都指向 `kzb://common/Styles/LocaleStyle_zh`)、`title`(launcher 自己的文案 key,已验证"文案表建在节点所在工程"可行) |
| | `System.theme` 消费 | 仅两处:Env 节点上一条 **disabled** 的绑定 + 一个调试 Text Block;**没有接任何 Theme 切换** |
| `IVI/demo/demo.kzproj` | token 消费先例 | 节点实际引用 `Color/Accent` / `Color/Surface` / `Color/TextPrimary` resource ID 和 `LocaleStyle` —— **跨工程消费 common token 已验证可行** |
| `IVI/car*` `IVI/environment` | 无 | 三个业务模块均无本地化/主题资产 |

### 3.2 现存问题(设计要解决的)

| # | 问题 | 影响 |
|---|------|------|
| G1 | **locale 值不统一**:契约注释 `en`,common 表列名 `en-US` | 若 Android 下发 `en`,Kanzi 表里没有 `en` 列 → 全部回退默认 locale,英文不生效 |
| G2 | launcher 表**缺 `en-US` 列**,`LocaleStyle` 两列都指 `_zh` | launcher 自己的文案/字体切不了英文 |
| G3 | `Screen.Locale` 写死、`System/locale` **无任何消费者** | 语言切换链路完全未通 |
| G4 | `System/theme` 无 Theme 消费者(仅 disabled Env 绑定) | 主题切换链路完全未通 |
| G5 | `AppTheme` 有一个杂散 key `a`;token 缺命名规范里的 `Color/Background` 与 `Font/* Size/* Motion/*` | 清理 + 补齐 |
| G6 | 业务模块(car_setting 等)未接 token/LocaleStyle/文案 key | 按规范接入 |

## 4. 目标架构

```mermaid
flowchart TB
    android["Android 渲染侧<br/>系统设置(语言/深色模式)"]
    ds["DroidDataSource(契约)<br/>System/locale = 'zh-CN' | 'en-US'<br/>System/theme = 0 Day | 1 Night"]

    subgraph launcher["launcher(唯一切换执行点,Screen 所在工程)"]
        lb1["绑定:Screen.Locale ← System/locale"]
        lb2["RootPage 属性 Launcher.ThemeRequest(int)<br/>← 绑定 System/theme"]
        tr["On Property Change Trigger ×2<br/>Condition ==0 → Activate Theme Day<br/>Condition ==1 → Activate Theme Night"]
        lb2 --> tr
    end

    subgraph common["common(唯一 token / 字体源)"]
        theme["AppTheme Theme Group<br/>Color/* token(Day/Night/DefaultValues)"]
        style["LocaleStyle(按 locale 切字体)<br/>+ NotoSansCJKsc"]
    end

    subgraph modules["业务模块(car_setting / car / environment / demo)"]
        ui["UI 节点:颜色=<Resource ID> token<br/>字体=LocaleStyle,文案=本模块表的 key"]
        env3d["3D 昼夜:State Manager / Data Trigger<br/>直接消费 System/theme"]
    end

    android --> ds
    ds --> lb1
    ds --> lb2
    ds --> env3d
    tr -->|"Screen 级生效"| theme
    lb1 -->|"Screen 级生效"| style
    theme --> ui
    style --> ui
```

要点:**数据驱动、单点执行、来源分离**——切换指令来自数据契约(与车辆真实数据同通道,Preview 里改 `datasource.xml` 默认值即可模拟);执行只在 launcher;样式值只在 common;模块只消费不切换。

## 5. 设计决策

### D1 locale 命名统一为 `zh-CN` / `en-US`(修 G1/G2)

Kanzi 的 locale 名就是字符串 ID,契约值必须与表列名**逐字符一致**。common 表已用 `en-US`,改动最小的统一方向:

- `datasource.xml`:`System/locale` 注释改为 `zh-CN / en-US`(值本身是 string,无结构变更,Android 侧同步确认);
- launcher 表补 `en-US` 列;`LocaleStyle` 行:`zh-CN`→`LocaleStyle_zh`,`en-US`→`LocaleStyle`(拉丁),`neutral`(默认回退)→`LocaleStyle_zh`(产品默认中文,与 Screen 默认 locale 一致);
- 新增语言 = 契约枚举 + 各表加列,**不改任何节点**。

### D2 token / 字体唯一源 = common(维持现状并补齐,修 G5)

- 保持 `AppTheme` 在 common(demo 已验证跨工程消费 token 可行);清理杂散 key `a`;
- 补 `Color/Background`;`Font/Title、Font/Body、Font/Caption`、`Size/*`、`Motion/*` 按 [naming-conventions.md](naming-conventions.md) 的 token 清单**用到即建**,不预建空 token;
- 模块规则不变:**只引用 token,禁止写死颜色/字号**(反模式见 §8)。

### D3 主题切换链路(修 G4)— Studio 内实现,零 C++

契约 `System/theme` 是 **int**,而激活主题是 **Action** 不是属性,因此不能直接绑定,用"绑定 + On Property Change"桥接:

1. RootPage 加自定义 int 属性 `Launcher.ThemeRequest`,**OneWay 绑定** `{DataContext.DroidDataSource.System.theme}`;
2. RootPage 挂两条 **On Property Change**(监视 `Launcher.ThemeRequest`)Trigger:
   - Condition `ThemeRequest == 0` → **Activate Theme** `AppTheme/Day`
   - Condition `ThemeRequest == 1` → **Activate Theme** `AppTheme/Night`
3. 启动初值:`AppTheme` 的 Selected Theme 设为与契约默认值(`theme=1` Night)一致。

> **验证点 V1**:Studio 的 Activate Theme action 能否直接选中**引用工程(common)**的 Theme Group。若不能:把 Theme Group 移到 launcher 定义(token resource ID 名不变,各 Theme 列仍指向 common 的 public brush)——旧文档"在含 Screen 的工程统一定义/合并主题"即此预案;模块侧引用的是 token ID,**不受影响**。C++ `activateTheme("kzb://common/Themes/AppTheme/Night")` 是第二兜底(URL 跨工程寻址是官方形态,car 模块已有 code-behind 先例)。

### D4 语言切换链路(修 G3)

首选:**Screen 的 `Locale` 属性直接 OneWay 绑定** `{DataContext.DroidDataSource.System.locale}`(Locale 是普通属性,官方允许用 Set Property 改它,绑定是等价的声明式写法;Screen/RootPage 已设 Data Context)。

> **验证点 V2**:若 Screen 节点上对该属性建绑定在 Studio 中不可用,退回官方字面做法:RootPage 加 `Launcher.LocaleRequest`(string)绑定契约值,On Property Change Trigger + **Set Property** action 写 `Screen.Locale`。

### D5 文案归属:key 建在**节点所在工程**的表里

- launcher 已有先例(key `title` 在 launcher 表);每个有文案的模块工程自建 Localization Table,**locale 列名三处统一**(D1);
- key 命名 `<模块>.<语义>`(`charging.title`、`common.ok`),交付后冻结只追加;
- **译文单一来源 = PO 文件**,放 `Shared/Resources/localization/<locale>.po`(符合 Shared/Resources 的"非 kzproj 原始资产"定位),各工程表从 PO 导入——官方支持导入时自动建 locale,保证各工程列名一致;
- 模块内**禁止 TextBlock 写死文字**。

> **验证点 V3**:模块 kzb 的 prefab 实例化到 launcher Screen 下后,切 `Screen.Locale` 是否会刷新该模块表里的文案(P2 用 car_setting 首个页面验证)。若跨 kzb 不生效,降级方案 = 旧文档 §1.1 的 **DataLayer 字符串中转**(launcher 集中解析 `string(acquire('key'))`,To-Source 写 common DataLayer,模块只绑普通 string)——架构上模块同样零感知,只是文案表集中到 launcher。

### D6 3D 场景日夜与 UI 主题解耦

Env 节点上那条 disabled 的 `System.theme` 绑定表达的意图是对的:**3D 昼夜不走 AppTheme**(光照/天空盒/贴图不是 brush token),environment / car 模块直接消费 `System/theme` 数据字段,用 State Manager(状态机规范见 [state-machine-guide.md](state-machine-guide.md))切光照与背景。UI 主题和 3D 昼夜是**同一数据源字段的两个消费者**,天然同步、互不耦合。

### D7 分包与 OTA(远期,预留已就位)

- **Locale pack**:量产语言多于 2 种时,把非默认语言标记为 locale pack,导出产物在 `IVI/assets/Locale_packs/`(Studio 固定目录名;注意**不是**此前预留的 `IVI/assets/Localization/`,该目录改为存放 PO 之外的本地化中间产物或直接留给 Locale_packs 的部署副本),Android 侧用 Engine API 按 locale 加载;
- 需要进主 kzb 的资源加 **Is Used By Code** 属性(官方机制,防止被拆进 pack);
- **主题不支持分包**(theme 资源在主 kzb),车型级差异将来用第二个 Theme Group(§2.2 官方多组示例)或 `Shared/Resources/carmodel/` 资源变体解决。

## 6. 落地改造清单(分阶段)

| 阶段 | 内容 | 验收 |
|------|------|------|
| **P0 修不一致**(G1/G2/G5) | 契约注释 `en`→`en-US`(Android 同步);launcher 表补 `en-US` 列并修 `LocaleStyle` 三列指向;清理 AppTheme 杂 key `a`;补 `Color/Background` | Dictionaries 里切 `en-US`,launcher 的 `title` 与字体正确切换 |
| **P1 打通切换链路**(G3/G4,D3/D4) | Screen.Locale 绑定;`Launcher.ThemeRequest` + 双 Trigger + Activate Theme;核销验证点 **V1/V2** | 改 `datasource.xml` 里 `locale`/`theme` 默认值 → 重启 Preview,语言与 Day/Night 随之变;运行期由 Android 改值即时切换 |
| **P2 首个业务模块接入**(G6,D5/D6) | car_setting 页面:颜色全部改 token、文字挂 `LocaleStyle` + 本模块表 key;PO 流程跑通;核销 **V3**;environment 接 `System/theme` 状态机 | 切语言/主题,car_setting 页面与 3D 场景全量正确刷新,无写死残留 |
| **P3 分包/OTA**(D7,远期) | 非默认语言 locale pack 化;Android 侧加载 API 联调 | 主 kzb 体积下降,动态加载语言包成功 |

## 7. 风险与验证点汇总

| # | 风险 | 预案 |
|---|------|------|
| V1 | Activate Theme action 选不了 common 的 Theme Group | Theme Group 移 launcher(token ID 不变,模块无感);或 C++ `activateTheme` |
| V2 | Screen.Locale 属性不可绑定 | On Property Change + Set Property(官方字面做法) |
| V3 | 模块 kzb 文案表不随 Screen.Locale 刷新 | DataLayer 字符串中转(旧方案,模块仍零感知) |
| — | Android 下发值与表列名漂移 | 契约是唯一枚举源(D1);新增语言走"契约先行"流程,禁止 Studio 单方面加列 |

## 8. 反模式(沿用并强化)

- TextBlock 直接填中文/英文字面量;节点写死十六进制颜色/固定字号。
- 模块工程里放 Activate Theme / Set Locale(**只允许 launcher**,trigger 白名单已约定)。
- 切主题用改 Prefab 属性的方式伪装(必须走 Theme Group resource ID)。
- 漏译回退成 key 名/空串不报缺陷;用默认值掩盖 `locale`/`theme` 数据无效。
