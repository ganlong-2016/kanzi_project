cmake_minimum_required(VERSION 3.10.0)
project(launcher)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/kanzi-locate.cmake)

if(MSVC)
    option(BUILD_SHARED_LIBS "Selects whether to build and link to shared or static libraries" ON)
endif()

if(NOT KANZI_ENGINE_BUILD)
    find_kanzi()
    find_package(Kanzi REQUIRED CONFIG CMAKE_FIND_ROOT_PATH_BOTH)
endif()

include(kanzi-common)

add_executable(launcher src/launcher.cpp)

if(ANDROID)
    target_link_libraries(launcher -Wl,--whole-archive Kanzi::kzappfw -Wl,--no-whole-archive)
else()
    target_link_libraries(launcher Kanzi::kzappfw)
endif()

target_link_libraries(launcher Kanzi::kzui Kanzi::kzcoreui)

# KANZI_LINK_FREETYPE and KANZI_LINK_ITYPE options determine which font backends are explicitly linked to your application. 
# By default including Kanzi config sets the following:
#  - KANZI_LINK_FREETYPE=ON in static build.
#  - Both OFF in dynamic build.
#
# In case you are working with dynamic libraries, Kanzi engine can load available font engine backend at runtime.
# Use FontEngine application configuration to choose which font engine backend Kanzi loads: 
# FontEngine=freetype|itype|none
target_link_font_engine_backends(launcher)

# [CodeBehind libs start]. Do not remove this identifier.
set(launcher_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../Tool_project/CodeBehind/launcher")
if(EXISTS "${launcher_codebehind_lib_dir}")
    add_subdirectory("${launcher_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/launcher")
    include_directories(${launcher_codebehind_lib_dir}/include)
    target_link_libraries(launcher launcher_CodeBehind)
endif()
# [environment CodeBehind lib start]. Do not remove or change this identifier.
set(environment_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../environment/CodeBehind/environment")
if(EXISTS "${environment_codebehind_lib_dir}")
    add_subdirectory("${environment_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/environment")
    include_directories(${environment_codebehind_lib_dir}/include)
    target_link_libraries(launcher environment_CodeBehind)
endif()
# [environment CodeBehind lib end]. Do not remove or change this identifier.
# [Car CodeBehind lib start]. Do not remove or change this identifier.
set(Car_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../car/CodeBehind/Car")
if(EXISTS "${Car_codebehind_lib_dir}")
    add_subdirectory("${Car_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/Car")
    include_directories(${Car_codebehind_lib_dir}/include)
    target_link_libraries(launcher Car_CodeBehind)
endif()
# [Car CodeBehind lib end]. Do not remove or change this identifier.
# [car_setting CodeBehind lib start]. Do not remove or change this identifier.
set(car_setting_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../car_setting/CodeBehind/car_setting")
if(EXISTS "${car_setting_codebehind_lib_dir}")
    add_subdirectory("${car_setting_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/car_setting")
    include_directories(${car_setting_codebehind_lib_dir}/include)
    target_link_libraries(launcher car_setting_CodeBehind)
endif()
# [car_setting CodeBehind lib end]. Do not remove or change this identifier.
# [common CodeBehind lib start]. Do not remove or change this identifier.
set(common_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../common/CodeBehind/common")
if(EXISTS "${common_codebehind_lib_dir}")
    add_subdirectory("${common_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/common")
    include_directories(${common_codebehind_lib_dir}/include)
    target_link_libraries(launcher common_CodeBehind)
endif()
# [common CodeBehind lib end]. Do not remove or change this identifier.
# [demo CodeBehind lib start]. Do not remove or change this identifier.
set(demo_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../demo/CodeBehind/demo")
if(EXISTS "${demo_codebehind_lib_dir}")
    add_subdirectory("${demo_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/demo")
    include_directories(${demo_codebehind_lib_dir}/include)
    target_link_libraries(launcher demo_CodeBehind)
endif()
# [demo CodeBehind lib end]. Do not remove or change this identifier.
# [Car CodeBehind lib start]. Do not remove or change this identifier.
set(Car_codebehind_lib_dir "${CMAKE_CURRENT_SOURCE_DIR}/../../car/CodeBehind/Car")
if(EXISTS "${Car_codebehind_lib_dir}")
    add_subdirectory("${Car_codebehind_lib_dir}" "${CMAKE_CURRENT_BINARY_DIR}/CodeBehind/Car")
    include_directories(${Car_codebehind_lib_dir}/include)
    target_link_libraries(launcher Car_CodeBehind)
endif()
# [Car CodeBehind lib end]. Do not remove or change this identifier.
# [CodeBehind libs end]. Do not remove this identifier.

# KZB / cfg 导出目录（与 launcher.kzproj 的 BinaryExportDirectory 一致：仓库根 assets/）
get_filename_component(KANZI_KZB_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../../../assets" ABSOLUTE)
get_filename_component(REPO_PLUGINS_DIRECTORY "${CMAKE_CURRENT_LIST_DIR}/../../../plugins" ABSOLUTE)

set_target_properties(launcher PROPERTIES VS_DEBUGGER_WORKING_DIRECTORY "${KANZI_KZB_DIRECTORY}")
set_target_properties(launcher PROPERTIES VS_DEBUGGER_ENVIRONMENT "${KANZI_VS_DEBUGGER_ENVIRONMENT}")

install_kanzi_libs_to_output_directory()
install_kzbs_to_output_directory("${KANZI_KZB_DIRECTORY}")
install_target_to_output_directory(launcher)

include(${CMAKE_CURRENT_LIST_DIR}/cmake/deploy-plugins.cmake)
deploy_kanzi_plugins(launcher "${KANZI_KZB_DIRECTORY}" "${REPO_PLUGINS_DIRECTORY}")
