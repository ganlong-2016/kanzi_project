# Windows 桌面运行 launcher（VS Debug）

## FAQ：为什么 Kanzi 新建的工程直接能跑，本工程要配这么多东西？

**差别不在 Preview Working Directory，而在本工程启用了 Java 引擎插件。**

- 向导新建的工程没有 Java 插件 → 不加载 `kzjvm.dll`、不起 JVM、不需要任何 jar，
  原始 CMake 自然什么都不用管。
- 本工程启用了 `DroidDataSourceplugin`（Java 数据源）→ kzb 记录了该依赖 →
  桌面上也要起 JVM，并按引擎硬编码规则从**工作目录根**找
  `kzjvm.jar` / `kzjava.jar` / `DroidDataSourceplugin.jar`。

**"jar 必须在工作目录"的依据是引擎自身行为，不是官方文档条文**：

- 报错 `Could not find ./kzjava.jar` —— `./` 即进程当前工作目录；
- 报错 `Could not read the plugin file ... from JAR plugin path 'null' or the
  working directory` —— 引擎 Java 侧 `PluginLoader` 只搜这两处，
  而 "JAR plugin path" 仅由宿主（Studio Preview / Android App）传入，
  独立 exe 下恒为 `null`。

官方文档（[Using Kanzi Engine plugins](https://docs.kanzi.com/3.9.15/en/working-with/plugins/installing-kanzi-engine-plugins.html)、
[Creating Kanzi Engine plugins](https://docs.kanzi.com/3.9.15/en/working-with/plugins/creating-kanzi-engine-plugins.html)）
只覆盖两种 Java 插件宿主：**Studio Preview**（需 `jvm.dll` 在 PATH/JAVA_HOME）
和 **Android droidfw**（"you can use Java plugins only with Kanzi Android
framework (droidfw) applications"）；`lib/java/Debug|Release/` 是 **Studio 导入**
的路径规范，不是运行时搜索路径。**独立 Windows exe + Java 插件**属于文档空白，
本仓库的 CMake 部署是按上述引擎实际搜索行为补的工程做法。
改 Working Directory（`Application/bin` → `assets/`）只决定复制到哪，
不是需要复制的原因。

**省心做法**：桌面只调 UI 时，在 Studio 里对 `DroidDataSourceplugin`
取消 **Is Enabled** 并重新 Export —— 桌面即回到与原生工程相同的状态。

## 复制 jar 后要不要重新编译？

**不要。**  
`assets\kzjava.jar` / `kzjvm.jar` 是运行时文件，改完直接 F5 即可。  
只有改了 `CMakeLists.txt` / 源码 / 需要重新部署插件时才要重新编译。

PowerShell 复制 Debug 系统 jar：

```powershell
Copy-Item -Force "D:\Kanzi 3_9_15_83\Studio\Bin\EnginePlugins\GL_vs2019_Debug\*.jar" `
  -Destination "D:\KanziWorkspace_3_9_15_83\Projects\NextEra\assets\"
Get-ChildItem "D:\KanziWorkspace_3_9_15_83\Projects\NextEra\assets\*.jar"
```

---

## 当前崩溃（`0xC0000005` 在 `java.dll` 之后）

日志顺序若是：

1. `Loading plugin 'kzjvm.dll'` OK  
2. 加载 `jvm.dll` / `java.dll` OK  
3. **没有** `Could not find ./kzjvm.jar`  
4. 立刻访问冲突  

说明 **jar 路径已通过**，崩在 **JVM/JNI 或 Java 插件**，不是缺文件，也不是“没编译”。

官方说明：Java Engine 插件主要面向 **Android (droidfw)**；Windows 上 `appfw` + `kzjvm` 仅用于 Preview/调试，兼容性因 JDK/插件而异。

### 步骤 A：隔离业务 Java 插件（优先做）

1. Studio 打开 `launcher.kzproj`  
2. `Library` → `Kanzi Engine Plugins` → `DroidDataSourceplugin`  
3. Properties → **取消 Is Enabled**  
4. **File → Export → Export KZB**（导出到 `assets/`）  
5. VS 再 F5  

| 结果 | 含义 |
|------|------|
| **不崩** | 问题在 `DroidDataSourceplugin` / 数据源；UI 可先不靠 Java 数据源在 Windows 上调 |
| **仍崩** | 问题在 `kzjvm` + JDK；做步骤 B |

桌面调 UI 时可以先关插件；真机/Android 再打开。

### 步骤 B：换 JDK 再试

当前加载的是 `C:\Users\LGAL28\.jdks\ms-17.0.17\...`。  
可临时改用 Android Studio 自带 JBR（64 位），保证 PATH 里只有一套：

```text
...\Android Studio\jbr\bin\server   （含 jvm.dll）
```

新开终端 / 重启 VS 后再 F5。

### 步骤 C：整套 Release

VS 配置改为 **Release**，并复制：

```powershell
Copy-Item -Force "D:\Kanzi 3_9_15_83\Studio\Bin\EnginePlugins\GL_vs2019_Release\*.jar" `
  -Destination "D:\KanziWorkspace_3_9_15_83\Projects\NextEra\assets\"
```

（引擎也会走 `GL_vs2019_Release_DLL`，与 jar 成套。）

### 步骤 D：McAfee

日志里有 `mfehcinj.dll`。若 A/B/C 仍崩，可对 `launcher.exe` / 工程目录加排除后再试（部分环境 JVM 会被注入干扰）。

---

## 报错：`Could not read the plugin file 'DroidDataSourceplugin.jar' from JAR plugin path 'null' or the working directory`

JVM 已正常启动（能看到这个 Java 断言栈说明 kzjvm/JNI 没问题），失败在**加载业务插件**。

桌面（win32 appfw）的 Java `PluginLoader` 只搜两个位置：

1. **JAR plugin path** —— 仅 Android（droidfw）由宿主 App 传入；桌面上无人设置，恒为 `null`
2. **工作目录根** —— 即 `assets\DroidDataSourceplugin.jar`

`assets\lib\java\Debug|Release\` 是 **Android 打包布局，桌面引擎不会去那里找**。

修复：把业务 jar 放到工作目录根（重新 CMake 编译会自动部署；或手动复制后直接 F5，无需重编）：

```powershell
Copy-Item -Force "D:\KanziWorkspace_3_9_15_83\Projects\NextEra\plugins\datasource\lib\java\Release\DroidDataSourceplugin.jar" `
  -Destination "D:\KanziWorkspace_3_9_15_83\Projects\NextEra\assets\"
```

> 附注：VS 调试时在 `jvm.dll`/`java.dll` 加载后看到的 first-chance `0xC0000005`（读地址 0）
> 多为 HotSpot 的隐式空指针检查/safepoint 机制，被 JVM 自己接住，**不是崩溃**；
> 以 Ctrl+F5 的实际报错和 `assets\hs_err_pid*.log` 是否生成为准。

## 为什么 Ctrl+F5 正常、F5 调试会"报 0xC0000005"？

HotSpot JVM **故意**用访问冲突实现隐式空指针检查和 safepoint 轮询，
并用自己的异常处理器接住恢复：

| 运行方式 | 异常去向 |
|---------|---------|
| Ctrl+F5（无调试器） | 直接交给 JVM 处理器，静默恢复 |
| F5（挂调试器） | 调试器有 first-chance 知情权，VS 先拦下来报告，再交还 JVM |

F5 下若中断，按 **继续(F5)** 即可照常运行；程序并没有崩。

一劳永逸：**调试 → 窗口 → 异常设置**(Ctrl+Alt+E) → Win32 Exceptions →
`c0000005 Access violation`：

- 取消勾选（未处理的真访问冲突仍会中断，不影响排查真 bug）；或
- 右键 → 编辑条件 → 模块名称 **不等于** `*jvm.dll`，只放行 JVM 内部异常。

---

## 正常 Windows 调试检查清单

| 项 | 期望 |
|----|------|
| VS 工作目录 | 仓库 `assets\` |
| `assets\launcher.kzb.cfg` | 已 Export |
| `assets\kzjava.jar` / `kzjvm.jar` | 与 Debug/Release 成套 |
| `assets\DroidDataSourceplugin.jar` | 若启用了数据源插件（桌面从工作目录根加载） |
| `KANZI_HOME` | Studio 安装（本机） |
| `Kanzi_DIR` | Workspace `Engine\lib\cmake\Kanzi` |
