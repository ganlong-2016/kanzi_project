# kanzi_project

Automotive IVI/HMI reference application built on the **Kanzi** framework (Rightware/Kanzi).
It is a single graphical `launcher` app composed of Kanzi Studio sub-projects:

- `IVI/launcher/` — main HMI app: C++ entry point (`Application/src/launcher.cpp`) + Kanzi Studio project (`Tool_project/launcher.kzproj`).
- `IVI/car/`, `IVI/environment/`, `IVI/common/` — 3D/asset sub-projects. Their compiled `.kzb` binaries are committed under each `Binary/` folder.
- `plugins/datasource/` — prebuilt Android/Java data-source plugin (`DroidDataSourceplugin.jar`).

## Cursor Cloud specific instructions

### Hard prerequisite: the proprietary Kanzi SDK (not in this repo)

Every build/run path depends on the **Kanzi SDK** (Kanzi Engine + Kanzi Studio), a commercial/licensed
product that is **not committed to this repo and cannot be installed freely**. Builds fail without it.

- The build locates the SDK via the `KANZI_HOME` environment variable (or `Kanzi_DIR`, or an
  Android `local.properties` `kanzi.home`, or a parent-dir search for `Engine/version.txt`).
  See `IVI/launcher/Application/cmake/kanzi-locate.cmake` and `configs/platforms/android_gradle/getkanzi.gradle`.
- Without the SDK, `cmake` fails with `ERROR: Could not locate Kanzi_DIR` / `Could not find a package
  configuration file provided by "Kanzi"`.
- The SDK is obtained via a Kanzi Account through **Kanzi Hub** (a Windows installer) with a valid
  license (Enterprise/trial/floating/dongle). See https://docs.kanzi.com and www.rightware.com/get-kanzi.
- **Kanzi Studio is Windows-only.** The `launcher.kzb` / `launcher.kzb.cfg` that `launcher.cpp` loads
  (`binaryName = "launcher.kzb.cfg"`) is **not** committed — it must be exported from `launcher.kzproj`
  using Kanzi Studio. The other `.kzb` assets (`common`, `car`, `environment`) are already committed.

Because of this, on a stock Cloud VM you can only configure/inspect; you cannot build, lint, test, or
run the application end-to-end until a licensed `KANZI_HOME` SDK is available.

### Toolchain (already present in the base image)

`cmake` (3.28), `gcc`/`g++` (13.3), `python3` (3.12), `java` (OpenJDK 21) are preinstalled.
Note: bare `cmake ..` may auto-select Clang, whose default link line misses `-lstdc++`; pass
`-DCMAKE_C_COMPILER=gcc -DCMAKE_CXX_COMPILER=g++` to use GCC. There are **no** repo-managed package
dependencies (no `requirements.txt`, `package.json`, etc.), so nothing needs installing here.

### Build / run (only works with a licensed `KANZI_HOME` set)

- Desktop (CMake): from `IVI/launcher/Application`, `cmake -S . -B build && cmake --build build`,
  then run the `launcher` target from its `bin/` working dir. Needs a GPU/OpenGL(ES) surface.
- Android (Gradle): from `IVI/launcher/Application/configs/platforms/android_gradle`, use `./gradlew`
  (AGP 7.4.2, Kanzi Gradle plugin `com.rightware.gradle:kanzi:0.8.1`, NDK 21.3.6528147, compileSdk 28).
- There are no automated tests, lint config, or CI in this repo.
