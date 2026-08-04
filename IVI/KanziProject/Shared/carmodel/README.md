# carmodel — 车型专属 3D 资源

按车型变体分目录存放 glb / 专属贴图 / 参数源文件:

- `v101_sedan/`
- `v102_suv/`
- `v201_ev/`

## 现状

当前工程使用的 `truck.glb` 仍在 [`../car/3D Assets/`](../car/3D%20Assets/)（`Car.kzproj` 的 `ImportedFrom` 指向工程内路径）。出现多车型切换需求时,再迁移到本目录对应变体下并统一 Import。
