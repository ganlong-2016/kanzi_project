# 导出与 kzb 依赖规范

## 1. 导出粒度

- 每个 `.kzproj` 导出**一个** kzb,文件名 = 工程名(全小写):
  `core.kzb`、`shell.kzb`、`launcher.kzb`、`charging.kzb`、`vehiclecontrol.kzb`、`interior.kzb`。
- core 的资源**不复制**进各模块 kzb,模块以 `kzb://core/...` 引用(单一来源、体积小)。

## 2. 导出顺序(被依赖者先导)

```text
1) core.kzb          # 地基,先导
2) shell.kzb         # 依赖 core
3) launcher.kzb / charging.kzb / vehiclecontrol.kzb / interior.kzb   # 依赖 core,可并行
```

- 所有上层 kzb 必须基于**同一版本的 core** 导出。
- core 变更后,需重导所有依赖它的 kzb。

## 3. kzb 依赖清单(交接给 Android 的运行时加载约束)

| kzb | 依赖 | 运行时加载约束 |
|-----|------|----------------|
| `core.kzb` | 无 | 必须最先加载;有任意上层在用时不可卸载 |
| `shell.kzb` | `core.kzb` | 加载前确保 core 已加载 |
| `launcher.kzb` | `core.kzb` | 同上 |
| `charging.kzb` | `core.kzb` | 同上 |
| `vehiclecontrol.kzb` | `core.kzb` | 同上 |
| `interior.kzb` | `core.kzb` | 同上 |

> 该表是交接物的一部分,任何依赖变化都要同步更新并通知下游。

## 4. 导出设置规范

- **纹理压缩**:按目标 GPU 选 **ASTC** 或 **ETC2**,禁止直接打包原始 PNG/JPG。
- **图集(Atlas)**:小图标合并图集,降低 draw call;图集规则在 core 统一约定。
- **未引用资源裁剪**:导出前清理无引用资源,控制 kzb 体积。
- **字体子集化**:中文字体按实际用字子集化,控制体积(详见 localization.md)。
- **命名稳定**:Screen / 页面根 Prefab / Data Source 字段命名在交付后冻结。

## 5. 命令行导出(纳入 CI,避免手点)

> 命令行工具名随版本不同(如 `KanziStudioConsole` / Studio 自带命令行导出),以本团队 Kanzi 版本为准。下方为流程伪代码,落地时替换为实际命令。

```bash
# 伪代码:实际命令以 Kanzi 版本文档为准
export_kzb core           studio-projects/Core/core.kzproj            -> out/core.kzb
export_kzb shell          studio-projects/Shell/shell.kzproj          -> out/shell.kzb
export_kzb launcher       studio-projects/Module_Launcher/launcher.kzproj
export_kzb charging       studio-projects/Module_Charging/charging.kzproj
export_kzb vehiclecontrol studio-projects/Module_VehicleControl/vehiclecontrol.kzproj
export_kzb interior       studio-projects/Module_Interior/interior.kzproj
```

CI 流程建议:
```text
导出 core → 导出 shell/各 module(基于同版本 core)
   → 校验:Data Source 字段 ⇔ 契约 JSON diff
   → 校验:缺失/未引用资源、kzb 体积阈值
   → 产物归档 + 更新依赖清单 → 交付
```

## 6. 校验关卡(质量门)

1. **数据契约一致性**:各工程 Data Source 字段须与 `contracts/vehicle-data.schema.json` 对齐(字段名/类型/枚举)。不一致则失败。
2. **依赖方向检查**:确认无 `core → 上层` 或 `module ↔ module` 引用。
3. **体积阈值**:每个 kzb 设上限,超限报警。
4. **命名冻结检查**:页面根 Prefab / 字段名相对上一交付版本无非预期改名。

> 任何校验失败应**显式中断流水线并报错**,不得跳过或以默认值掩盖。

## 7. 版本控制约定

- `.kzproj` 与设计资源进 Git;大资源(3D/高清纹理/字体)用 Git LFS。
- **导出产物(`*.kzb`)不进 Git**(见仓库 `.gitignore`),由 CI 生成并归档。
