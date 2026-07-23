# car 3D 模型分组

> 本文描述 `truck.glb` 的**当前实际分组**(过渡态);拆模与分组的**目标规范**(完整节点树、pivot/轴向、材质、验收清单)见 [truck-model-grouping-spec.md](truck-model-grouping-spec.md)。
>
> 3D 场景里**摄像头视角切换与滑动手势**的协作说明见 [architecture/camera-view-and-gesture.md](architecture/camera-view-and-gesture.md)。

> **当前优先级**: demo 暂停,car 3D 模型分组与可控性优先。

## 节点结构（`Prefabs/Car`）

按规范重组后 `Car` 预制体内部结构（**加粗** = 有 mesh;其余为**空分组预留**,等拆模后填入）:

```text
Car (EmptyNode)
├── Body
│   ├── Cab_Shell        ← 驾驶室外壳 18 mesh（a08, a18–a32 系列）
│   ├── Chassis_Frame    ← 底盘/大梁/踏板/保险杠 10 mesh（a01–a10 系列, a45, a46）
│   ├── Fifth_Wheel      ← 空,pivot ≈ (0, 1.3, -3.14)
│   │   └── Trailer_Anchor ← 空,挂车锚点预留
│   ├── Interior         ← 座舱件 a11 + SW（方向盘组 a12–a16）
│   └── Glass_Static     ← 前挡风玻璃 a17（玻璃材质 05 - Default.005）
├── Doors
│   ├── Door_FL          ← 左前门（pivot 在前缘铰链 (1.59, 3.0, 3.79)）
│   │   ├── DoorShell_FL ← 门壳 a18.002, a19.1, a21.3, a27.1
│   │   ├── Window_FL    ← 升降玻璃 window_L（pivot 在玻璃底边中点）
│   │   └── Mirror_L     ← 后视镜 a26.002, a31.002（pivot 在折叠轴）
│   └── Door_FR          ← 右前门,结构同上（window_R / a26.1, a31.1 等）
├── Wheels
│   ├── Steer_FL         ← 空转向节点,pivot 在主销轴 (1.49, 0.76, 2.20),只转 Yaw
│   │   └── Wheel_FL     ← 左前轮 a40–a44,绕轮心滚动
│   ├── Steer_FR
│   │   └── Wheel_FR     ← 右前轮 a53–a57
│   ├── Wheel_RL         ← 左后轮（双胎）a47–a52,pivot 在轮心 (1.30, 0.76, -3.14)
│   └── Wheel_RR         ← 右后轮 a58–a63
├── Lights
│   ├── Headlights       ← 前大灯灯罩 a05（HL_Glass 材质,单 mesh 横贯左右,暂未拆 L/R）
│   ├── Headlight_L / Headlight_R ← 空,预留（a05 拆分后填入）
│   ├── DRL_L/R、FogLight_L/R、TurnSignal_FL/FR/RL/RR、
│   │   Taillight_L/R、ReverseLight_L/R、MarkerLights、Worklight ← 空,预留
└── Movables
    ├── Wiper_L / Wiper_R      ← 空,预留
    ├── Grille_Front           ← 空,预留
    ├── ChargePort_Door        ← 空,预留
    └── FuelCap / SunVisor     ← 空,预留
```

坐标轴向（`truck.glb` 模型空间）: **+Z 车头方向,+X 左侧,Y 向上**;原点近似后轴投影。

## Pivot 与补偿变换

规范要求 pivot 在物理转轴上,但 glb 网格顶点是**模型空间烘焙坐标**,因此每个带 pivot 的组节点都在其子节点上放了**反向平移补偿**,净变换为 0(外观不变):

| 组节点 | Pivot (Translation) | 补偿位置 |
|--------|---------------------|----------|
| `Door_FL` | (1.59, 3.0, 3.79) 前缘铰链 | `DoorShell_FL` = (-1.59, -3.0, -3.79) |
| `Door_FR` | (-1.59, 3.0, 3.79) | `DoorShell_FR` 同理取反 |
| `Window_FL/FR` | 玻璃底边中点(相对门 (0, 0.18, -0.76)) | window mesh 节点 |
| `Mirror_L/R` | 折叠轴(相对门 (±0.17, 0.54, -0.39)) | 镜壳 mesh 节点 |
| `Steer_FL/FR` | 主销 (±1.49, 0.76, 2.20) | `Wheel_FL/FR` 内各 mesh |
| `Wheel_RL/RR` | 轮心 (±1.30, 0.76, -3.14) | 组内各 mesh |
| `Fifth_Wheel` | (0, 1.3, -3.14)(近似,空组) | 无 mesh,无需补偿 |

控制方式:

- **开门**: 旋转 `Door_FL` 的 `Render Transformation` 绕 Y 轴(0°~65°),窗和镜随门联动。
- **升窗**: 沿 `Window_FL` 本地导轨方向平移。
- **转向**: 旋转 `Steer_FL/FR` 绕 Y 轴(-35°~+35°)。
- **滚动**: 旋转 `Wheel_*` 绕 X 轴(轮轴),前轮在 `Steer_*` 内,两级旋转互不污染。
- **大灯**: `Lights/Headlights`(a05)切 emissive 材质;拆出 L/R mesh 后移入 `Headlight_L/R`。

## 现状与待拆模项

`truck.glb` 网格仍是 `a01`…`a63` 编号名(违反规范 §7 命名铁律),且以下部件**没有独立 mesh**,对应空分组仅占位:

- `Fifth_Wheel`(牵引座)、`Lights` 下除 `Headlights` 外的所有功能灯、`Movables` 全部(雨刮/格栅/充电口盖/油箱盖/遮阳罩)。
- `Headlights` 的 a05 是横贯左右的单 mesh,无法单侧点亮,需在 DCC 拆成 `Headlight_L/R`。

拆模交付要求见 [truck-model-grouping-spec.md](truck-model-grouping-spec.md) §7–§9。

## 在 Kanzi Studio 中检查

1. 打开 `IVI/car/Car.kzproj` → `Prefabs` → 双击 `Car`。
2. Node Tree 应看到 `Body` / `Doors` / `Wheels` / `Lights` / `Movables` 五个一级组。
3. 选中 `Door_FL` 绕 Y 轴旋转,门壳、窗、镜应绕前缘铰链联动;选中 `Wheel_FL` 绕 X 轴旋转应绕轮心滚动,无位移漂移。
4. 空分组(`Movables` 等)选中后 gizmo 应落在对应物理位置附近(近似值,拆模后精调)。

## 重新生成分组（仓库脚本）

若从旧版结构恢复,可运行:

```bash
python3 scripts/group_car_model.py
```

（会按脚本内的网格分配表与 pivot 表重写 `Car` 预制体子节点;网格→分组的归属依据是 `truck.glb` 的包围盒空间位置 + 材质分析,见脚本头部注释。）

## 与数据源

| 数据字段 (`datasource.xml`) | 建议绑定目标 |
|-----------------------------|--------------|
| `VehicleControl/doorFrontLeft` | `Doors/Door_FL` 旋转 |
| `VehicleControl/doorFrontRight` | `Doors/Door_FR` |
| `VehicleControl/windowFrontLeft` | `Door_FL/Window_FL` 平移 |
| `VehicleControl/headlightOn` | `Lights/Headlights` emissive 切换 |
| `Vehicle/speed`（或新增 `wheelRotation`） | 各 `Wheel_*` 绕轮轴旋转 |
| 新增 `VehicleControl/steeringAngle` | `Steer_FL/FR` 绕 Y 旋转 |

绑定在 **launcher** 或 **car** 预制体 expose 属性上均可,见 [data-source.md](data-source.md)。完整字段映射见 [truck-model-grouping-spec.md](truck-model-grouping-spec.md) §8。
