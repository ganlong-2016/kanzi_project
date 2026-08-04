# 卡车 3D 模型标准拆件分组规范

> 本文是**目标规范**:给美术(Blender/DCC)拆模、给 Studio 侧建组用的完整分组标准。
> `car` 模块**当前实际分组**(`scania4.glb` 的过渡态)见 [car-model-grouping.md](car-model-grouping.md);命名铁律见 [architecture/naming-conventions.md](architecture/naming-conventions.md)。

## 1. 拆件核心原则

拆不拆、怎么分组,只看一条:

> **凡是需要独立"动、亮、换材质、显隐"的部件,必须是独立 mesh + 独立节点,且 pivot(轴心)放在它的物理转轴/滑轨上;不需要独立控制的,全部合并进静态组以减少 Draw Call。**

由此派生的四条规则:

1. **层级 = 物理从属**。窗装在门里,门开时窗要跟着转,所以 `Window_*` 必须是 `Door_*` 的子节点;镜子装在门上就挂门下,装在 A 柱上才挂驾驶室下。
2. **Pivot = 物理转轴**。开门绕铰链、车轮绕轮心、转向绕主销;pivot 错了动画就得靠补偿变换硬凑,后患无穷。
3. **两种旋转不共用一个节点**。转向(Yaw)与滚动(Pitch)分两级:`Steer_FL`(空节点,只转 Yaw)嵌套 `Wheel_FL`(mesh,只转 Pitch),否则两个旋转互相污染。
4. **透明与自发光材质独立成件**。玻璃需要单独的渲染排序,车灯"点亮"是切 emissive 材质而不是动 transform,都要求 mesh 独立。

## 2. 完整节点树(标准版,无驾驶室前倾)

坐标原点:**后轴中心投影到地面**;车头朝向 +Z(与 Studio 内约定一致,导入后核对)。

```text
Truck (Root, EmptyNode)
├── Body                              ← 静态合并组(非动件,尽量合并减少 Draw Call)
│   ├── Cab_Shell                     ← 驾驶室外壳 / 车漆件 / 塑料包围
│   ├── Chassis_Frame                 ← 大梁、悬架、传动轴、油箱、尿素罐、储气罐
│   ├── Fifth_Wheel                   ← 牵引座 / 鞍座(挂车连接锚点,子节点留 Trailer_Anchor 空节点)
│   ├── Interior                      ← 内饰(仅座舱视角 / 透明车窗方案需要时保留)
│   └── Glass_Static                  ← 固定玻璃:前挡风、后窗、角窗(透明材质独立排序)
│
├── Doors
│   ├── Door_FL                       ← 左前门组(空节点,Pivot 在前缘铰链轴)
│   │   ├── DoorShell_FL              ← 门壳 mesh(含内饰板)
│   │   ├── Window_FL                 ← 升降玻璃(沿门本地导轨方向平移,开度 0-100)
│   │   └── Mirror_L                  ← 后视镜(若装在门上;Pivot 在折叠轴)
│   ├── Door_FR
│   │   ├── DoorShell_FR
│   │   ├── Window_FR
│   │   └── Mirror_R
│   └── (双排座 / 乘员舱车型才有 Door_RL / Door_RR,结构同上)
│
├── Wheels                            ← 每个轮位一组
│   ├── Steer_FL                      ← 左前转向空节点(Pivot 在主销垂直轴,只转 Yaw)
│   │   └── Wheel_FL                  ← 左前轮 mesh(Pivot 在轮心,只转 Pitch = 滚动)
│   ├── Steer_FR
│   │   └── Wheel_FR
│   ├── Wheel_RL                      ← 后驱动轮(双胎并装合并为单 mesh,Pivot 在轮心)
│   ├── Wheel_RR
│   └── (三轴车型:Wheel_ML / Wheel_MR,浮动轴可再套升降空节点)
│
├── Lights                            ← 仅自发光面(Emissive Mesh);灯壳外罩留在 Body/Glass_Static
│   ├── Headlight_L / Headlight_R     ← 近光 / 远光(保险杠内,随底盘)
│   ├── DRL_L / DRL_R                 ← 日间行车灯
│   ├── FogLight_L / FogLight_R      ← 前雾灯
│   ├── TurnSignal_FL / FR / RL / RR ← 转向灯(含镜壳转向灯可并入对应件)
│   ├── Taillight_L / Taillight_R    ← 尾灯 / 刹车灯(共用灯罩时单 mesh,亮度用材质状态切换)
│   ├── ReverseLight_L / ReverseLight_R ← 倒车灯
│   ├── MarkerLights                  ← 顶部示廓灯 / 侧标志灯组(法规灯,可合并为一件统一点亮)
│   └── Worklight                     ← 车尾工作灯
│
└── Movables                          ← 其余动件 / 交互件
    ├── Wiper_L / Wiper_R             ← 雨刮(Pivot 在摆轴)
    ├── Grille_Front                  ← 前格栅 / 检修盖(Pivot 在顶部或底部铰链)
    ├── ChargePort_Door               ← 充电口盖(Pivot 在铰链)
    ├── FuelCap                       ← 油箱盖 / 尿素口盖
    └── SunVisor                      ← 外遮阳罩(通常静态,可并入 Body;需动才独立)
```

要点:

- **`Window_*`、`Mirror_*` 在 `Door_*` 之下**,不在 `Movables` 平级——开门时它们必须随门转。
- **灯按安装位置归属**:保险杠灯随底盘;顶置示廓灯如果做驾驶室前倾(§3)要挂到 Cab 组里。
- 非动件(踏板、挡泥板、排气管、天线等)一律并进 `Body` 子组,不单独建节点。

## 3. 扩展版:驾驶室前倾(Cab Tilt)

平头卡车(Scania 等)没有独立引擎盖,对应的"检修/展示"动作是**驾驶室整体前倾**。
`Cab_Tilt` 不是 `Movables` 里的叶子——它必须是所有驾驶室部件的**祖先节点**:

```text
Truck (Root)
├── Cab_Tilt                          ← 空节点,Pivot 在驾驶室前端翻转轴
│   ├── Cab_Shell / Interior / Glass_Static(前挡、侧窗)
│   ├── Doors(整组,含窗、镜)
│   ├── Wiper_L / Wiper_R
│   ├── Grille_Front
│   └── MarkerLights(顶置灯随驾驶室)
├── Chassis_Frame / Fifth_Wheel       ← 不随驾驶室翻
├── Wheels
├── Lights(保险杠内灯组,随底盘)
└── Movables(ChargePort_Door / FuelCap 等底盘侧动件)
```

> **不做前倾功能就不要这层**:多一级嵌套所有驾驶室部件的世界变换就多算一级,别为用不到的功能付渲染成本。

## 4. 挂车(Trailer)

挂车**单独一个 Root**(独立 Prefab / 独立 glb),运行时通过 `Fifth_Wheel/Trailer_Anchor` 锚点做父子绑定,便于单独展示、更换挂车类型:

```text
Trailer (Root, 原点在牵引销 Kingpin)
├── Trailer_Body                      ← 厢体 / 大梁(静态合并)
├── Landing_Gear                      ← 支腿(可收放,Pivot 在收放轴)
├── Trailer_Doors
│   ├── Trailer_Door_L / Trailer_Door_R ← 后开门(Pivot 在侧铰链,开度可达 270°)
├── Trailer_Wheels
│   ├── Wheel_T1L / T1R / T2L / T2R / T3L / T3R ← 三轴六轮位
└── Trailer_Lights
    ├── Taillight_L/R、TurnSignal_L/R、ReverseLight_L/R、MarkerLights
```

## 5. Pivot 与轴向约定

一律用**本地轴**表述(glTF 导入 Kanzi 后世界轴向可能与 Blender 不一致,以本地轴为准):

| 部件 | Pivot 位置 | 运动 | 本地轴 | 典型范围 |
|------|-----------|------|--------|----------|
| `Door_*` | 前缘铰链轴 | 旋转 | Y(垂直) | 0° ~ 65° |
| `Window_*` | 玻璃底边中点 | 平移 | 沿门导轨方向 | 0 ~ 行程(开度 0-100 映射) |
| `Steer_*` | 主销垂直轴 | 旋转(Yaw) | Y | -35° ~ +35° |
| `Wheel_*` | 轮心 | 旋转(Pitch = 滚动) | X(轮轴) | 连续 |
| `Mirror_*` | 折叠轴 | 旋转 | Y | 0° ~ 90° |
| `Wiper_*` | 摆轴 | 旋转 | 垂直于风挡 | 0° ~ 90° |
| `Grille_Front` | 顶部/底部铰链 | 旋转 | X(横向) | 0° ~ 45° |
| `Cab_Tilt` | 驾驶室前端翻转轴 | 旋转 | X(横向) | 0° ~ 60° |
| `ChargePort_Door` / `FuelCap` | 铰链 | 旋转 | 视安装 | 0° ~ 90° |
| `Landing_Gear` | 收放轴 | 旋转 | X(横向) | 0° ~ 90° |
| `Trailer_Door_*` | 侧铰链 | 旋转 | Y | 0° ~ 270° |

## 6. 材质拆分要求

| 材质组 | 覆盖件 | 要求 |
|--------|--------|------|
| 车漆 Paint | Cab_Shell、DoorShell_* | 独立材质,支持换色(clear coat) |
| 玻璃 Glass | Glass_Static、Window_* | 透明,独立渲染队列;窗与固定玻璃**分 mesh 不必分材质** |
| 灯罩发光面 Emissive | Lights 下所有件 | 每个功能灯独立材质槽(或共用材质 + 属性覆盖),亮/灭 = 切 emissive |
| 轮胎橡胶 / 轮毂金属 | Wheel_* | 胎、毂可同 mesh 分材质槽 |
| 底盘金属 / 塑料 | Chassis_Frame 等 | 可合并,使用图集贴图 |
| 镜面 Mirror | Mirror_* 镜片 | 需要实时反射时独立材质(RTT / cubemap) |

## 7. 命名规范(与 [naming-conventions.md](architecture/naming-conventions.md) 对齐)

- **节点 / 组**:PascalCase + 位置后缀 `_FL/_FR/_RL/_RR/_L/_R`,与 `datasource.xml` 字段后缀一致(`Wheel_FL` ↔ `statusFL`)。
- **DCC 侧 mesh**:`内外饰_部件_功能_材质`,如 `ext_door_fl_hinge_metal`、`ext_wheel_fl_tire_rubber`。**禁止交付 Blender 默认名**(`Cube.014`、`Circle.076`)。
- 命名交付后**冻结,只追加不改名**;禁止中文、空格、特殊字符。
- 命名统一后,Studio 侧分组脚本(`scripts/tools/group_car_model.py`)可从"按网格名对表猜位置"简化为**按命名前缀直接归组**。

## 8. 与数据契约(`IVI/assets/xml/datasource.xml`)的映射

### 8.1 现有字段 → 节点

| 数据字段 | 绑定目标 | 驱动方式 |
|----------|----------|----------|
| `VehicleControl/doorFrontLeft` … `doorRearRight` | `Door_FL` … `Door_RR` | bool → 铰链旋转(状态机/动画) |
| `VehicleControl/windowFrontLeft` | `Door_FL/Window_FL` | 开度 0-100 → 导轨平移 |
| `VehicleControl/headlightOn` | `Lights/Headlight_L`、`Headlight_R` | bool → emissive 材质切换 |
| `Vehicle/speed` | `Wheels` 各 `Wheel_*` | 速度 → 滚动角速度 |
| `Vehicle/gear`(R 挡) | `Lights/ReverseLight_*` | 枚举 → emissive |
| `Chassis/suspensionLevel` | `Truck` 根或 `Body` | 高度档 → 整车 Y 平移(状态机 sm-chassis) |
| `Tires/statusFL` … | `Wheel_*`(高亮/故障材质) | 枚举 → 材质/描边(状态机 sm-tires) |
| `Charging/plugConnected` | `Movables/ChargePort_Door` | bool → 口盖开合 |

### 8.2 建议追加的字段(拆模前与数据侧一起定稿)

| 建议字段 | 类型 | 对应节点 |
|----------|------|----------|
| `VehicleControl/windowFrontRight` | int(0-100) | `Window_FR` |
| `VehicleControl/mirrorFolded` | bool | `Mirror_L/R` |
| `VehicleControl/turnSignal` | int(0 无 1 左 2 右 3 双闪) | `TurnSignal_*` |
| `VehicleControl/wiperLevel` | int(0-3) | `Wiper_*` |
| `VehicleControl/steeringAngle` | float(°) | `Steer_FL/FR` |
| `VehicleControl/markerLightOn` | bool | `MarkerLights` |
| `VehicleControl/cabTilt` | float(0-100)(若做 §3) | `Cab_Tilt` |

> 原则:**先定交互列表和数据字段,再拆模**——避免美术拆了引擎侧用不上的件,或引擎要控的件没拆出来。

## 9. 拆模验收清单(交付评审用)

- [ ] 每个动件独立 mesh + 语义化命名(§7),无 Blender 默认名
- [ ] 每个动件 pivot 在物理转轴/滑轨上,本地轴向符合 §5
- [ ] `Window_*` / 门装 `Mirror_*` 是 `Door_*` 的子节点(开门联动验证)
- [ ] 转向轮为 `Steer_*` ▶ `Wheel_*` 两级嵌套,两级旋转互不污染
- [ ] 玻璃、灯发光面材质独立;车漆支持换色
- [ ] 非动件已合并进 `Body` 子组(检查 Draw Call 数)
- [ ] (若做前倾)驾驶室部件全部在 `Cab_Tilt` 之下,翻转联动验证
- [ ] 节点后缀与 `datasource.xml` 字段后缀一一对应(§8)
- [ ] 挂车独立 Root,牵引销原点、`Trailer_Anchor` 锚点就位(§4)
- [ ] 导入 Kanzi 后在 Preview 中逐件验证 transform(转门、升窗、转轮)无位移漂移
