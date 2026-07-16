# 业务插件：仓库 plugins/
# 系统插件（kzjvm / kzjava 等）：Kanzi 安装目录（KANZI_HOME）

function(_kanzi_resolve_root _out_var)
    if(DEFINED KANZI_ROOT AND NOT "${KANZI_ROOT}" STREQUAL "")
        set(${_out_var} "${KANZI_ROOT}" PARENT_SCOPE)
    elseif(DEFINED ENV{KANZI_HOME} AND NOT "$ENV{KANZI_HOME}" STREQUAL "")
        set(${_out_var} "$ENV{KANZI_HOME}" PARENT_SCOPE)
    endif()
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

    # --- 系统插件：Kanzi 安装目录 ---
    _kanzi_resolve_root(_kanzi_root)
    if(NOT DEFINED _kanzi_root)
        message(WARNING "KANZI_HOME not set — cannot deploy kzjvm.dll / kzjava.jar")
        return()
    endif()

    _kanzi_copy_first_existing(_kzjava_jar
        "${_kanzi_root}/Engine/lib/java/kzjava.jar"
        "${_kanzi_root}/Engine/lib/java/Release/kzjava.jar"
    )
    if(DEFINED _kzjava_jar)
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_kzjava_jar}" "${kzb_directory}/kzjava.jar"
            COMMENT "Deploy kzjava.jar from Kanzi install -> assets/"
        )
    else()
        message(WARNING "kzjava.jar not found under ${_kanzi_root}/Engine/lib/java")
    endif()

    _kanzi_copy_first_existing(_kzjvm_dll
        "${_kanzi_root}/Studio/Bin/EnginePlugins/GL_vs2019_Release/kzjvm.dll"
        "${_kanzi_root}/Studio/Bin/EnginePlugins/GL_vs2022_Release/kzjvm.dll"
        "${_kanzi_root}/Studio/Bin/EnginePlugins/GL_vs2019_Debug/kzjvm.dll"
        "${_kanzi_root}/Studio/Bin/EnginePlugins/GL_vs2022_Debug/kzjvm.dll"
        "${_kanzi_root}/Engine/plugins/jvm/lib/win64/GL_vs2019_Release_DLL/kzjvm.dll"
        "${_kanzi_root}/Engine/plugins/jvm/lib/win64/GL_vs2022_Release_DLL/kzjvm.dll"
    )
    if(DEFINED _kzjvm_dll)
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_kzjvm_dll}" "$<TARGET_FILE_DIR:${target}>"
            COMMENT "Deploy kzjvm.dll from Kanzi install -> exe directory"
        )
    else()
        message(WARNING "kzjvm.dll not found under ${_kanzi_root}/Studio/Bin/EnginePlugins "
            "or Engine/plugins/jvm — check KANZI_HOME and VS build configuration")
    endif()
endfunction()
