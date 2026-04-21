cmake_minimum_required(VERSION 3.10)
project(wildfire_sim)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/cadmium_v2/include
)

add_executable(wildfire_sim
    main.cpp
)

target_link_libraries(wildfire_sim pthread)
