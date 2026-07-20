# 按 Kanzi 官方 Application/bin 布局部署运行时文件。
# 参考:
# - Installing plugins: Preview Working Directory = ../Application/bin
# - Java plugins (3.9.5+): lib/java/Debug|Release/<plugin>.jar
# - kzjava.jar: 工作目录根下的 ./kzjava.jar
# - Studio 自带 kzjava.jar: Studio/Bin/EnginePlugins/GL_vs<VS>_<Debug|Release>/

cmake_minimum_required(VERSION 3.15)

if(NOT CONFIG)
    message(FATAL_ERROR "deploy-runtime.cmake: CONFIG not set (Debug/Release)")
endif()
if(NOT KZB_DIRECTORY)
    message(FATAL_ERROR "deploy-runtime.cmake: KZB_DIRECTORY not set")
endif()

if(CONFIG MATCHES "Debug|RelWithDebInfo")
    set(_build_suffix "Debug")
else()
    set(_build_suffix "Release")
endif()

# --- 解析 Studio 根目录 ---
set(_studio_candidates)
if(DEFINED ENV{KANZI_STUDIO_HOME} AND NOT "$ENV{KANZI_STUDIO_HOME}" STREQUAL "")
    list(APPEND _studio_candidates "$ENV{KANZI_STUDIO_HOME}")
endif()
if(DEFINED ENV{KANZI_HOME} AND NOT "$ENV{KANZI_HOME}" STREQUAL "")
    list(APPEND _studio_candidates "$ENV{KANZI_HOME}")
endif()

set(_engine_plugins_dir "")
foreach(_root IN LISTS _studio_candidates)
    foreach(_bin IN ITEMS "Studio/Bin" "Bin")
        set(_candidate "${_root}/${_bin}/EnginePlugins")
        if(IS_DIRECTORY "${_candidate}")
            set(_engine_plugins_dir "${_candidate}")
            break()
        endif()
    endforeach()
    if(_engine_plugins_dir)
        break()
    endif()
endforeach()

# --- kzjava.jar（系统，来自 Studio EnginePlugins，与 VS Debug/Release 对齐）---
set(_kzjava_src "")
if(_engine_plugins_dir)
    foreach(_vs IN ITEMS "vs2019" "vs2022")
        set(_path "${_engine_plugins_dir}/GL_${_vs}_${_build_suffix}/kzjava.jar")
        if(EXISTS "${_path}")
            set(_kzjava_src "${_path}")
            break()
        endif()
    endforeach()
endif()

if(_kzjava_src)
    file(MAKE_DIRECTORY "${KZB_DIRECTORY}")
    execute_process(COMMAND "${CMAKE_COMMAND}" -E copy_if_different
        "${_kzjava_src}" "${KZB_DIRECTORY}/kzjava.jar")
    message(STATUS "deploy-runtime: kzjava.jar <- ${_kzjava_src}")
else()
    message(WARNING "deploy-runtime: kzjava.jar not found under ${_engine_plugins_dir}/GL_vs*_${_build_suffix}/")
endif()

# --- 业务 Java 插件：仓库 plugins/ -> lib/java/<Debug|Release>/ ---
if(PLUGINS_DIRECTORY)
    set(_datasource "${PLUGINS_DIRECTORY}/datasource/lib/java/Release/DroidDataSourceplugin.jar")
    if(NOT EXISTS "${_datasource}")
        set(_datasource "${PLUGINS_DIRECTORY}/datasource/lib/java/Debug/DroidDataSourceplugin.jar")
    endif()
    if(EXISTS "${_datasource}")
        set(_dest_dir "${KZB_DIRECTORY}/lib/java/${_build_suffix}")
        file(MAKE_DIRECTORY "${_dest_dir}")
        execute_process(COMMAND "${CMAKE_COMMAND}" -E copy_if_different
            "${_datasource}" "${_dest_dir}/DroidDataSourceplugin.jar")
        message(STATUS "deploy-runtime: DroidDataSourceplugin.jar -> ${_dest_dir}/")
    else()
        message(WARNING "deploy-runtime: DroidDataSourceplugin.jar not found under ${PLUGINS_DIRECTORY}/datasource/")
    endif()
endif()
