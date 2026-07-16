# 业务插件：仓库 plugins/
# 系统插件（kzjava.jar 等）：Kanzi 安装目录（KANZI_HOME / KANZI_STUDIO_HOME）

function(_kanzi_resolve_roots _workspace_out _studio_out)
    unset(_workspace)
    unset(_studio)

    if(DEFINED KANZI_ROOT AND NOT "${KANZI_ROOT}" STREQUAL "")
        set(_workspace "${KANZI_ROOT}")
    elseif(DEFINED ENV{KANZI_HOME} AND NOT "$ENV{KANZI_HOME}" STREQUAL "")
        set(_workspace "$ENV{KANZI_HOME}")
    endif()

    if(DEFINED ENV{KANZI_STUDIO_HOME} AND NOT "$ENV{KANZI_STUDIO_HOME}" STREQUAL "")
        set(_studio "$ENV{KANZI_STUDIO_HOME}")
    elseif(_workspace AND EXISTS "${_workspace}/Studio/Bin")
        set(_studio "${_workspace}")
    endif()

    set(${_workspace_out} "${_workspace}" PARENT_SCOPE)
    set(${_studio_out} "${_studio}" PARENT_SCOPE)
endfunction()

function(_kanzi_copy_first_existing _out_var)
    foreach(_candidate IN LISTS ARGN)
        if(EXISTS "${_candidate}")
            set(${_out_var} "${_candidate}" PARENT_SCOPE)
            return()
        endif()
    endforeach()
    unset(${_out_var} PARENT_SCOPE)
endfunction()

function(_kanzi_find_kzjava_jar _out_var kanzi_workspace kanzi_studio)
    set(_candidates)

    if(kanzi_workspace)
        list(APPEND _candidates
            "${kanzi_workspace}/Engine/lib/java/Debug/kzjava.jar"
            "${kanzi_workspace}/Engine/lib/java/Release/kzjava.jar"
            "${kanzi_workspace}/Engine/lib/java/kzjava.jar"
        )
        if(kanzi_studio STREQUAL kanzi_workspace OR NOT kanzi_studio)
            list(APPEND _candidates
                "${kanzi_workspace}/Studio/Bin/kzjava.jar"
                "${kanzi_workspace}/Studio/Bin/EnginePlugins/GL_vs2019_Debug/kzjava.jar"
                "${kanzi_workspace}/Studio/Bin/EnginePlugins/GL_vs2019_Release/kzjava.jar"
                "${kanzi_workspace}/Studio/Bin/EnginePlugins/GL_vs2022_Debug/kzjava.jar"
                "${kanzi_workspace}/Studio/Bin/EnginePlugins/GL_vs2022_Release/kzjava.jar"
            )
        endif()
    endif()

    if(kanzi_studio AND NOT kanzi_studio STREQUAL kanzi_workspace)
        list(APPEND _candidates
            "${kanzi_studio}/Studio/Bin/kzjava.jar"
            "${kanzi_studio}/Bin/kzjava.jar"
            "${kanzi_studio}/Bin/EnginePlugins/GL_vs2019_Debug/kzjava.jar"
            "${kanzi_studio}/Bin/EnginePlugins/GL_vs2019_Release/kzjava.jar"
            "${kanzi_studio}/Bin/EnginePlugins/GL_vs2022_Debug/kzjava.jar"
            "${kanzi_studio}/Bin/EnginePlugins/GL_vs2022_Release/kzjava.jar"
        )
    endif()

    _kanzi_copy_first_existing(_found ${_candidates})
    set(${_out_var} "${_found}" PARENT_SCOPE)
endfunction()

function(deploy_kanzi_plugins target kzb_directory plugins_directory)
    if(NOT WIN32 OR ANDROID)
        return()
    endif()

    # --- 业务插件：仓库 plugins/ ---
    if(IS_DIRECTORY "${plugins_directory}")
        set(_datasource_jar
            "${plugins_directory}/datasource/lib/java/Release/DroidDataSourceplugin.jar")
        if(EXISTS "${_datasource_jar}")
            add_custom_command(TARGET ${target} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}/lib/java/Release"
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_datasource_jar}"
                    "${kzb_directory}/lib/java/Release/DroidDataSourceplugin.jar"
                COMMENT "Deploy plugins/datasource -> assets/lib/java/Release/"
            )
        else()
            message(WARNING "Missing ${_datasource_jar}")
        endif()

        file(GLOB_RECURSE _custom_dlls
            "${plugins_directory}/*/lib/win64/*/*.dll")
        foreach(_dll IN LISTS _custom_dlls)
            add_custom_command(TARGET ${target} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_dll}" "$<TARGET_FILE_DIR:${target}>"
                COMMENT "Deploy custom plugin DLL from plugins/ -> exe directory"
            )
        endforeach()
    else()
        message(WARNING "plugins directory not found: ${plugins_directory}")
    endif()

    # --- 系统：kzjava.jar -> assets/（工作目录）---
    # kzjvm.dll 由 install_kanzi_libs_to_output_directory() 从 Engine/lib/Win64 部署，此处不重复复制。
    _kanzi_resolve_roots(_kanzi_workspace _kanzi_studio)
    if(NOT _kanzi_workspace AND NOT _kanzi_studio)
        message(WARNING "KANZI_HOME / KANZI_STUDIO_HOME not set — cannot deploy kzjava.jar to ${kzb_directory}")
        return()
    endif()

    _kanzi_find_kzjava_jar(_kzjava_jar "${_kanzi_workspace}" "${_kanzi_studio}")
    if(DEFINED _kzjava_jar)
        message(STATUS "deploy kzjava.jar: ${_kzjava_jar} -> ${kzb_directory}/kzjava.jar")
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_kzjava_jar}" "${kzb_directory}/kzjava.jar"
            COMMENT "Deploy kzjava.jar -> assets/ (VS working directory)"
        )
    else()
        message(WARNING
            "kzjava.jar not found. Searched under:\n"
            "  KANZI_HOME=${_kanzi_workspace}\n"
            "  KANZI_STUDIO_HOME=${_kanzi_studio}\n"
            "Set KANZI_STUDIO_HOME to Studio 安装根目录（如 D:/Kanzi 3_9_15_83），"
            "或手动复制 kzjava.jar 到 ${kzb_directory}/kzjava.jar")
    endif()
endfunction()
