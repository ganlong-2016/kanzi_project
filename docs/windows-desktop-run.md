# Windows 桌面运行 launcher（VS Debug）

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

## 正常 Windows 调试检查清单

| 项 | 期望 |
|----|------|
| VS 工作目录 | 仓库 `assets\` |
| `assets\launcher.kzb.cfg` | 已 Export |
| `assets\kzjava.jar` / `kzjvm.jar` | 与 Debug/Release 成套 |
| `assets\lib\java\Debug\DroidDataSourceplugin.jar` | 若启用了数据源插件 |
| `KANZI_HOME` | Studio 安装（本机） |
| `Kanzi_DIR` | Workspace `Engine\lib\cmake\Kanzi` |
