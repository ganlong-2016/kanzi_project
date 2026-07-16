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

## 插件

| 类型 | 位置 |
|------|------|
| 业务插件（数据源 JAR） | 仓库 [`plugins/`](../plugins/README.md) |
| 系统插件（`kzjvm.dll`、`kzjava.jar`） | Kanzi 安装目录；编译时自动部署 |

| 现象 | 处理 |
|------|------|
| `Could not find ./kzjava.jar` | 编译后 `assets/kzjava.jar` 不存在 | 设 `KANZI_STUDIO_HOME` 指向 Studio 安装根目录，重新 CMake 配置并编译；见 [`plugins/README.md`](../plugins/README.md) |
| `Failed to load plugin 'kzjvm.dll'` | 确认安装目录有 `Studio\Bin\EnginePlugins\<VS配置>\kzjvm.dll`；配置 JDK |

## 导出

1. `launcher.kzproj` → **Project > Properties** → Binary Export Directory = `..\..\..\assets`
2. **File > Export > Export KZB**（先 common，再各模块，最后 launcher）
3. 确认本目录出现 `launcher.kzb` / `launcher.kzb.cfg`

## 与 `Application/bin` 的关系

Kanzi 官方模板默认用 `IVI/launcher/Application/bin`。  
本工程**刻意**改用 `assets/`，便于与 `datasource.xml` 同目录；**不必**再维护两份 kzb。

若本地仍往 `Application/bin` 导出，要么改 Studio 导出路径，要么在 VS 里手动把工作目录改回 `bin`（二选一，勿混用）。
