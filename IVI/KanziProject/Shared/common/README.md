# Shared/common — 共享资源工程

- **`common.kzproj`**:跨模块字体 / Color Brush / Theme / Named Style(被 `kzb://common/...` 引用)。
- **`v101_sedan/` / `v102_suv/` / `v201_ev/`**:按车型扩展的共享资源预留目录(贴图包、主题增量等);**不要**把 `common.kzproj` 拆进变体目录。

其他工程引用路径(相对本模块旁路):

```text
..\Shared\common\common.kzproj
```

(从 `launcher/Tool_project` 则为 `..\..\Shared\common\common.kzproj`。)
