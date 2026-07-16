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

## Java 插件运行时（`DroidDataSourceplugin`）

`launcher` 注册了 **Java 数据源插件**。VS 工作目录为 `assets/` 时，引擎会在该目录查找：

| 文件 | 路径（相对 `assets/`） | 来源 |
|------|------------------------|------|
| `kzjava.jar` | `./kzjava.jar` | Kanzi Engine（`%KANZI_HOME%\Engine\lib\java\`） |
| `DroidDataSourceplugin.jar` | `lib/java/Release/DroidDataSourceplugin.jar` | 仓库 `plugins/datasource/lib/java/Release/` |
| `kzjvm.dll` | 与 **`launcher.exe` 同目录** | `%KANZI_HOME%\Engine\plugins\jvm\lib\win64\...` |

| 现象 | 原因 | 处理 |
|------|------|------|
| `kzjvm: Could not find ./kzjava.jar` | 工作目录改为 `assets/` 后未部署 Java 运行时 | 重新 CMake 生成并编译（`deploy-java-runtime.cmake` 会自动复制）；或手动把 `kzjava.jar` 放到 `assets/` |
| `Failed to load plugin 'kzjvm.dll'` | JVM 桥接 DLL 不在 exe 目录，或 JDK 未配置 | 确认 `kzjvm.dll` 在 exe 旁；`PATH` 含 `%JAVA_HOME%\bin\server`（`jvm.dll`） |

> 官方模板默认工作目录为 `Application/bin`，其中预置了 `kzjava.jar` 与 `lib/java/Release/`。迁到 `assets/` 后需由构建脚本补齐上述文件。

`install_kanzi_libs_to_output_directory()` 只部署 Kanzi **核心**运行时，**不包含** `kzjava.jar` / 业务 Java 插件 JAR。

## 导出

1. `launcher.kzproj` → **Project > Properties** → Binary Export Directory = `..\..\..\assets`
2. **File > Export > Export KZB**（先 common，再各模块，最后 launcher）
3. 确认本目录出现 `launcher.kzb` / `launcher.kzb.cfg`

## 与 `Application/bin` 的关系

Kanzi 官方模板默认用 `IVI/launcher/Application/bin`。  
本工程**刻意**改用 `assets/`，便于与 `datasource.xml` 同目录；**不必**再维护两份 kzb。

若本地仍往 `Application/bin` 导出，要么改 Studio 导出路径，要么在 VS 里手动把工作目录改回 `bin`（二选一，勿混用）。
