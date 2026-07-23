# 仓库目录结构 — 分层设计与调整说明

> 本次结构调整参考了「量产级 Kanzi Studio 工程结构」建议稿,并结合本项目实际(kzproj 相对引用、Kanzi 运行时工作目录契约、现有 CMake 体系)落地。本文记录:**目标结构、每条调整的理由与收益、以及建议稿中哪些点没有照搬和为什么**。

## 1. 调整后的目录结构

```text
<repo>/
├── README.md
├── .gitattributes                # Git LFS(png/dds/otf/glb/jar/MeshData)
├── .gitignore
├── CMakeLists.txt                # ★新增:根构建入口
│
├── IVI/                          # ★ Kanzi Studio 构建工作区(自包含)
│   ├── assets/                   # ★从仓库根移入:kzb 导出 + 运行时工作目录
│   │   ├── datasource.xml        #   数据契约(单一来源)
│   │   ├── application.cfg
│   │   ├── Localization/         #   预留:本地化资源包
│   │   ├── lz4/                  #   预留:lz4 压缩资源包
│   │   └── pc_exe/               #   预留:桌面打包产物
│   ├── launcher/                 # 集成主工程(Tool_project + Application)
│   ├── common/                   # 共享资源工程(字体/主题/Brush)
│   ├── car/  car_setting/  environment/   # 功能子工程
│   └── demo/                     # 样板工程(暂停,保留作参考)
│
├── Shared/                       # ★新增:共享组件层(跨模块/跨端)
│   ├── Plugins/                  # ★从仓库根 plugins/ 移入:业务 Kanzi 插件
│   │   └── datasource/           #   Java 数据源插件(JAR)
│   └── Resources/                # ★新增:非 kzproj 管理的共享原始资源
│       ├── carmodel/             #   预留:车型变体资源(T101_Truck/ ...)
│       └── ota/                  #   预留:热更新资源包
│
├── BuildConfigs/                 # ★新增(预留):构建变体配置
├── Android/                      # ★新增(预留):Android 渲染侧工程
├── scripts/                      # 自动化脚本(模型分组 / Confluence 上传)
└── docs/                         # 文档与图源
```

## 2. 每条调整的理由与收益

### 2.1 `assets/` → `IVI/assets/`

**理由**:`assets/` 不是普通静态资源,它是各 kzproj 的 **kzb 导出目标 + 运行时工作目录**(`launcher.kzproj` 的 `BinaryExportDirectory`、VS 调试工作目录、CMake 的 `KANZI_KZB_DIRECTORY` 三者共同指向的地方),和 `IVI/` 下的工程是同一生命周期的东西。放在仓库根,和 `docs/`、`scripts/` 这类"仓库级"目录混在一起,层次是错的。

**收益**:

- **`IVI/` 成为自包含的 Studio 工作区**:工程源(kzproj)+ 产物/运行时(assets)都在一个目录里,拷走 `IVI/` 就能在 Studio 里完整工作;
- 仓库根只剩"仓库级"条目(构建入口、共享层、文档、脚本),一眼能看清分层;
- 与建议稿的 `IVI/assets/` 对齐,后续按建议稿演进(lz4 / pc_exe / Localization 分包)有明确落点。

**同步修改的路径引用**(这是本调整的全部代价,均已改完):

| 位置 | 修改 |
|------|------|
| `IVI/launcher/Tool_project/launcher.kzproj` | `BinaryExportDirectory`:`..\..\..\assets` → `..\..\assets`(2 处) |
| `IVI/launcher/Application/CMakeLists.txt` | `KANZI_KZB_DIRECTORY`:`../../../assets` → `../../assets` |
| `.gitignore` | `assets/*.jar`、`assets/lib/` → `IVI/assets/...` |
| Studio 各人本地 | **Project Properties → Preview Working Directory** 改为 `..\..\assets`(与 `Shared/Plugins/README.md` §4 表格一致) |
| 全部文档 | `assets/` 路径统一改为 `IVI/assets/` |

### 2.2 `plugins/` → `Shared/Plugins/`

**理由**:建议稿的 `Shared/` 是"跨模块复用层"。数据源插件(JAR)正是最典型的跨端复用件——桌面运行时由 CMake 复制进 `IVI/assets/`,Android 侧将来打进 apk;它不属于某个 Kanzi 工程,也不属于仓库根。

**收益**:

- 复用边界显式化:今后自研 C++ 插件(DLL)、第二个 Java 插件都进 `Shared/Plugins/<插件名>/`,`deploy-plugins.cmake` 的 DLL 通配部署逻辑已按该布局写好(`*/lib/win64/*/*.dll`),放进去即生效;
- 和 `Shared/Resources/` 一起构成完整的共享层,与 `IVI/`(工程)、`Android/`(端)的职责切分清晰。

**同步修改**:`CMakeLists.txt` 的 `REPO_PLUGINS_DIRECTORY` → `../../../Shared/Plugins`;文档路径同步。**Studio 里插件导入路径**下次重新导入时用 `Shared/Plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar`。

### 2.3 新增 `Shared/Resources/`(carmodel / ota,预留)

**理由**:建议稿要求车型专属资源(`carmodel/`)与热更新资源(`ota/`)有独立落点,按车型变体分目录。本项目当前只有一个车型(truck),glb 还在 `IVI/car/3D Assets/`(`Car.kzproj` 的 `ImportedFrom` 指向工程内路径,移动会破坏重导入链路),所以**先立目录与约定,不搬现有文件**——与"car 模型分组先建空组预留"同一思路:结构先行,内容随需求填入。

**收益**:第二个车型变体出现时,资源有约定好的去处(`carmodel/<变体>/`),不会散落进各工程;OTA 分包方案启动时不需要再讨论目录。

### 2.4 新增 `BuildConfigs/`、`Android/`(预留)

**理由**:建议稿中的构建变体层与 Android 端层,本项目现在还没有内容,但这两个是**确定会来的**(多分辨率/多车型变体的 `application.cfg`;Android 渲染侧工程)。预留目录 + README 说清"什么东西将来放这里、与现状的关系"(如 `application.cfg` 目前为何必须留在 `IVI/assets/` 根)。

**收益**:扩展点有名字、有文档,新成员不用猜"Android 工程该建在哪";也避免将来临时起意建出 `android_app/`、`configs2/` 这类随手目录。

### 2.5 新增根 `CMakeLists.txt`

**理由**:建议稿在仓库根有统一构建入口;原来构建必须 `cd IVI/launcher/Application` 再跑 bat,入口藏在三层目录下。

**收益**:`cmake -S . -B build_vs2022 -G "Visual Studio 17 2022" -A x64 -T v142` 在仓库根即可出解决方案;CI 接入不需要知道工程内部布局。原有 bat 入口**不受影响**,两者产物一致。

### 2.6 `IVI/assets/` 内新增 `Localization/`、`lz4/`、`pc_exe/`(预留)

对应建议稿 `IVI/assets` 下的分包目录。当前为空(`.gitkeep` 占位),用途见 [`IVI/assets/README.md`](../IVI/assets/README.md) 的目录布局表。

## 3. 建议稿中**没有照搬**的点及原因

| 建议稿 | 本仓库的做法 | 原因 |
|--------|--------------|------|
| `assets/kzb/`、`assets/xml/` 子目录 | kzb / cfg / `datasource.xml` / jar 一律留在 `IVI/assets/` **根** | **Kanzi 运行时契约**:引擎按 `./launcher.kzb.cfg`、`./kzjvm.jar` 相对**工作目录根**查找;`launcher.kzproj` 里数据源 File 属性是裸文件名 `datasource.xml`。拆子目录会直接跑不起来(详见 `Shared/Plugins/README.md` FAQ)。`Localization/ lz4/ pc_exe/` 只作预留,不迁移运行时必需文件 |
| 模块清单 `EV/ SR/ AVM/ aircondition/ vpa/` | 保留现有 `car/ car_setting/ environment/ demo/` | 那是另一产品形态的模块清单;本项目的模块就是现在这些。新模块按 [add-new-module.md](add-new-module.md) 建立,不预建空工程目录(空 kzproj 无法预留,反而制造死目录) |
| `Shared/Resources/Common/` | 用 `IVI/common/` 共享资源工程承担 | Kanzi 里"通用资源"要被其他工程 `kzb://` 引用,**必须是 kzproj 工程**,不能是裸文件目录;`common` 与其他工程的相对引用(`..\common\common.kzproj`)也不允许把它移出 `IVI/` |
| `Docs/`、`Scripts/`(大写) | 保留小写 `docs/`、`scripts/` | 纯大小写改名,在 Windows(大小写不敏感文件系统)上 git 改名极易出错,且会打断全部文档内链与 Confluence 上传脚本,零功能收益 |
| 车型变体三层全建(`V101_Sedan/` 等) | 只建 `carmodel/`、`ota/` 两层,变体目录随首个变体创建 | 变体代号应由产品定义(本项目是卡车,不会有 `V101_Sedan`),预建假代号只会误导 |

## 4. 调整后的分层原则(维护指南)

1. **`IVI/` = Studio 工作区**:所有 kzproj 工程与它们的导出/运行时目录。工程间引用全部是 `IVI/` 内部相对路径,整个目录可整体搬移。
2. **`Shared/` = 复用层**:不属于单个 Kanzi 工程、会被多端(桌面/Android)或多模块消费的东西——插件二进制、车型原始资产、OTA 包。
3. **仓库根 = 入口与元信息**:构建入口(`CMakeLists.txt`)、端接入点(`Android/`)、变体配置(`BuildConfigs/`)、文档(`docs/`)、脚本(`scripts/`)。
4. **预留目录必须带 README**:说明"将来放什么、怎么接入现状";空目录用 `.gitkeep` 占位。
5. **改动运行时路径 = 三处同改**:Studio Export 目录、CMake `KANZI_KZB_DIRECTORY`、VS 工作目录——三者必须永远指向同一目录(当前为 `IVI/assets/`)。
