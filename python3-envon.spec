%global srcname envon

Name:           python3-%{srcname}
Version:        0.1.1
Release:        1%{?dist}
Summary:        Emit the activation command for the nearest Python virtual environment

License:        MIT
URL:            https://github.com/userfrom1995/%{srcname}
Source0:        https://github.com/userfrom1995/%{srcname}/archive/refs/tags/v%{version}.tar.gz#/%{srcname}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-build
BuildRequires:  python3-hatchling
BuildRequires:  python3-installer

Requires:       python3-virtualenv >= 20

%description
envon is a cross-shell Python virtual environment activator that emits the correct
activation command for your shell. It auto-detects the nearest or specified virtual
environment and supports bash, zsh, sh, fish, powershell, pwsh, nushell, cmd, and
csh/tcsh/cshell.

%prep
%autosetup -n %{srcname}-%{version}

%build
python3 -m build --wheel --no-isolation

%install
python3 -m installer --destdir=%{buildroot} dist/*.whl

# Create directories for shell bootstrap files
mkdir -p %{buildroot}%{_datadir}/%{srcname}

# Install bootstrap files
cp -r src/%{srcname}/bootstrap_*.sh %{buildroot}%{_datadir}/%{srcname}/
cp -r src/%{srcname}/bootstrap_*.fish %{buildroot}%{_datadir}/%{srcname}/
cp -r src/%{srcname}/bootstrap_*.ps1 %{buildroot}%{_datadir}/%{srcname}/
cp -r src/%{srcname}/bootstrap_*.csh %{buildroot}%{_datadir}/%{srcname}/
cp -r src/%{srcname}/bootstrap_*.nu %{buildroot}%{_datadir}/%{srcname}/

%files
%license LICENSE
%doc README.md docs/
%{python3_sitelib}/%{srcname}-%{version}.dist-info/
%{python3_sitelib}/%{srcname}/
%{_bindir}/%{srcname}
%{_datadir}/%{srcname}/

%changelog
* Tue Nov 18 2025 User1995 <userfrom1995@gmail.com> - 0.1.1-1
- Initial package</content>
<parameter name="filePath">\\wsl.localhost\Ubuntu\home\base\envon\python-envon.spec