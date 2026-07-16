# Kanzi Engine Plugins（统一目录）

本仓库**所有** Kanzi 引擎插件（业务 JAR / JVM 桥接 DLL / 其它 DLL）统一放在此目录，**不要**再从 `%KANZI_HOME%` 散落复制。

Studio 导入插件时，请选本目录下对应文件（见各子目录说明）。

## 目录约定

```
plugins/
├── datasource/                 # 数据源插件（已入库）
│   └── lib/java/Release/
│       └── DroidDataSourceplugin.jar
├── java/                       # Java 运行时（从 Kanzi 安装包复制一次，见下）
│   └── kzjava.jar
└── jvm/                        # JVM 桥接 DLL（从 Kanzi 安装包复制一次）
    └── lib/win64/GL_vs2019_Release_DLL/
        └── kzjvm.dll
```

按需可增加，例如去掉 Shapes 后不必建 `shapes/`；若以后再用：

```
plugins/shapes/lib/win64/GL_vs2019_Release_DLL/kzshapes.dll
```

## 首次准备（Windows 桌面调试）

从本机 Kanzi 3.9.15 安装目录**复制到上述路径**（只需做一次）：

| 复制源 | 放到 |
|--------|------|
| `%KANZI_HOME%\Engine\lib\java\kzjava.jar` | `plugins/java/kzjava.jar` |
| `%KANZI_HOME%\Engine\plugins\jvm\lib\win64\<你的 VS 配置>\kzjvm.dll` | `plugins/jvm/lib/win64/<同目录>/kzjvm.dll` |

VS 方案为 **VS2022 Release** 时，选 `GL_vs2022_Release_DLL` 或 `vs2022_Release_DLL` 下与 Studio **Preview** 配置一致的变体。

## 与运行时的关系

| 角色 | 目录 |
|------|------|
| **插件源（Git / 人工维护）** | `plugins/`（本目录） |
| **KZB / datasource.xml** | `assets/`（Studio 导出 + 契约 XML） |
| **VS 工作目录** | `assets/`（读 `launcher.kzb.cfg`） |
| **launcher.exe** | CMake 输出目录（Kanzi 核心 DLL + `kzjvm.dll` 等） |

编译 `launcher` 时，CMake 会把 `plugins/` 里已有的 JAR **镜像**到 `assets/`（引擎要求 `./kzjava.jar` 与 `lib/java/Release/` 相对工作目录），并把 `plugins/**/lib/win64/**/*.dll` 复制到 exe 旁。

**不要**手动往 `assets/` 或 `KANZI_HOME` 维护插件副本；只维护 `plugins/`。

## Studio

`launcher.kzproj` → **Kanzi Engine Plugins** → `DroidDataSourceplugin` 路径应为：

`plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`
