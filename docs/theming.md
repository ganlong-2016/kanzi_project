# 主题(日 / 夜)方案

## 1. 目标

- 支持 **白天 `Day`** 与 **夜间 `Night`** 主题运行时切换。
- 所有颜色/字体/尺寸/动效时长一律 **token 化**,集中在 `core` 的 Resource Dictionary;**禁止在 Prefab 里写死任何样式值**。切换主题只换 Dictionary,不动任何 Prefab。

## 2. Studio 中的结构

```text
core / Resource Dictionaries/
├── Theme_Day        # 白天:各 token 的取值
├── Theme_Night      # 夜间:各 token 的取值
└── (可选) Base       # 与主题无关的尺寸/字号/动效时长等公共 token
```

- 组件与页面引用 token 键(如 `kzb://core/Resource Dictionaries/Color/Background`),取值由当前激活的主题决定。
- 运行时切换激活的 Resource Dictionary(Day/Night),所有引用自动刷新。

## 3. token 分类与键命名

键形如 `<类别>/<语义>`:

| 类别 | token 键 | 说明 |
|------|----------|------|
| Color | `Color/Background` | 页面背景 |
| Color | `Color/Surface` | 卡片/面板 |
| Color | `Color/Accent` | 品牌强调色 |
| Color | `Color/TextPrimary` | 主文字 |
| Color | `Color/TextSecondary` | 次文字 |
| Color | `Color/Divider` | 分隔线 |
| Color | `Color/Success` | 正常/成功(如充电中) |
| Color | `Color/Warning` | 告警(如胎压异常) |
| Color | `Color/Error` | 故障/不可用 |
| Font | `Font/Title` | 标题字体/字重/字号 |
| Font | `Font/Body` | 正文 |
| Font | `Font/Caption` | 辅助说明 |
| Size | `Size/RadiusS` `Size/RadiusM` `Size/RadiusL` | 圆角 |
| Size | `Size/SpacingS` `Size/SpacingM` `Size/SpacingL` | 间距 |
| Motion | `Motion/DurationFast` `Motion/DurationNormal` | 动效时长 |

> 取值见 `design-tokens/tokens.json`(供 Studio 内填 Resource Dictionary 时对齐;同时作为设计与开发的单一事实来源)。

## 4. 主题与状态色的关系(与故障显示)

- 故障/不可用状态统一用 `Color/Error` + 本地化 `common.unavailable`,**不要用默认值伪装正常**。
- 告警(如胎压偏低、充电异常)用 `Color/Warning`。
- 这些语义色在 Day/Night 两套主题里都要有清晰可辨的取值(尤其夜间避免过暗导致告警不可见)。

## 5. 反模式(严禁)

- 在 Prefab/节点上直接填十六进制颜色、固定字号、固定圆角。
- 为夜间单独复制一套 Prefab(应只切 Dictionary,不复制结构)。
- 主题 token 在某个模块里"就地覆盖"成硬编码值。
