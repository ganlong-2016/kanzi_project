# launcher 的 CMake 构建体系与 VS 运行(F5 / Ctrl+F5)详解

本文回答两个问题:

1. `IVI/launcher/Application/` 下的几个 CMake 文件各是什么意思、怎么配合运行的;
2. 为什么 **Ctrl+F5 正常运行,F5 调试却"报 0xC0000005 错"**。

相关文档:[Windows 桌面运行排查](windows-desktop-run.md) · [插件部署原理](../plugins/README.md)

---

## 一、文件全景:谁在什么时间点干活

整个体系是 **1 个 bat 脚本 + 4 个 CMake 文件**,分别在三个时间点生效:
**生成工程时(configure)→ 每次编译后(POST_BUILD)→ VS 按 F5 运行时**。

```text
① generate_cmake_vs2022_solution.bat     ← 手动双击,只跑一次
        │  调用 cmake configure
        ▼
② CMakeLists.txt                          ← 总指挥,include 其余三个
        │
        ├──► ③ cmake/kanzi-locate.cmake   ← configure 阶段:找 Kanzi 引擎在哪
        │        (随后 find_package 加载官方 kanzi-common 模块)
        └──► ④ cmake/deploy-plugins.cmake ← configure 阶段:只"登记"编译后要做的事
                  │  注册 POST_BUILD 命令
                  ▼
             ⑤ cmake/deploy-runtime.cmake ← 每次编译成功后:真正复制 jar 到 assets/
```

| 时间点 | 谁在干活 | 产出 |
|--------|---------|------|
| 双击 bat | CMake configure:②③④ 依次执行 | `build_vs2022/launcher.sln`(内含工作目录=`assets/`、POST_BUILD 钩子) |
| VS 点"生成" | 编译 `launcher.cpp` → 官方函数拷引擎 DLL → ⑤ 复制 jar | `runtime/Debug/launcher.exe` + `assets/` 下 jar 齐备 |
| F5 / Ctrl+F5 | 进程以 `assets/` 为工作目录启动 | 引擎按 `./launcher.kzb.cfg` 读 kzb、按 `./kzjvm.jar` 起 JVM、加载 `./DroidDataSourceplugin.jar` |

> 隐含约定贯穿全程:**Studio 的 Export 目录、CMake 的 `KANZI_KZB_DIRECTORY`、
> VS 调试工作目录,三者都指向仓库根 `assets/`**。kzb 由 Studio 导出进去,
> jar 由 CMake 编译后送进去,运行时引擎从同一目录读出来。任何一环指错目录,
> 就会出现"找不到 xxx"系列错误。

---

## 二、逐文件讲解(按执行顺序)

### ① `generate_cmake_vs2022_solution.bat`

```bat
cmake -S . -B build_vs2022 -G "Visual Studio 17 2022" -A x64 -T v142
```

- `-S .`:源码目录(`Application/`,含 `CMakeLists.txt`);`-B build_vs2022`:生成的 `.sln`/`.vcxproj` 输出目录;
- `-G "Visual Studio 17 2022"`:用 VS2022 打开;
- **`-T v142` 是关键**:强制使用 VS2019 工具集编译。因为 Kanzi 引擎 DLL 是
  `GL_vs2019_Debug_DLL` 这类 vs2019 编译的版本,exe 必须用同代工具链才二进制兼容。
  这就是 configure 日志里编译器是 `MSVC 19.29`(v142)而非 VS2022 默认 v143 的原因。

### ② `CMakeLists.txt`(总指挥)

configure 阶段从上到下执行:

1. **找到并加载引擎**:`find_kanzi()`(来自 ③)设好 `Kanzi_DIR` →
   `find_package(Kanzi)` 读官方 `KanziConfig.cmake`,引入所有 `Kanzi::xxx`
   库目标和官方辅助函数(`kanzi-common`)。日志里的
   `Found Boost / Found GLESv2 / ...` 都由这行触发。
2. **定义可执行文件**:`add_executable(launcher src/launcher.cpp)`,链接
   `Kanzi::kzappfw`(应用框架/主循环)、`Kanzi::kzui`、`Kanzi::kzcoreui`。
   Android 分支的 `--whole-archive` 是防止 JNI 入口符号被链接器裁掉,Windows 不走。
3. **CodeBehind 占位块**:每个子工程(car、environment……)若存在
   `CodeBehind/` 目录就编译链接进来;**目前仓库一个都没有,全部跳过**。
4. **定路径 + VS 调试工作目录**:

   ```cmake
   get_filename_component(KANZI_KZB_DIRECTORY ".../assets" ABSOLUTE)
   set_target_properties(launcher PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${KANZI_KZB_DIRECTORY}")
   ```

   `VS_DEBUGGER_WORKING_DIRECTORY` 写进生成的 `.vcxproj`——这就是
   "F5 时进程工作目录是 `assets\`"的出处。
5. **官方部署函数**:`install_kanzi_libs_to_output_directory()` 等三个,
   编译后把引擎 DLL、kzb 同步到 `build_vs2022/runtime/<Config>/`。
6. **推断 Studio 安装根**(系统 jar 来源):优先环境变量 `KANZI_STUDIO_HOME`;
   否则若 `KANZI_HOME` 下有 `Studio/Bin/EnginePlugins` 就沿用
   (日志 `KANZI_STUDIO_HOME=... (system jars)` 即此段输出)。
7. **挂插件部署**:`include(deploy-plugins.cmake)` +
   `deploy_kanzi_plugins(launcher <assets> <plugins>)`。

### ③ `cmake/kanzi-locate.cmake`(只干一件事:找引擎)

`find_kanzi()` 按四级优先级找 `KanziConfig.cmake`:

1. 命令行 `-DKanzi_DIR=...`;
2. **环境变量 `Kanzi_DIR`**(本机走这条,日志:
   `Using Kanzi from Kanzi_DIR environment variable: 'D:/KanziWorkspace_.../Engine/lib/cmake/Kanzi'`);
3. `KANZI_HOME` 下若存在 `Engine/lib/cmake/Kanzi` 才用——若 `KANZI_HOME`
   指向 Studio 安装(无 Engine),打一条 "treated as Studio install for jars"
   后跳过。**刻意设计:`Kanzi_DIR` 管引擎,`KANZI_HOME` 管 jar,互不干扰**;
4. 兜底:从工程目录逐级向上找(适配官方 `KanziWorkspace/Projects/` 布局)。

全部失败才 FATAL_ERROR 并提示设置 `Kanzi_DIR`。

### ④ `cmake/deploy-plugins.cmake`(configure 时登记,编译后触发)

只在 Windows 桌面生效(`if(NOT WIN32 OR ANDROID) return()`;Android 走 Gradle 打包)。做两件事:

1. `plugins/` 下若有自研 **DLL** 插件,登记 POST_BUILD 复制到 exe 目录
   (当前仓库只有 Java 插件,此段空转);
2. **核心**:给 `launcher` 挂一条 POST_BUILD 命令——每次编译成功后用
   `cmake -P` 以脚本模式执行 ⑤,传入 `$<CONFIG>`(生成器表达式,编译时才
   展开成 Debug/Release)、`assets/` 路径、`plugins/` 路径、`KANZI_STUDIO_HOME`。

> 注意:configure 阶段**什么都没复制**,只是把"编译完要跑这个脚本"写进 vcxproj。
> 所以 configure 日志里看不到任何 `deploy-runtime:` 输出——那些在**编译**时
> 才出现在 VS 的"生成"输出里。

### ⑤ `cmake/deploy-runtime.cmake`(每次编译后真正干活)

以独立脚本运行,三段逻辑:

1. **定成套配置**:`CONFIG` 为 Debug/RelWithDebInfo → `Debug` 后缀,否则 `Release`;
2. **复制系统 jar**:在 Studio 根下找 `EnginePlugins/GL_vs2019_<配置>`,要求
   `kzjava.jar` 与 `kzjvm.jar` **同时存在**才选用(防止 Debug 引擎配 Release jar
   的半套组合),把该目录全部 jar `copy_if_different` 到 `assets/`;
   找不到成套目录则打 WARNING 说明后果;
3. **复制业务插件**:`plugins/datasource/lib/java/.../DroidDataSourceplugin.jar`
   → `assets/` **根目录**(桌面引擎实际加载位置)+ `assets/lib/java/Debug|Release/`
   (Android 布局镜像)。

---

## 三、为什么 Ctrl+F5 正常、F5 调试"报 0xC0000005"?

**结论:那不是程序错误,是 HotSpot JVM 的正常工作机制;没有调试器时 JVM
自己悄悄处理掉,挂上调试器后 VS 抢先把它拦下来给你看。**

### 机制

HotSpot JVM(`jvm.dll`)在设计上就**故意制造访问冲突**来实现两个优化:

- **隐式空指针检查**:JIT 代码不逐一写 `if (ptr == null)`,而是直接解引用;
  真遇到 null 触发一次"读地址 0"的访问冲突,由 JVM 注册的异常处理器接住,
  转换成 Java 的 `NullPointerException` 或按预期路径恢复;
- **Safepoint 轮询**:通过访问受保护内存页让所有 Java 线程在 GC 等时机停下,
  同样靠硬件异常实现。

### 两种运行方式的差别

| 运行方式 | 异常的去向 |
|---------|-----------|
| Ctrl+F5(无调试器) | 异常直接交给 JVM 的处理器,静默恢复,什么都看不到 |
| F5(挂调试器) | Windows 规定**调试器有 first-chance 优先知情权**,VS 先拦下来报告,再交还 JVM 处理 |

所以 F5 下看到的:

```text
0x... 处(位于 launcher.exe 中)引发的异常: 0xC0000005: 读取位置 0x0000000000000000 时发生访问冲突。
```

只是 VS 在**转播 JVM 的内部机制**。特征佐证:

- 异常地址是高位动态地址(JIT 生成的代码区,不属于任何 DLL 模块);
- 进程退出码是 **0**,不是 0xC0000005(真崩溃时退出码就是异常码);
- `assets\` 下**没有** `hs_err_pid*.log`(JVM 真崩溃必写此文件)。

若 VS 在此中断,按**继续(F5)**程序照常运行——它并没有崩。

### 一劳永逸:调整 VS 异常设置

**调试 → 窗口 → 异常设置**(Ctrl+Alt+E)→ Win32 Exceptions →
`c0000005 Access violation`:

- 简单做法:**取消勾选**。你自己 C++ 代码里真正的**未处理**访问冲突仍会让
  调试器中断,不影响排查真 bug;
- 精细做法:保持勾选,右键该项 → **编辑条件** → 添加
  "模块名称 **不等于** `*jvm.dll`",只放行 JVM 内部的这类异常。

### 判断真假崩溃的口诀

1. **以 Ctrl+F5 的行为为准**:窗口能出来 → F5 下的异常是噪音;
2. 看**退出码**:0 = 正常退出;0xC0000005 = 真崩溃;
3. 看 `assets\hs_err_pid*.log`:存在 = JVM 真崩溃(内附 Java 栈);
4. F5 中断时按继续,能继续跑 = 已被处理的 first-chance 异常。
