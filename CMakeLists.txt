cmake_minimum_required(VERSION 3.23)

project(Minesweeper)

#Using C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)

#Give the list of sources an alias
file(GLOB SCAN_SRC 
	"${Minesweeper_SOURCE_DIR}/src/*.cpp")

#Create the executable
add_executable(Minesweeper ${SCAN_SRC})