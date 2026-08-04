# 运行时资源目录 (`IVI/assets/`)

本目录在运行时等价于 Kanzi 官方的 **`Application/bin`**（见 [`IVI/plugins/README.md`](../plugins/README.md)）。

- **KZB / cfg**：Studio 导出到本目录**根**（`launcher.kzproj` 的 `BinaryExportDirectory` = `..\..\..\assets`）
- **Java 运行时布局**：编译 `launcher` 后由 CMake 自动生成：
  - `kzjava.jar`、`kzjvm.jar`（来自 Studio `EnginePlugins/…`）
  - `lib/java/<Debug|Release>/DroidDataSourceplugin.jar`（来自 `IVI/plugins/`）

## 目录布局

| 内容 | 说明 |
|------|------|
| `*.kzb`、`launcher.kzb.cfg`、`application.cfg`、`*.jar` | **必须在本目录根**:引擎按 `./xxx` 相对工作目录根查找 |
| `xml/` | 数据契约与配置 XML(`datasource.xml`、`VehicleControl.xml` 等);Studio 数据源 File = `xml\datasource.xml` |
| `localization/` | 预留:多语言资源包。Studio locale pack 导出目录名固定为 `Locale_packs/` |
| `lz4/` | 预留:lz4 压缩资源包 |
| `kzb/` | 预留:发布归档用;日常 Export/调试仍用本目录根(见 [repo-structure.md](../../docs/repo-structure.md) §3) |
| `pc_exe/` | 预留:桌面端打包产物 |

## Visual Studio 调试

工作目录 = 本目录。缺 `launcher.kzb.cfg` → 先 Export KZB。

## 插件相关报错

| 现象 | 处理 |
|------|------|
| `Could not find ./kzjava.jar` 或 `./kzjvm.jar` | 设 `KANZI_STUDIO_HOME`；**重新编译** launcher |
| Java 插件未加载 | 确认 `lib/java/Debug|Release/` 与根目录业务 JAR |

## 导出

`IVI/KanziProject/launcher/Tool_project/launcher.kzproj` → Binary Export Directory = `..\..\..\assets` → 按 `docs/export-kzb.md` 顺序 Export。
