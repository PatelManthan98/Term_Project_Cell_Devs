cmake_minimum_required(VERSION 3.10)
project(WildfireSpreadSimulator)

include_directories(${CMAKE_SOURCE_DIR}/boost_local)

include_directories(${CMAKE_SOURCE_DIR}/libraries)
include_directories(${CMAKE_SOURCE_DIR}/libraries/cadmium/include)
include_directories(${CMAKE_SOURCE_DIR}/include)


add_executable(WildfireSpreadSimulator
    main.cpp
    scenario.cpp
)
