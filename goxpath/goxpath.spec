%if 0%{?fedora} || 0%{?rhel}
%global with_devel 1
%global with_bundled 0
%global with_debug 0
%global with_check 1
%global with_unit_test 1
%else
%global with_devel 1
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         ChrisTrenkamp
%global repo            goxpath
# https://github.com/ChrisTrenkamp/goxpath
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          c385f95c6022e7756e91beac5f5510872f7dcb7d
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           goxpath
Version:        1.0.alpha3
Release:        0.2.git%{shortcommit}%{?dist}
Summary:        An XPath 1.0 implementation written in Go
License:        MIT
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

BuildRequires:  help2man

%description
%{summary}

%if 0%{?with_devel}
%package -n golang-%{provider}-%{project}-%{repo}-devel
Summary:        %{summary}
BuildArch:      noarch

%if 0%{?with_check}
BuildRequires:  golang(golang.org/x/net/html/charset)
BuildRequires:  golang(golang.org/x/text/language)
%endif

Requires:       golang(golang.org/x/net/html/charset)
Requires:       golang(golang.org/x/text/language)

Provides:       golang(%{import_path}) = %{version}-%{release}
Provides:       golang(%{import_path}/lexer) = %{version}-%{release}
Provides:       golang(%{import_path}/parser) = %{version}-%{release}
Provides:       golang(%{import_path}/parser/pathexpr) = %{version}-%{release}
Provides:       golang(%{import_path}/tree) = %{version}-%{release}
Provides:       golang(%{import_path}/tree/xmlstruct) = %{version}-%{release}
Provides:       golang(%{import_path}/tree/xmltree) = %{version}-%{release}
Provides:       golang(%{import_path}/tree/xmltree/xmlbuilder) = %{version}-%{release}
Provides:       golang(%{import_path}/tree/xmltree/xmlele) = %{version}-%{release}
Provides:       golang(%{import_path}/tree/xmltree/xmlnode) = %{version}-%{release}
Provides:       golang(%{import_path}/xconst) = %{version}-%{release}

%description -n golang-%{provider}-%{project}-%{repo}-devel
%{summary}

This package contains library source intended for building other packages
which use import path with %{import_path} prefix.
%endif

%if 0%{?with_unit_test}
%package -n golang-%{provider}-%{project}-%{repo}-unit-test
Summary:        Unit tests for %{name} package
BuildArch:      noarch
# If go_arches not defined fall through to implicit golang archs
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:       golang-github-christrenkamp-goxpath-devel = %{version}-%{release}

Requires:       golang(gopkg.in/check.v1)

%description -n golang-%{provider}-%{project}-%{repo}-unit-test
%{summary}

This package contains unit tests for project providing packages
with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build
mkdir -p src/%{provider}.%{provider_tld}/%{project}
ln -s ../../../ src/%{import_path}

%if ! 0%{?with_bundled}
export GOPATH=$(pwd):%{gopath}
%else
export GOPATH=$(pwd):$(pwd)/Godeps/_workspace:%{gopath}
%endif

%gobuild -o bin/goxpath %{import_path}/cmd/goxpath
help2man -n "An XPath 1.0 implementation written in Go" \
    --version-string="%{version}" \
    --no-info --no-discard-stderr \
    bin/goxpath > goxpath.1

%install
# install binaries
install -d %{buildroot}%{_bindir}
install -p -m 755 bin/goxpath %{buildroot}%{_bindir}/goxpath

# install man-pages
install -d %{buildroot}%{_mandir}/man1
cp -p goxpath.1 %{buildroot}%{_mandir}/man1/

# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if 0%{?with_bundled}
export GOPATH=$(pwd)/Godeps/_workspace:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

# properly include relative file paths
pushd src/%{import_path}/cmd/goxpath
%gotest
popd

%gotest %{import_path}
%gotest %{import_path}/lexer/...
%gotest %{import_path}/parser/...
%gotest %{import_path}/tree/...
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%files
%license LICENSE
%doc README.md
%{_bindir}/goxpath
%{_mandir}/man1/goxpath.1.gz

%if 0%{?with_devel}
%files -n golang-%{provider}-%{project}-%{repo}-devel -f devel.file-list
%license LICENSE
%doc README.md
%endif

%if 0%{?with_unit_test}
%files -n golang-%{provider}-%{project}-%{repo}-unit-test -f unit-test.file-list
%license LICENSE
%doc README.md
%endif

%changelog
* Mon Nov 27 2017 Reto Gantenbein <reto.gantenbein@linuxmonk.ch> 1.0.alpha3-0.1.gitc385f95
- new package built with tito

