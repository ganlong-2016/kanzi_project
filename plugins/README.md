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
├── GL_vs2019_Debug/
│   ├── kzjava.jar
│   └── kzjvm.jar          ← 工作目录也要 ./kzjvm.jar
└── GL_vs2019_Release/
    ├── kzjava.jar
    └── kzjvm.jar
```

CMake 编译时会把**匹配 VS 配置**的目录下 **所有 `*.jar`** 复制到 `assets/`（工作目录根）。若只有 `Release` 目录、没有 `Debug`，会自动回退到 `GL_vs2019_Release`。

### 环境变量（两个根目录，不要搞混）

| 变量 | 指向 | 示例 | 用途 |
|------|------|------|------|
| **`KANZI_HOME`** | Kanzi **Workspace**（含 `Engine\lib\cmake\Kanzi`） | `D:\KanziWorkspace_3_9_15_83` | CMake `find_package(Kanzi)`、引擎 DLL |
| **`KANZI_STUDIO_HOME`** | Kanzi **Studio 安装** | `D:\Kanzi 3_9_15_83` | 仅部署 `kzjava.jar` / `kzjvm.jar` |

```bat
setx KANZI_HOME "D:\KanziWorkspace_3_9_15_83"
setx KANZI_STUDIO_HOME "D:\Kanzi 3_9_15_83"
```

若把 `KANZI_HOME` 设成 Studio 安装目录，CMake 会报：

`Could not locate Kanzi_DIR. Input 'D:\Kanzi 3_9_15_83/Engine/lib/cmake/Kanzi/' is probably invalid`

因为 Studio 安装树里**没有** `Engine\lib\cmake\Kanzi\`。

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
assets/kzjvm.jar
assets/lib/java/Debug/DroidDataSourceplugin.jar
```

CMake 输出应含：`deploy-runtime: kzjava.jar <- .../GL_vs2019_Debug/kzjava.jar`

若仍报 `Could not find ./kzjava.jar`：检查 `KANZI_STUDIO_HOME`、是否**重新编译**（非仅 F5）、以及 `assets/` 下文件是否生成。

---

## FAQ：为什么要把 jar 复制到 `assets/`，不能直接用安装目录吗？

### 简短结论

**不是冲突，是引擎硬编码了相对路径。**  
报错文案是 `Could not find ./kzjvm.jar` —— 前面的 **`./`** 表示：只在**进程当前工作目录**下找同名文件，**没有**公开的 `application.cfg` / 环境变量去指定绝对路径。

官方默认工作目录是 `Application/bin`，那里同时放 kzb **和** 这些 jar。本工程工作目录改成了 `assets/`（为了和 kzb / `datasource.xml` 同目录），所以必须在 `assets/` 复现同样布局；复制是最稳妥的做法。

### DLL 和 JAR 为什么待遇不同？

| 文件 | 谁加载 | 搜索规则 | 能否留在安装目录 |
|------|--------|----------|------------------|
| `kzjvm.dll` / `kzjava.dll` / `kzcore*.dll` | Windows `LoadLibrary` | exe 目录、`PATH`、Kanzi `Engine\lib\Win64\...` | **可以**（你日志里已从 Workspace Engine 加载） |
| `kzjava.jar` / `kzjvm.jar` | `kzjvm` 插件启动 JVM 时 | **写死**为工作目录下的 `./xxx.jar` | **不能直接引用**（除非工作目录就设到那个目录） |

所以：系统 DLL 继续用安装目录没问题；系统 JAR 必须出现在**工作目录根**。

### 能不能改工作目录到 Studio 的 EnginePlugins？

不行。工作目录若设成：

`D:\Kanzi 3_9_15_83\Studio\Bin\EnginePlugins\GL_vs2019_Release`

引擎能找到 jar，但找不到：

- `launcher.kzb.cfg` / `*.kzb`
- `application.cfg`
- `datasource.xml`

这些在 `assets/`。**一个进程只有一个当前工作目录**，不能同时指向两处。

### 有没有“配置路径”的官方开关？

公开文档里：

- 有：Preview Working Directory、`application.cfg` 里的 ModuleNames / BinaryName 等  
- **没有**：`KzJavaJarPath=`、`JavaClasspath=` 这类可把 `kzjava.jar` 指到安装目录的选项  

因此 VS 侧常见做法就是：工作目录 = 放 kzb 的目录，构建时把所需 jar **镜像**进去（本仓库 CMake `deploy-runtime.cmake`）。

### 复制会不会有版本冲突？

一般不会：

- 复制的是 **当前 Kanzi 安装里** 与 Debug/Release 匹配的那一套 jar  
- `assets/*.jar` 已在 `.gitignore`，不入库  
- 换 Kanzi 版本后重新编译即覆盖  

真正要避的是：**工作目录里混用旧 jar + 新 `kzjvm.dll`**（所以用 `copy_if_different` 从当前 `KANZI_STUDIO_HOME` 同步）。

### 可选替代（都不比复制更简单）

1. **工作目录改回官方 `Application/bin`**，jar 也放那里 —— 仍是“放进工作目录”，只是目录名不是 `assets/`  
2. **目录联接 / 符号链接** 把 `assets\kzjvm.jar` 链到安装目录 —— Windows 权限/便携性差，CI 易碎  
3. **改 Kanzi 源码** 支持绝对路径 —— 超出本项目范围  

**推荐**：保持现状 —— 源在安装目录，构建时同步到工作目录。

---

## FAQ：过了 jar 查找后出现 `0xC0000005` 空指针崩溃

典型现象：

- 日志已能 `Loading plugin 'kzjvm.dll'`，并加载 `jvm.dll`
- 不再报 `Could not find ./kzjava.jar` / `./kzjvm.jar`
- 随后弹出 `0xC0000005: 读取位置 0x0000000000000000`，反汇编里常见 `xor esi,esi` 后立刻 `mov eax,[rsi]`
- 调用堆栈只有一行「未知」→ 多半在 **JVM JIT / JNI** 里，没有 C++ 符号

这通常**不是** `launcher.cpp` 写坏了，而是 Java 桥接初始化或插件执行时崩了。

### 优先排查（按顺序）

1. **Debug/Release 必须成套**  
   VS **Debug** 时，`assets/kzjava.jar` / `kzjvm.jar` 应来自：
   ```
   ...\EnginePlugins\GL_vs2019_Debug\
   ```
   若编译日志显示复制自 `GL_vs2019_Release`，而引擎 DLL 是 `GL_vs2019_Debug_DLL`，极易 JNI 空指针。  
   → 确认 `D:\Kanzi 3_9_15_83\Studio\Bin\EnginePlugins\GL_vs2019_Debug\` 下有 jar，重新编译；或改用 VS **Release** 整套跑。

2. **看 Output 里崩溃前最后几行 Kanzi 日志**  
   是否还有 `Loading plugin 'DroidDataSourceplugin'`、数据源/XML 相关 error。把从 `Kanzi version` 到崩溃前的日志贴出来最有用。

3. **JDK**  
   你之前加载的是 `ms-17.0.17`。若怀疑兼容性，可临时改用 Android Studio 自带 JBR，或 Temurin **11/17** 的 `bin\server` 进 PATH，保证 64 位。

4. **隔离是不是数据源插件**  
   Studio 里暂时取消勾选 `DroidDataSourceplugin` 的 **Is Enabled**，重新 Export KZB 再跑：  
   - 不崩 → 问题在业务 Java 插件 / `datasource.xml`  
   - 仍崩 → 问题在 `kzjvm`/`kzjava` 与引擎/JDK 组合

5. **临时验证**  
   手动把 `GL_vs2019_Debug`（或你 VS 配置对应目录）下的 **全部 jar** 拷到 `assets\`，再 F5（绕过 CMake 看是否配置问题）。
