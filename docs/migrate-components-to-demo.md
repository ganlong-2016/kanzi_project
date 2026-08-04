# 将 UI 组件从 common 迁到 demo（Kanzi Studio 操作）

> **背景**: `common` 只放**资源**(Brush / Theme / Font / Named Style)。Card、LabelText 等 **UI 组件 Prefab 归 `demo`**,作为可照着抄的样板,不在 common 里维护。

**本仓库状态**: `IVI/KanziProject/demo/demo.kzproj` 已含 `Card` / `LabelText` / `ToggleSwitch` / `Slider`;`IVI/KanziProject/Shared/common/common.kzproj` 的 `Prefabs` 下仅剩 Studio 内置预览项。若你本地仍是旧布局,按下面步骤在 **Kanzi Studio 3.9.15** 迁移一次。

## 迁移范围

**从 common 移出 → 放进 demo:**

- `Card`、`LabelText`、`ToggleSwitch`、`Slider`
- 以及 demo 专用的 `Button`、`ProgressBar`、`StatusIcon`、`ImageBox`、`ListItem` 等(若在 common 里)

**留在 common 不动:**

- `Library > Brushes` 下全部 Color Brush
- `Library > Themes > AppTheme`
- `Library > Fonts`、`Library > Styles`(LocaleStyle 等)
- `Library > Localization`(若有)

## 步骤

### 1. 把 Prefab 合并进 demo

1. 打开 `IVI/KanziProject/demo/demo.kzproj`
2. **File → Import → Merge Project** → 选 `IVI/KanziProject/Shared/common/common.kzproj`
3. 在合并对话框中**只勾选** `Prefabs` 下要迁的项:`Card`、`LabelText`、`ToggleSwitch`、`Slider` 等
4. 冲突时选 **Resolve to source**(以 common 里的版本为准)
5. 点 **Merge** — Prefab 会出现在 demo 的 `Prefabs` 下

### 2. 改组件内的资源引用

合并后,组件里对 brush / style 的引用应仍指向 common(通过 Project Reference):

- Background Brush 等继续用 `< Resource ID >` → `Color/Surface`、`Color/TextPrimary` 等
- Style 继续用 `LocaleStyle`
- 若某处写死了 `common/Brushes/Brush_*` 的绝对路径,可保留(跨工程引用)或改成 resource ID

**不要**把 Brush / Theme 复制进 demo。

### 3. 更新 demo 内对已迁组件的引用

在 demo 工程内全局检查,把:

- `kzb://common/Prefabs/Card` → `kzb://demo/Prefabs/Card`
- `kzb://common/Prefabs/LabelText` → `kzb://demo/Prefabs/LabelText`
- 其余 Prefab 同理

(`DemoPage` 里 Grid 上的 Card 实例、Properties 里的 Prefab Template 都要改。)

### 4. 从 common 删除已迁走的 Prefab

1. 打开 `IVI/KanziProject/Shared/common/common.kzproj`
2. `Prefabs` 里删除 `Card`、`LabelText`、`ToggleSwitch`、`Slider` 及试验品 `Card2`、`Slider 2D`
3. 若 `Property Types` 里只剩这些组件用的类型且无别处引用,可一并清理
4. Save

### 5. Make Public 与导出

1. demo 里:选中迁过来的 Prefab → **Make Public**(或工程级 `Resource Visibility Across Projects = Public`)
2. 导出顺序不变:**common.kzb → demo.kzb → launcher.kzb**

## 新模块怎么学 demo

业务模块(`car_setting` 等)**不要**引用 `kzb://demo/Prefabs/Card`。

正确做法:

1. **引用 common** — 拿主题、字体、颜色 token
2. **打开 demo 工程对照** — 看 Card 怎么搭、属性怎么 expose、绑定怎么写
3. **在自己的模块里建自己的 Prefab** — 可复制 demo 的结构,路径是 `kzb://<你的模块>/Prefabs/...`

`demo` 是教科书,不是运行时依赖库。

## 验收

- [x] common 的 `Prefabs` 下无 Card / LabelText / ToggleSwitch / Slider(主分支已满足)
- [x] demo 的 `Prefabs` 下有上述组件
- [x] demo 内 Prefab Template 指向 `kzb://demo/Prefabs/...`
- [ ] demo Preview 卡片与文字正常;主题在 **Dictionaries → Locales and Themes** 选 Day 后颜色正确(需在 Studio 验证)
- [ ] common / demo / launcher 均能正常导出 kzb(需在 Studio 验证)
