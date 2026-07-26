# Minimal HIP imported targets for OpenMandriva FHS layout (rocm-hip-devel).
# Generated for packaging consumers (rocPRIM, etc.) until full CMake export
# is restored in the rocclr package.

if(NOT TARGET hip::amdhip64)
  add_library(hip::amdhip64 SHARED IMPORTED)
  set_target_properties(hip::amdhip64 PROPERTIES
    IMPORTED_LOCATION "${CMAKE_CURRENT_LIST_DIR}/../../libamdhip64.so"
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_LIST_DIR}/../../../include"
  )
endif()

if(NOT TARGET hip::host)
  add_library(hip::host INTERFACE IMPORTED)
  set_target_properties(hip::host PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_LIST_DIR}/../../../include"
    INTERFACE_COMPILE_DEFINITIONS "__HIP_PLATFORM_AMD__=1;__HIP_PLATFORM_HCC__=1"
    INTERFACE_LINK_LIBRARIES "hip::amdhip64"
  )
endif()

if(NOT TARGET hip::device)
  add_library(hip::device INTERFACE IMPORTED)
  set_target_properties(hip::device PROPERTIES
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_LIST_DIR}/../../../include"
    INTERFACE_COMPILE_DEFINITIONS "__HIP_PLATFORM_AMD__=1;__HIP_PLATFORM_HCC__=1"
    INTERFACE_LINK_LIBRARIES "hip::amdhip64"
  )
endif()

if(NOT TARGET hip::hiprtc AND EXISTS "${CMAKE_CURRENT_LIST_DIR}/../../libhiprtc.so")
  add_library(hip::hiprtc SHARED IMPORTED)
  set_target_properties(hip::hiprtc PROPERTIES
    IMPORTED_LOCATION "${CMAKE_CURRENT_LIST_DIR}/../../libhiprtc.so"
    INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_LIST_DIR}/../../../include"
  )
endif()

# Alias often expected by clients
if(NOT TARGET hip::hip)
  add_library(hip::hip INTERFACE IMPORTED)
  set_target_properties(hip::hip PROPERTIES
    INTERFACE_LINK_LIBRARIES "hip::host;hip::device"
  )
endif()
