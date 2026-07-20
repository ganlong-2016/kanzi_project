@echo off
REM Generate VS2022 solution using MSVC toolset v142 (VS2019), matching Kanzi Engine GL_vs2019_* DLLs.
REM
REM Expected env (keep as-is if already set):
REM   Kanzi_DIR  = ...\KanziWorkspace_*\Engine\lib\cmake\Kanzi
REM   KANZI_HOME = Studio install (e.g. D:\Kanzi 3_9_15_83) for system jars

setlocal
cd /d "%~dp0"

cmake -S . -B build_vs2022 -G "Visual Studio 17 2022" -A x64 -T v142 %*
if errorlevel 1 exit /b 1
echo.
echo Open: %cd%\build_vs2022\launcher.sln
endlocal
