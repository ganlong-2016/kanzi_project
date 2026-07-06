# car 3D 模型分组说明

> **当前优先级**: demo 暂停,car 3D 模型分组与可控性优先。

## 节点结构（`Prefabs/car`）

重组后 `car` 预制体内部结构:

```text
car (EmptyNode)
├── <ResourceDictionaryInNode>   (Studio 内部,勿动)
├── Body                           ← 车身 / 底盘 / 灯光等（非轮非门）
├── Wheels
│   ├── Wheel_FL                   ← 左前轮
│   ├── Wheel_FR                   ← 右前轮
│   ├── Wheel_RL                   ← 左后轮（含双轮部分）
│   └── Wheel_RR                   ← 右后轮
└── Doors
    ├── Door_FL                    ← 左前车门（空组 + 铰链 pivot）
    ├── Door_FR
    ├── Door_RL
    └── Door_RR
```

## 轮胎分组

按 `scania4.glb` 网格空间位置 + 材质（`teker.005` / `bb.005` / `Baki1.005` 等）划入四轮组:

| 组 | 包含网格（示例） |
|----|------------------|
| `Wheel_FL` | `Circle.028`, `Circle.032`, `Circle.033`, `Circle.037`, `Cube.014`, `Plane.007` |
| `Wheel_FR` | `Circle.011`, `Circle.016`, `Circle.020`, `Cube.012`, `Plane.008` |
| `Wheel_RL` | `Circle.001`, `Circle.004`, `Circle.006`, `Circle.010`, `Cube.005`, `Cube.008` |
| `Wheel_RR` | `Cube.006`, `Cube.007`, `Cube.010`, `Cube.016`, `Cube.020`, `Cube.021` |

**单独控制轮胎**: 在 Node Tree 选中 `Wheel_FL` 等组,改 `Render Transformation`（旋转 = 滚动,绕 Y 轴）;或给组加 **Animation Clip / 绑定** 驱动旋转。

> 原 GLB 导出名为 `Cube.014` 等 Blender 默认名,分组后请按上表在 Studio 里核对位置;若某轮 mesh 划错,在 Studio 里拖到正确 `Wheel_*` 下即可。

## 车门分组

**现状**: `scania4.glb` **没有独立车门网格**,车门与车身 `paint.005` 合并在一起。因此 `Door_*` 目前是**带铰链 pivot 的空 Empty Node**,供后续:

1. 在 Blender 拆出 `door_FL` … `door_RR` 四个对象后重新导入;或
2. 在 Studio 里把拆出的 mesh 拖到对应 `Door_*` 下。

`Door_*` 已预设 pivot 近似位置（米）:

| 节点 | Translation (X, Y, Z) |
|------|------------------------|
| `Door_FL` | (-1.15, 1.2, 1.2) |
| `Door_FR` | (1.15, 1.2, 1.2) |
| `Door_RL` | (-1.15, 1.2, 0.2) |
| `Door_RR` | (1.15, 1.2, 0.2) |

**开门动画**: 选中 `Door_FL` → 绕铰链轴（通常 Y）旋转 `Render Transformation`;或绑 `VehicleControl/doorFrontLeft` 等数据源字段（见 `assets/datasource.xml`）。

## 在 Kanzi Studio 中检查

1. 打开 `IVI/car/Car.kzproj` → `Prefabs` → 双击 `car`。
2. Node Tree 应看到 `Body` / `Wheels` / `Doors` 三个一级组。
3. 展开 `Wheels` → 四轮下应有轮胎/轮毂 mesh。
4. `Doors` 下四个空组,待拆模或手动拖 mesh。

## 重新生成分组（仓库脚本）

若从旧版 flat 列表恢复,可运行:

```bash
python3 scripts/group_car_model.py
```

（会按 `scripts/group_car_model.py` 内 `WHEEL_GROUPS` 表重写 `car` 预制体子节点。）

## 与数据源

| 数据字段 (`datasource.xml`) | 建议绑定目标 |
|-----------------------------|--------------|
| `VehicleControl/doorFrontLeft` | `Door_FL` 旋转 |
| `VehicleControl/doorFrontRight` | `Door_FR` |
| `VehicleControl/doorRearLeft` | `Door_RL` |
| `VehicleControl/doorRearRight` | `Door_RR` |
| `Vehicle/speed`（或新增 `wheelRotation`） | `Wheels` 或各 `Wheel_*` 绕轴旋转 |

绑定在 **launcher** 或 **car** 预制体 expose 属性上均可,见 [data-source.md](data-source.md)。
