# Root CMakeLists.txt: DO NOT EDIT!
# Author: Snow Yang
# Date  : 2022/03/08

cmake_minimum_required(VERSION 3.22.2)

set(MXOS_BASE ${CMAKE_CURRENT_SOURCE_DIR})

include(mxos/module/${MODULE}/config.cmake)
include(mxos/cmake/app/boilerplate.cmake)

cmake_path(GET APP STEM APP_TARGET)

project(${APP_TARGET})
add_executable(${APP_TARGET}.elf mxos/misc/empty_file.c)
target_link_libraries(${APP_TARGET}.elf PRIVATE mxos_interface)

# Use APP git status value as C/C++ macro `MXOS_APP_VERSION`
get_git_status(app_git_status)
mxos_compile_definitions(
  MXOS_APP_VERSION="${app_git_status}"
)

add_subdirectory(${APP})
# mxos MUST be the last subdirectory to be added!
add_subdirectory(mxos)