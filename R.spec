Name     : R
Version  : 4.4.0
Release  : 186
URL      : https://ftp.osuosl.org/pub/cran/src/base/R-4/R-4.4.0.tar.gz
Source0  : https://ftp.osuosl.org/pub/cran/src/base/R-4/R-4.4.0.tar.gz
Summary  : Simple Package with NameSpace and S4 Methods and Classes
Group    : Development/Tools
License  : BSD-2-Clause BSD-3-Clause GPL-2.0 GPL-2.0+
Requires: R-bin = %{version}-%{release}
Requires: R-lib = %{version}-%{release}
Requires: R-doc = %{version}-%{release}
Requires: which
BuildRequires : bison
BuildRequires : bzip2-dev
BuildRequires : cairo-dev
BuildRequires : curl-dev
BuildRequires : icu4c-dev
BuildRequires : less
BuildRequires : libidn-dev
BuildRequires : libjpeg-turbo-dev
BuildRequires : libpng-dev
BuildRequires : libssh2-dev
BuildRequires : ncurses-dev
BuildRequires : nghttp2-dev
BuildRequires : openblas
BuildRequires : openblas-staticdev
BuildRequires : openssl-dev
BuildRequires : pango-dev
BuildRequires : pcre2-dev
BuildRequires : readline-dev
BuildRequires : tcl-dev
BuildRequires : tk-dev
BuildRequires : texinfo
BuildRequires : tzdata
BuildRequires : util-linux
BuildRequires : xz-dev
BuildRequires : zip
BuildRequires : pkgconfig(x11)
BuildRequires : pkgconfig(ice)
BuildRequires : pkgconfig(sm)
BuildRequires : pkgconfig(xext)
BuildRequires : gtk3-dev
BuildRequires : libxcb-dev
BuildRequires : xorgproto-dev
BuildRequires : pkgconfig(xi)
BuildRequires : libXt-dev
# R constructs a test program for tcltk support using the link flags listed in
# /usr/lib64/tkConfig.sh (see tk package), but the associated libraries are
# listed under Libs.private in tk.pc, so they should be private to tk... Until
# we resolve this packaging issue, require libXss for the R build.
BuildRequires : pkgconfig(xscrnsaver)
Patch1: 0001-Add-a-2-slot-cache-for-big-malloc-s.patch
Patch2: 0002-help-the-gcc-vectorizer.patch
Patch3: 0003-support-for-.avx2-and-.avx512-so-files.patch
Patch4: 0004-Don-t-force-GC-all-the-time.patch
Patch5: 0005-Set-m4-macro-directory.patch
Patch6: 0006-Add-Rbench-as-PGO-profiling-workload.patch
Patch7: 0007-Adjust-gettext-autotools-config-to-fix-build.patch
Patch8: 0008-libR.pc-link-to-libRblas-as-well.patch
Patch9: lto.patch
Patch10: better-rdb-deltas.patch

%define debug_package %{nil}
%define __strip /bin/true


%description
(See "doc/FAQ" and "doc/RESOURCES" for more detailed information
- these files are only in the tarballs)
(See "INSTALL"             for help on installation)

%package bin
Summary: bin components for the R package.
Group: Binaries

%description bin
bin components for the R package.


%package dev
Summary: dev components for the R package.
Group: Development
Requires: R-lib = %{version}-%{release}
Requires: R-bin = %{version}-%{release}
Provides: R-devel = %{version}-%{release}

%description dev
dev components for the R package.


%package doc
Summary: doc components for the R package.
Group: Documentation

%description doc
doc components for the R package.



%package lib
Summary: lib components for the R package.
Group: Libraries

%description lib
lib components for the R package.


%prep

# Package cannot be built on non-AVX512 capable systems at the moment
if ! grep -qP '^flags\t+:.*\bavx512vl\b' /proc/cpuinfo; then
  echo "ERROR: AVX512 support required for building. The \"avx512vl\" feature flag is missing."
  exit 1
fi

%setup -q
#%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1

pushd ..
cp -a R-%{version} R-%{version}-avx2
cp -a R-%{version} R-%{version}-avx512
cp -a R-%{version} R-%{version}-pgo
popd

%build
export http_proxy=http://127.0.0.1:9/
export https_proxy=http://127.0.0.1:9/
export no_proxy=localhost,127.0.0.1,0.0.0.0
export LANG=C
export SOURCE_DATE_EPOCH=1496604342
unset LD_AS_NEEDED
export CFLAGS_STUB="$CFLAGS -O3 -fno-semantic-interposition -flto=auto -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz=zstd -g1 "
export FCFLAGS_STUB="$CFLAGS -O3 -fno-semantic-interposition -flto=auto -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz=zstd -g1 "
export FFLAGS_STUB="$CFLAGS -O3 -fno-semantic-interposition -flto=auto -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz=zstd -g1 "
export CXXFLAGS_STUB="$CXXFLAGS -O3 -fno-semantic-interposition -flto=auto -gno-variable-location-views -gno-column-info -femit-struct-debug-baseonly -gz=zstd -g1 "

# Ensure that C and C++ shared libraries contain debuginfo by adding -g to
# linker command lines. Note that -g is appended to the default linker flags.
export SHLIB_LDFLAGS="-g"
export SHLIB_CXXLDFLAGS="-g"

export PGO_GEN="-fprofile-generate -fprofile-dir=/var/tmp/pgo "
export PGO_USE="-fprofile-use -fprofile-dir=/var/tmp/pgo -fprofile-correction "
export PGO_GEN_AVX2="-fprofile-generate -fprofile-dir=/var/tmp/pgo_avx2 "
export PGO_USE_AVX2="-fprofile-use -fprofile-dir=/var/tmp/pgo_avx2 -fprofile-correction "
export PGO_GEN_AVX512="-fprofile-generate -fprofile-dir=/var/tmp/pgo_avx512 "
export PGO_USE_AVX512="-fprofile-use -fprofile-dir=/var/tmp/pgo_avx512 -fprofile-correction "

pushd ../R-%{version}-pgo
export CFLAGS="$CFLAGS_STUB $PGO_GEN"
export FCFLAGS="$FCFLAGS_STUB $PGO_GEN"
export FFLAGS="$FFLAGS_STUB $PGO_GEN"
export CXXFLAGS="$CXXFLAGS_STUB $PGO_GEN"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
./bin/Rscript R-benchmark-25/R-benchmark-25.R
make distclean
popd

pushd ../R-%{version}-pgo
export CFLAGS="$CFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_GEN_AVX2"
export FCFLAGS="$FCFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_GEN_AVX2"
export FFLAGS="$FFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_GEN_AVX2"
export CXXFLAGS="$CXXFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_GEN_AVX2"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
./bin/Rscript R-benchmark-25/R-benchmark-25.R
make distclean
popd

pushd ../R-%{version}-pgo
export CFLAGS="$CFLAGS_STUB -march=x86-64-v4 -mprefer-vector-width=256 -flto=auto $PGO_GEN_AVX512"
export FCFLAGS="$FCFLAGS_STUB -march=x86-64-v4 -mprefer-vector-width=256 -flto=auto $PGO_GEN_AVX512"
export FFLAGS="$FFLAGS_STUB -march=x86-64-v4 -mprefer-vector-width=256 -flto=auto $PGO_GEN_AVX512"
export CXXFLAGS="$CXXFLAGS_STUB -march=x86-64-v4 -mprefer-vector-width=256 -flto=auto $PGO_GEN_AVX512"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
./bin/Rscript R-benchmark-25/R-benchmark-25.R
make distclean
popd

### PGO Phase II
export CFLAGS="$CFLAGS_STUB $PGO_USE"
export FCFLAGS="$FCFLAGS_STUB $PGO_USE"
export FFLAGS="$FFLAGS_STUB $PGO_USE"
export CXXFLAGS="$CXXFLAGS_STUB $PGO_USE"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}

pushd ../R-%{version}-avx2
export CFLAGS="$CFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_USE_AVX2"
export FCFLAGS="$FCFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_USE_AVX2"
export FFLAGS="$FFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_USE_AVX2"
export CXXFLAGS="$CXXFLAGS_STUB -march=x86-64-v3 -flto=auto $PGO_USE_AVX2"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
popd

pushd ../R-%{version}-avx512
export CFLAGS="$CFLAGS_STUB -march=x86-64-v4 -flto=auto $PGO_USE_AVX512"
export FCFLAGS="$FCFLAGS_STUB -march=x86-64-v4 -flto=auto $PGO_USE_AVX512"
export FFLAGS="$FFLAGS_STUB -march=x86-64-v4 -flto=auto $PGO_USE_AVX512"
export CXXFLAGS="$CXXFLAGS_STUB -march=x86-64-v4 -flto=auto $PGO_USE_AVX512"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
popd


%install
export SOURCE_DATE_EPOCH=1496604342
rm -rf %{buildroot}

pushd ../R-%{version}-avx512
%make_install_v4
popd

pushd ../R-%{version}-avx2
%make_install_v3
popd

%make_install install-tests
sed -i -e "s/-march=x86-64-v3//g" %{buildroot}/usr/lib64/R/etc/Makeconf

/usr/bin/elf-move.py avx2 %{buildroot}-v3 %{buildroot} %{buildroot}/usr/share/clear/filemap/filemap-%{name}
/usr/bin/elf-move.py avx512 %{buildroot}-v4 %{buildroot} %{buildroot}/usr/share/clear/filemap/filemap-%{name}


%files
%defattr(-,root,root,-)
/usr/lib64/R/COPYING
/usr/lib64/R/SVN-REVISION
/usr/lib64/R/bin/
/V*/usr/lib64/R/bin/
/usr/lib64/R/doc/
%exclude /usr/lib64/R/doc/manual/*.html
/usr/lib64/R/etc/
/usr/lib64/R/library/
/V*//usr/lib64/R/library/
%exclude /usr/lib64/R/library/*/libs/*.so
/usr/lib64/R/share/
/usr/lib64/R/tests/

%files bin
%defattr(-,root,root,-)
/usr/bin/R
/usr/bin/Rscript
/V3/usr/bin/Rscript
/V4/usr/bin/Rscript

%files dev
%defattr(-,root,root,-)
/usr/lib64/R/include/*.h
/usr/lib64/R/include/R_ext/*.h
/usr/lib64/R/library/*/include/*.h
/usr/lib64/pkgconfig/libR.pc

%files doc
%defattr(-,root,root,-)
%doc /usr/share/man/man1/*
/usr/lib64/R/doc/manual/*.html

%files lib
%defattr(-,root,root,-)
/usr/lib64/R/lib/*.so
/usr/lib64/R/library/*/libs/*.so
/V*//usr/lib64/R/modules/*.so
/V*/usr/lib64/R/library/*/libs/*.so
/usr/lib64/R/modules/*.so
/V3/usr/lib64/R/lib/libR.so
/V3/usr/lib64/R/lib/libRblas.so
/V3/usr/lib64/R/lib/libRlapack.so
/V4/usr/lib64/R/lib/libR.so
/V4/usr/lib64/R/lib/libRblas.so
/V4/usr/lib64/R/lib/libRlapack.so