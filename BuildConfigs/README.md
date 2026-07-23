# BuildConfigs — 构建变体配置（预留）

按量产级工程结构建议预留,用于存放**按变体区分**的构建配置,例如:

- 不同车型 / 屏幕分辨率的 `application.cfg`
- 不同变体要打包的 kzb 清单
- Debug / Release / 量产签名等差异化配置

## 现状

- 当前唯一的运行时配置 `application.cfg` 在 [`IVI/assets/`](../IVI/assets/)(Kanzi 运行时工作目录,运行时按裸文件名读取,不能移走)。
- 平台构建配置在 [`IVI/launcher/Application/configs/platforms/`](../IVI/launcher/Application/configs/)(Kanzi 官方应用工程模板自带,CMake 依赖该路径)。

出现第二个构建变体时,在本目录建 `<变体名>/`,由 CMake 选项(如 `-DIVI_VARIANT=xxx`)在构建期把对应配置复制/生成到 `IVI/assets/`,而不是手工改动运行时目录。
