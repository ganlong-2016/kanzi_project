cmake_minimum_required(VERSION 3.10.0)

# Locate Kanzi Engine CMake package (KanziConfig.cmake).
#
# Supported layout (do NOT require changing user env):
#   Kanzi_DIR  (env or -D) → Workspace Engine cmake, e.g.
#              D:/KanziWorkspace_3_9_15_83/Engine/lib/cmake/Kanzi
#   KANZI_HOME (env)       → may be Studio install OR Workspace;
#              only used for Engine if .../Engine/lib/cmake/Kanzi exists.
#   Otherwise              → walk up from project (under Workspace/Projects/...).

function(_kanzi_try_start_dir out_var candidate)
    set(${out_var} "" PARENT_SCOPE)
    if("${candidate}" STREQUAL "")
        return()
    endif()
    get_filename_component(_abs "${candidate}" ABSOLUTE)
    if(EXISTS "${_abs}")
        set(${out_var} "${_abs}" PARENT_SCOPE)
    endif()
endfunction()

function(find_kanzi)
    set(found_dir "")
    set(found_message "")
    set(start_dir "")

    # 1) Explicit Kanzi_DIR (CMake -D or cache)
    if((DEFINED Kanzi_DIR) AND NOT ("${Kanzi_DIR}" STREQUAL "Kanzi_DIR-NOTFOUND") AND NOT ("${Kanzi_DIR}" STREQUAL ""))
        _kanzi_try_start_dir(start_dir "${Kanzi_DIR}")
        if(start_dir)
            set(found_message "Using Kanzi from Kanzi_DIR (CMake)")
        endif()
    endif()

    # 2) Environment Kanzi_DIR (user env: Workspace Engine cmake path)
    if(NOT start_dir AND DEFINED ENV{Kanzi_DIR} AND NOT "$ENV{Kanzi_DIR}" STREQUAL "")
        _kanzi_try_start_dir(start_dir "$ENV{Kanzi_DIR}")
        if(start_dir)
            set(found_message "Using Kanzi from Kanzi_DIR environment variable")
        endif()
    endif()

    # 3) KANZI_HOME only if it actually contains Engine cmake (Workspace)
    if(NOT start_dir AND DEFINED KANZI_HOME AND NOT "${KANZI_HOME}" STREQUAL "")
        _kanzi_try_start_dir(start_dir "${KANZI_HOME}/Engine/lib/cmake/Kanzi")
        if(start_dir)
            set(found_message "Using Kanzi from KANZI_HOME (CMake)")
        endif()
    endif()
    if(NOT start_dir AND DEFINED ENV{KANZI_HOME} AND NOT "$ENV{KANZI_HOME}" STREQUAL "")
        _kanzi_try_start_dir(start_dir "$ENV{KANZI_HOME}/Engine/lib/cmake/Kanzi")
        if(start_dir)
            set(found_message "Using Kanzi from KANZI_HOME environment variable")
        else()
            message(STATUS
                "KANZI_HOME=$ENV{KANZI_HOME} has no Engine/lib/cmake/Kanzi "
                "(treated as Studio install for jars). Engine resolved via Kanzi_DIR or project path.")
        endif()
    endif()

    # 4) Walk up from project / optional hint
    if(NOT start_dir)
        if((1 LESS ${ARGC}) AND NOT ("${ARGV1}" STREQUAL ""))
            get_filename_component(start_dir "${ARGV1}" ABSOLUTE)
        else()
            get_filename_component(start_dir "." ABSOLUTE)
        endif()
        set(found_message "Using Kanzi from parent directory search")
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
            if((EXISTS "${curr_dir}/Engine/lib/cmake/Kanzi/KanziConfig.cmake") OR
               (EXISTS "${curr_dir}/Engine/lib/cmake/Kanzi/kanzi-config.cmake"))
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
            get_filename_component(KANZI_ROOT "${found_dir}/../../../.." ABSOLUTE)
            set(KANZI_ROOT "${KANZI_ROOT}" PARENT_SCOPE)
        else()
            message(FATAL_ERROR
                "Could not locate KanziConfig.cmake.\n"
                "Set env Kanzi_DIR to Workspace Engine cmake, e.g.\n"
                "  D:\\KanziWorkspace_3_9_15_83\\Engine\\lib\\cmake\\Kanzi")
        endif()
    else()
        message(FATAL_ERROR "Could not locate Kanzi_DIR. start_dir='${start_dir}' is invalid.")
    endif()
endfunction()
