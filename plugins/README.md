# Kanzi 引擎插件

## 官方怎么配（Kanzi 3.9.15）

依据 [Installing Kanzi Engine plugins](https://docs.kanzi.com/3.9.15/en/working-with/plugins/installing-kanzi-engine-plugins.html) 与 [Creating Kanzi Engine plugins](https://docs.kanzi.com/3.9.15/en/working-with/plugins/creating-kanzi-engine-plugins.html)：

### 1. 工作目录 = `Application/bin`（本工程等价于 `assets/`）

C++ 应用运行时，当前目录下应有：

```
<工作目录>/
├── kzjava.jar                          ← 根目录（./kzjava.jar）
├── application.cfg
├── launcher.kzb.cfg
├── *.kzb
└── lib/java/
    ├── Debug/DroidDataSourceplugin.jar   ← VS Debug 时用
    └── Release/DroidDataSourceplugin.jar ← VS Release 时用
```

官方默认 **Preview Working Directory** = `..\Application\bin`。本工程把 kzb 导出到 `assets/`，VS 工作目录也设为 `assets/`，因此须在 `assets/` **复现上述 bin 布局**（由 CMake 编译后自动部署）。

### 2. 系统 `kzjava.jar`：Studio `EnginePlugins`（不要放进仓库 `plugins/`）

与 `kzjvm.dll` 一样，属于 Kanzi 安装自带，路径形如：

```
<KANZI_STUDIO_HOME>/Studio/Bin/EnginePlugins/
├── GL_vs2019_Debug/kzjava.jar      ← VS **Debug** 时用
└── GL_vs2019_Release/kzjava.jar    ← VS **Release** 时用
```

示例：`D:\Kanzi 3_9_15_83\Studio\Bin\EnginePlugins\GL_vs2019_Debug\kzjava.jar`

设置环境变量（Workspace 与 Studio 分开时）：

```
KANZI_STUDIO_HOME=D:\Kanzi 3_9_15_83
```

### 3. 业务 Java 插件：仓库 `plugins/`（3.9.5+ 路径规范）

自研 JAR 放在：

```
plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar
```

（若有 Debug 包，也可放 `lib/java/Debug/`。）

Studio 导入路径：`plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`

### 4. Studio Project Properties 须与 VS 一致

| 属性 | VS Debug 示例 | VS Release 示例 |
|------|---------------|-----------------|
| Preview OpenGL ES Wrapper | GL | GL |
| Preview Build Configuration | **Debug** | **Release** |
| Preview Visual Studio Version | 2019（与引擎 DLL 后缀一致） | 2019 |
| Preview Working Directory | `..\..\..\assets` | 同左 |

> 引擎 DLL 实际从 `KANZI_HOME\Engine\lib\Win64\GL_vs2019_Debug_DLL\` 加载（`install_kanzi_libs`），与 Studio `EnginePlugins\GL_vs2019_Debug\` 的 **Debug/Release、VS 版本** 须对齐。

### 5. JDK（加载 Java 插件）

`PATH` 须包含 64 位 JDK 的 `jvm.dll` 目录，例如 `%JAVA_HOME%\bin\server`。

---

## 本仓库 `plugins/` 只放业务插件

```
plugins/
└── datasource/
    └── lib/java/Release/
        └── DroidDataSourceplugin.jar
```

**不要**把 `kzjava.jar` / `kzjvm.dll` 放进 `plugins/`。

## 编译后自检

VS **Debug** 编译 `launcher` 后确认：

```
assets/kzjava.jar
assets/lib/java/Debug/DroidDataSourceplugin.jar
```

CMake 输出应含：`deploy-runtime: kzjava.jar <- .../GL_vs2019_Debug/kzjava.jar`

若仍报 `Could not find ./kzjava.jar`：检查 `KANZI_STUDIO_HOME`、是否**重新编译**（非仅 F5）、以及 `assets/` 下文件是否生成。
