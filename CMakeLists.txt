# 根构建入口：整仓唯一 CMake 起点，等价于直接在 IVI/KanziProject/launcher/Application 下配置。
#
#   cmake -S . -B build_vs2022 -G "Visual Studio 17 2022" -A x64 -T v142
#
# 也可继续使用 IVI/KanziProject/launcher/Application/generate_cmake_vs20xx_solution.bat（两者产物一致）。
# 详见 docs/cmake-build-and-run.md 与 docs/repo-structure.md。

cmake_minimum_required(VERSION 3.15)

project(Scania_IVI)

add_subdirectory(IVI/KanziProject/launcher/Application)
