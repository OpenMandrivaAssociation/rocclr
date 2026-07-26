# HIP language package for OpenMandriva FHS (/usr) + system clang.
# Satisfies CMake enable_language(HIP) / find_package(hip-lang).

set(HIP_COMPILER "clang")
set(HIP_RUNTIME "rocclr")

# FHS bitcode lives under lib64/amdgcn/bitcode (not $ROCM_PATH/amdgcn)
# /usr/lib64/cmake/hip-lang -> /usr
get_filename_component(_HIP_LANG_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
get_filename_component(_HIP_LANG_PREFIX "${_HIP_LANG_DIR}/../../.." ABSOLUTE)
set(_ROCM_BITCODE "${_HIP_LANG_PREFIX}/lib64/amdgcn/bitcode")
if(NOT EXISTS "${_ROCM_BITCODE}")
  set(_ROCM_BITCODE "${_HIP_LANG_PREFIX}/lib/amdgcn/bitcode")
endif()
if(EXISTS "${_ROCM_BITCODE}")
  # Ensure try_compile / user projects find device libs with raw clang
  set(_HIP_FHS_FLAGS "--rocm-path=${_HIP_LANG_PREFIX} --rocm-device-lib-path=${_ROCM_BITCODE}")
  if(NOT CMAKE_HIP_FLAGS MATCHES "rocm-device-lib-path")
    set(CMAKE_HIP_FLAGS "${CMAKE_HIP_FLAGS} ${_HIP_FHS_FLAGS}" CACHE STRING "HIP flags" FORCE)
  endif()
  if(NOT DEFINED ENV{HIP_DEVICE_LIB_PATH})
    set(ENV{HIP_DEVICE_LIB_PATH} "${_ROCM_BITCODE}")
  endif()
  unset(_HIP_FHS_FLAGS)
endif()

include("${CMAKE_CURRENT_LIST_DIR}/hip-lang-targets.cmake")

set_target_properties(hip-lang::device PROPERTIES
  INTERFACE_INCLUDE_DIRECTORIES "$<$<COMPILE_LANGUAGE:HIP>:${_HIP_LANG_PREFIX}/include>"
  INTERFACE_SYSTEM_INCLUDE_DIRECTORIES "$<$<COMPILE_LANGUAGE:HIP>:${_HIP_LANG_PREFIX}/include>"
  INTERFACE_COMPILE_DEFINITIONS "$<$<COMPILE_LANGUAGE:HIP>:__HIP_ROCclr__=1;__HIP_PLATFORM_AMD__=1;__HIP_PLATFORM_HCC__=1>"
)

set_target_properties(hip-lang::amdhip64 PROPERTIES
  INTERFACE_COMPILE_DEFINITIONS "$<$<COMPILE_LANGUAGE:HIP>:__HIP_ROCclr__=1;__HIP_PLATFORM_AMD__=1;__HIP_PLATFORM_HCC__=1>"
  INTERFACE_INCLUDE_DIRECTORIES "$<$<COMPILE_LANGUAGE:HIP>:${_HIP_LANG_PREFIX}/include>"
  INTERFACE_SYSTEM_INCLUDE_DIRECTORIES "$<$<COMPILE_LANGUAGE:HIP>:${_HIP_LANG_PREFIX}/include>"
)

set_property(TARGET hip-lang::device APPEND PROPERTY
  INTERFACE_LINK_OPTIONS "$<$<LINK_LANGUAGE:HIP>:--hip-link>"
)

if(CMAKE_HIP_COMPILER AND NOT WIN32)
  execute_process(
    COMMAND ${CMAKE_HIP_COMPILER} -print-libgcc-file-name --rtlib=compiler-rt -unwindlib=libgcc
    OUTPUT_VARIABLE _CLANGRT_BUILTINS
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE _CLANGRT_RC
    ERROR_QUIET)
  if(_CLANGRT_RC EQUAL 0)
    set_property(TARGET hip-lang::device APPEND PROPERTY
      INTERFACE_LINK_OPTIONS "$<$<LINK_LANGUAGE:HIP>:--rtlib=compiler-rt;-unwindlib=libgcc>"
    )
  else()
    message(STATUS "hip-lang: compiler-rt not resolved (rc=${_CLANGRT_RC}); driver defaults used")
  endif()
  unset(_CLANGRT_BUILTINS)
  unset(_CLANGRT_RC)
endif()

set(_CMAKE_HIP_DEVICE_RUNTIME_TARGET "hip-lang::device")
unset(_HIP_LANG_DIR)
unset(_HIP_LANG_PREFIX)
unset(_ROCM_BITCODE)
