cmake_minimum_required(VERSION 3.2)
project(tankoid)

# Resolve external dependencies.
find_package(SFML 2.2 REQUIRED COMPONENTS graphics window audio system)

# Set the resource path. This has to be adjusted when the user is installing
# the package.
set(RESOURCES_PATH "${PROJECT_SOURCE_DIR}/../resources")

# Configure config header.
set(GENERATED_SOURCES_PATH "${PROJECT_BINARY_DIR}/generated")
configure_file(src/config.hpp.in "${GENERATED_SOURCES_PATH}/config.hpp" @ONLY)

# Build source file list.
file(GLOB_RECURSE SOURCES src/**.cpp src/**.hpp)
file(
  GLOB_RECURSE GENERATED_SOURCES "${GENERATED_SOURCES_PATH}/**.cpp"
  "${GENERATED_SOURCES_PATH}/**.hpp"
)

# Set default compiler options. These can be overriden by setting
# CMAKE_CXX_FLAGS. The list of triggers is inspired by this post:
# http://stackoverflow.com/a/401276/683669
set(
  CMAKE_CXX_FLAGS
  "-std=c++11 -Wall -Weffc++ -pedantic -pedantic-errors -Wextra \
  -Waggregate-return -Wcast-align -Wcast-qual -Wchar-subscripts -Wcomment \
  -Wconversion -Wdisabled-optimization -Werror -Wfloat-equal -Wformat \
  -Wformat=2 -Wformat-nonliteral -Wformat-security -Wformat-y2k -Wimplicit \
  -Wimport -Winit-self -Winline -Winvalid-pch \
  -Wlong-long -Wmissing-braces -Wmissing-field-initializers \
  -Wmissing-format-attribute -Wmissing-include-dirs -Wmissing-noreturn \
  -Wpacked -Wpadded -Wparentheses -Wpointer-arith -Wredundant-decls \
  -Wreturn-type -Wsequence-point -Wshadow -Wsign-compare -Wstack-protector \
  -Wstrict-aliasing -Wstrict-aliasing=2 -Wswitch -Wswitch-default \
  -Wswitch-enum -Wtrigraphs -Wuninitialized -Wunknown-pragmas \
  -Wunreachable-code -Wunused -Wunused-function -Wunused-label \
  -Wunused-parameter -Wunused-value -Wunused-variable -Wvariadic-macros \
  -Wvolatile-register-var -Wwrite-strings \
  ${CMAKE_CXX_FLAGS}"
)

# Set search directories.
include_directories("${GENERATED_SOURCES_PATH}")
include_directories("${SFML_INCLUDE_DIR}")

# Tankoid target.
add_executable(tankoid ${SOURCES} ${GENERATED_SOURCES})

# Link to dependencies.
target_link_libraries(tankoid "${SFML_LIBRARIES}")
