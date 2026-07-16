# launcher 运行时目录 (`Application/bin`)

Visual Studio 调试时 **工作目录** 设为此文件夹（见 `CMakeLists.txt` 的 `VS_DEBUGGER_WORKING_DIRECTORY`）。

## 必需文件（由 Kanzi Studio 导出，不入 Git）

| 文件 | 来源 |
|------|------|
| `launcher.kzb.cfg` | `launcher.kzproj` → **File > Export > Export KZB** |
| `launcher.kzb` | 同上 |
| `common.kzb`、`car.kzb` 等 | 各子工程按依赖顺序导出（见 `docs/export-kzb.md`） |
| `application.cfg` | 可手写或随导出；引擎通用配置 |

若缺少 `launcher.kzb.cfg`，运行 exe 会报错：

```text
Cannot open the kzb configuration file 'launcher.kzb.cfg'.
```

## 导出步骤（首次 / Studio 改工程后）

1. 在 Kanzi Studio 打开 `IVI/launcher/Tool_project/launcher.kzproj`。
2. 确认 **Project > Properties > Binary Export Directory** = `..\Application\bin`（相对 `Tool_project`）。
3. 先导出依赖工程（顺序）：`common` → `car` / `car_setting` / `environment` → **`launcher`**。  
   各工程 Export KZB 到**同一** `Application/bin`（子模块若导出到各自 `Binary/`，需复制到此处或改 launcher 引用）。
4. 菜单 **File > Export > Export KZB**。
5. 检查本目录是否出现 `launcher.kzb`、`launcher.kzb.cfg`。
6. 再在 Visual Studio 中 F5 运行 `launcher`。

## 可选：User Preferences

**Edit > User Preferences > Advanced**：勾选 **Create table of contents of kzb file**，确保生成 `.kzb.cfg` 目录文件。
