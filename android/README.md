# Android — Android 渲染侧工程（预留）

按量产级工程结构建议预留。本仓库的产物是各 Kanzi 工程导出的 **kzb**(输出到 [`IVI/assets/`](../IVI/assets/)),由 Android 渲染侧加载并提供真实数据(见根 [README](../README.md) 架构总览)。

Android 工程(Gradle 工程、JNI 加载层、`lib/java/<Debug|Release>/` 业务 JAR 布局)接入本仓库时放在本目录,预期内容:

- `app/`:Android 应用工程,assets 里打包 kzb + `DroidDataSourceplugin.jar`
- 构建脚本:从 `IVI/assets/` 同步 kzb、从 `IVI/plugins/` 同步业务插件 JAR
