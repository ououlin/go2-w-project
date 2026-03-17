cmake_minimum_required(VERSION 3.10)
project(go2w_control)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# 寻找unitree_sdk2
find_package(unitree_sdk2 REQUIRED)

# 包含头文件
include_directories(${unitree_sdk2_INCLUDE_DIRS})

# 创建可执行文件
add_executable(go2w_control go2w_control.cpp)

# 链接库
target_link_libraries(go2w_control ${unitree_sdk2_LIBRARIES})
