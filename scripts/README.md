# Confluence 文档上传（Python）

将 `docs/architecture/` 下的架构文档（Markdown、PlantUML、draw.io）批量同步到 Confluence。行为与 Gradle 插件 `uploadAllDocsToConfluence` 对齐。

## 环境准备

```bash
cd scripts
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
```

需要本机已安装：

- **Python 3.10+**
- **Java 8+**（渲染 PlantUML；`plantuml.jar` 回退路径）
- **Java 21+**（可选，用于 `PlantUmlCliMain` 中文字体注册；推荐 Android Studio JBR）
- **draw.io Desktop CLI**（可选；无 CLI 时默认跳过 `.drawio`）

### Java 版本说明

`PlantUmlCliMain` 由 Gradle 以 **Java 21** 编译。若系统默认 `java` 是 17，脚本会**自动回退**到 `plantuml.jar` + Python 预处理。

若要启用完整中文渲染，请指定 Java 21：

```properties
# local.properties 或 gradle.properties
confluence.javaHome=C:\\Program Files\\Android\\Android Studio\\jbr
```

或环境变量：

```bash
set CONFLUENCE_JAVA=C:\Program Files\Android\Android Studio\jbr\bin\java.exe
```

## 配置凭据

与 Gradle 插件相同，任选其一（优先级：环境变量 > `local.properties` > `gradle.properties`）：

```properties
confluence.apiToken=your-token
confluence.url=https://confluence.scania.com.cn
confluence.parentPageId=93520482
confluence.drawioExecutable=D:\\Programs\\draw.io-30.0.4-windows\\draw.io.exe
confluence.plantumlFontName=Microsoft YaHei
```

或环境变量：`CONFLUENCE_API_TOKEN`、`CONFLUENCE_URL`、`CONFLUENCE_PARENT_PAGE_ID`。

## 上传

在仓库根目录执行：

```bash
python scripts/upload_docs_to_confluence.py
```

或：

```bash
python -m confluence_upload --project-root .
```

常用参数：

```bash
# 仅预览
python scripts/upload_docs_to_confluence.py --dry-run

# 指定文档目录
python scripts/upload_docs_to_confluence.py --docs-dir docs/architecture
```

## 生成物目录

| 类型 | 路径 |
|------|------|
| 最终 PNG | `docs/.confluence-export/`（gitignore） |
| PlantUML 临时目录 | `docs/architecture/**/.plantuml-tmp/`（任务后自动删除） |
| draw.io 临时目录 | `docs/.confluence-export/.work/drawio/` |

## 与 Gradle 插件的关系

- **Python 脚本**：`scripts/upload_docs_to_confluence.py`，适合 CI 或非 Gradle 环境
- **Gradle 任务**：`./gradlew uploadAllDocsToConfluence`，适合 Android 工程内一键上传

两者扫描同一 `docs/architecture/` 目录，共用 `gradle.properties` / `local.properties` 凭据。

PlantUML 渲染优先调用项目已构建的 `PlantUmlCliMain`（支持 Windows 中文）；若 jar 不存在，会回退到 `~/.gradle/caches` 中的 `plantuml.jar` 并做 Python 侧预处理。

## 目录结构

```
scripts/
├── requirements.txt
├── upload_docs_to_confluence.py      # 入口脚本
├── README.md
└── confluence_upload/
    ├── __main__.py                   # python -m confluence_upload
    ├── config.py                     # 配置加载
    ├── client.py                     # Confluence REST
    ├── scanner.py                    # 文档扫描
    ├── renderers.py                  # PlantUML / draw.io
    ├── document_renderer.py          # Markdown / 页面 HTML
    └── paths.py                      # 导出路径
```
