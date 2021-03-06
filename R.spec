Name     : R
Version  : 4.0.3
Release  : 132
URL      : https://ftp.osuosl.org/pub/cran/src/base/R-4/R-4.0.3.tar.gz
Source0  : https://ftp.osuosl.org/pub/cran/src/base/R-4/R-4.0.3.tar.gz
Summary  : Simple Package with NameSpace and S4 Methods and Classes
Group    : Development/Tools
License  : BSD-2-Clause BSD-3-Clause GPL-2.0 GPL-2.0+
Requires: R-bin
Requires: R-lib
Requires: R-doc
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
Patch8: lto.patch

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
Requires: R-lib
Requires: R-bin
Provides: R-devel

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
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1

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
export CFLAGS_STUB="$CFLAGS -O3 -falign-functions=32 -fno-semantic-interposition -flto=12 "
export FCFLAGS_STUB="$CFLAGS -O3 -falign-functions=32 -fno-semantic-interposition -flto=12 "
export FFLAGS_STUB="$CFLAGS -O3 -falign-functions=32 -fno-semantic-interposition -flto=12 "
export CXXFLAGS_STUB="$CXXFLAGS -O3 -falign-functions=32 -fno-semantic-interposition -flto=12 "

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
export CFLAGS="$CFLAGS_STUB -march=haswell -flto=12 $PGO_GEN_AVX2"
export FCFLAGS="$FCFLAGS_STUB -march=haswell -flto=12 $PGO_GEN_AVX2"
export FFLAGS="$FFLAGS_STUB -march=haswell -flto=12 $PGO_GEN_AVX2"
export CXXFLAGS="$CXXFLAGS_STUB -march=haswell -flto=12 $PGO_GEN_AVX2"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
./bin/Rscript R-benchmark-25/R-benchmark-25.R
make distclean
popd

pushd ../R-%{version}-pgo
export CFLAGS="$CFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_GEN_AVX512"
export FCFLAGS="$FCFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_GEN_AVX512"
export FFLAGS="$FFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_GEN_AVX512"
export CXXFLAGS="$CXXFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_GEN_AVX512"
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
export CFLAGS="$CFLAGS_STUB -march=haswell -flto=12 $PGO_USE_AVX2"
export FCFLAGS="$FCFLAGS_STUB -march=haswell -flto=12 $PGO_USE_AVX2"
export FFLAGS="$FFLAGS_STUB -march=haswell -flto=12 $PGO_USE_AVX2"
export CXXFLAGS="$CXXFLAGS_STUB -march=haswell -flto=12 $PGO_USE_AVX2"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
popd

pushd ../R-%{version}-avx512
export CFLAGS="$CFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_USE_AVX512"
export FCFLAGS="$FCFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_USE_AVX512"
export FFLAGS="$FFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_USE_AVX512"
export CXXFLAGS="$CXXFLAGS_STUB -march=skylake-avx512 -flto=12 $PGO_USE_AVX512"
%reconfigure --disable-static --with-system-zlib --with-system-bzlib --with-system-pcre --with-system-xz --enable-BLAS-shlib --enable-R-shlib --with-blas="-lopenblas" --with-cairo --enable-lto --disable-long-double
make V=1  %{?_smp_mflags}
popd


%install
export SOURCE_DATE_EPOCH=1496604342
rm -rf %{buildroot}

pushd ../R-%{version}-avx512
%make_install
mkdir -p %{buildroot}/usr/lib64/R/lib/haswell/avx512_1
mv %{buildroot}/usr/lib64/R/lib/*.so %{buildroot}/usr/lib64/R/lib/haswell/avx512_1
for i in `find %{buildroot}/usr/lib64/R/library/ -name "*.so"`; do mv $i $i.avx512 ; done
rm `find %{buildroot} -type f | grep -v avx512 | grep -v haswell`  || :
popd

pushd ../R-%{version}-avx2
%make_install
mkdir -p %{buildroot}/usr/lib64/R/lib/haswell/
mv %{buildroot}/usr/lib64/R/lib/*.so %{buildroot}/usr/lib64/R/lib/haswell/
for i in `find %{buildroot}/usr/lib64/R/library/ -name "*.so"`; do mv $i $i.avx2 ; done
rm `find %{buildroot} -type f | grep -v avx2 | grep -v avx512 | grep -v haswell`  || :
popd

%make_install install-tests
sed -i -e "s/-march=haswell//g" %{buildroot}/usr/lib64/R/etc/Makeconf


%files
%defattr(-,root,root,-)
/usr/lib64/R/COPYING
/usr/lib64/R/SVN-REVISION
/usr/lib64/R/bin/BATCH
/usr/lib64/R/bin/COMPILE
/usr/lib64/R/bin/INSTALL
/usr/lib64/R/bin/LINK
/usr/lib64/R/bin/R
/usr/lib64/R/bin/REMOVE
/usr/lib64/R/bin/Rcmd
/usr/lib64/R/bin/Rd2pdf
/usr/lib64/R/bin/Rdconv
/usr/lib64/R/bin/Rdiff
/usr/lib64/R/bin/Rprof
/usr/lib64/R/bin/Rscript
/usr/lib64/R/bin/SHLIB
/usr/lib64/R/bin/Stangle
/usr/lib64/R/bin/Sweave
/usr/lib64/R/bin/build
/usr/lib64/R/bin/check
/usr/lib64/R/bin/config
/usr/lib64/R/bin/exec/R
/usr/lib64/R/bin/javareconf
/usr/lib64/R/bin/libtool
/usr/lib64/R/bin/mkinstalldirs
/usr/lib64/R/bin/pager
/usr/lib64/R/bin/rtags
/usr/lib64/R/doc/AUTHORS
/usr/lib64/R/doc/BioC_mirrors.csv
/usr/lib64/R/doc/COPYING
/usr/lib64/R/doc/COPYRIGHTS
/usr/lib64/R/doc/CRAN_mirrors.csv
/usr/lib64/R/doc/FAQ
/usr/lib64/R/doc/KEYWORDS
/usr/lib64/R/doc/KEYWORDS.db
/usr/lib64/R/doc/NEWS
/usr/lib64/R/doc/NEWS.0
/usr/lib64/R/doc/NEWS.1
/usr/lib64/R/doc/NEWS.2
/usr/lib64/R/doc/NEWS.2.rds
/usr/lib64/R/doc/NEWS.3
/usr/lib64/R/doc/NEWS.3.rds
/usr/lib64/R/doc/NEWS.pdf
/usr/lib64/R/doc/NEWS.rds
/usr/lib64/R/doc/RESOURCES
/usr/lib64/R/doc/THANKS
/usr/lib64/R/doc/html/NEWS.2.html
/usr/lib64/R/doc/html/NEWS.3.html
/usr/lib64/R/doc/html/NEWS.html
/usr/lib64/R/doc/html/R.css
/usr/lib64/R/doc/html/Rlogo.pdf
/usr/lib64/R/doc/html/Rlogo.svg
/usr/lib64/R/doc/html/Search.html
/usr/lib64/R/doc/html/SearchOn.html
/usr/lib64/R/doc/html/about.html
/usr/lib64/R/doc/html/favicon.ico
/usr/lib64/R/doc/html/index.html
/usr/lib64/R/doc/html/left.jpg
/usr/lib64/R/doc/html/logo.jpg
/usr/lib64/R/doc/html/packages-head-utf8.html
/usr/lib64/R/doc/html/packages.html
/usr/lib64/R/doc/html/resources.html
/usr/lib64/R/doc/html/right.jpg
/usr/lib64/R/doc/html/up.jpg
/usr/lib64/R/doc/manual/images/QQ.png
/usr/lib64/R/doc/manual/images/ecdf.png
/usr/lib64/R/doc/manual/images/fig11.png
/usr/lib64/R/doc/manual/images/fig12.png
/usr/lib64/R/doc/manual/images/hist.png
/usr/lib64/R/doc/manual/images/ice.png
/usr/lib64/R/etc/Makeconf
/usr/lib64/R/etc/Renviron
/usr/lib64/R/etc/javaconf
/usr/lib64/R/etc/ldpaths
/usr/lib64/R/etc/repositories
/usr/lib64/R/library/KernSmooth/DESCRIPTION
/usr/lib64/R/library/KernSmooth/INDEX
/usr/lib64/R/library/KernSmooth/Meta/Rd.rds
/usr/lib64/R/library/KernSmooth/Meta/features.rds
/usr/lib64/R/library/KernSmooth/Meta/hsearch.rds
/usr/lib64/R/library/KernSmooth/Meta/links.rds
/usr/lib64/R/library/KernSmooth/Meta/nsInfo.rds
/usr/lib64/R/library/KernSmooth/Meta/package.rds
/usr/lib64/R/library/KernSmooth/NAMESPACE
/usr/lib64/R/library/KernSmooth/R/KernSmooth
/usr/lib64/R/library/KernSmooth/R/KernSmooth.rdb
/usr/lib64/R/library/KernSmooth/R/KernSmooth.rdx
/usr/lib64/R/library/KernSmooth/help/AnIndex
/usr/lib64/R/library/KernSmooth/help/KernSmooth.rdb
/usr/lib64/R/library/KernSmooth/help/KernSmooth.rdx
/usr/lib64/R/library/KernSmooth/help/aliases.rds
/usr/lib64/R/library/KernSmooth/help/paths.rds
/usr/lib64/R/library/KernSmooth/html/00Index.html
/usr/lib64/R/library/KernSmooth/html/R.css
/usr/lib64/R/library/KernSmooth/po/de/LC_MESSAGES/R-KernSmooth.mo
/usr/lib64/R/library/KernSmooth/po/en@quot/LC_MESSAGES/R-KernSmooth.mo
/usr/lib64/R/library/KernSmooth/po/fr/LC_MESSAGES/R-KernSmooth.mo
/usr/lib64/R/library/KernSmooth/po/ko/LC_MESSAGES/R-KernSmooth.mo
/usr/lib64/R/library/KernSmooth/po/pl/LC_MESSAGES/R-KernSmooth.mo
/usr/lib64/R/library/MASS/CITATION
/usr/lib64/R/library/MASS/DESCRIPTION
/usr/lib64/R/library/MASS/INDEX
/usr/lib64/R/library/MASS/Meta/Rd.rds
/usr/lib64/R/library/MASS/Meta/data.rds
/usr/lib64/R/library/MASS/Meta/features.rds
/usr/lib64/R/library/MASS/Meta/hsearch.rds
/usr/lib64/R/library/MASS/Meta/links.rds
/usr/lib64/R/library/MASS/Meta/nsInfo.rds
/usr/lib64/R/library/MASS/Meta/package.rds
/usr/lib64/R/library/MASS/NAMESPACE
/usr/lib64/R/library/MASS/NEWS
/usr/lib64/R/library/MASS/R/MASS
/usr/lib64/R/library/MASS/R/MASS.rdb
/usr/lib64/R/library/MASS/R/MASS.rdx
/usr/lib64/R/library/MASS/data/Rdata.rdb
/usr/lib64/R/library/MASS/data/Rdata.rds
/usr/lib64/R/library/MASS/data/Rdata.rdx
/usr/lib64/R/library/MASS/help/AnIndex
/usr/lib64/R/library/MASS/help/MASS.rdb
/usr/lib64/R/library/MASS/help/MASS.rdx
/usr/lib64/R/library/MASS/help/aliases.rds
/usr/lib64/R/library/MASS/help/paths.rds
/usr/lib64/R/library/MASS/html/00Index.html
/usr/lib64/R/library/MASS/html/R.css
/usr/lib64/R/library/MASS/po/de/LC_MESSAGES/R-MASS.mo
/usr/lib64/R/library/MASS/po/en@quot/LC_MESSAGES/R-MASS.mo
/usr/lib64/R/library/MASS/po/fr/LC_MESSAGES/R-MASS.mo
/usr/lib64/R/library/MASS/po/ko/LC_MESSAGES/R-MASS.mo
/usr/lib64/R/library/MASS/po/pl/LC_MESSAGES/R-MASS.mo
/usr/lib64/R/library/MASS/scripts/ch01.R
/usr/lib64/R/library/MASS/scripts/ch02.R
/usr/lib64/R/library/MASS/scripts/ch03.R
/usr/lib64/R/library/MASS/scripts/ch04.R
/usr/lib64/R/library/MASS/scripts/ch05.R
/usr/lib64/R/library/MASS/scripts/ch06.R
/usr/lib64/R/library/MASS/scripts/ch07.R
/usr/lib64/R/library/MASS/scripts/ch08.R
/usr/lib64/R/library/MASS/scripts/ch09.R
/usr/lib64/R/library/MASS/scripts/ch10.R
/usr/lib64/R/library/MASS/scripts/ch11.R
/usr/lib64/R/library/MASS/scripts/ch12.R
/usr/lib64/R/library/MASS/scripts/ch13.R
/usr/lib64/R/library/MASS/scripts/ch14.R
/usr/lib64/R/library/MASS/scripts/ch15.R
/usr/lib64/R/library/MASS/scripts/ch16.R
/usr/lib64/R/library/Matrix/Copyrights
/usr/lib64/R/library/Matrix/DESCRIPTION
/usr/lib64/R/library/Matrix/Doxyfile
/usr/lib64/R/library/Matrix/INDEX
/usr/lib64/R/library/Matrix/LICENCE
/usr/lib64/R/library/Matrix/Meta/Rd.rds
/usr/lib64/R/library/Matrix/Meta/data.rds
/usr/lib64/R/library/Matrix/Meta/features.rds
/usr/lib64/R/library/Matrix/Meta/hsearch.rds
/usr/lib64/R/library/Matrix/Meta/links.rds
/usr/lib64/R/library/Matrix/Meta/nsInfo.rds
/usr/lib64/R/library/Matrix/Meta/package.rds
/usr/lib64/R/library/Matrix/Meta/vignette.rds
/usr/lib64/R/library/Matrix/NAMESPACE
/usr/lib64/R/library/Matrix/NEWS.Rd
/usr/lib64/R/library/Matrix/R/Matrix
/usr/lib64/R/library/Matrix/R/Matrix.rdb
/usr/lib64/R/library/Matrix/R/Matrix.rdx
/usr/lib64/R/library/Matrix/data/CAex.R
/usr/lib64/R/library/Matrix/data/KNex.R
/usr/lib64/R/library/Matrix/data/USCounties.R
/usr/lib64/R/library/Matrix/doc/Announce.txt
/usr/lib64/R/library/Matrix/doc/Comparisons.R
/usr/lib64/R/library/Matrix/doc/Comparisons.Rnw
/usr/lib64/R/library/Matrix/doc/Comparisons.pdf
/usr/lib64/R/library/Matrix/doc/Design-issues.R
/usr/lib64/R/library/Matrix/doc/Design-issues.Rnw
/usr/lib64/R/library/Matrix/doc/Design-issues.pdf
/usr/lib64/R/library/Matrix/doc/Intro2Matrix.R
/usr/lib64/R/library/Matrix/doc/Intro2Matrix.Rnw
/usr/lib64/R/library/Matrix/doc/Intro2Matrix.pdf
/usr/lib64/R/library/Matrix/doc/Introduction.R
/usr/lib64/R/library/Matrix/doc/Introduction.Rnw
/usr/lib64/R/library/Matrix/doc/Introduction.pdf
/usr/lib64/R/library/Matrix/doc/SuiteSparse/AMD.txt
/usr/lib64/R/library/Matrix/doc/SuiteSparse/CHOLMOD.txt
/usr/lib64/R/library/Matrix/doc/SuiteSparse/COLAMD.txt
/usr/lib64/R/library/Matrix/doc/SuiteSparse/SPQR.txt
/usr/lib64/R/library/Matrix/doc/SuiteSparse/SuiteSparse_config.txt
/usr/lib64/R/library/Matrix/doc/SuiteSparse/UserGuides.txt
/usr/lib64/R/library/Matrix/doc/index.html
/usr/lib64/R/library/Matrix/doc/sparseModels.R
/usr/lib64/R/library/Matrix/doc/sparseModels.Rnw
/usr/lib64/R/library/Matrix/doc/sparseModels.pdf
/usr/lib64/R/library/Matrix/external/CAex_slots.rda
/usr/lib64/R/library/Matrix/external/KNex_slots.rda
/usr/lib64/R/library/Matrix/external/USCounties_slots.rda
/usr/lib64/R/library/Matrix/external/lund_a.mtx
/usr/lib64/R/library/Matrix/external/lund_a.rsa
/usr/lib64/R/library/Matrix/external/pores_1.mtx
/usr/lib64/R/library/Matrix/external/symA.rda
/usr/lib64/R/library/Matrix/external/symW.rda
/usr/lib64/R/library/Matrix/external/test3comp.rda
/usr/lib64/R/library/Matrix/external/utm300.rua
/usr/lib64/R/library/Matrix/external/wrong.mtx
/usr/lib64/R/library/Matrix/help/AnIndex
/usr/lib64/R/library/Matrix/help/Matrix.rdb
/usr/lib64/R/library/Matrix/help/Matrix.rdx
/usr/lib64/R/library/Matrix/help/aliases.rds
/usr/lib64/R/library/Matrix/help/paths.rds
/usr/lib64/R/library/Matrix/html/00Index.html
/usr/lib64/R/library/Matrix/html/R.css
/usr/lib64/R/library/Matrix/include/Matrix_stubs.c
/usr/lib64/R/library/Matrix/po/de/LC_MESSAGES/Matrix.mo
/usr/lib64/R/library/Matrix/po/de/LC_MESSAGES/R-Matrix.mo
/usr/lib64/R/library/Matrix/po/en@quot/LC_MESSAGES/Matrix.mo
/usr/lib64/R/library/Matrix/po/en@quot/LC_MESSAGES/R-Matrix.mo
/usr/lib64/R/library/Matrix/po/fr/LC_MESSAGES/Matrix.mo
/usr/lib64/R/library/Matrix/po/fr/LC_MESSAGES/R-Matrix.mo
/usr/lib64/R/library/Matrix/po/ko/LC_MESSAGES/R-Matrix.mo
/usr/lib64/R/library/Matrix/po/pl/LC_MESSAGES/Matrix.mo
/usr/lib64/R/library/Matrix/po/pl/LC_MESSAGES/R-Matrix.mo
/usr/lib64/R/library/Matrix/test-tools-1.R
/usr/lib64/R/library/Matrix/test-tools-Matrix.R
/usr/lib64/R/library/Matrix/test-tools.R
/usr/lib64/R/library/base/CITATION
/usr/lib64/R/library/base/DESCRIPTION
/usr/lib64/R/library/base/INDEX
/usr/lib64/R/library/base/Meta/Rd.rds
/usr/lib64/R/library/base/Meta/demo.rds
/usr/lib64/R/library/base/Meta/features.rds
/usr/lib64/R/library/base/Meta/hsearch.rds
/usr/lib64/R/library/base/Meta/links.rds
/usr/lib64/R/library/base/Meta/package.rds
/usr/lib64/R/library/base/R/Rprofile
/usr/lib64/R/library/base/R/base
/usr/lib64/R/library/base/R/base.rdb
/usr/lib64/R/library/base/R/base.rdx
/usr/lib64/R/library/base/demo/error.catching.R
/usr/lib64/R/library/base/demo/is.things.R
/usr/lib64/R/library/base/demo/recursion.R
/usr/lib64/R/library/base/demo/scoping.R
/usr/lib64/R/library/base/help/AnIndex
/usr/lib64/R/library/base/help/aliases.rds
/usr/lib64/R/library/base/help/base.rdb
/usr/lib64/R/library/base/help/base.rdx
/usr/lib64/R/library/base/help/paths.rds
/usr/lib64/R/library/base/html/00Index.html
/usr/lib64/R/library/base/html/R.css
/usr/lib64/R/library/boot/CITATION
/usr/lib64/R/library/boot/DESCRIPTION
/usr/lib64/R/library/boot/INDEX
/usr/lib64/R/library/boot/Meta/Rd.rds
/usr/lib64/R/library/boot/Meta/data.rds
/usr/lib64/R/library/boot/Meta/features.rds
/usr/lib64/R/library/boot/Meta/hsearch.rds
/usr/lib64/R/library/boot/Meta/links.rds
/usr/lib64/R/library/boot/Meta/nsInfo.rds
/usr/lib64/R/library/boot/Meta/package.rds
/usr/lib64/R/library/boot/NAMESPACE
/usr/lib64/R/library/boot/R/boot
/usr/lib64/R/library/boot/R/boot.rdb
/usr/lib64/R/library/boot/R/boot.rdx
/usr/lib64/R/library/boot/bd.q
/usr/lib64/R/library/boot/data/Rdata.rdb
/usr/lib64/R/library/boot/data/Rdata.rds
/usr/lib64/R/library/boot/data/Rdata.rdx
/usr/lib64/R/library/boot/help/AnIndex
/usr/lib64/R/library/boot/help/aliases.rds
/usr/lib64/R/library/boot/help/boot.rdb
/usr/lib64/R/library/boot/help/boot.rdx
/usr/lib64/R/library/boot/help/paths.rds
/usr/lib64/R/library/boot/html/00Index.html
/usr/lib64/R/library/boot/html/R.css
/usr/lib64/R/library/boot/po/de/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/boot/po/en@quot/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/boot/po/fr/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/boot/po/ko/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/boot/po/pl/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/boot/po/ru/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/class/CITATION
/usr/lib64/R/library/class/DESCRIPTION
/usr/lib64/R/library/class/INDEX
/usr/lib64/R/library/class/Meta/Rd.rds
/usr/lib64/R/library/class/Meta/features.rds
/usr/lib64/R/library/class/Meta/hsearch.rds
/usr/lib64/R/library/class/Meta/links.rds
/usr/lib64/R/library/class/Meta/nsInfo.rds
/usr/lib64/R/library/class/Meta/package.rds
/usr/lib64/R/library/class/NAMESPACE
/usr/lib64/R/library/class/NEWS
/usr/lib64/R/library/class/R/class
/usr/lib64/R/library/class/R/class.rdb
/usr/lib64/R/library/class/R/class.rdx
/usr/lib64/R/library/class/help/AnIndex
/usr/lib64/R/library/class/help/aliases.rds
/usr/lib64/R/library/class/help/class.rdb
/usr/lib64/R/library/class/help/class.rdx
/usr/lib64/R/library/class/help/paths.rds
/usr/lib64/R/library/class/html/00Index.html
/usr/lib64/R/library/class/html/R.css
/usr/lib64/R/library/class/po/de/LC_MESSAGES/R-class.mo
/usr/lib64/R/library/class/po/en@quot/LC_MESSAGES/R-class.mo
/usr/lib64/R/library/class/po/fr/LC_MESSAGES/R-class.mo
/usr/lib64/R/library/class/po/it/LC_MESSAGES/R-class.mo
/usr/lib64/R/library/class/po/ko/LC_MESSAGES/R-class.mo
/usr/lib64/R/library/class/po/pl/LC_MESSAGES/R-class.mo
/usr/lib64/R/library/cluster/CITATION
/usr/lib64/R/library/cluster/DESCRIPTION
/usr/lib64/R/library/cluster/INDEX
/usr/lib64/R/library/cluster/Meta/Rd.rds
/usr/lib64/R/library/cluster/Meta/data.rds
/usr/lib64/R/library/cluster/Meta/features.rds
/usr/lib64/R/library/cluster/Meta/hsearch.rds
/usr/lib64/R/library/cluster/Meta/links.rds
/usr/lib64/R/library/cluster/Meta/nsInfo.rds
/usr/lib64/R/library/cluster/Meta/package.rds
/usr/lib64/R/library/cluster/NAMESPACE
/usr/lib64/R/library/cluster/NEWS.Rd
/usr/lib64/R/library/cluster/R/cluster
/usr/lib64/R/library/cluster/R/cluster.rdb
/usr/lib64/R/library/cluster/R/cluster.rdx
/usr/lib64/R/library/cluster/data/Rdata.rdb
/usr/lib64/R/library/cluster/data/Rdata.rds
/usr/lib64/R/library/cluster/data/Rdata.rdx
/usr/lib64/R/library/cluster/help/AnIndex
/usr/lib64/R/library/cluster/help/aliases.rds
/usr/lib64/R/library/cluster/help/cluster.rdb
/usr/lib64/R/library/cluster/help/cluster.rdx
/usr/lib64/R/library/cluster/help/paths.rds
/usr/lib64/R/library/cluster/html/00Index.html
/usr/lib64/R/library/cluster/html/R.css
/usr/lib64/R/library/cluster/po/de/LC_MESSAGES/R-cluster.mo
/usr/lib64/R/library/cluster/po/de/LC_MESSAGES/cluster.mo
/usr/lib64/R/library/cluster/po/en@quot/LC_MESSAGES/R-cluster.mo
/usr/lib64/R/library/cluster/po/en@quot/LC_MESSAGES/cluster.mo
/usr/lib64/R/library/cluster/po/fr/LC_MESSAGES/R-cluster.mo
/usr/lib64/R/library/cluster/po/ko/LC_MESSAGES/R-cluster.mo
/usr/lib64/R/library/cluster/po/ko/LC_MESSAGES/cluster.mo
/usr/lib64/R/library/cluster/po/pl/LC_MESSAGES/R-cluster.mo
/usr/lib64/R/library/cluster/test-tools.R
/usr/lib64/R/library/codetools/DESCRIPTION
/usr/lib64/R/library/codetools/INDEX
/usr/lib64/R/library/codetools/Meta/Rd.rds
/usr/lib64/R/library/codetools/Meta/features.rds
/usr/lib64/R/library/codetools/Meta/hsearch.rds
/usr/lib64/R/library/codetools/Meta/links.rds
/usr/lib64/R/library/codetools/Meta/nsInfo.rds
/usr/lib64/R/library/codetools/Meta/package.rds
/usr/lib64/R/library/codetools/NAMESPACE
/usr/lib64/R/library/codetools/R/codetools
/usr/lib64/R/library/codetools/R/codetools.rdb
/usr/lib64/R/library/codetools/R/codetools.rdx
/usr/lib64/R/library/codetools/help/AnIndex
/usr/lib64/R/library/codetools/help/aliases.rds
/usr/lib64/R/library/codetools/help/codetools.rdb
/usr/lib64/R/library/codetools/help/codetools.rdx
/usr/lib64/R/library/codetools/help/paths.rds
/usr/lib64/R/library/codetools/html/00Index.html
/usr/lib64/R/library/codetools/html/R.css
/usr/lib64/R/library/compiler/DESCRIPTION
/usr/lib64/R/library/compiler/INDEX
/usr/lib64/R/library/compiler/Meta/Rd.rds
/usr/lib64/R/library/compiler/Meta/features.rds
/usr/lib64/R/library/compiler/Meta/hsearch.rds
/usr/lib64/R/library/compiler/Meta/links.rds
/usr/lib64/R/library/compiler/Meta/nsInfo.rds
/usr/lib64/R/library/compiler/Meta/package.rds
/usr/lib64/R/library/compiler/NAMESPACE
/usr/lib64/R/library/compiler/R/compiler
/usr/lib64/R/library/compiler/R/compiler.rdb
/usr/lib64/R/library/compiler/R/compiler.rdx
/usr/lib64/R/library/compiler/help/AnIndex
/usr/lib64/R/library/compiler/help/aliases.rds
/usr/lib64/R/library/compiler/help/compiler.rdb
/usr/lib64/R/library/compiler/help/compiler.rdx
/usr/lib64/R/library/compiler/help/paths.rds
/usr/lib64/R/library/compiler/html/00Index.html
/usr/lib64/R/library/compiler/html/R.css
/usr/lib64/R/library/datasets/DESCRIPTION
/usr/lib64/R/library/datasets/INDEX
/usr/lib64/R/library/datasets/Meta/Rd.rds
/usr/lib64/R/library/datasets/Meta/data.rds
/usr/lib64/R/library/datasets/Meta/features.rds
/usr/lib64/R/library/datasets/Meta/hsearch.rds
/usr/lib64/R/library/datasets/Meta/links.rds
/usr/lib64/R/library/datasets/Meta/nsInfo.rds
/usr/lib64/R/library/datasets/Meta/package.rds
/usr/lib64/R/library/datasets/NAMESPACE
/usr/lib64/R/library/datasets/data/Rdata.rdb
/usr/lib64/R/library/datasets/data/Rdata.rds
/usr/lib64/R/library/datasets/data/Rdata.rdx
/usr/lib64/R/library/datasets/data/morley.tab
/usr/lib64/R/library/datasets/help/AnIndex
/usr/lib64/R/library/datasets/help/aliases.rds
/usr/lib64/R/library/datasets/help/datasets.rdb
/usr/lib64/R/library/datasets/help/datasets.rdx
/usr/lib64/R/library/datasets/help/paths.rds
/usr/lib64/R/library/datasets/html/00Index.html
/usr/lib64/R/library/datasets/html/R.css
/usr/lib64/R/library/foreign/COPYRIGHTS
/usr/lib64/R/library/foreign/DESCRIPTION
/usr/lib64/R/library/foreign/INDEX
/usr/lib64/R/library/foreign/Meta/Rd.rds
/usr/lib64/R/library/foreign/Meta/features.rds
/usr/lib64/R/library/foreign/Meta/hsearch.rds
/usr/lib64/R/library/foreign/Meta/links.rds
/usr/lib64/R/library/foreign/Meta/nsInfo.rds
/usr/lib64/R/library/foreign/Meta/package.rds
/usr/lib64/R/library/foreign/NAMESPACE
/usr/lib64/R/library/foreign/R/foreign
/usr/lib64/R/library/foreign/R/foreign.rdb
/usr/lib64/R/library/foreign/R/foreign.rdx
/usr/lib64/R/library/foreign/files/HillRace.SYD
/usr/lib64/R/library/foreign/files/Iris.syd
/usr/lib64/R/library/foreign/files/electric.sav
/usr/lib64/R/library/foreign/files/sids.dbf
/usr/lib64/R/library/foreign/files/testdata.sav
/usr/lib64/R/library/foreign/help/AnIndex
/usr/lib64/R/library/foreign/help/aliases.rds
/usr/lib64/R/library/foreign/help/foreign.rdb
/usr/lib64/R/library/foreign/help/foreign.rdx
/usr/lib64/R/library/foreign/help/paths.rds
/usr/lib64/R/library/foreign/html/00Index.html
/usr/lib64/R/library/foreign/html/R.css
/usr/lib64/R/library/foreign/po/de/LC_MESSAGES/R-foreign.mo
/usr/lib64/R/library/foreign/po/de/LC_MESSAGES/foreign.mo
/usr/lib64/R/library/foreign/po/en@quot/LC_MESSAGES/R-foreign.mo
/usr/lib64/R/library/foreign/po/en@quot/LC_MESSAGES/foreign.mo
/usr/lib64/R/library/foreign/po/fr/LC_MESSAGES/R-foreign.mo
/usr/lib64/R/library/foreign/po/fr/LC_MESSAGES/foreign.mo
/usr/lib64/R/library/foreign/po/pl/LC_MESSAGES/R-foreign.mo
/usr/lib64/R/library/foreign/po/pl/LC_MESSAGES/foreign.mo
/usr/lib64/R/library/grDevices/DESCRIPTION
/usr/lib64/R/library/grDevices/INDEX
/usr/lib64/R/library/grDevices/Meta/Rd.rds
/usr/lib64/R/library/grDevices/Meta/demo.rds
/usr/lib64/R/library/grDevices/Meta/features.rds
/usr/lib64/R/library/grDevices/Meta/hsearch.rds
/usr/lib64/R/library/grDevices/Meta/links.rds
/usr/lib64/R/library/grDevices/Meta/nsInfo.rds
/usr/lib64/R/library/grDevices/Meta/package.rds
/usr/lib64/R/library/grDevices/NAMESPACE
/usr/lib64/R/library/grDevices/R/grDevices
/usr/lib64/R/library/grDevices/R/grDevices.rdb
/usr/lib64/R/library/grDevices/R/grDevices.rdx
/usr/lib64/R/library/grDevices/afm/ArialMT-Bold.afm.gz
/usr/lib64/R/library/grDevices/afm/ArialMT-BoldItalic.afm.gz
/usr/lib64/R/library/grDevices/afm/ArialMT-Italic.afm.gz
/usr/lib64/R/library/grDevices/afm/ArialMT.afm.gz
/usr/lib64/R/library/grDevices/afm/CM_boldx_10.afm.gz
/usr/lib64/R/library/grDevices/afm/CM_boldx_italic_10.afm.gz
/usr/lib64/R/library/grDevices/afm/CM_italic_10.afm.gz
/usr/lib64/R/library/grDevices/afm/CM_regular_10.afm.gz
/usr/lib64/R/library/grDevices/afm/CM_symbol_10.afm.gz
/usr/lib64/R/library/grDevices/afm/Courier-Bold.afm.gz
/usr/lib64/R/library/grDevices/afm/Courier-BoldOblique.afm.gz
/usr/lib64/R/library/grDevices/afm/Courier-Oblique.afm.gz
/usr/lib64/R/library/grDevices/afm/Courier.afm.gz
/usr/lib64/R/library/grDevices/afm/Helvetica-Bold.afm.gz
/usr/lib64/R/library/grDevices/afm/Helvetica-BoldOblique.afm.gz
/usr/lib64/R/library/grDevices/afm/Helvetica-Oblique.afm.gz
/usr/lib64/R/library/grDevices/afm/Helvetica.afm.gz
/usr/lib64/R/library/grDevices/afm/MustRead.html
/usr/lib64/R/library/grDevices/afm/README
/usr/lib64/R/library/grDevices/afm/Symbol.afm.gz
/usr/lib64/R/library/grDevices/afm/Times-Bold.afm.gz
/usr/lib64/R/library/grDevices/afm/Times-BoldItalic.afm.gz
/usr/lib64/R/library/grDevices/afm/Times-Italic.afm.gz
/usr/lib64/R/library/grDevices/afm/Times-Roman.afm.gz
/usr/lib64/R/library/grDevices/afm/ZapfDingbats.afm.gz
/usr/lib64/R/library/grDevices/afm/a010013l.afm.gz
/usr/lib64/R/library/grDevices/afm/a010015l.afm.gz
/usr/lib64/R/library/grDevices/afm/a010033l.afm.gz
/usr/lib64/R/library/grDevices/afm/a010035l.afm.gz
/usr/lib64/R/library/grDevices/afm/agd_____.afm.gz
/usr/lib64/R/library/grDevices/afm/agdo____.afm.gz
/usr/lib64/R/library/grDevices/afm/agw_____.afm.gz
/usr/lib64/R/library/grDevices/afm/agwo____.afm.gz
/usr/lib64/R/library/grDevices/afm/b018012l.afm.gz
/usr/lib64/R/library/grDevices/afm/b018015l.afm.gz
/usr/lib64/R/library/grDevices/afm/b018032l.afm.gz
/usr/lib64/R/library/grDevices/afm/b018035l.afm.gz
/usr/lib64/R/library/grDevices/afm/bkd_____.afm.gz
/usr/lib64/R/library/grDevices/afm/bkdi____.afm.gz
/usr/lib64/R/library/grDevices/afm/bkl_____.afm.gz
/usr/lib64/R/library/grDevices/afm/bkli____.afm.gz
/usr/lib64/R/library/grDevices/afm/c059013l.afm.gz
/usr/lib64/R/library/grDevices/afm/c059016l.afm.gz
/usr/lib64/R/library/grDevices/afm/c059033l.afm.gz
/usr/lib64/R/library/grDevices/afm/c059036l.afm.gz
/usr/lib64/R/library/grDevices/afm/cmbxti10.afm.gz
/usr/lib64/R/library/grDevices/afm/cmti10.afm.gz
/usr/lib64/R/library/grDevices/afm/cob_____.afm.gz
/usr/lib64/R/library/grDevices/afm/cobo____.afm.gz
/usr/lib64/R/library/grDevices/afm/com_____.afm.gz
/usr/lib64/R/library/grDevices/afm/coo_____.afm.gz
/usr/lib64/R/library/grDevices/afm/hv______.afm.gz
/usr/lib64/R/library/grDevices/afm/hvb_____.afm.gz
/usr/lib64/R/library/grDevices/afm/hvbo____.afm.gz
/usr/lib64/R/library/grDevices/afm/hvn_____.afm.gz
/usr/lib64/R/library/grDevices/afm/hvnb____.afm.gz
/usr/lib64/R/library/grDevices/afm/hvnbo___.afm.gz
/usr/lib64/R/library/grDevices/afm/hvno____.afm.gz
/usr/lib64/R/library/grDevices/afm/hvo_____.afm.gz
/usr/lib64/R/library/grDevices/afm/n019003l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019004l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019023l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019024l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019043l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019044l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019063l.afm.gz
/usr/lib64/R/library/grDevices/afm/n019064l.afm.gz
/usr/lib64/R/library/grDevices/afm/n021003l.afm.gz
/usr/lib64/R/library/grDevices/afm/n021004l.afm.gz
/usr/lib64/R/library/grDevices/afm/n021023l.afm.gz
/usr/lib64/R/library/grDevices/afm/n021024l.afm.gz
/usr/lib64/R/library/grDevices/afm/n022003l.afm.gz
/usr/lib64/R/library/grDevices/afm/n022004l.afm.gz
/usr/lib64/R/library/grDevices/afm/n022023l.afm.gz
/usr/lib64/R/library/grDevices/afm/n022024l.afm.gz
/usr/lib64/R/library/grDevices/afm/ncb_____.afm.gz
/usr/lib64/R/library/grDevices/afm/ncbi____.afm.gz
/usr/lib64/R/library/grDevices/afm/nci_____.afm.gz
/usr/lib64/R/library/grDevices/afm/ncr_____.afm.gz
/usr/lib64/R/library/grDevices/afm/p052003l.afm.gz
/usr/lib64/R/library/grDevices/afm/p052004l.afm.gz
/usr/lib64/R/library/grDevices/afm/p052023l.afm.gz
/usr/lib64/R/library/grDevices/afm/p052024l.afm.gz
/usr/lib64/R/library/grDevices/afm/pob_____.afm.gz
/usr/lib64/R/library/grDevices/afm/pobi____.afm.gz
/usr/lib64/R/library/grDevices/afm/poi_____.afm.gz
/usr/lib64/R/library/grDevices/afm/por_____.afm.gz
/usr/lib64/R/library/grDevices/afm/s050000l.afm.gz
/usr/lib64/R/library/grDevices/afm/sy______.afm.gz
/usr/lib64/R/library/grDevices/afm/tib_____.afm.gz
/usr/lib64/R/library/grDevices/afm/tibi____.afm.gz
/usr/lib64/R/library/grDevices/afm/tii_____.afm.gz
/usr/lib64/R/library/grDevices/afm/tir_____.afm.gz
/usr/lib64/R/library/grDevices/demo/colors.R
/usr/lib64/R/library/grDevices/demo/hclColors.R
/usr/lib64/R/library/grDevices/enc/AdobeStd.enc
/usr/lib64/R/library/grDevices/enc/AdobeSym.enc
/usr/lib64/R/library/grDevices/enc/CP1250.enc
/usr/lib64/R/library/grDevices/enc/CP1251.enc
/usr/lib64/R/library/grDevices/enc/CP1253.enc
/usr/lib64/R/library/grDevices/enc/CP1257.enc
/usr/lib64/R/library/grDevices/enc/Cyrillic.enc
/usr/lib64/R/library/grDevices/enc/Greek.enc
/usr/lib64/R/library/grDevices/enc/ISOLatin1.enc
/usr/lib64/R/library/grDevices/enc/ISOLatin2.enc
/usr/lib64/R/library/grDevices/enc/ISOLatin7.enc
/usr/lib64/R/library/grDevices/enc/ISOLatin9.enc
/usr/lib64/R/library/grDevices/enc/KOI8-R.enc
/usr/lib64/R/library/grDevices/enc/KOI8-U.enc
/usr/lib64/R/library/grDevices/enc/MacRoman.enc
/usr/lib64/R/library/grDevices/enc/PDFDoc.enc
/usr/lib64/R/library/grDevices/enc/TeXtext.enc
/usr/lib64/R/library/grDevices/enc/WinAnsi.enc
/usr/lib64/R/library/grDevices/help/AnIndex
/usr/lib64/R/library/grDevices/help/aliases.rds
/usr/lib64/R/library/grDevices/help/grDevices.rdb
/usr/lib64/R/library/grDevices/help/grDevices.rdx
/usr/lib64/R/library/grDevices/help/paths.rds
/usr/lib64/R/library/grDevices/html/00Index.html
/usr/lib64/R/library/grDevices/html/R.css
/usr/lib64/R/library/grDevices/icc/srgb
/usr/lib64/R/library/grDevices/icc/srgb.flate
/usr/lib64/R/library/graphics/DESCRIPTION
/usr/lib64/R/library/graphics/INDEX
/usr/lib64/R/library/graphics/Meta/Rd.rds
/usr/lib64/R/library/graphics/Meta/demo.rds
/usr/lib64/R/library/graphics/Meta/features.rds
/usr/lib64/R/library/graphics/Meta/hsearch.rds
/usr/lib64/R/library/graphics/Meta/links.rds
/usr/lib64/R/library/graphics/Meta/nsInfo.rds
/usr/lib64/R/library/graphics/Meta/package.rds
/usr/lib64/R/library/graphics/NAMESPACE
/usr/lib64/R/library/graphics/R/graphics
/usr/lib64/R/library/graphics/R/graphics.rdb
/usr/lib64/R/library/graphics/R/graphics.rdx
/usr/lib64/R/library/graphics/demo/Hershey.R
/usr/lib64/R/library/graphics/demo/Japanese.R
/usr/lib64/R/library/graphics/demo/graphics.R
/usr/lib64/R/library/graphics/demo/image.R
/usr/lib64/R/library/graphics/demo/persp.R
/usr/lib64/R/library/graphics/demo/plotmath.R
/usr/lib64/R/library/graphics/help/AnIndex
/usr/lib64/R/library/graphics/help/aliases.rds
/usr/lib64/R/library/graphics/help/figures/mai.pdf
/usr/lib64/R/library/graphics/help/figures/mai.png
/usr/lib64/R/library/graphics/help/figures/oma.pdf
/usr/lib64/R/library/graphics/help/figures/oma.png
/usr/lib64/R/library/graphics/help/figures/pch.pdf
/usr/lib64/R/library/graphics/help/figures/pch.png
/usr/lib64/R/library/graphics/help/figures/pch.svg
/usr/lib64/R/library/graphics/help/graphics.rdb
/usr/lib64/R/library/graphics/help/graphics.rdx
/usr/lib64/R/library/graphics/help/paths.rds
/usr/lib64/R/library/graphics/html/00Index.html
/usr/lib64/R/library/graphics/html/R.css
/usr/lib64/R/library/grid/DESCRIPTION
/usr/lib64/R/library/grid/INDEX
/usr/lib64/R/library/grid/Meta/Rd.rds
/usr/lib64/R/library/grid/Meta/features.rds
/usr/lib64/R/library/grid/Meta/hsearch.rds
/usr/lib64/R/library/grid/Meta/links.rds
/usr/lib64/R/library/grid/Meta/nsInfo.rds
/usr/lib64/R/library/grid/Meta/package.rds
/usr/lib64/R/library/grid/NAMESPACE
/usr/lib64/R/library/grid/R/grid
/usr/lib64/R/library/grid/R/grid.rdb
/usr/lib64/R/library/grid/R/grid.rdx
/usr/lib64/R/library/grid/doc/DivByZero.txt
/usr/lib64/R/library/grid/doc/changes.txt
/usr/lib64/R/library/grid/doc/displaylist.pdf
/usr/lib64/R/library/grid/doc/frame.pdf
/usr/lib64/R/library/grid/doc/grid.pdf
/usr/lib64/R/library/grid/doc/grobs.pdf
/usr/lib64/R/library/grid/doc/interactive.pdf
/usr/lib64/R/library/grid/doc/locndimn.pdf
/usr/lib64/R/library/grid/doc/moveline.pdf
/usr/lib64/R/library/grid/doc/nonfinite.pdf
/usr/lib64/R/library/grid/doc/plotexample.pdf
/usr/lib64/R/library/grid/doc/rotated.pdf
/usr/lib64/R/library/grid/doc/saveload.pdf
/usr/lib64/R/library/grid/doc/sharing.pdf
/usr/lib64/R/library/grid/doc/viewports.pdf
/usr/lib64/R/library/grid/help/AnIndex
/usr/lib64/R/library/grid/help/aliases.rds
/usr/lib64/R/library/grid/help/grid.rdb
/usr/lib64/R/library/grid/help/grid.rdx
/usr/lib64/R/library/grid/help/paths.rds
/usr/lib64/R/library/grid/html/00Index.html
/usr/lib64/R/library/grid/html/R.css
/usr/lib64/R/library/lattice/CITATION
/usr/lib64/R/library/lattice/DESCRIPTION
/usr/lib64/R/library/lattice/INDEX
/usr/lib64/R/library/lattice/Meta/Rd.rds
/usr/lib64/R/library/lattice/Meta/data.rds
/usr/lib64/R/library/lattice/Meta/demo.rds
/usr/lib64/R/library/lattice/Meta/features.rds
/usr/lib64/R/library/lattice/Meta/hsearch.rds
/usr/lib64/R/library/lattice/Meta/links.rds
/usr/lib64/R/library/lattice/Meta/nsInfo.rds
/usr/lib64/R/library/lattice/Meta/package.rds
/usr/lib64/R/library/lattice/NAMESPACE
/usr/lib64/R/library/lattice/NEWS
/usr/lib64/R/library/lattice/R/lattice
/usr/lib64/R/library/lattice/R/lattice.rdb
/usr/lib64/R/library/lattice/R/lattice.rdx
/usr/lib64/R/library/lattice/data/Rdata.rdb
/usr/lib64/R/library/lattice/data/Rdata.rds
/usr/lib64/R/library/lattice/data/Rdata.rdx
/usr/lib64/R/library/lattice/demo/intervals.R
/usr/lib64/R/library/lattice/demo/labels.R
/usr/lib64/R/library/lattice/demo/lattice.R
/usr/lib64/R/library/lattice/demo/panel.R
/usr/lib64/R/library/lattice/help/AnIndex
/usr/lib64/R/library/lattice/help/aliases.rds
/usr/lib64/R/library/lattice/help/lattice.rdb
/usr/lib64/R/library/lattice/help/lattice.rdx
/usr/lib64/R/library/lattice/help/paths.rds
/usr/lib64/R/library/lattice/html/00Index.html
/usr/lib64/R/library/lattice/html/R.css
/usr/lib64/R/library/lattice/po/de/LC_MESSAGES/R-lattice.mo
/usr/lib64/R/library/lattice/po/en@quot/LC_MESSAGES/R-lattice.mo
/usr/lib64/R/library/lattice/po/fr/LC_MESSAGES/R-lattice.mo
/usr/lib64/R/library/lattice/po/ko/LC_MESSAGES/R-lattice.mo
/usr/lib64/R/library/lattice/po/pl/LC_MESSAGES/R-lattice.mo
/usr/lib64/R/library/methods/DESCRIPTION
/usr/lib64/R/library/methods/INDEX
/usr/lib64/R/library/methods/Meta/Rd.rds
/usr/lib64/R/library/methods/Meta/features.rds
/usr/lib64/R/library/methods/Meta/hsearch.rds
/usr/lib64/R/library/methods/Meta/links.rds
/usr/lib64/R/library/methods/Meta/nsInfo.rds
/usr/lib64/R/library/methods/Meta/package.rds
/usr/lib64/R/library/methods/NAMESPACE
/usr/lib64/R/library/methods/R/methods
/usr/lib64/R/library/methods/R/methods.rdb
/usr/lib64/R/library/methods/R/methods.rdx
/usr/lib64/R/library/methods/help/AnIndex
/usr/lib64/R/library/methods/help/aliases.rds
/usr/lib64/R/library/methods/help/methods.rdb
/usr/lib64/R/library/methods/help/methods.rdx
/usr/lib64/R/library/methods/help/paths.rds
/usr/lib64/R/library/methods/html/00Index.html
/usr/lib64/R/library/methods/html/R.css
/usr/lib64/R/library/mgcv/CITATION
/usr/lib64/R/library/mgcv/DESCRIPTION
/usr/lib64/R/library/mgcv/INDEX
/usr/lib64/R/library/mgcv/Meta/Rd.rds
/usr/lib64/R/library/mgcv/Meta/data.rds
/usr/lib64/R/library/mgcv/Meta/features.rds
/usr/lib64/R/library/mgcv/Meta/hsearch.rds
/usr/lib64/R/library/mgcv/Meta/links.rds
/usr/lib64/R/library/mgcv/Meta/nsInfo.rds
/usr/lib64/R/library/mgcv/Meta/package.rds
/usr/lib64/R/library/mgcv/NAMESPACE
/usr/lib64/R/library/mgcv/R/mgcv
/usr/lib64/R/library/mgcv/R/mgcv.rdb
/usr/lib64/R/library/mgcv/R/mgcv.rdx
/usr/lib64/R/library/mgcv/data/columb.polys.rda
/usr/lib64/R/library/mgcv/data/columb.rda
/usr/lib64/R/library/mgcv/help/AnIndex
/usr/lib64/R/library/mgcv/help/aliases.rds
/usr/lib64/R/library/mgcv/help/mgcv.rdb
/usr/lib64/R/library/mgcv/help/mgcv.rdx
/usr/lib64/R/library/mgcv/help/paths.rds
/usr/lib64/R/library/mgcv/html/00Index.html
/usr/lib64/R/library/mgcv/html/R.css
/usr/lib64/R/library/mgcv/po/de/LC_MESSAGES/R-mgcv.mo
/usr/lib64/R/library/mgcv/po/de/LC_MESSAGES/mgcv.mo
/usr/lib64/R/library/mgcv/po/en@quot/LC_MESSAGES/R-mgcv.mo
/usr/lib64/R/library/mgcv/po/en@quot/LC_MESSAGES/mgcv.mo
/usr/lib64/R/library/mgcv/po/fr/LC_MESSAGES/R-mgcv.mo
/usr/lib64/R/library/mgcv/po/fr/LC_MESSAGES/mgcv.mo
/usr/lib64/R/library/mgcv/po/ko/LC_MESSAGES/R-mgcv.mo
/usr/lib64/R/library/mgcv/po/ko/LC_MESSAGES/mgcv.mo
/usr/lib64/R/library/mgcv/po/pl/LC_MESSAGES/R-mgcv.mo
/usr/lib64/R/library/mgcv/po/pl/LC_MESSAGES/mgcv.mo
/usr/lib64/R/library/nlme/CITATION
/usr/lib64/R/library/nlme/DESCRIPTION
/usr/lib64/R/library/nlme/INDEX
/usr/lib64/R/library/nlme/LICENCE
/usr/lib64/R/library/nlme/Meta/Rd.rds
/usr/lib64/R/library/nlme/Meta/data.rds
/usr/lib64/R/library/nlme/Meta/features.rds
/usr/lib64/R/library/nlme/Meta/hsearch.rds
/usr/lib64/R/library/nlme/Meta/links.rds
/usr/lib64/R/library/nlme/Meta/nsInfo.rds
/usr/lib64/R/library/nlme/Meta/package.rds
/usr/lib64/R/library/nlme/NAMESPACE
/usr/lib64/R/library/nlme/R/nlme
/usr/lib64/R/library/nlme/R/nlme.rdb
/usr/lib64/R/library/nlme/R/nlme.rdx
/usr/lib64/R/library/nlme/data/Rdata.rdb
/usr/lib64/R/library/nlme/data/Rdata.rds
/usr/lib64/R/library/nlme/data/Rdata.rdx
/usr/lib64/R/library/nlme/help/AnIndex
/usr/lib64/R/library/nlme/help/aliases.rds
/usr/lib64/R/library/nlme/help/nlme.rdb
/usr/lib64/R/library/nlme/help/nlme.rdx
/usr/lib64/R/library/nlme/help/paths.rds
/usr/lib64/R/library/nlme/html/00Index.html
/usr/lib64/R/library/nlme/html/R.css
/usr/lib64/R/library/nlme/mlbook/README
/usr/lib64/R/library/nlme/mlbook/ch04.R
/usr/lib64/R/library/nlme/mlbook/ch05.R
/usr/lib64/R/library/nlme/po/de/LC_MESSAGES/R-nlme.mo
/usr/lib64/R/library/nlme/po/de/LC_MESSAGES/nlme.mo
/usr/lib64/R/library/nlme/po/en@quot/LC_MESSAGES/R-nlme.mo
/usr/lib64/R/library/nlme/po/en@quot/LC_MESSAGES/nlme.mo
/usr/lib64/R/library/nlme/po/fr/LC_MESSAGES/R-nlme.mo
/usr/lib64/R/library/nlme/po/fr/LC_MESSAGES/nlme.mo
/usr/lib64/R/library/nlme/po/ko/LC_MESSAGES/R-nlme.mo
/usr/lib64/R/library/nlme/po/ko/LC_MESSAGES/nlme.mo
/usr/lib64/R/library/nlme/po/pl/LC_MESSAGES/R-nlme.mo
/usr/lib64/R/library/nlme/po/pl/LC_MESSAGES/nlme.mo
/usr/lib64/R/library/nlme/scripts/ch01.R
/usr/lib64/R/library/nlme/scripts/ch02.R
/usr/lib64/R/library/nlme/scripts/ch03.R
/usr/lib64/R/library/nlme/scripts/ch04.R
/usr/lib64/R/library/nlme/scripts/ch05.R
/usr/lib64/R/library/nlme/scripts/ch06.R
/usr/lib64/R/library/nlme/scripts/ch08.R
/usr/lib64/R/library/nlme/scripts/runme.R
/usr/lib64/R/library/nlme/scripts/sims.rda
/usr/lib64/R/library/nnet/CITATION
/usr/lib64/R/library/nnet/DESCRIPTION
/usr/lib64/R/library/nnet/INDEX
/usr/lib64/R/library/nnet/Meta/Rd.rds
/usr/lib64/R/library/nnet/Meta/features.rds
/usr/lib64/R/library/nnet/Meta/hsearch.rds
/usr/lib64/R/library/nnet/Meta/links.rds
/usr/lib64/R/library/nnet/Meta/nsInfo.rds
/usr/lib64/R/library/nnet/Meta/package.rds
/usr/lib64/R/library/nnet/NAMESPACE
/usr/lib64/R/library/nnet/NEWS
/usr/lib64/R/library/nnet/R/nnet
/usr/lib64/R/library/nnet/R/nnet.rdb
/usr/lib64/R/library/nnet/R/nnet.rdx
/usr/lib64/R/library/nnet/help/AnIndex
/usr/lib64/R/library/nnet/help/aliases.rds
/usr/lib64/R/library/nnet/help/nnet.rdb
/usr/lib64/R/library/nnet/help/nnet.rdx
/usr/lib64/R/library/nnet/help/paths.rds
/usr/lib64/R/library/nnet/html/00Index.html
/usr/lib64/R/library/nnet/html/R.css
/usr/lib64/R/library/nnet/po/de/LC_MESSAGES/R-nnet.mo
/usr/lib64/R/library/nnet/po/en@quot/LC_MESSAGES/R-nnet.mo
/usr/lib64/R/library/nnet/po/fr/LC_MESSAGES/R-nnet.mo
/usr/lib64/R/library/nnet/po/ko/LC_MESSAGES/R-nnet.mo
/usr/lib64/R/library/nnet/po/pl/LC_MESSAGES/R-nnet.mo
/usr/lib64/R/library/parallel/DESCRIPTION
/usr/lib64/R/library/parallel/INDEX
/usr/lib64/R/library/parallel/Meta/Rd.rds
/usr/lib64/R/library/parallel/Meta/features.rds
/usr/lib64/R/library/parallel/Meta/hsearch.rds
/usr/lib64/R/library/parallel/Meta/links.rds
/usr/lib64/R/library/parallel/Meta/nsInfo.rds
/usr/lib64/R/library/parallel/Meta/package.rds
/usr/lib64/R/library/parallel/NAMESPACE
/usr/lib64/R/library/parallel/R/parallel
/usr/lib64/R/library/parallel/R/parallel.rdb
/usr/lib64/R/library/parallel/R/parallel.rdx
/usr/lib64/R/library/parallel/doc/parallel.pdf
/usr/lib64/R/library/parallel/help/AnIndex
/usr/lib64/R/library/parallel/help/aliases.rds
/usr/lib64/R/library/parallel/help/parallel.rdb
/usr/lib64/R/library/parallel/help/parallel.rdx
/usr/lib64/R/library/parallel/help/paths.rds
/usr/lib64/R/library/parallel/html/00Index.html
/usr/lib64/R/library/parallel/html/R.css
/usr/lib64/R/library/rpart/DESCRIPTION
/usr/lib64/R/library/rpart/INDEX
/usr/lib64/R/library/rpart/Meta/Rd.rds
/usr/lib64/R/library/rpart/Meta/data.rds
/usr/lib64/R/library/rpart/Meta/features.rds
/usr/lib64/R/library/rpart/Meta/hsearch.rds
/usr/lib64/R/library/rpart/Meta/links.rds
/usr/lib64/R/library/rpart/Meta/nsInfo.rds
/usr/lib64/R/library/rpart/Meta/package.rds
/usr/lib64/R/library/rpart/Meta/vignette.rds
/usr/lib64/R/library/rpart/NAMESPACE
/usr/lib64/R/library/rpart/NEWS.Rd
/usr/lib64/R/library/rpart/R/rpart
/usr/lib64/R/library/rpart/R/rpart.rdb
/usr/lib64/R/library/rpart/R/rpart.rdx
/usr/lib64/R/library/rpart/data/Rdata.rdb
/usr/lib64/R/library/rpart/data/Rdata.rds
/usr/lib64/R/library/rpart/data/Rdata.rdx
/usr/lib64/R/library/rpart/doc/index.html
/usr/lib64/R/library/rpart/doc/longintro.R
/usr/lib64/R/library/rpart/doc/longintro.Rnw
/usr/lib64/R/library/rpart/doc/longintro.pdf
/usr/lib64/R/library/rpart/doc/usercode.R
/usr/lib64/R/library/rpart/doc/usercode.Rnw
/usr/lib64/R/library/rpart/doc/usercode.pdf
/usr/lib64/R/library/rpart/help/AnIndex
/usr/lib64/R/library/rpart/help/aliases.rds
/usr/lib64/R/library/rpart/help/paths.rds
/usr/lib64/R/library/rpart/help/rpart.rdb
/usr/lib64/R/library/rpart/help/rpart.rdx
/usr/lib64/R/library/rpart/html/00Index.html
/usr/lib64/R/library/rpart/html/R.css
/usr/lib64/R/library/rpart/po/de/LC_MESSAGES/R-rpart.mo
/usr/lib64/R/library/rpart/po/de/LC_MESSAGES/rpart.mo
/usr/lib64/R/library/rpart/po/en@quot/LC_MESSAGES/R-rpart.mo
/usr/lib64/R/library/rpart/po/en@quot/LC_MESSAGES/rpart.mo
/usr/lib64/R/library/rpart/po/fr/LC_MESSAGES/R-rpart.mo
/usr/lib64/R/library/rpart/po/fr/LC_MESSAGES/rpart.mo
/usr/lib64/R/library/rpart/po/ko/LC_MESSAGES/R-rpart.mo
/usr/lib64/R/library/rpart/po/ko/LC_MESSAGES/rpart.mo
/usr/lib64/R/library/rpart/po/pl/LC_MESSAGES/R-rpart.mo
/usr/lib64/R/library/rpart/po/pl/LC_MESSAGES/rpart.mo
/usr/lib64/R/library/rpart/po/ru/LC_MESSAGES/R-rpart.mo
/usr/lib64/R/library/rpart/po/ru/LC_MESSAGES/rpart.mo
/usr/lib64/R/library/spatial/CITATION
/usr/lib64/R/library/spatial/DESCRIPTION
/usr/lib64/R/library/spatial/INDEX
/usr/lib64/R/library/spatial/Meta/Rd.rds
/usr/lib64/R/library/spatial/Meta/features.rds
/usr/lib64/R/library/spatial/Meta/hsearch.rds
/usr/lib64/R/library/spatial/Meta/links.rds
/usr/lib64/R/library/spatial/Meta/nsInfo.rds
/usr/lib64/R/library/spatial/Meta/package.rds
/usr/lib64/R/library/spatial/NAMESPACE
/usr/lib64/R/library/spatial/NEWS
/usr/lib64/R/library/spatial/PP.files
/usr/lib64/R/library/spatial/R/spatial
/usr/lib64/R/library/spatial/R/spatial.rdb
/usr/lib64/R/library/spatial/R/spatial.rdx
/usr/lib64/R/library/spatial/help/AnIndex
/usr/lib64/R/library/spatial/help/aliases.rds
/usr/lib64/R/library/spatial/help/paths.rds
/usr/lib64/R/library/spatial/help/spatial.rdb
/usr/lib64/R/library/spatial/help/spatial.rdx
/usr/lib64/R/library/spatial/html/00Index.html
/usr/lib64/R/library/spatial/html/R.css
/usr/lib64/R/library/spatial/po/de/LC_MESSAGES/R-spatial.mo
/usr/lib64/R/library/spatial/po/en@quot/LC_MESSAGES/R-spatial.mo
/usr/lib64/R/library/spatial/po/fr/LC_MESSAGES/R-spatial.mo
/usr/lib64/R/library/spatial/po/ko/LC_MESSAGES/R-spatial.mo
/usr/lib64/R/library/spatial/po/pl/LC_MESSAGES/R-spatial.mo
/usr/lib64/R/library/spatial/ppdata/agter.dat
/usr/lib64/R/library/spatial/ppdata/caveolae.dat
/usr/lib64/R/library/spatial/ppdata/cells.dat
/usr/lib64/R/library/spatial/ppdata/davis.dat
/usr/lib64/R/library/spatial/ppdata/drumlin.dat
/usr/lib64/R/library/spatial/ppdata/eagles.dat
/usr/lib64/R/library/spatial/ppdata/fig1b.dat
/usr/lib64/R/library/spatial/ppdata/fig1c.dat
/usr/lib64/R/library/spatial/ppdata/fig2a.dat
/usr/lib64/R/library/spatial/ppdata/fig2b.dat
/usr/lib64/R/library/spatial/ppdata/fig3a.dat
/usr/lib64/R/library/spatial/ppdata/fig3b.dat
/usr/lib64/R/library/spatial/ppdata/fig3c.dat
/usr/lib64/R/library/spatial/ppdata/grocery.dat
/usr/lib64/R/library/spatial/ppdata/hccells.dat
/usr/lib64/R/library/spatial/ppdata/nztrees.dat
/usr/lib64/R/library/spatial/ppdata/pairfn.dat
/usr/lib64/R/library/spatial/ppdata/pereg.dat
/usr/lib64/R/library/spatial/ppdata/pines.dat
/usr/lib64/R/library/spatial/ppdata/redwood.dat
/usr/lib64/R/library/spatial/ppdata/schools.dat
/usr/lib64/R/library/spatial/ppdata/stowns1.dat
/usr/lib64/R/library/spatial/ppdata/tokyo.dat
/usr/lib64/R/library/spatial/ppdata/towns.dat
/usr/lib64/R/library/splines/DESCRIPTION
/usr/lib64/R/library/splines/INDEX
/usr/lib64/R/library/splines/Meta/Rd.rds
/usr/lib64/R/library/splines/Meta/features.rds
/usr/lib64/R/library/splines/Meta/hsearch.rds
/usr/lib64/R/library/splines/Meta/links.rds
/usr/lib64/R/library/splines/Meta/nsInfo.rds
/usr/lib64/R/library/splines/Meta/package.rds
/usr/lib64/R/library/splines/NAMESPACE
/usr/lib64/R/library/splines/R/splines
/usr/lib64/R/library/splines/R/splines.rdb
/usr/lib64/R/library/splines/R/splines.rdx
/usr/lib64/R/library/splines/help/AnIndex
/usr/lib64/R/library/splines/help/aliases.rds
/usr/lib64/R/library/splines/help/paths.rds
/usr/lib64/R/library/splines/help/splines.rdb
/usr/lib64/R/library/splines/help/splines.rdx
/usr/lib64/R/library/splines/html/00Index.html
/usr/lib64/R/library/splines/html/R.css
/usr/lib64/R/library/stats/COPYRIGHTS.modreg
/usr/lib64/R/library/stats/DESCRIPTION
/usr/lib64/R/library/stats/INDEX
/usr/lib64/R/library/stats/Meta/Rd.rds
/usr/lib64/R/library/stats/Meta/demo.rds
/usr/lib64/R/library/stats/Meta/features.rds
/usr/lib64/R/library/stats/Meta/hsearch.rds
/usr/lib64/R/library/stats/Meta/links.rds
/usr/lib64/R/library/stats/Meta/nsInfo.rds
/usr/lib64/R/library/stats/Meta/package.rds
/usr/lib64/R/library/stats/NAMESPACE
/usr/lib64/R/library/stats/R/stats
/usr/lib64/R/library/stats/R/stats.rdb
/usr/lib64/R/library/stats/R/stats.rdx
/usr/lib64/R/library/stats/SOURCES.ts
/usr/lib64/R/library/stats/demo/glm.vr.R
/usr/lib64/R/library/stats/demo/lm.glm.R
/usr/lib64/R/library/stats/demo/nlm.R
/usr/lib64/R/library/stats/demo/smooth.R
/usr/lib64/R/library/stats/help/AnIndex
/usr/lib64/R/library/stats/help/aliases.rds
/usr/lib64/R/library/stats/help/paths.rds
/usr/lib64/R/library/stats/help/stats.rdb
/usr/lib64/R/library/stats/help/stats.rdx
/usr/lib64/R/library/stats/html/00Index.html
/usr/lib64/R/library/stats/html/R.css
/usr/lib64/R/library/stats4/DESCRIPTION
/usr/lib64/R/library/stats4/INDEX
/usr/lib64/R/library/stats4/Meta/Rd.rds
/usr/lib64/R/library/stats4/Meta/features.rds
/usr/lib64/R/library/stats4/Meta/hsearch.rds
/usr/lib64/R/library/stats4/Meta/links.rds
/usr/lib64/R/library/stats4/Meta/nsInfo.rds
/usr/lib64/R/library/stats4/Meta/package.rds
/usr/lib64/R/library/stats4/NAMESPACE
/usr/lib64/R/library/stats4/R/stats4
/usr/lib64/R/library/stats4/R/stats4.rdb
/usr/lib64/R/library/stats4/R/stats4.rdx
/usr/lib64/R/library/stats4/help/AnIndex
/usr/lib64/R/library/stats4/help/aliases.rds
/usr/lib64/R/library/stats4/help/paths.rds
/usr/lib64/R/library/stats4/help/stats4.rdb
/usr/lib64/R/library/stats4/help/stats4.rdx
/usr/lib64/R/library/stats4/html/00Index.html
/usr/lib64/R/library/stats4/html/R.css
/usr/lib64/R/library/survival/CITATION
/usr/lib64/R/library/survival/COPYRIGHTS
/usr/lib64/R/library/survival/DESCRIPTION
/usr/lib64/R/library/survival/INDEX
/usr/lib64/R/library/survival/Meta/Rd.rds
/usr/lib64/R/library/survival/Meta/data.rds
/usr/lib64/R/library/survival/Meta/features.rds
/usr/lib64/R/library/survival/Meta/hsearch.rds
/usr/lib64/R/library/survival/Meta/links.rds
/usr/lib64/R/library/survival/Meta/nsInfo.rds
/usr/lib64/R/library/survival/Meta/package.rds
/usr/lib64/R/library/survival/Meta/vignette.rds
/usr/lib64/R/library/survival/NAMESPACE
/usr/lib64/R/library/survival/NEWS.Rd
/usr/lib64/R/library/survival/R/survival
/usr/lib64/R/library/survival/R/survival.rdb
/usr/lib64/R/library/survival/R/survival.rdx
/usr/lib64/R/library/survival/data/Rdata.rdb
/usr/lib64/R/library/survival/data/Rdata.rds
/usr/lib64/R/library/survival/data/Rdata.rdx
/usr/lib64/R/library/survival/doc/adjcurve.R
/usr/lib64/R/library/survival/doc/adjcurve.Rnw
/usr/lib64/R/library/survival/doc/adjcurve.pdf
/usr/lib64/R/library/survival/doc/approximate.R
/usr/lib64/R/library/survival/doc/approximate.Rnw
/usr/lib64/R/library/survival/doc/approximate.pdf
/usr/lib64/R/library/survival/doc/compete.R
/usr/lib64/R/library/survival/doc/compete.Rnw
/usr/lib64/R/library/survival/doc/compete.pdf
/usr/lib64/R/library/survival/doc/concordance.R
/usr/lib64/R/library/survival/doc/concordance.Rnw
/usr/lib64/R/library/survival/doc/concordance.pdf
/usr/lib64/R/library/survival/doc/index.html
/usr/lib64/R/library/survival/doc/multi.Rnw
/usr/lib64/R/library/survival/doc/multi.pdf
/usr/lib64/R/library/survival/doc/other.Rnw
/usr/lib64/R/library/survival/doc/other.pdf
/usr/lib64/R/library/survival/doc/population.R
/usr/lib64/R/library/survival/doc/population.Rnw
/usr/lib64/R/library/survival/doc/population.pdf
/usr/lib64/R/library/survival/doc/splines.R
/usr/lib64/R/library/survival/doc/splines.Rnw
/usr/lib64/R/library/survival/doc/splines.pdf
/usr/lib64/R/library/survival/doc/tiedtimes.R
/usr/lib64/R/library/survival/doc/tiedtimes.Rnw
/usr/lib64/R/library/survival/doc/tiedtimes.pdf
/usr/lib64/R/library/survival/doc/timedep.R
/usr/lib64/R/library/survival/doc/timedep.Rnw
/usr/lib64/R/library/survival/doc/timedep.pdf
/usr/lib64/R/library/survival/doc/validate.R
/usr/lib64/R/library/survival/doc/validate.Rnw
/usr/lib64/R/library/survival/doc/validate.pdf
/usr/lib64/R/library/survival/help/AnIndex
/usr/lib64/R/library/survival/help/aliases.rds
/usr/lib64/R/library/survival/help/paths.rds
/usr/lib64/R/library/survival/help/survival.rdb
/usr/lib64/R/library/survival/help/survival.rdx
/usr/lib64/R/library/survival/html/00Index.html
/usr/lib64/R/library/survival/html/R.css
/usr/lib64/R/library/tcltk/DESCRIPTION
/usr/lib64/R/library/tcltk/INDEX
/usr/lib64/R/library/tcltk/Meta/Rd.rds
/usr/lib64/R/library/tcltk/Meta/demo.rds
/usr/lib64/R/library/tcltk/Meta/features.rds
/usr/lib64/R/library/tcltk/Meta/hsearch.rds
/usr/lib64/R/library/tcltk/Meta/links.rds
/usr/lib64/R/library/tcltk/Meta/nsInfo.rds
/usr/lib64/R/library/tcltk/Meta/package.rds
/usr/lib64/R/library/tcltk/NAMESPACE
/usr/lib64/R/library/tcltk/R/tcltk
/usr/lib64/R/library/tcltk/R/tcltk.rdb
/usr/lib64/R/library/tcltk/R/tcltk.rdx
/usr/lib64/R/library/tcltk/demo/tkcanvas.R
/usr/lib64/R/library/tcltk/demo/tkdensity.R
/usr/lib64/R/library/tcltk/demo/tkfaq.R
/usr/lib64/R/library/tcltk/demo/tkttest.R
/usr/lib64/R/library/tcltk/exec/Tk-frontend.R
/usr/lib64/R/library/tcltk/exec/console.tcl
/usr/lib64/R/library/tcltk/exec/hierarchy.tcl
/usr/lib64/R/library/tcltk/exec/pkgIndex.tcl
/usr/lib64/R/library/tcltk/exec/progressbar.tcl
/usr/lib64/R/library/tcltk/exec/util-dump.tcl
/usr/lib64/R/library/tcltk/exec/util-expand.tcl
/usr/lib64/R/library/tcltk/exec/util-number.tcl
/usr/lib64/R/library/tcltk/exec/util-string.tcl
/usr/lib64/R/library/tcltk/exec/util-tk.tcl
/usr/lib64/R/library/tcltk/exec/util.tcl
/usr/lib64/R/library/tcltk/exec/widget.tcl
/usr/lib64/R/library/tcltk/help/AnIndex
/usr/lib64/R/library/tcltk/help/aliases.rds
/usr/lib64/R/library/tcltk/help/paths.rds
/usr/lib64/R/library/tcltk/help/tcltk.rdb
/usr/lib64/R/library/tcltk/help/tcltk.rdx
/usr/lib64/R/library/tcltk/html/00Index.html
/usr/lib64/R/library/tcltk/html/R.css
/usr/lib64/R/library/tools/DESCRIPTION
/usr/lib64/R/library/tools/INDEX
/usr/lib64/R/library/tools/Meta/Rd.rds
/usr/lib64/R/library/tools/Meta/features.rds
/usr/lib64/R/library/tools/Meta/hsearch.rds
/usr/lib64/R/library/tools/Meta/links.rds
/usr/lib64/R/library/tools/Meta/nsInfo.rds
/usr/lib64/R/library/tools/Meta/package.rds
/usr/lib64/R/library/tools/NAMESPACE
/usr/lib64/R/library/tools/R/sysdata.rdb
/usr/lib64/R/library/tools/R/sysdata.rdx
/usr/lib64/R/library/tools/R/tools
/usr/lib64/R/library/tools/R/tools.rdb
/usr/lib64/R/library/tools/R/tools.rdx
/usr/lib64/R/library/tools/help/AnIndex
/usr/lib64/R/library/tools/help/aliases.rds
/usr/lib64/R/library/tools/help/paths.rds
/usr/lib64/R/library/tools/help/tools.rdb
/usr/lib64/R/library/tools/help/tools.rdx
/usr/lib64/R/library/tools/html/00Index.html
/usr/lib64/R/library/tools/html/R.css
/usr/lib64/R/library/translations/DESCRIPTION
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/da/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/de/LC_MESSAGES/utils.mo
/usr/lib64/R/library/translations/en/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/en@quot/LC_MESSAGES/utils.mo
/usr/lib64/R/library/translations/en_GB/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/en_GB/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/en_GB/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/es/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/es/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/es/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/fa/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/fa/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/fa/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/fa/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/fr/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/it/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/ja/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/ko/LC_MESSAGES/utils.mo
/usr/lib64/R/library/translations/nn/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/nn/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/nn/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/nn/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/pl/LC_MESSAGES/utils.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/pt_BR/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/ru/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/tr/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-base.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-compiler.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-grDevices.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-graphics.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-grid.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-methods.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-parallel.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-splines.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-stats.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-stats4.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-tcltk.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-tools.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R-utils.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/grDevices.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/grid.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/methods.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/parallel.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/splines.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/stats.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/tcltk.mo
/usr/lib64/R/library/translations/zh_CN/LC_MESSAGES/tools.mo
/usr/lib64/R/library/translations/zh_TW/LC_MESSAGES/R.mo
/usr/lib64/R/library/translations/zh_TW/LC_MESSAGES/RGui.mo
/usr/lib64/R/library/translations/zh_TW/LC_MESSAGES/graphics.mo
/usr/lib64/R/library/utils/DESCRIPTION
/usr/lib64/R/library/utils/INDEX
/usr/lib64/R/library/utils/Meta/Rd.rds
/usr/lib64/R/library/utils/Meta/features.rds
/usr/lib64/R/library/utils/Meta/hsearch.rds
/usr/lib64/R/library/utils/Meta/links.rds
/usr/lib64/R/library/utils/Meta/nsInfo.rds
/usr/lib64/R/library/utils/Meta/package.rds
/usr/lib64/R/library/utils/NAMESPACE
/usr/lib64/R/library/utils/R/sysdata.rdb
/usr/lib64/R/library/utils/R/sysdata.rdx
/usr/lib64/R/library/utils/R/utils
/usr/lib64/R/library/utils/R/utils.rdb
/usr/lib64/R/library/utils/R/utils.rdx
/usr/lib64/R/library/utils/Sweave/Sweave-test-1.Rnw
/usr/lib64/R/library/utils/Sweave/example-1.Rnw
/usr/lib64/R/library/utils/doc/Sweave.pdf
/usr/lib64/R/library/utils/help/AnIndex
/usr/lib64/R/library/utils/help/aliases.rds
/usr/lib64/R/library/utils/help/paths.rds
/usr/lib64/R/library/utils/help/utils.rdb
/usr/lib64/R/library/utils/help/utils.rdx
/usr/lib64/R/library/utils/html/00Index.html
/usr/lib64/R/library/utils/html/R.css
/usr/lib64/R/library/utils/iconvlist
/usr/lib64/R/library/utils/misc/exDIF.csv
/usr/lib64/R/library/utils/misc/exDIF.dif
/usr/lib64/R/share/R/REMOVE.R
/usr/lib64/R/share/R/examples-footer.R
/usr/lib64/R/share/R/examples-header.R
/usr/lib64/R/share/R/nspackloader.R
/usr/lib64/R/share/R/tests-startup.R
/usr/lib64/R/share/Rd/macros/system.Rd
/usr/lib64/R/share/dictionaries/en_stats.rds
/usr/lib64/R/share/encodings/Adobe-glyphlist
/usr/lib64/R/share/encodings/character-sets
/usr/lib64/R/share/java/README
/usr/lib64/R/share/java/getsp.class
/usr/lib64/R/share/licenses/AGPL-3
/usr/lib64/R/share/licenses/Artistic-2.0
/usr/lib64/R/share/licenses/BSD_2_clause
/usr/lib64/R/share/licenses/BSD_3_clause
/usr/lib64/R/share/licenses/GPL-2
/usr/lib64/R/share/licenses/GPL-3
/usr/lib64/R/share/licenses/LGPL-2
/usr/lib64/R/share/licenses/LGPL-2.1
/usr/lib64/R/share/licenses/LGPL-3
/usr/lib64/R/share/licenses/MIT
/usr/lib64/R/share/licenses/license.db
/usr/lib64/R/share/make/basepkg.mk
/usr/lib64/R/share/make/check_vars_ini.mk
/usr/lib64/R/share/make/check_vars_out.mk
/usr/lib64/R/share/make/clean.mk
/usr/lib64/R/share/make/config.mk
/usr/lib64/R/share/make/lazycomp.mk
/usr/lib64/R/share/make/shlib.mk
/usr/lib64/R/share/make/vars.mk
/usr/lib64/R/share/make/winshlib.mk
/usr/lib64/R/share/sh/echo.sh
/usr/lib64/R/share/texmf/bibtex/bib/RJournal.bib
/usr/lib64/R/share/texmf/bibtex/bib/Rnews.bib
/usr/lib64/R/share/texmf/bibtex/bst/jss.bst
/usr/lib64/R/share/texmf/tex/latex/Rd.sty
/usr/lib64/R/share/texmf/tex/latex/Sweave.sty
/usr/lib64/R/share/texmf/tex/latex/jss.cls
/usr/lib64/R/share/texmf/tex/latex/omsaer.fd
/usr/lib64/R/share/texmf/tex/latex/omsaett.fd
/usr/lib64/R/share/texmf/tex/latex/omscmtt.fd
/usr/lib64/R/share/texmf/tex/latex/ts1aer.fd
/usr/lib64/R/share/texmf/tex/latex/ts1aett.fd
/usr/lib64/R/tests/
/usr/lib64/R/library/*/tests/*
/usr/lib64/R/library/KernSmooth/po/it/LC_MESSAGES/R-KernSmooth.mo
/usr/lib64/R/library/MASS/po/it/LC_MESSAGES/R-MASS.mo
/usr/lib64/R/library/boot/po/it/LC_MESSAGES/R-boot.mo
/usr/lib64/R/library/foreign/po/it/LC_MESSAGES/R-foreign.mo
/usr/lib64/R/library/foreign/po/it/LC_MESSAGES/foreign.mo
/usr/lib64/R/library/nnet/po/it/LC_MESSAGES/R-nnet.mo
/usr/lib64/R/library/spatial/po/it/LC_MESSAGES/R-spatial.mo

%files bin
%defattr(-,root,root,-)
/usr/bin/R
/usr/bin/Rscript

%files dev
%defattr(-,root,root,-)
/usr/lib64/R/include/R.h
/usr/lib64/R/include/R_ext/Altrep.h
/usr/lib64/R/include/R_ext/Applic.h
/usr/lib64/R/include/R_ext/Arith.h
/usr/lib64/R/include/R_ext/BLAS.h
/usr/lib64/R/include/R_ext/Boolean.h
/usr/lib64/R/include/R_ext/Callbacks.h
/usr/lib64/R/include/R_ext/Complex.h
/usr/lib64/R/include/R_ext/Connections.h
/usr/lib64/R/include/R_ext/Constants.h
/usr/lib64/R/include/R_ext/Error.h
/usr/lib64/R/include/R_ext/GetX11Image.h
/usr/lib64/R/include/R_ext/GraphicsDevice.h
/usr/lib64/R/include/R_ext/GraphicsEngine.h
/usr/lib64/R/include/R_ext/Itermacros.h
/usr/lib64/R/include/R_ext/Lapack.h
/usr/lib64/R/include/R_ext/Linpack.h
/usr/lib64/R/include/R_ext/MathThreads.h
/usr/lib64/R/include/R_ext/Memory.h
/usr/lib64/R/include/R_ext/Parse.h
/usr/lib64/R/include/R_ext/Print.h
/usr/lib64/R/include/R_ext/PrtUtil.h
/usr/lib64/R/include/R_ext/QuartzDevice.h
/usr/lib64/R/include/R_ext/R-ftp-http.h
/usr/lib64/R/include/R_ext/RS.h
/usr/lib64/R/include/R_ext/RStartup.h
/usr/lib64/R/include/R_ext/Rallocators.h
/usr/lib64/R/include/R_ext/Random.h
/usr/lib64/R/include/R_ext/Rdynload.h
/usr/lib64/R/include/R_ext/Riconv.h
/usr/lib64/R/include/R_ext/Utils.h
/usr/lib64/R/include/R_ext/Visibility.h
/usr/lib64/R/include/R_ext/eventloop.h
/usr/lib64/R/include/R_ext/libextern.h
/usr/lib64/R/include/R_ext/stats_package.h
/usr/lib64/R/include/R_ext/stats_stubs.h
/usr/lib64/R/include/Rconfig.h
/usr/lib64/R/include/Rdefines.h
/usr/lib64/R/include/Rembedded.h
/usr/lib64/R/include/Rinterface.h
/usr/lib64/R/include/Rinternals.h
/usr/lib64/R/include/Rmath.h
/usr/lib64/R/include/Rversion.h
/usr/lib64/R/include/S.h
/usr/lib64/R/library/Matrix/include/Matrix.h
/usr/lib64/R/library/Matrix/include/cholmod.h
/usr/lib64/pkgconfig/libR.pc

%files doc
%defattr(-,root,root,-)
%doc /usr/share/man/man1/*
/usr/lib64/R/doc/manual/R-FAQ.html
/usr/lib64/R/doc/manual/R-admin.html
/usr/lib64/R/doc/manual/R-data.html
/usr/lib64/R/doc/manual/R-exts.html
/usr/lib64/R/doc/manual/R-intro.html
/usr/lib64/R/doc/manual/R-ints.html
/usr/lib64/R/doc/manual/R-lang.html
/usr/lib64/R/library/rpart/help/figures/rpart.png
/usr/lib64/R/library/survival/doc/survival.R
/usr/lib64/R/library/survival/doc/survival.Rnw
/usr/lib64/R/library/survival/doc/survival.pdf
/usr/lib64/R/library/survival/help/figures/logo.png

%files lib
%defattr(-,root,root,-)
/usr/lib64/R/lib/haswell/libR.so
/usr/lib64/R/lib/haswell/libRblas.so
/usr/lib64/R/lib/haswell/libRlapack.so
/usr/lib64/R/lib/libR.so
/usr/lib64/R/lib/libRblas.so
/usr/lib64/R/lib/libRlapack.so
/usr/lib64/R/library/KernSmooth/libs/KernSmooth.so
/usr/lib64/R/library/MASS/libs/MASS.so
/usr/lib64/R/library/Matrix/libs/Matrix.so
/usr/lib64/R/library/class/libs/class.so
/usr/lib64/R/library/cluster/libs/cluster.so
/usr/lib64/R/library/foreign/libs/foreign.so
/usr/lib64/R/library/grDevices/libs/cairo.so
/usr/lib64/R/library/grDevices/libs/grDevices.so
/usr/lib64/R/library/graphics/libs/graphics.so
/usr/lib64/R/library/grid/libs/grid.so
/usr/lib64/R/library/lattice/libs/lattice.so
/usr/lib64/R/library/methods/libs/methods.so
/usr/lib64/R/library/mgcv/libs/mgcv.so
/usr/lib64/R/library/nlme/libs/nlme.so
/usr/lib64/R/library/nnet/libs/nnet.so
/usr/lib64/R/library/parallel/libs/parallel.so
/usr/lib64/R/library/rpart/libs/rpart.so
/usr/lib64/R/library/spatial/libs/spatial.so
/usr/lib64/R/library/splines/libs/splines.so
/usr/lib64/R/library/stats/libs/stats.so
/usr/lib64/R/library/survival/libs/survival.so
/usr/lib64/R/library/tcltk/libs/tcltk.so
/usr/lib64/R/library/tools/libs/tools.so
/usr/lib64/R/library/utils/libs/utils.so
/usr/lib64/R/modules/R_X11.so
/usr/lib64/R/modules/R_de.so
/usr/lib64/R/modules/internet.so
/usr/lib64/R/modules/lapack.so
/usr/lib64/R/library/*/libs/*.so.avx2

/usr/lib64/R/lib/haswell/avx512_1/libR.so
/usr/lib64/R/lib/haswell/avx512_1/libRblas.so
/usr/lib64/R/lib/haswell/avx512_1/libRlapack.so
/usr/lib64/R/library/*/libs/*.so.avx512

