# Shared/common — 按车型区分的共享资源工程

每个车型变体各自一份 `common.kzproj`(字体 / Color Brush / Theme / Named Style,被 `kzb://common/...` 引用)。

| 目录 | 状态 |
|------|------|
| `v101_sedan/` | **当前使用**:`common.kzproj` + `Fonts/` + `Images/` |
| `v102_suv/` | 预留(后续补齐同结构) |
| `v201_ev/` | 预留(后续补齐同结构) |

其他工程引用路径(相对模块旁路,以当前车型为例):

```text
..\Shared\common\v101_sedan\common.kzproj
```

(从 `launcher/Tool_project` 则为 `..\..\Shared\common\v101_sedan\common.kzproj`。)

切换车型时,同步改各模块的 Project Reference 指向对应变体下的 `common.kzproj`。
