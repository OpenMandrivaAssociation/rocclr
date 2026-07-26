# Copyright (c) Advanced Micro Devices, Inc., or its affiliates.
#
# SPDX-License-Identifier: MIT


####### Expanded from @PACKAGE_INIT@ by configure_package_config_file() #######
####### Any changes to this file will be overwritten by the next CMake run ####
####### The input file was hiprtc-config.cmake.in                            ########

get_filename_component(PACKAGE_PREFIX_DIR "${CMAKE_CURRENT_LIST_DIR}/../../../" ABSOLUTE)

# Use original install prefix when loaded through a "/usr move"
# cross-prefix symbolic link such as /lib -> /usr/lib.
get_filename_component(_realCurr "${CMAKE_CURRENT_LIST_DIR}" REALPATH)
get_filename_component(_realOrig "/usr/lib64/cmake/hiprtc" REALPATH)
if(_realCurr STREQUAL _realOrig)
  set(PACKAGE_PREFIX_DIR "/usr")
endif()
unset(_realOrig)
unset(_realCurr)

macro(set_and_check _var _file)
  set(${_var} "${_file}")
  if(NOT EXISTS "${_file}")
    message(FATAL_ERROR "File or directory ${_file} referenced by variable ${_var} does not exist !")
  endif()
endmacro()

macro(check_required_components _NAME)
  foreach(comp ${${_NAME}_FIND_COMPONENTS})
    if(NOT ${_NAME}_${comp}_FOUND)
      if(${_NAME}_FIND_REQUIRED_${comp})
        set(${_NAME}_FOUND FALSE)
      endif()
    endif()
  endforeach()
endmacro()

####################################################################################
include(CMakeFindDependencyMacro)
set_and_check(hiprtc_INCLUDE_DIR "${PACKAGE_PREFIX_DIR}/include")
set_and_check(hiprtc_LIB_INSTALL_DIR "${PACKAGE_PREFIX_DIR}/lib64")
set_and_check(hiprtc_BIN_INSTALL_DIR "${PACKAGE_PREFIX_DIR}/bin")

# Windows Specific Definition here:
if(WIN32)
  if(DEFINED ENV{HIP_PATH})
    file(TO_CMAKE_PATH "$ENV{HIP_PATH}" HIP_PATH)
  elseif(DEFINED ENV{HIP_DIR})
    file(TO_CMAKE_PATH "$ENV{HIP_DIR}" HIP_DIR)
  else()
    # using the HIP found
    set(HIP_PATH ${PACKAGE_PREFIX_DIR})
  endif()
endif()
include("${CMAKE_CURRENT_LIST_DIR}/hiprtc-targets.cmake")
