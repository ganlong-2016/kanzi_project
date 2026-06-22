# 工程引用与依赖规范

## 1. 依赖关系图(唯一合法形态)

```text
core   ← 被引用,不引用任何工程
shell          → core
launcher       → core
charging       → core
vehiclecontrol → core
interior       → core
```

- 只允许 `shell/module → core` 这一种引用方向。
- **禁止**:`core → 任何工程`、`module → shell`、`module → module`、`shell → module 内部节点`。

## 2. 在 Kanzi Studio 中建立引用

> 菜单名称随 Kanzi 版本略有差异,以本团队所用版本为准(大致为 *Library / Add Project Reference / Referenced Projects*)。

在 `shell` 或某个 `module` 工程中:
1. 打开"引用工程 / Referenced Projects"。
2. 添加对 `core.kzproj`(或其导出物)的引用。
3. 此后即可在本工程中实例化 `kzb://core/Prefabs/Components/...` 的组件、绑定 `kzb://core/Data Sources/VehicleData` 的字段、使用 core 的主题与字体。

## 3. 跨工程 URL 约定

```text
kzb://core/Prefabs/Components/<组件名>
kzb://core/Resource Dictionaries/Theme_Day
kzb://core/Resource Dictionaries/Theme_Night
kzb://core/Data Sources/VehicleData/<字段路径>
kzb://core/Localization/<字符串键>
```

- 模块内部资源用 `kzb://<module>/...`,例如 `kzb://charging/Prefabs/Pages/ChargingPage`。
- **URL 中的工程名即 Kanzi 工程名**,必须全小写、稳定不变(见命名规范)。

## 4. 运行时加载依赖(交接给下游的关键信息)

由于模块通过 URL 引用 core 的资源,**加载顺序有强约束**:

```text
1) 先加载 core.kzb
2) 再加载 shell.kzb / 任意 module.kzb
```

- 加载任一 `module.kzb` 之前,`core.kzb` 必须已在内存中,否则 `kzb://core/...` 解析失败。
- 卸载时:**只要还有任意 module/shell 在用,就不能卸载 core.kzb**。
- 该依赖关系需写入交接文档(见 export-kzb.md 的"依赖清单")。

## 5. 变更管理(core 是地基)

- core 的 token / 组件接口 / 数据字段一旦发布,**视为冻结接口**,修改需走变更评审。
- core 变更后,**所有依赖它的 kzb 都需重新导出并回归**(纳入 CI 校验)。
- 新增共享内容时优先**追加**而非**修改/删除**已有项,避免破坏下游引用。

## 6. 反模式(严禁)

| 反模式 | 后果 | 正确做法 |
|--------|------|----------|
| core 引用 shell/module | 循环依赖,导出/加载失败 | 共享内容下沉 core,上层只引用 core |
| 两个模块互相引用 | 耦合 + 循环依赖 | 公共部分抽到 core |
| 同一图标/组件在多个模块各放一份 | 资源冗余、视觉漂移 | 下沉到 core 统一维护 |
| 加载 module.kzb 不加载 core.kzb | URL 解析失败、UI 缺资源 | 先加载 core.kzb |
| 交付后修改 core 组件/字段命名 | 下游引用与下游加载全断 | 命名冻结,只追加 |
