# _ModuleTemplate — 功能模块模板

新增功能模块时,**复制本目录结构**起步,保证所有模块风格统一、引用规范一致。

## 标准模块结构

```text
<module>.kzproj   (引用 core)
├── Prefabs/
│   ├── Pages/
│   │   └── <域>Page          # 模块根 Prefab(命名稳定,供下游按名加载)
│   └── Widgets/              # 本模块的组合控件
├── Materials & Textures/     # 本模块专属资源(通用的下沉 core)
└── State Managers / Animations/
```

## 接入清单(复制后逐项替换)

1. **工程名 / kzb 名**:全小写,如 `charging` → `charging.kzb`(见 naming-conventions.md)。
2. **引用 core**:添加对 `core` 的工程引用。
3. **根页面**:`Prefabs/Pages/<域>Page`,作为模块入口。
4. **数据绑定**:绑定到 `kzb://core/Data Sources/VehicleData/<分组>` 对应字段;含 `<signal>Valid` 故障态处理。
5. **文案**:全部走 `kzb://core/Localization/<key>`,zh-CN/en 双语,禁止硬编码。
6. **样式**:全部引用 `core` 的主题 token,禁止写死颜色/字号/圆角。
7. **导出**:独立导出 `<module>.kzb`,运行时依赖 `core.kzb`(见 export-kzb.md)。

## 自检(交付前)

- [ ] 无对 shell / 其他 module 的引用
- [ ] 无硬编码文字、颜色、尺寸
- [ ] 所有信号处理了 `Valid==false` 的故障态
- [ ] 根 Prefab / 绑定字段命名与契约一致且冻结
