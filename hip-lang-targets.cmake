# Imported targets for hip-lang (FHS: libs in lib64, headers in include)
# Do not unset shared prefix vars used by hip-lang-config.cmake after include().

if(NOT TARGET hip-lang::amdhip64)
  add_library(hip-lang::amdhip64 SHARED IMPORTED)
  get_filename_component(_HIP_LANG_TGT_DIR "${CMAKE_CURRENT_LIST_FILE}" PATH)
  # /usr/lib64/cmake/hip-lang -> /usr
  get_filename_component(_HIP_LANG_PREFIX "${_HIP_LANG_TGT_DIR}/../../.." ABSOLUTE)
  set(_HIP_LANG_LIBDIR "${_HIP_LANG_PREFIX}/lib64")
  if(NOT EXISTS "${_HIP_LANG_LIBDIR}/libamdhip64.so")
    set(_HIP_LANG_LIBDIR "${_HIP_LANG_PREFIX}/lib")
  endif()
  set_target_properties(hip-lang::amdhip64 PROPERTIES
    IMPORTED_LOCATION "${_HIP_LANG_LIBDIR}/libamdhip64.so"
    INTERFACE_INCLUDE_DIRECTORIES "${_HIP_LANG_PREFIX}/include"
  )
  unset(_HIP_LANG_TGT_DIR)
  unset(_HIP_LANG_LIBDIR)
  # Keep _HIP_LANG_PREFIX for hip-lang-config.cmake
endif()

if(NOT TARGET hip-lang::host)
  add_library(hip-lang::host INTERFACE IMPORTED)
  set_target_properties(hip-lang::host PROPERTIES
    INTERFACE_LINK_LIBRARIES "hip-lang::amdhip64"
  )
endif()

if(NOT TARGET hip-lang::device)
  add_library(hip-lang::device INTERFACE IMPORTED)
  set_target_properties(hip-lang::device PROPERTIES
    INTERFACE_LINK_LIBRARIES "hip-lang::host"
  )
endif()
