# Kanzi 引擎插件

## 两类插件

| 类型 | 存放位置 | 示例 |
|------|----------|------|
| **业务 / 自研** | 本仓库 `plugins/` | `DroidDataSourceplugin.jar` |
| **系统（Kanzi 自带）** | Kanzi **安装目录**，不入库 | `kzjvm.dll`、`kzjava.jar` |

系统插件在 VS 编译时由 CMake 从 `%KANZI_HOME%`（或 `KANZI_ROOT`）自动复制到运行目录，**不必**复制进 `plugins/`。

典型安装路径（以 3.9.15 为例）：

```
D:\Kanzi 3_9_15_83\
├── Studio\Bin\EnginePlugins\GL_vs2019_Release\kzjvm.dll   ← JVM 桥接
└── Engine\lib\java\kzjava.jar                             ← Java 运行时
```

VS 方案须与 `GL_vs2019_Release` / `GL_vs2022_Release` 等目录名一致（与 Studio **Preview** 配置对齐）。

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
| `kzjava.jar` | `%KANZI_HOME%\Engine\lib\java\` | `assets/kzjava.jar` |
| `kzjvm.dll` | `%KANZI_HOME%\Studio\Bin\EnginePlugins\<配置>\` | `launcher.exe` 同目录 |

`assets/` 仅作 VS **工作目录**（kzb + 镜像后的 JAR），插件源文件不在此维护。

## Studio 导入

`launcher.kzproj` → **Kanzi Engine Plugins** → `DroidDataSourceplugin`：

`plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`
