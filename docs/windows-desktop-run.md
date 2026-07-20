# Windows 桌面运行 launcher（VS Debug）

## FAQ：为什么 Kanzi 新建的工程直接能跑，本工程要配这么多东西？

**差别不在 Preview Working Directory，而在本工程启用了 Java 引擎插件。**

- 向导新建的工程没有 Java 插件 → 不加载 `kzjvm.dll`、不起 JVM、不需要任何 jar，
  原始 CMake 自然什么都不用管。
- 本工程启用了 `DroidDataSourceplugin`（Java 数据源）→ kzb 记录了该依赖 →
  桌面上也要起 JVM，并按引擎硬编码规则从**工作目录根**找
  `kzjvm.jar` / `kzjava.jar` / `DroidDataSourceplugin.jar`（官方文档的做法是手动复制）。

本仓库的 CMake 改动只是**把官方要求的手动复制自动化**；改 Working Directory
（`Application/bin` → `assets/`）只决定复制到哪，不是需要复制的原因。
官方也说明 Java 插件主要面向 Android，桌面 `kzjvm` 仅供 Preview/调试。

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
