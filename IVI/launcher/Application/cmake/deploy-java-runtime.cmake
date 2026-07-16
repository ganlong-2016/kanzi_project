# Deploy Kanzi Java runtime files for Windows desktop (appfw) debugging.
# launcher 使用 DroidDataSourceplugin（Java 插件）；VS 工作目录为 assets/ 时，
# kzjvm 会在当前目录查找 ./kzjava.jar，并在 lib/java/<Config>/ 下加载业务 JAR。

function(_kanzi_resolve_root _out_var)
    if(DEFINED KANZI_ROOT AND NOT "${KANZI_ROOT}" STREQUAL "")
        set(${_out_var} "${KANZI_ROOT}" PARENT_SCOPE)
    elseif(DEFINED ENV{KANZI_HOME} AND NOT "$ENV{KANZI_HOME}" STREQUAL "")
        set(${_out_var} "$ENV{KANZI_HOME}" PARENT_SCOPE)
    endif()
endfunction()

function(_kanzi_copy_first_existing _out_var _candidates)
    foreach(_candidate IN LISTS ARGN)
        if(EXISTS "${_candidate}")
            set(${_out_var} "${_candidate}" PARENT_SCOPE)
            return()
        endif()
    endforeach()
    unset(${_out_var} PARENT_SCOPE)
endfunction()

function(deploy_kanzi_java_runtime target kzb_directory)
    if(NOT WIN32 OR ANDROID)
        return()
    endif()

    _kanzi_resolve_root(_kanzi_root)
    if(NOT DEFINED _kanzi_root)
        message(WARNING "KANZI_ROOT / KANZI_HOME not set — cannot deploy kzjava.jar for Java plugins.")
        return()
    endif()

    _kanzi_copy_first_existing(_kzjava_jar
        "${_kanzi_root}/Engine/lib/java/kzjava.jar"
        "${_kanzi_root}/Engine/lib/java/Release/kzjava.jar"
        "${_kanzi_root}/Engine/java/kzjava.jar"
    )
    if(DEFINED _kzjava_jar)
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_kzjava_jar}" "${kzb_directory}/kzjava.jar"
            COMMENT "Copy kzjava.jar to runtime working directory (${kzb_directory})"
        )
    else()
        message(WARNING "kzjava.jar not found under ${_kanzi_root}/Engine — "
            "copy it manually to ${kzb_directory}/kzjava.jar")
    endif()

    get_filename_component(_datasource_plugin_jar
        "${CMAKE_CURRENT_LIST_DIR}/../../../../plugins/datasource/lib/java/Release/DroidDataSourceplugin.jar"
        ABSOLUTE)
    if(EXISTS "${_datasource_plugin_jar}")
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}/lib/java/Release"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_datasource_plugin_jar}"
                "${kzb_directory}/lib/java/Release/DroidDataSourceplugin.jar"
            COMMENT "Copy DroidDataSourceplugin.jar to assets/lib/java/Release"
        )
    else()
        message(WARNING "DroidDataSourceplugin.jar not found at ${_datasource_plugin_jar}")
    endif()

    if(DEFINED _kanzi_root)
        set(_kzjvm_candidates
            "${_kanzi_root}/Engine/plugins/jvm/lib/win64/GL_vs2019_Release_DLL/kzjvm.dll"
            "${_kanzi_root}/Engine/plugins/jvm/lib/win64/GL_vs2022_Release_DLL/kzjvm.dll"
            "${_kanzi_root}/Engine/plugins/jvm/lib/win64/vs2019_Release_DLL/kzjvm.dll"
            "${_kanzi_root}/Engine/plugins/jvm/lib/win64/vs2022_Release_DLL/kzjvm.dll"
            "${_kanzi_root}/Engine/plugins/jvm/lib/win64/GL_vs2019_Debug_DLL/kzjvm.dll"
            "${_kanzi_root}/Engine/plugins/jvm/lib/win64/GL_vs2022_Debug_DLL/kzjvm.dll"
        )
        _kanzi_copy_first_existing(_kzjvm_dll ${_kzjvm_candidates})
        if(DEFINED _kzjvm_dll)
            add_custom_command(TARGET ${target} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_kzjvm_dll}" "$<TARGET_FILE_DIR:${target}>"
                COMMENT "Copy kzjvm.dll next to ${target}"
            )
        endif()
    endif()
endfunction()
