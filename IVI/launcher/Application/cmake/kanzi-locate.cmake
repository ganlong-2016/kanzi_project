cmake_minimum_required(VERSION 3.10.0)

# Locate Kanzi Engine (Workspace), NOT Kanzi Studio install.
#   KANZI_HOME  → KanziWorkspace_* （含 Engine/lib/cmake/Kanzi）
#   KANZI_STUDIO_HOME → Studio 安装根（如 D:/Kanzi 3_9_15_83），仅用于 jar，见 deploy-runtime.cmake

function(find_kanzi)
    set(found_dir "")
    set(found_message "")
    set(start_dir "")

    if((DEFINED Kanzi_DIR) AND NOT ("${Kanzi_DIR}" STREQUAL "Kanzi_DIR-NOTFOUND") AND NOT ("${Kanzi_DIR}" STREQUAL ""))
        set(start_dir "${Kanzi_DIR}")
        set(found_message "Using Kanzi from Kanzi_DIR definition")
    elseif((DEFINED KANZI_HOME) AND NOT ("${KANZI_HOME}" STREQUAL ""))
        set(start_dir "${KANZI_HOME}/Engine/lib/cmake/Kanzi/")
        set(found_message "Using Kanzi from KANZI_HOME definition")
    elseif((DEFINED ENV{KANZI_HOME}) AND (NOT "$ENV{KANZI_HOME}" STREQUAL ""))
        set(start_dir "$ENV{KANZI_HOME}/Engine/lib/cmake/Kanzi/")
        set(found_message "Using Kanzi from KANZI_HOME environment variable")
    endif()

    # 若 KANZI_HOME 指到了 Studio 安装目录（无 Engine cmake），回退到工程向上搜索 Workspace
    if(start_dir AND NOT EXISTS "${start_dir}")
        message(WARNING
            "KANZI_HOME points to a path without Engine CMake config:\n"
            "  ${start_dir}\n"
            "  KANZI_HOME must be the Kanzi *Workspace* (e.g. D:/KanziWorkspace_3_9_15_83),\n"
            "  not the Studio install (e.g. D:/Kanzi 3_9_15_83).\n"
            "  Falling back to parent-directory search from the project.")
        set(start_dir "")
        set(found_message "Using Kanzi from parent directory search (KANZI_HOME was invalid)")
    endif()

    if(NOT start_dir)
        if((1 LESS ${ARGC}) AND NOT ("${ARGV1}" STREQUAL ""))
            get_filename_component(start_dir "${ARGV1}" ABSOLUTE)
            set(found_message "Using Kanzi from parent directory search")
        else()
            get_filename_component(start_dir "." ABSOLUTE)
            set(found_message "Using Kanzi from parent directory search")
        endif()
    endif()

    get_filename_component(curr_dir "${start_dir}" ABSOLUTE)
    if(NOT EXISTS "${curr_dir}")
        set(prepend_dir "../")
        foreach(it RANGE 8)
            get_filename_component(curr_dir "${prepend_dir}/${start_dir}" ABSOLUTE)
            if(EXISTS "${curr_dir}")
                break()
            endif()
            set(prepend_dir "../${prepend_dir}")
        endforeach()
    endif()

    if(EXISTS "${curr_dir}")
        while(NOT "${last_dir}" STREQUAL "${curr_dir}")
            if((EXISTS "${curr_dir}/KanziConfig.cmake") OR (EXISTS "${curr_dir}/kanzi-config.cmake"))
                set(found_dir "${curr_dir}")
                break()
            endif()
            if((EXISTS "${curr_dir}/Engine/lib/cmake/Kanzi/KanziConfig.cmake") OR (EXISTS "${curr_dir}/Engine/lib/cmake/Kanzi/kanzi-config.cmake"))
                set(found_dir "${curr_dir}/Engine/lib/cmake/Kanzi")
                break()
            endif()
            set(last_dir "${curr_dir}")
            get_filename_component(curr_dir "${last_dir}/.." ABSOLUTE)
        endwhile()
        if(NOT found_dir STREQUAL "")
            message(STATUS "${found_message}: '${found_dir}'")
            set(Kanzi_DIR "${found_dir}" CACHE STRING "Location of KanziConfig.cmake" FORCE)
            set(Kanzi_DIR "${found_dir}" PARENT_SCOPE)
            set(KANZI_ROOT "${Kanzi_DIR}/../../../.." PARENT_SCOPE)
        else()
            message(FATAL_ERROR "Could not locate Kanzi_DIR (KanziConfig.cmake). "
                "Set KANZI_HOME to your Kanzi Workspace, e.g. D:/KanziWorkspace_3_9_15_83")
        endif()
    else()
        message(FATAL_ERROR "Could not locate Kanzi_DIR. Input '${start_dir}' is probably invalid. "
            "Set KANZI_HOME to Kanzi Workspace (not Studio install).")
    endif()
endfunction()
