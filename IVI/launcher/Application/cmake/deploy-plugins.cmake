# 部署 Kanzi 运行时：业务插件来自仓库 plugins/，系统 kzjava.jar 来自 Studio EnginePlugins。

function(deploy_kanzi_plugins target kzb_directory plugins_directory)
    if(NOT WIN32 OR ANDROID)
        return()
    endif()

    # 自研 DLL 插件（若有）
    if(IS_DIRECTORY "${plugins_directory}")
        file(GLOB_RECURSE _custom_dlls
            "${plugins_directory}/*/lib/win64/*/*.dll")
        foreach(_dll IN LISTS _custom_dlls)
            add_custom_command(TARGET ${target} POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                    "${_dll}" "$<TARGET_FILE_DIR:${target}>"
                COMMENT "Deploy custom plugin DLL from plugins/"
            )
        endforeach()
    endif()

    # Java 运行时：官方 Application/bin 布局（工作目录 = assets/）
    set(_deploy_script "${CMAKE_CURRENT_LIST_DIR}/deploy-runtime.cmake")
    add_custom_command(TARGET ${target} POST_BUILD
        COMMAND ${CMAKE_COMMAND}
            -DCONFIG=$<CONFIG>
            -DKZB_DIRECTORY=${kzb_directory}
            -DPLUGINS_DIRECTORY=${plugins_directory}
            -P ${_deploy_script}
        COMMENT "Deploy Kanzi Java runtime (kzjava.jar + lib/java/$<CONFIG>)"
        VERBATIM
    )
endfunction()
