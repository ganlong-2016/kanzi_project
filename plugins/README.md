# Kanzi 引擎插件

## 两类插件

| 类型 | 存放位置 | 示例 |
|------|----------|------|
| **业务 / 自研** | 本仓库 `plugins/` | `DroidDataSourceplugin.jar` |
| **系统（Kanzi 自带）** | Kanzi **安装目录**，不入库 | `kzjvm.dll`、`kzjava.jar` |

系统插件在 VS 编译时由 CMake 从 `%KANZI_HOME%`（或 `KANZI_ROOT`）自动复制到运行目录，**不必**复制进 `plugins/`。

典型路径（Workspace 与 Studio **分开安装**时常见）：

```
D:\KanziWorkspace_3_9_15_83\          ← KANZI_HOME（Engine，含 kzjvm.dll）
D:\Kanzi 3_9_15_83\Studio\Bin\      ← Studio 安装（含 kzjava.jar）
    kzjava.jar
    EnginePlugins\GL_vs2019_Debug\kzjvm.dll
```

若 `KANZI_HOME` 指向 Workspace 且其下**没有** `Studio/Bin/kzjava.jar`，请额外设置环境变量：

```
KANZI_STUDIO_HOME=D:\Kanzi 3_9_15_83
```

然后 **重新 CMake 配置 + 编译**。CMake 配置日志应出现：

```
-- deploy kzjava.jar: ... -> .../assets/kzjava.jar
```

编译后确认存在：`<仓库>/assets/kzjava.jar`。

VS 方案须与 `GL_vs2019_Debug` / `GL_vs2019_Release` 等目录名一致（你当前 Debug 日志显示引擎使用 `GL_vs2019_Debug_DLL`）。

## 本仓库 `plugins/` 目录

只放**项目自己的**插件：

```
plugins/
└── datasource/
    └── lib/java/Release/
        └── DroidDataSourceplugin.jar
```

以后若有自研 DLL 插件，可按 Kanzi 惯例放在：

```
plugins/<name>/lib/win64/<VS配置>/<plugin>.dll
```

编译时会复制到 `launcher.exe` 同目录。

## 运行时部署（CMake 自动完成）

| 文件 | 源 | 部署到 |
|------|-----|--------|
| `DroidDataSourceplugin.jar` | `plugins/datasource/...` | `assets/lib/java/Release/` |
| `kzjava.jar` | `KANZI_HOME` 或 `KANZI_STUDIO_HOME` 下的 `Studio/Bin/` 等 | `assets/kzjava.jar`（**VS 工作目录**） |
| `kzjvm.dll` 等核心 DLL | `KANZI_HOME\Engine\lib\Win64\...` | `runtime\Debug\`（`install_kanzi_libs` 自动） |

`assets/` 仅作 VS **工作目录**（kzb + 镜像后的 JAR），插件源文件不在此维护。

## Studio 导入

`launcher.kzproj` → **Kanzi Engine Plugins** → `DroidDataSourceplugin`：

`plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`
