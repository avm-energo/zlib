cmake_minimum_required(VERSION 3.12...3.31)

project(
    avm-zlib
    LANGUAGES C
    VERSION 1.4.1.1
    HOMEPAGE_URL "https://git.avmenergo.ru/avm-energo/zlib"
    DESCRIPTION "a general-purpose lossless data-compression library")

# ============================================================================
# configuration
# ============================================================================

include(CheckCSourceCompiles)
include(CheckFunctionExists)
include(CheckIncludeFile)
include(CMakePackageConfigHelpers)
include(CheckTypeSize)
include(GNUInstallDirs)

if(NOT ZLIB_CONF_WRITTEN)
    set(CONF_OUT_FILE ${PROJECT_BINARY_DIR}/zconf.h.cmakein)
    file(READ ${PROJECT_SOURCE_DIR}/zconf.h ZCONF_CONTENT LIMIT 245)
    file(WRITE ${CONF_OUT_FILE} ${ZCONF_CONTENT})
    file(APPEND ${CONF_OUT_FILE} "#cmakedefine HAVE_STDARG_H 1\n")
    file(APPEND ${CONF_OUT_FILE} "#cmakedefine HAVE_UNISTD_H 1\n")
    file(READ ${PROJECT_SOURCE_DIR}/zconf.h ZCONF_CONTENT OFFSET 244)
    set(FIRST_ITEM TRUE)

    foreach(item IN LISTS ZCONF_CONTENT)
        if(FIRST_ITEM)
            string(APPEND OUT_CONTENT ${item})
            set(FIRST_ITEM FALSE)
        else(FIRST_ITEM)
            string(APPEND OUT_CONTENT "\;" ${item})
        endif(FIRST_ITEM)
    endforeach(item IN LISTS ${ZCONF_CONTENT})

    file(APPEND ${CONF_OUT_FILE} ${OUT_CONTENT})
    set(ZLIB_CONF_WRITTEN
        TRUE
        CACHE BOOL "zconf.h.cmakein was created")
    mark_as_advanced(ZLIB_CONF_WRITTEN)
endif(NOT ZLIB_CONF_WRITTEN)

#
# Check to see if we have large file support
#
set(CMAKE_REQUIRED_DEFINITIONS -D_LARGEFILE64_SOURCE=1)
check_type_size(off64_t OFF64_T)
unset(CMAKE_REQUIRED_DEFINITIONS) # clear variable

#
# Check for fseeko
#
check_function_exists(fseeko HAVE_FSEEKO)

#
# Check for stdarg.h
#
check_include_file(stdarg.h HAVE_STDARG_H)

#
# Check for unistd.h
#
check_include_file(unistd.h HAVE_UNISTD_H)

if(MSVC)
    set(CMAKE_REQUIRED_FLAGS "-WX")
else(MSVC)
    set(CMAKE_REQUIRED_FLAGS "-WError")
endif(MSVC)

if(UNIX)
    # On unix-like platforms the library is almost always called libz
    set_target_properties(
        ${PROJECT_NAME}
        PROPERTIES LINK_FLAGS
                   "-Wl,--version-script,\"${PROJECT_SOURCE_DIR}/zlib.map\"")
endif(UNIX)

check_c_source_compiles(
    "
        #include <stdlib.h>
        static void f(void) __attribute__ ((visibility(\"hidden\")));
        int main(void) {return 0;}
    "
    HAVE___ATTR__VIS_HIDDEN)

unset(CMAKE_COMPILE_FLAGS)
configure_file(${PROJECT_BINARY_DIR}/zconf.h.cmakein ${PROJECT_BINARY_DIR}/zconf.h)

# ============================================================================
# zlib
# ============================================================================

set(ZLIB_PUBLIC_HDRS ${PROJECT_BINARY_DIR}/zconf.h zlib.h)

set(ZLIB_PRIVATE_HDRS
    crc32.h
    deflate.h
    gzguts.h
    inffast.h
    inffixed.h
    inflate.h
    inftrees.h
    trees.h
    zutil.h)

set(ZLIB_SRCS
    adler32.c
    compress.c
    crc32.c
    deflate.c
    gzclose.c
    gzlib.c
    gzread.c
    gzwrite.c
    inflate.c
    infback.c
    inftrees.c
    inffast.c
    trees.c
    uncompr.c
    zutil.c)

if(BUILD_SHARED_LIBS)
    add_library(
        ${PROJECT_NAME} SHARED ${ZLIB_SRCS} ${ZLIB_PUBLIC_HDRS} ${ZLIB_PRIVATE_HDRS})
    target_compile_definitions(${PROJECT_NAME} PRIVATE -DZLIB_EXPORTS)
    target_compile_definitions(${PROJECT_NAME} INTERFACE -DZLIB_IMPORTS)
else()
    add_library(${PROJECT_NAME} STATIC ${ZLIB_SRCS} ${ZLIB_PUBLIC_HDRS}
                                  ${ZLIB_PRIVATE_HDRS})
    target_compile_definitions(${PROJECT_NAME} PUBLIC -DHAVE_STATIC_BUILD)
endif()

# Set project version as gen target property
set_target_properties(${PROJECT_NAME} PROPERTIES
  VERSION ${PROJECT_VERSION}
  SOVERSION ${PROJECT_VERSION_MAJOR}
  PUBLIC_HEADER "${public_headers}"
)

target_include_directories(
    ${PROJECT_NAME}
    PUBLIC $<BUILD_INTERFACE:${PROJECT_BINARY_DIR}>
           $<BUILD_INTERFACE:${PROJECT_SOURCE_DIR}>
           $<INSTALL_INTERFACE:${CMAKE_INSTALL_INCLUDEDIR}>)

# add synonim for zlib
add_library(avm-energo::${PROJECT_NAME} ALIAS ${PROJECT_NAME})

install(
    TARGETS ${PROJECT_NAME}
    EXPORT ${PROJECT_NAME}_Targets
    RUNTIME DESTINATION "${CMAKE_INSTALL_BINDIR}"
    ARCHIVE DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}"
    PUBLIC_HEADER DESTINATION ${CMAKE_INSTALL_INCLUDEDIR})

configure_package_config_file(
    ${PROJECT_SOURCE_DIR}/cmake/${PROJECT_NAME}Config.cmake.in
    "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
    INSTALL_DESTINATION
    ${CMAKE_INSTALL_DATAROOTDIR}/${PROJECT_NAME}/cmake)

write_basic_package_version_file(${PROJECT_NAME}ConfigVersion.cmake
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY SameMajorVersion)

install(EXPORT ${PROJECT_NAME}_Targets
        FILE ${PROJECT_NAME}Targets.cmake
        NAMESPACE ${PROJECT_NAME}::
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/${PROJECT_NAME}/cmake)

install(FILES "${PROJECT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
        "${PROJECT_BINARY_DIR}/${PROJECT_NAME}ConfigVersion.cmake"
        DESTINATION ${CMAKE_INSTALL_DATAROOTDIR}/${PROJECT_NAME}/cmake)

set(VERSION_IN ${CMAKE_CURRENT_SOURCE_DIR}/VERSION.in)
set(VERSION_OUT ${CMAKE_CURRENT_SOURCE_DIR}/package/src/VERSION)
configure_file(${VERSION_IN} ${VERSION_OUT} @ONLY)
