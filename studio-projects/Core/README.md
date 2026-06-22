# core — 共享资源工程

**工程名**:`core` · **产物**:`core.kzb` · **角色**:地基,被所有工程单向引用,**自己不引用任何工程**。

在 Kanzi Studio 中于本目录创建 `core.kzproj`,并提交工程文件与资源到此目录。

## 必须包含

```text
core.kzproj
├── Resource Dictionaries/
│   ├── Theme_Day            # 日间 token 取值(见 design-tokens/tokens.json)
│   ├── Theme_Night          # 夜间 token 取值
│   └── Base                 # 与主题无关:Font/Size/Motion token
├── Prefabs/
│   └── Components/          # 通用组件库(对外属性定义清晰)
│       Button / ToggleSwitch / Card / ListItem / Popup / Toast / Slider / ProgressBar / StatusBar
├── Data Sources/
│   └── VehicleData          # 按 contracts/vehicle-data.schema.json 建模(stub 值)
├── Localization/            # zh-CN / en 字符串表(见 docs/localization.md)
└── Fonts/                   # font_cjk(子集化)/ font_latin
```

## 约束

- 这里是**唯一**定义主题、通用组件、字体、数据契约、字符串表的地方。
- 任何被 2 个及以上模块需要的东西,下沉到这里。
- 命名冻结,只追加(见 docs/naming-conventions.md)。
- **先完成并导出 `core.kzb`,其它工程才能开工。**
