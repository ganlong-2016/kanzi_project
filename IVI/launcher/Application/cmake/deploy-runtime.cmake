# 按 Kanzi 官方 Application/bin 布局部署运行时文件。
# 工作目录根：kzjava.jar / kzjvm.jar（须与 VS Debug|Release 及引擎 DLL 成套）
# lib/java/Debug|Release/：业务 Java 插件

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

set(_studio_roots)
foreach(_cand IN ITEMS
        "${KANZI_STUDIO_HOME}"
        "$ENV{KANZI_STUDIO_HOME}"
        "${KANZI_HOME}"
        "$ENV{KANZI_HOME}")
    if(NOT "${_cand}" STREQUAL "")
        list(APPEND _studio_roots "${_cand}")
    endif()
endforeach()
list(REMOVE_DUPLICATES _studio_roots)

set(_engine_plugins_dir "")
foreach(_root IN LISTS _studio_roots)
    foreach(_bin IN ITEMS "Studio/Bin" "Bin")
        if(IS_DIRECTORY "${_root}/${_bin}/EnginePlugins")
            set(_engine_plugins_dir "${_root}/${_bin}/EnginePlugins")
            break()
        endif()
    endforeach()
    if(_engine_plugins_dir)
        break()
    endif()
endforeach()

# 只使用与当前 VS CONFIG 匹配的目录（禁止 Debug 引擎 + Release jar）
set(_selected_variant "")
if(_engine_plugins_dir)
    foreach(_vs IN ITEMS "vs2019" "vs2022")
        set(_dir "${_engine_plugins_dir}/GL_${_vs}_${_build_suffix}")
        if(EXISTS "${_dir}/kzjava.jar" AND EXISTS "${_dir}/kzjvm.jar")
            set(_selected_variant "${_dir}")
            break()
        endif()
    endforeach()
endif()

if(_selected_variant)
    file(MAKE_DIRECTORY "${KZB_DIRECTORY}")
    file(GLOB _system_jars "${_selected_variant}/*.jar")
    foreach(_jar IN LISTS _system_jars)
        get_filename_component(_jar_name "${_jar}" NAME)
        execute_process(COMMAND "${CMAKE_COMMAND}" -E copy_if_different
            "${_jar}" "${KZB_DIRECTORY}/${_jar_name}")
        message(STATUS "deploy-runtime: ${_jar_name} <- ${_jar}")
    endforeach()
else()
    message(WARNING
        "deploy-runtime: missing matching EnginePlugins jars for CONFIG=${CONFIG} (${_build_suffix}).\n"
        "  Need both kzjava.jar and kzjvm.jar under e.g.\n"
        "  ${_engine_plugins_dir}/GL_vs2019_${_build_suffix}/\n"
        "  Debug 构建勿用 Release 目录的 jar，否则易在 jvm.dll 加载后 0xC0000005 崩溃。")
endif()

# 业务插件：win32 的 Java PluginLoader 只查 "JAR plugin path"（桌面为 null）
# 和工作目录根，因此必须复制到 KZB_DIRECTORY 根；lib/java/<cfg>/ 布局仅 Android 使用。
if(PLUGINS_DIRECTORY)
    set(_datasource "${PLUGINS_DIRECTORY}/datasource/lib/java/Release/DroidDataSourceplugin.jar")
    if(NOT EXISTS "${_datasource}")
        set(_datasource "${PLUGINS_DIRECTORY}/datasource/lib/java/Debug/DroidDataSourceplugin.jar")
    endif()
    if(EXISTS "${_datasource}")
        execute_process(COMMAND "${CMAKE_COMMAND}" -E copy_if_different
            "${_datasource}" "${KZB_DIRECTORY}/DroidDataSourceplugin.jar")
        message(STATUS "deploy-runtime: DroidDataSourceplugin.jar -> ${KZB_DIRECTORY}/ (工作目录根，桌面加载路径)")
        foreach(_cfg IN ITEMS Debug Release)
            set(_dest_dir "${KZB_DIRECTORY}/lib/java/${_cfg}")
            file(MAKE_DIRECTORY "${_dest_dir}")
            execute_process(COMMAND "${CMAKE_COMMAND}" -E copy_if_different
                "${_datasource}" "${_dest_dir}/DroidDataSourceplugin.jar")
            message(STATUS "deploy-runtime: DroidDataSourceplugin.jar -> ${_dest_dir}/")
        endforeach()
    else()
        message(WARNING "deploy-runtime: DroidDataSourceplugin.jar not found under ${PLUGINS_DIRECTORY}/datasource/")
    endif()
endif()
