# 从仓库 plugins/ 部署到 VS 运行时目录（不从 KANZI_HOME 拉取）。

function(deploy_plugins_from_repo target kzb_directory plugins_directory)
    if(NOT WIN32 OR ANDROID)
        return()
    endif()

    if(NOT IS_DIRECTORY "${plugins_directory}")
        message(WARNING "plugins directory not found: ${plugins_directory}")
        return()
    endif()

    set(_kzjava "${plugins_directory}/java/kzjava.jar")
    if(EXISTS "${_kzjava}")
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_kzjava}" "${kzb_directory}/kzjava.jar"
            COMMENT "Deploy plugins/java/kzjava.jar -> assets/"
        )
    else()
        message(WARNING "Missing ${plugins_directory}/java/kzjava.jar — "
            "copy from %KANZI_HOME%\\Engine\\lib\\java\\ (see plugins/README.md)")
    endif()

    set(_datasource_jar
        "${plugins_directory}/datasource/lib/java/Release/DroidDataSourceplugin.jar")
    if(EXISTS "${_datasource_jar}")
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E make_directory "${kzb_directory}/lib/java/Release"
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_datasource_jar}"
                "${kzb_directory}/lib/java/Release/DroidDataSourceplugin.jar"
            COMMENT "Deploy DroidDataSourceplugin.jar -> assets/lib/java/Release/"
        )
    endif()

    file(GLOB_RECURSE _plugin_dlls
        "${plugins_directory}/*/lib/win64/*/*.dll")
    foreach(_dll IN LISTS _plugin_dlls)
        add_custom_command(TARGET ${target} POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${_dll}" "$<TARGET_FILE_DIR:${target}>"
            COMMENT "Deploy ${plugins_directory} DLL -> exe directory"
        )
    endforeach()
endfunction()
