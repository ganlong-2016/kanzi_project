# scripts — 自动化脚本

| 子目录 | 用途 |
|--------|------|
| `build/` | 构建/打包脚本(预留) |
| `tools/` | 资源转换、代码生成、文档上传 |
| `ci/` | CI/CD Pipeline(预留) |

## tools 现有入口

```bash
# 重组 Car Prefab 分组
python3 scripts/tools/group_car_model.py

# Confluence 文档上传(需先配环境)
cd scripts/tools
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python upload_docs_to_confluence.py
```

更细的 Confluence 说明见历史文档段落;配置项与原先 `scripts/` 根目录时相同。
