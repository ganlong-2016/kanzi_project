# launcher 运行时目录 (`Application/bin`)

> **本仓库 KZB 已改到仓库根 [`assets/`](../../../assets/README.md)**，VS 调试工作目录由 CMake 指向 `assets/`，不再使用本目录加载 kzb。
>
> 仅保留 `application.cfg` 作参考；实际运行请使用 `assets/application.cfg`。

## 历史说明（Kanzi 官方默认）

官方模板默认 Export KZB 到 `Application/bin`，并在 CMake 中设置 `VS_DEBUGGER_WORKING_DIRECTORY` 为此目录。
