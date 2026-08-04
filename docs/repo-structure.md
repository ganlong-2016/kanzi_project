# 仓库目录结构 — Scania_IVI 分层

> 本仓库按 **Scania_IVI** 量产目录规划落地。本文记录目标结构、相对旧布局的迁移映射、以及因 Kanzi 运行时契约而未机械照搬的点。

## 1. 目标结构

```text
Scania_IVI/                         # 仓库根(=本仓库)
├── README.md
├── .gitignore
├── CMakeLists.txt                  # 顶层 CMake 入口
│
├── IVI/                            # [主工程] IVI 核心业务
│   ├── assets/                     # KZB 打包资源 & 运行时依赖
│   │   ├── localization/           # 多语言文本/资源包(预留)
│   │   ├── lz4/                    # LZ4 压缩资源块(预留)
│   │   ├── kzb/                    # 编译产物归档区(预留;运行时仍见 §3)
│   │   ├── xml/                    # 配置/数据契约(datasource.xml 等)
│   │   ├── pc_exe/                 # PC 模拟器打包产物(预留)
│   │   ├── application.cfg         # ★须留在 assets 根(引擎按裸文件名读)
│   │   └── *.jar / *.kzb …         # ★运行时工作目录根文件(见 §3)
│   │
│   ├── KanziProject/               # Kanzi Studio 工程根
│   │   ├── launcher/               # 启动器 & 全局状态(Tool_project + Application)
│   │   ├── environment/            # 3D 场景/光照
│   │   ├── car/                    # 3D 车模(当前主研)
│   │   ├── car_setting/            # 车辆设置
│   │   ├── demo/                   # 样板(暂停)
│   │   ├── ev/  sr/  avm/          # 预留模块(仅 README)
│   │   ├── aircondition/  vpa/     # 预留模块(仅 README)
│   │   └── Shared/
│   │       ├── common/             # 按车型: v101_sedan/common.kzproj (+ v102_suv / v201_ev 预留)
│   │       ├── ota/                # OTA 热更新预备
│   │       └── carmodel/           # 车型专属原始 3D/贴图
│   │
│   └── plugins/                    # 业务 Kanzi/Java 插件
│       └── datasource/             # 车辆数据源插件(JAR)
│
├── build_configs/                  # 构建变体(Debug/Release/车型/市场)
├── android/                        # Android 平台适配(预留)
├── tests/                          # unit / integration / uitest
├── scripts/
│   ├── build/                      # 构建/打包(预留)
│   ├── tools/                      # 资源转换、文档上传等
│   └── ci/                         # CI Pipeline(预留)
└── docs/
    ├── architecture/               # 架构设计
    ├── api/                        # 接口文档(预留)
    └── onboarding/                 # 新人入门
```

## 2. 相对旧结构的迁移映射

| 旧路径 | 新路径 |
|--------|--------|
| `IVI/launcher/` 等各 kzproj | `IVI/KanziProject/<module>/` |
| `IVI/common/` | `IVI/KanziProject/Shared/common/v101_sedan/` |
| `Shared/Plugins/` | `IVI/plugins/` |
| `Shared/Resources/{carmodel,ota}/` | `IVI/KanziProject/Shared/{carmodel,ota}/` |
| `BuildConfigs/` | `build_configs/` |
| `Android/` | `android/` |
| `IVI/assets/Localization/` | `IVI/assets/localization/` |
| `scripts/tools/group_car_model.py` 等 | `scripts/tools/` |
| — | 新增 `tests/`、`docs/api/`、`docs/onboarding/`、预留模块目录、`assets/kzb/` |

同步已改的引用:

- `launcher.kzproj`:`BinaryExportDirectory` → `..\..\..\assets`;`common` → `..\..\Shared\common\v101_sedan\common.kzproj`
- 子工程对 `common` 的引用 → `..\Shared\common\v101_sedan\common.kzproj`
- 根 `CMakeLists.txt` → `IVI/KanziProject/launcher/Application`
- `KANZI_KZB_DIRECTORY` / `REPO_PLUGINS_DIRECTORY` 深度与 `IVI/plugins` 路径

## 3. 未机械照搬的点(运行时契约)

| 建议路径 | 实际做法 | 原因 |
|----------|----------|------|
| 运行时 `*.kzb` / `*.jar` 只放 `assets/kzb/` | **Studio 导出与 VS 工作目录仍指向 `IVI/assets/` 根**;`assets/kzb/` 作归档/预留 | 引擎按工作目录根查找 `./launcher.kzb.cfg`、`./kzjvm.jar`;拆到子目录会直接跑不起来。归档流程就绪后再把“发布副本”同步进 `kzb/` |
| `application.cfg` 进变体目录 | 留在 `assets/` 根;`build_configs/` 存变体源,构建期复制进去 | 运行时按裸文件名读取 |
| 预留模块建空 `.kzproj` | 只放 `README.md` | 空 kzproj 无法预留相对引用,反而制造死工程;真正开做时按 [add-new-module.md](add-new-module.md) 创建 |
| 多车型共用一份 `common.kzproj` | **`common.kzproj` 按车型放在 `Shared/common/<variant>/`**(当前 `v101_sedan`) | 车型差异资源隔离;`kzb://common/...` 仍按工程名解析 |

## 4. 分层原则

1. **`IVI/assets/`** — 运行时工作目录 + 导出落点(引擎契约优先于“目录美观”)。
2. **`IVI/KanziProject/`** — 全部 Studio 工程与跨模块 Shared 资源。
3. **`IVI/plugins/`** — 业务插件二进制(桌面 CMake 部署到 assets;Android 将来打进 apk)。
4. **仓库根** — 构建入口、端适配、测试、脚本、文档。
5. **改运行时路径 = 三处同改**:Studio Export、`KANZI_KZB_DIRECTORY`、VS Working Directory。
