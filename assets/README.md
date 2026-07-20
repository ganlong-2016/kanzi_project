# 运行时资源目录 (`assets/`)

本目录在运行时等价于 Kanzi 官方的 **`Application/bin`**（见 [`plugins/README.md`](../plugins/README.md)）。

- **KZB / cfg**：Studio 导出到此目录  
- **Java 运行时布局**：编译 `launcher` 后由 CMake 自动生成：
  - `kzjava.jar`（来自 Studio `EnginePlugins/GL_vs2019_<Debug|Release>/`）
  - `lib/java/<Debug|Release>/DroidDataSourceplugin.jar`（来自仓库 `plugins/`）

## Visual Studio 调试

工作目录 = 本目录。缺 `launcher.kzb.cfg` → 先 Export KZB。

## 插件相关报错

| 现象 | 处理 |
|------|------|
| `Could not find ./kzjava.jar` | 设 `KANZI_STUDIO_HOME`；**重新编译** launcher；确认本目录有 `kzjava.jar` |
| Java 插件未加载 | 确认 `lib/java/Debug/`（Debug 构建）或 `Release/` 下有业务 JAR |

## 导出

`launcher.kzproj` → Binary Export Directory = `..\..\..\assets` → 按 `docs/export-kzb.md` 顺序 Export。
