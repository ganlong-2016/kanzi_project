@echo off
REM Generate VS2022 solution using MSVC toolset v142 (VS2019), matching Kanzi Engine GL_vs2019_* DLLs.
REM
REM Environment (two different roots!):
REM   KANZI_HOME        = Kanzi Workspace, e.g. D:\KanziWorkspace_3_9_15_83
REM   KANZI_STUDIO_HOME = Studio install,  e.g. D:\Kanzi 3_9_15_83   (optional, for kzjava.jar)

setlocal
cd /d "%~dp0"

if not defined KANZI_HOME (
  echo WARNING: KANZI_HOME is not set. Expected Workspace like D:\KanziWorkspace_3_9_15_83
)

cmake -S . -B build_vs2022 -G "Visual Studio 17 2022" -A x64 -T v142 %*
if errorlevel 1 exit /b 1
echo.
echo Open: %cd%\build_vs2022\launcher.sln
endlocal
