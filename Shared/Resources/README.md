# Shared/Resources — 跨模块共享资源（非代码）

分层规划（参考量产级工程结构建议,当前为**预留骨架**）:

| 子目录 | 用途 | 现状 |
|--------|------|------|
| `carmodel/` | **车型专属资源**:按车型变体分目录(如 `T101_Truck/`、`T201_EV/`),存放各变体的 glb 模型、专属贴图 | 预留。当前唯一车型的 `truck.glb` 仍在 `IVI/car/3D Assets/` — `Car.kzproj` 的 `ImportedFrom` 引用指向工程内路径,出现第二个车型变体时再迁移并统一从这里引用 |
| `ota/` | **热更新资源预备**:打包后可独立下发的 kzb / 贴图 | 预留 |

## 为什么"通用资源"不在这里?

建议稿中的 `Resources/Common/`(字体、主题、Brush 等通用资源)在 Kanzi 工程里**必须以 kzproj 工程形式被其他工程 `kzb://` 引用**才能复用,因此它的落地形态是 [`IVI/common/`](../../IVI/common/) 共享资源工程,而不是裸文件目录。本目录只放**不进 kzproj 资源树**的原始资产(DCC 交付物、OTA 包)。

## 使用约定

- 新增车型变体:在 `carmodel/` 下建 `<变体代号>_<名称>/`,内放 `*.glb` + 贴图源文件;Studio 工程从这里 Import。
- 大文件一律走 Git LFS(`.gitattributes` 已覆盖 glb/png/dds 等)。
