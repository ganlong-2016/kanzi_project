# 运行时资源目录 (`assets/`)

本仓库将 **Kanzi KZB 导出** 与 **数据源 XML** 统一放在仓库根 `assets/`（launcher `BinaryExportDirectory` = `../../../assets`）。

## Visual Studio 调试

CMake 已将 `launcher` 的 **工作目录** 设为绝对路径指向本目录。  
引擎启动时在当前目录查找 `launcher.kzb.cfg`（见 `launcher.cpp` 的 `configuration.binaryName`）。

## 必需文件（Studio 导出，*.kzb* 不入 Git）

| 文件 | 说明 |
|------|------|
| `datasource.xml` | 数据源契约（已入库） |
| `application.cfg` | 引擎通用配置（已入库） |
| `launcher.kzb.cfg` | Export KZB 生成 |
| `launcher.kzb` 及依赖 kzb | 按 `docs/export-kzb.md` 顺序导出 |

缺 `launcher.kzb.cfg` 时会报错：`Cannot open the kzb configuration file 'launcher.kzb.cfg'`。

## Engine Plugins（`kzshapes.dll` 等）

`launcher` 引用了 **demo** 模块；demo 使用 **Kanzi Shapes**（`Rectangle2D` 等），导出后的 `launcher.kzb.cfg` 会要求加载 `kzshapes.dll`。

| 现象 | 原因 | 处理 |
|------|------|------|
| `Failed to load plugin 'kzshapes.dll'` | 插件 DLL 不在 **`launcher.exe` 同目录**（与 kzb 工作目录 `assets/` 无关） | 确认已安装 Kanzi Shapes；重新 CMake 生成并编译（CMake 会尝试从 `KANZI_HOME` 复制）；或手动复制 `Engine/plugins/shapes/lib/win64/.../kzshapes.dll` 到 exe 输出目录 |
| 仍失败 | VS 方案与插件变体不一致（Release/Debug、VS2019/2022、GL/非 GL） | Studio **Project > Properties** 与 VS 配置对齐；在 demo 中重新 Import `kzshapes.dll` 对应目录 |

`install_kanzi_libs_to_output_directory()` 只部署 Kanzi **核心**运行时，**不包含** Engine Plugins。

## 导出

1. `launcher.kzproj` → **Project > Properties** → Binary Export Directory = `..\..\..\assets`
2. **File > Export > Export KZB**（先 common，再各模块，最后 launcher）
3. 确认本目录出现 `launcher.kzb` / `launcher.kzb.cfg`

## 与 `Application/bin` 的关系

Kanzi 官方模板默认用 `IVI/launcher/Application/bin`。  
本工程**刻意**改用 `assets/`，便于与 `datasource.xml` 同目录；**不必**再维护两份 kzb。

若本地仍往 `Application/bin` 导出，要么改 Studio 导出路径，要么在 VS 里手动把工作目录改回 `bin`（二选一，勿混用）。
