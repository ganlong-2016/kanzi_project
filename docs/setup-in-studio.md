# 在 Kanzi Studio 中建工程操作手册

本手册指导团队在 `studio-projects/` 下逐个建立 `.kzproj`。**严格按顺序:先 `core` → 再 `shell` → 再各模块。**

> 不同 Kanzi 版本的菜单名称略有差异,以本团队所用版本为准;下文给出操作意图与对应位置。

---

## 0. 前置准备

- 安装与团队一致版本的 Kanzi Studio(版本号统一,避免工程文件不兼容)。
- 克隆本仓库,已有目录骨架 `studio-projects/Core`、`Shell`、`Module_*`、`_ModuleTemplate`。
- 通读:[架构](architecture.md)、[引用与依赖](project-references.md)、[命名规范](naming-conventions.md)、[导出](export-kzb.md)、[数据契约](data-source-contract.md)、[主题](theming.md)、[多语言](localization.md)。

---

## 1. 通用建工程步骤(每个工程都一样)

1. **New Project**,工程名用全小写规范名(`core` / `shell` / `launcher` / `charging` / `vehiclecontrol` / `interior`)。
2. **保存位置**:存到对应目录,使最终结构为
   `studio-projects/<目录>/Tool_project/<name>.kzproj`(Studio 会同时生成 `Application/`,已被 `.gitignore` 忽略,无需处理)。
3. **设置 kzb 导出输出路径**到仓库根的独立目录,例如 `out/<name>.kzb`(项目设置 / Binary 导出配置中),**不要依赖 `Application/` 下默认路径**。
4. **不要**在此工程编译 / 依赖 `Application/`(C++ 脚手架,本项目不用)。
5. 建完提交 `Tool_project/` 进 Git(`Application/` 自动忽略)。

> `_ModuleTemplate/` 不建工程,只是复制蓝本。

---

## 2. 建 `core`(共享资源,必须最先完成)

目录:`studio-projects/Core/`,工程名 `core`。

### 2.1 Resource Dictionaries(主题 token)
1. 建 `Resource Dictionaries/Base`:放与主题无关的 token —— `Font/Title|Body|Caption`、`Size/Radius*`、`Size/Spacing*`、`Motion/Duration*`。取值见 [`design-tokens/tokens.json`](../design-tokens/tokens.json) 的 `base`。
2. 建 `Resource Dictionaries/Theme_Day` 与 `Theme_Night`:各放全部 `Color/*` token,取值见 tokens.json 的 `themes.Day` / `themes.Night`。
3. 约定运行时通过切换激活的 Dictionary 实现日/夜切换。

### 2.2 Fonts
- 导入 `font_cjk`(中文,按用字子集化)与 `font_latin`(拉丁)。字号/字重通过 `Font/*` token 引用,不在节点写死。

### 2.3 Localization(中/英)
- 建字符串表,locale 列 `zh-CN`、`en`,按 [localization.md](localization.md) 的键表录入(`common.*`、`launcher.*`、`charging.*`、`vehicle_control.*`、`interior.*`)。

### 2.4 Prefabs/Components(通用组件库)
按需建以下组件 Prefab(对外属性清晰、引用 token、文本绑定 Localization):
`Button`、`ToggleSwitch`、`Card`、`ListItem`、`Popup`、`Toast`、`Slider`、`ProgressBar`、`StatusBar`。

### 2.5 Data Sources/VehicleData(stub)
- 按 [`contracts/vehicle-data.schema.json`](../contracts/vehicle-data.schema.json) 建分组与字段:`System` / `Charging` / `VehicleControl` / `Interior`。
- 字段类型映射:`bool→Bool`、`int/enum→Int`、`real→Real`、`string→String`、`list→List`。
- 用契约里的 `stub` 值作默认值,**含每个 `<signal>Valid` 字段**。

### 2.6 导出验证
- 导出 `out/core.kzb`,确认无报错。**core 完成前,其它工程不要开工。**

---

## 3. 建 `shell`(主工程)

目录:`studio-projects/Shell/`,工程名 `shell`。

1. New Project(同第 1 节),**添加对 `core` 的工程引用**(Library / Add Project Reference)。
2. 在 `Screens/` 建 Screen 根 + 视口。
3. 建 `Prefabs/Pages/LauncherShell`:状态栏 + 内容区 + 导航框架。
4. 实例化 core 的 `StatusBar`,绑定 `kzb://core/Data Sources/VehicleData/System`(时间/网络/蓝牙/车外温度)。
5. 放置**模块加载占位点**(内容区),实际模块由下游运行时加载 kzb 注入;**不在设计期硬连模块内部节点**。
6. 加全局入口:语言切换(切 locale)、主题切换(切 Day/Night Dictionary)。
7. 导出 `out/shell.kzb`(确保已基于最新 `core` 导出)。

---

## 4. 建各功能模块(launcher / charging / vehiclecontrol / interior)

每个模块步骤一致,以 `charging` 为例:

1. 参照 `_ModuleTemplate/README.md` 与对应模块目录 README。
2. New Project 到 `studio-projects/Module_Charging/`,工程名 `charging`,**添加对 `core` 的引用**。
3. 建根页面 `Prefabs/Pages/ChargingPage`(命名稳定,供下游加载)。
4. 用 core 的组件搭 UI;新建本模块的 `Prefabs/Widgets/*`(如 `SocRing`、`ChargeCurve`)。
5. **数据绑定**:绑定到 `kzb://core/Data Sources/VehicleData/Charging/*`;对每个 `<signal>Valid==false` 实现故障态(文案 `common.unavailable`、色 `Color/Error`)。
6. **文案**全部走 Localization 键;**样式**全部走主题 token;**不硬编码**。
7. 导出 `out/charging.kzb`。

其余模块(`launcher` / `vehiclecontrol` / `interior`)同理,分别绑定契约的 `System` / `VehicleControl` / `Interior` 分组。模块之间**不互相引用**。

---

## 5. 导出顺序与 CI

```text
1) out/core.kzb            # 先导
2) out/shell.kzb           # 依赖 core
3) out/launcher.kzb / charging.kzb / vehiclecontrol.kzb / interior.kzb   # 依赖 core,可并行
```

- 所有上层基于**同版本 core** 导出;core 改动后重导依赖它的全部 kzb。
- 推荐命令行导出纳入 CI(见 [export-kzb.md](export-kzb.md))。

---

## 6. 最小链路验证(全铺开前必须先过)

只用 `core + shell + charging` 验证:

- [ ] charging 能正确引用 core 的组件 / 主题 / Localization / 数据(`kzb://core/...` 解析正常)
- [ ] 切换 `zh-CN` / `en`,跨工程文本全部刷新
- [ ] 切换 `Day` / `Night`,跨工程样式全部刷新
- [ ] 三个工程各自导出 kzb 成功,且先导 core
- [ ] 把某信号的 `Valid` 置 false(改 stub),UI 正确显示故障态
- [ ] 页面根 Prefab 名 / 绑定字段名与契约一致

通过后再并行铺开 `launcher` / `vehiclecontrol` / `interior`。

---

## 7. 常见问题

| 问题 | 原因 / 处理 |
|------|-------------|
| 模块里看不到 core 的组件/颜色/字段 | 没添加对 `core` 的工程引用;或 core 未先导出 |
| `kzb://core/...` 解析失败(运行时) | 加载模块 kzb 前未加载 `core.kzb`(见 export-kzb.md 依赖清单) |
| 切语言不生效 | 文本直接填了字面量,没绑定 Localization 键 |
| 切主题不生效 | 节点写死了颜色/字号,没引用 token |
| 删了 `Application/` 后导出报路径错 | kzb 导出路径还指向 `Application/`;改到独立 `out/` |
| 多人改同一工程冲突频繁 | 工程拆分不够;一个模块尽量少人编辑,公共部分下沉 core |
