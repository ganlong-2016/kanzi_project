# 架构图(PlantUML)

本目录是 PlantUML 源文件。Markdown 文档里另内嵌了 Mermaid 图(在 GitHub 可直接渲染),这里的 `.puml` 提供更完整、可导出的版本。

| 文件 | 内容 |
|------|------|
| `architecture-overview.puml` | 工程/组件关系(launcher / common / 模块 / 插件 / Android) |
| `data-flow.puml` | 数据源插件与绑定读写流 |
| `runtime-composition.puml` | 运行时节点组合(launcher 拼装模块) |
| `build-pipeline.puml` | 导出 kzb 与交付流水线 |

## 如何渲染

- VS Code:安装 **PlantUML** 扩展,打开 `.puml` 按 `Alt+D` 预览。
- 命令行:`plantuml docs/diagrams/*.puml`(需 Java + Graphviz),生成 PNG/SVG。
- 在线:把内容贴到 [plantuml.com](https://www.plantuml.com/plantuml)。
