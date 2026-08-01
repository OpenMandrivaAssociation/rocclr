# ROCclr + HIP runtime (TheRock 7.14). OpenCL ICD optional.
# Build needs: rocm-runtime, rocm-comgr, rocm-device-libs, rocprofiler-register.
# hipcc is optional at configure time if HIP_PLATFORM=amd is set.

Name:		rocclr
Version:	7.14.0
Release:	2
%{!?rocm_llvm_maj_ver:%global rocm_llvm_maj_ver 23}
Summary:	ROCm Compute Language Runtime
License:	MIT AND Apache-2.0 AND MIT-Khronos-old
Group:		System/Libraries
URL:		https://github.com/ROCm/rocm-systems
Source0:	https://github.com/ROCm/rocm-systems/releases/download/therock-7.14/clr.tar.gz#/clr-%{version}.tar.gz
Source1:	https://github.com/ROCm/rocm-systems/releases/download/therock-7.14/hip.tar.gz#/hip-%{version}.tar.gz
# Minimal IMPORTED targets until full cmake export is restored
Source2:	hip-targets.cmake
# CMake enable_language(HIP) package (FHS, system clang)
Source3:	hip-lang-config.cmake
Source4:	hip-lang-targets.cmake
Source5:	hip-lang-config-version.cmake
Source6:	hiprtc-config.cmake
Source7:	hiprtc-config-version.cmake
Source8:	hiprtc-targets.cmake
Source9:	hiprtc-targets-relwithdebinfo.cmake

# Full version string in soname is awkward; use major for Provides
%global hip_so_major 7

BuildRequires:	rocm-rpm-macros
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	clang >= %{rocm_llvm_maj_ver}
BuildRequires:	clang-devel >= %{rocm_llvm_maj_ver}
BuildRequires:	llvm-devel >= %{rocm_llvm_maj_ver}
BuildRequires:	cmake(hsa-runtime64)
BuildRequires:	cmake(amd_comgr)
BuildRequires:	rocm-device-libs
BuildRequires:	rocprofiler-register-devel
BuildRequires:	pkgconfig(libdrm)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(glx)
BuildRequires:	pkgconfig(opengl)
BuildRequires:	pkgconfig(libelf)
BuildRequires:	pkgconfig(OpenCL)
BuildRequires:	opencl-headers
BuildRequires:	python3
BuildRequires:	python%{pyver}dist(cppheaderparser)


%description
ROCclr is the shared runtime underneath HIP and ROCm OpenCL.

%package -n rocm-hip
Summary:	HIP runtime for AMD GPUs
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	rocm-comgr%{?_isa}
Requires:	rocm-device-libs%{?_isa}
Requires:	rocm-runtime%{?_isa}
Requires:	rocprofiler-register%{?_isa}
Recommends:	hipcc

%description -n rocm-hip
HIP runtime libraries (libamdhip64, libhiprtc) and headers for AMD GPUs.

%package -n rocm-hip-devel
Summary:	HIP development files
Group:		Development/C++
Requires:	rocm-hip%{?_isa} = %{version}-%{release}
Requires:	hipcc

%description -n rocm-hip-devel
HIP headers and CMake packages.

%package -n rocm-opencl
Summary:	ROCm OpenCL ICD
Requires:	%{name}%{?_isa} = %{version}-%{release}
Obsoletes:	rocm-opencl < %{EVRD}
Provides:	rocm-opencl = %{EVRD}

%description -n rocm-opencl
AMD ROCm OpenCL platform (libamdocl64). Mesa Rusticl remains an alternative ICD.

%prep
%setup -q -n clr
# hip tarball extracts as top-level "hip/"
tar -xf %{SOURCE1} -C ..
# ensure hip is at ../hip relative to clr, or move
if [ ! -d hip ] && [ -d ../hip ]; then
	ln -sfn ../hip hip
fi
# Disable doxygen ALL target (broken doxygen vs clang 23 soname)
sed -i 's/add_custom_target(build_doxygen ALL/add_custom_target(build_doxygen/' \
	hipamd/packaging/CMakeLists.txt

# Absolute path: %%cmake cds into build/
HIP_COMMON_DIR="$(pwd)/hip"
export HIP_COMMON_DIR
test -d "$HIP_COMMON_DIR" || { echo "missing hip sources at $HIP_COMMON_DIR"; ls -la; exit 1; }

%cmake \
	-DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCLR_BUILD_HIP=ON \
	-DCLR_BUILD_OCL=ON \
	-DHIP_COMMON_DIR="${HIP_COMMON_DIR}" \
	-DHIP_PLATFORM=amd \
	-DROCM_PATH=%{_prefix} \
	-DPROF_API_HEADER_PATH= \
	-G Ninja

%build
%ninja_build -C build amdhip64 amdocl clinfo
# hiprtc libs if available as separate targets
%ninja_build -C build hiprtc hiprtc-builtins 2>/dev/null || true

%install
mkdir -p %{buildroot}%{_libdir} %{buildroot}%{_includedir} \
	%{buildroot}%{_libdir}/cmake/hip \
	%{buildroot}%{_sysconfdir}/OpenCL/vendors \
	%{buildroot}%{_bindir}

# Libraries (hiprtc may live under hipamd/lib)
cp -a build/hipamd/lib/libamdhip64.so* %{buildroot}%{_libdir}/
cp -a build/hipamd/lib/libhiprtc.so* %{buildroot}%{_libdir}/ 2>/dev/null || true
cp -a build/hipamd/lib/libhiprtc-builtins.so* %{buildroot}%{_libdir}/ 2>/dev/null || true
find build -name 'libhiprtc*.so*' -exec cp -a {} %{buildroot}%{_libdir}/ \; 2>/dev/null || true
cp -a build/opencl/amdocl/libamdocl64.so* %{buildroot}%{_libdir}/
# fix broken soname "libamdocl64.so." if present
if [ -e %{buildroot}%{_libdir}/libamdocl64.so. ]; then
	mv %{buildroot}%{_libdir}/libamdocl64.so. %{buildroot}%{_libdir}/libamdocl64.so.2.0.0
	ln -sfn libamdocl64.so.2.0.0 %{buildroot}%{_libdir}/libamdocl64.so.2
	ln -sfn libamdocl64.so.2 %{buildroot}%{_libdir}/libamdocl64.so
fi

# Headers
cp -a hip/include/hip %{buildroot}%{_includedir}/
cp -a build/hipamd/include/hip/. %{buildroot}%{_includedir}/hip/ 2>/dev/null || true

# CMake packages
cp -a build/hipamd/hip-config*.cmake %{buildroot}%{_libdir}/cmake/hip/ 2>/dev/null || true
cp -a build/hipamd/hip-targets*.cmake %{buildroot}%{_libdir}/cmake/hip/ 2>/dev/null || true
if [ -d hip/cmake ]; then
	cp -a hip/cmake/. %{buildroot}%{_libdir}/cmake/hip/ 2>/dev/null || true
fi
# Ensure hip::amdhip64 / hip::device / hip::host exist for consumers
if [ ! -e %{buildroot}%{_libdir}/cmake/hip/hip-targets.cmake ]; then
	install -m 644 %{SOURCE2} %{buildroot}%{_libdir}/cmake/hip/hip-targets.cmake
fi
# hip-lang: required by CMake enable_language(HIP) with clang (not hipcc)
mkdir -p %{buildroot}%{_libdir}/cmake/hip-lang
# Prefer build-generated export if present, else FHS hand-rolled package
if [ -e build/hipamd/src/hip-lang-config.cmake ]; then
	cp -a build/hipamd/src/hip-lang-config.cmake \
		build/hipamd/src/hip-lang-config-version.cmake \
		%{buildroot}%{_libdir}/cmake/hip-lang/ 2>/dev/null || true
	# export file may be next to config or under CMakeFiles
	find build/hipamd -name 'hip-lang-targets*.cmake' -exec cp -a {} %{buildroot}%{_libdir}/cmake/hip-lang/ \; 2>/dev/null || true
fi
if [ ! -e %{buildroot}%{_libdir}/cmake/hip-lang/hip-lang-config.cmake ]; then
	install -m 644 %{SOURCE3} %{buildroot}%{_libdir}/cmake/hip-lang/hip-lang-config.cmake
	install -m 644 %{SOURCE4} %{buildroot}%{_libdir}/cmake/hip-lang/hip-lang-targets.cmake
	install -m 644 %{SOURCE5} %{buildroot}%{_libdir}/cmake/hip-lang/hip-lang-config-version.cmake
fi
# hiprtc is a separate find_package (rocFFT etc.)
mkdir -p %{buildroot}%{_libdir}/cmake/hiprtc
cp -a build/hipamd/hiprtc-config*.cmake %{buildroot}%{_libdir}/cmake/hiprtc/ 2>/dev/null || true
cp -a build/hipamd/hiprtc-targets*.cmake %{buildroot}%{_libdir}/cmake/hiprtc/ 2>/dev/null || true
# Always ensure targets exist (build tree often omits export files under FHS layout)
if [ ! -e %{buildroot}%{_libdir}/cmake/hiprtc/hiprtc-config.cmake ]; then
  install -m 644 %{SOURCE6} %{buildroot}%{_libdir}/cmake/hiprtc/hiprtc-config.cmake
  install -m 644 %{SOURCE7} %{buildroot}%{_libdir}/cmake/hiprtc/hiprtc-config-version.cmake
fi
if [ ! -e %{buildroot}%{_libdir}/cmake/hiprtc/hiprtc-targets.cmake ]; then
  install -m 644 %{SOURCE8} %{buildroot}%{_libdir}/cmake/hiprtc/hiprtc-targets.cmake
  install -m 644 %{SOURCE9} %{buildroot}%{_libdir}/cmake/hiprtc/hiprtc-targets-relwithdebinfo.cmake
fi

# OpenCL ICD
echo '%{_libdir}/libamdocl64.so' > %{buildroot}%{_sysconfdir}/OpenCL/vendors/amdocl64.icd
# clinfo (optional)
find build -type f -name clinfo -executable -exec install -m755 {} %{buildroot}%{_bindir}/rocm-clinfo \; 2>/dev/null || true

# hip version file for hipconfig/hipcc (KEY=VALUE format required)
mkdir -p %{buildroot}%{_datadir}/hip
cat > %{buildroot}%{_datadir}/hip/version <<EOF
HIP_VERSION_MAJOR=%{rocm_major}
HIP_VERSION_MINOR=%{rocm_minor}
HIP_VERSION_PATCH=%{rocm_patch}
HIP_VERSION_GITHASH=therock-%{rocm_release}
EOF

# clang --rocm-path=/usr hardcodes $ROCM_PATH/lib (not lib64) for libamdhip64.
# Real libraries live in %{_libdir}; ship compatibility symlinks for multi-lib.
%if "%{_lib}" == "lib64"
mkdir -p %{buildroot}/usr/lib
for f in libamdhip64.so.%{hip_so_major} libhiprtc.so.%{hip_so_major} libhiprtc-builtins.so.%{hip_so_major}; do
	if [ -e %{buildroot}%{_libdir}/$f ]; then
		ln -sfn ../lib64/$f %{buildroot}/usr/lib/$f
	fi
done
# unversioned .so for the linker (devel also uses these names under lib64)
for f in libamdhip64.so libhiprtc.so libhiprtc-builtins.so; do
	if [ -e %{buildroot}%{_libdir}/$f ]; then
		ln -sfn ../lib64/$f %{buildroot}/usr/lib/$f
	fi
done
%endif


%files
# meta package holding shared rocclr pieces if any; currently empty runtime
# (HIP and OpenCL libs live in subpackages)
%doc README.md
%license LICENSE.md

%files -n rocm-hip
%{_libdir}/libamdhip64.so.%{hip_so_major}*
%{_libdir}/libhiprtc.so.%{hip_so_major}*
%{_libdir}/libhiprtc-builtins.so.%{hip_so_major}*
%{_datadir}/hip/
%if "%{_lib}" == "lib64"
/usr/lib/libamdhip64.so.%{hip_so_major}
/usr/lib/libhiprtc.so.%{hip_so_major}
/usr/lib/libhiprtc-builtins.so.%{hip_so_major}
%endif

%files -n rocm-hip-devel
%{_includedir}/hip/
%{_libdir}/libamdhip64.so
%{_libdir}/libhiprtc.so
%{_libdir}/libhiprtc-builtins.so
%{_libdir}/cmake/hip/
%{_libdir}/cmake/hip-lang/
%{_libdir}/cmake/hiprtc/
%if "%{_lib}" == "lib64"
/usr/lib/libamdhip64.so
/usr/lib/libhiprtc.so
/usr/lib/libhiprtc-builtins.so
%endif

%files -n rocm-opencl
%{_libdir}/libamdocl64.so*
%config(noreplace) %{_sysconfdir}/OpenCL/vendors/amdocl64.icd
%{_bindir}/rocm-clinfo
