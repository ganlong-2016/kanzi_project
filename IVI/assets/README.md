# 运行时资源目录 (`IVI/assets/`)

本目录在运行时等价于 Kanzi 官方的 **`Application/bin`**（见 [`Shared/Plugins/README.md`](../../Shared/Plugins/README.md)）。

- **KZB / cfg**：Studio 导出到此目录  
- **Java 运行时布局**：编译 `launcher` 后由 CMake 自动生成：
  - `kzjava.jar`、`kzjvm.jar`（来自 Studio `EnginePlugins/GL_vs2019_<Debug|Release>/` 下全部 `*.jar`）
  - `lib/java/<Debug|Release>/DroidDataSourceplugin.jar`（来自仓库 `Shared/Plugins/`）

## 目录布局

| 内容 | 说明 |
|------|------|
| `*.kzb`、`launcher.kzb.cfg`、`application.cfg`、`datasource.xml`、`*.jar` | **必须在本目录根**:引擎与数据源插件按裸文件名 / `./xxx.jar` 相对工作目录根查找,不能移入子目录 |
| `Localization/` | 预留:本地化中间产物。注意 Studio 导出 locale pack 的目录名固定为 `Locale_packs/`(生成在本目录下,见 [localization-theme-design.md](../../docs/architecture/localization-theme-design.md) §D7) |
| `lz4/` | 预留:lz4 压缩的资源包 |
| `pc_exe/` | 预留:桌面端打包产物(exe + 运行时依赖) |

## Visual Studio 调试

工作目录 = 本目录。缺 `launcher.kzb.cfg` → 先 Export KZB。

## 插件相关报错

| 现象 | 处理 |
|------|------|
| `Could not find ./kzjava.jar` 或 `./kzjvm.jar` | 设 `KANZI_STUDIO_HOME`；**重新编译** launcher；确认本目录有对应 jar |
| Java 插件未加载 | 确认 `lib/java/Debug/`（Debug 构建）或 `Release/` 下有业务 JAR |

## 导出

`launcher.kzproj` → Binary Export Directory = `..\..\assets` → 按 `docs/export-kzb.md` 顺序 Export。
