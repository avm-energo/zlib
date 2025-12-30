Name:       avm-zlib
Version:    @PROJECT_VERSION_MAJOR@.@PROJECT_VERSION_MINOR@.@PROJECT_VERSION_PATCH@
Release:    1%{?dist}
Summary:    ZLib for AVM-Energo projects

License:    GPLv3
URL:        https://git.avmenergo.ru/avm-energo/zlib.git
Source0:    https://git.avmenergo.ru/avm-energo/zlib.git

BuildArch:  ${arch}
BuildRequires:  cmake
Requires:
Provides:   avm-zlib

%description
ZLib library for AVM-Energo projects

%prep
%{__rm} -rf
%{__tar} -xzvf %{SOURCE0} -C rpmbuild/BUILD --strip-components 1

%build
cd rpmbuild/BUILD
%cmake -DBUILD_SHARED_LIBS:BOOL=ON -DCMAKE_TOOLCHAIN_FILE=../../../cmake/arch/${arch}.cmake -DCMAKE_INSTALL_PREFIX=rpmbuild/BUILDROOT
%cmake_build

%install
%cmake_install

%package devel

%description devel
ZLib library development files for AVM-Energo projects

%files
%license add-license-file-here
rpmbuild/BUILDROOT/avm-zlib.so*

%changelog
* Tue Dec 30 2025 anton <vao@asu-vei.ru>
- initial rpm build
