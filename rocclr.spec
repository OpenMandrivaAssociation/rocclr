%define _empty_manifest_terminate_build 0
%global debug_package %{nil}
%global build_ldflags %{build_ldflags} -Wl,--undefined-version

# ROCclr loads comgr at run time by soversion, so this needs to be checked when
# updating this package as it's used for the comgr requires for opencl and hip:
%global comgr_maj_api_ver 2
# See the file "rocclr/device/comgrctx.cpp" for reference:
# https://github.com/ROCm-Developer-Tools/ROCclr/blob/develop/device/comgrctx.cpp#L62
 
%global rocm_release %(echo %{version}|cut -d. -f1-2)
%global rocm_patch %(echo %{version}|cut -d. -f3-)
 
Name:           rocclr
Version:        6.3.3
Release:        1
Summary:        ROCm Compute Language Runtime
Group:          System/Configuration/ROCm
Url:            https://github.com/ROCm-Developer-Tools/clr
License:        MIT
Source0:        https://github.com/ROCm-Developer-Tools/clr/archive/refs/tags/rocm-%{version}.tar.gz#/clr-rocm-%{version}.tar.gz
Source1:	https://github.com/ROCm-Developer-Tools/HIP/archive/refs/tags/rocm-%{version}.tar.gz#/HIP-%{version}.tar.gz
 
BuildRequires:  cmake
BuildRequires:  cmake(Clang)
BuildRequires:  doxygen
BuildRequires:  fdupes
BuildRequires:  pkgconfig(libffi)
BuildRequires:  cmake(LLVM)
BuildRequires:  perl
BuildRequires:  perl-generators
BuildRequires:  pkgconfig(opengl)
BuildRequires:  pkgconfig(numa)
BuildRequires:  pkgconfig(OpenCL)
BuildRequires:  python-cppheaderparser
BuildRequires:  cmake(amd_comgr)
BuildRequires:	cmake(rocprofiler-register)
BuildRequires:	rocm-opencl-devel
BuildRequires:  rocm-runtime-devel >= %{rocm_release}
BuildRequires:  rocminfo >= %{rocm_release}
BuildRequires:	rocm-comgr
BuildRequires:  pkgconfig(zlib)
 
# rocclr bundles OpenCL 2.2 headers
# Some work is needed to unbundle this, as it fails to compile with latest
Provides:       bundled(opencl-headers) = 2.2
 
%description
ROCm Compute Language Runtime
 
%package -n rocm-opencl
Summary:        ROCm OpenCL platform and device tool
Requires:       rocm-comgr
Requires:	%mklibname OpenCL
 
%description -n rocm-opencl
ROCm OpenCL language runtime.
Supports offline and in-process/in-memory compilation.
 
%package -n rocm-opencl-devel
Summary:        ROCm OpenCL development package
Requires:       rocm-opencl%{?_isa} = %{version}-%{release}
Requires:       pkgconfig(OpenCL)
 
%description -n rocm-opencl-devel
The AMD ROCm OpenCL development package.
 
%package -n rocm-clinfo
Summary:        ROCm OpenCL platform and device tool
 
%description -n rocm-clinfo
A simple ROCm OpenCL application that enumerates all possible platform and
device information.
 
%prep
%autosetup -n clr-rocm-%{version} -p1 -a 1
# Enable experimental pre vega platforms
sed -i 's/\(ROC_ENABLE_PRE_VEGA.*\)false/\1true/' rocclr/utils/flags.hpp

cat > README.%_real_vendor <<EOF
=============================================================
New users will have to be added to render and video groups.
Already existing users are taken care of during installation.
=============================================================
EOF

TOP="$(pwd)"
%cmake \
	-DCLR_BUILD_OCL=ON \
	-DHIP_COMMON_DIR="${TOP}/HIP-rocm-%{version}" \
	-DHIPCC_BIN_DIR="%{_bindir}" \
	-DHIP_PLATFORM=amd \
	-DCLR_BUILD_HIP=ON \
	-G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build

#install -m644 README.%_real_vendor README.urpmi

cat > rocm.conf <<EOF
%{_libdir}/rocm
EOF
install -Dm644 rocm.conf %{buildroot}%{_sysconfdir}/ld.so.conf.d/rocm.conf

mkdir -p %{buildroot}%{_sysconfdir}/OpenCL/vendors
echo '%{_libdir}/rocm/libamdocl64.so' > 'amdocl64.icd'
install -Dm644 amdocl64.icd %{buildroot}%{_sysconfdir}/OpenCL/vendors/amdocl64.icd

#Specific lib folder for ROCm
mkdir -p %{buildroot}%{_libdir}/rocm
mv %{buildroot}%{_libdir}/lib* %{buildroot}%{_libdir}/rocm

#Avoid file conflicts with opencl-headers package:
mkdir -p %{buildroot}%{_includedir}/rocm
mv %{buildroot}%{_includedir}/CL %{buildroot}%{_includedir}/rocm/CL

#Avoid file conflicts with clinfo package:
mv %{buildroot}/%{_bindir}/clinfo %{buildroot}/%{_bindir}/rocm-clinfo

#Avoid duplicate
rm -rf %{buildroot}/%{_usr}/opencl


%post
#To add existing users to the video and render groups
userlist=($(ls /home | cut -d/ -f1))
for existinguser in "${userlist[@]}"; do
if [ "$existinguser" != "lost+found" ]; then
echo "Update groups of $existinguser"
usermod -a -G render,video $existinguser
su -l $existinguser
su -l $USER
fi
done

#apply configuration
echo "Run ldconfig"
ldconfig


%files -n rocm-opencl
%license opencl/LICENSE.txt
%config(noreplace) %{_sysconfdir}/OpenCL/vendors/amdocl64.icd
%{_sysconfdir}/ld.so.conf.d/rocm.conf
%{_libdir}/rocm
#Duplicated files:
%exclude %{_docdir}/*/LICENSE*
 
%files -n rocm-opencl-devel
%{_includedir}/rocm/CL
%{_bindir}/hipcc*
%{_bindir}/hipconfig*
%{_bindir}/hipdemangleatp
%{_bindir}/hipvars.pm
%{_bindir}/roc-obj*
%{_includedir}/hip
%{_includedir}/hip_prof_str.h
%{_libdir}/.hipInfo
%{_libdir}/cmake/hip*
%{_datadir}/hip
%doc %{_docdir}/hip
 
%files -n rocm-clinfo
%license opencl/LICENSE.txt
%{_bindir}/rocm-clinfo
