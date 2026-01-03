%global srcname envon

Name:           python3-%{srcname}
Version:        0.1.4
Release:        1%{?dist}
Summary:        Cross-shell Python virtual environment activator

License:        MIT
URL:            https://github.com/Userfrom1995/%{srcname}
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
envon is a cross-shell Python virtual environment activator that emits
the correct activation command for your shell. It auto-detects the
nearest or specified virtual environment and supports bash, zsh, sh,
fish, powershell, pwsh, nushell, cmd, and csh/tcsh/cshell.

It simplifies virtual environment activation across different shells
and provides a unified interface for discovering and activating
Python virtual environments in your projects.

%prep
%autosetup -n %{srcname}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{srcname}

# Install shell bootstrap files to datadir
install -d -m 0755 %{buildroot}%{_datadir}/%{srcname}
install -p -m 0644 src/%{srcname}/bootstrap_bash.sh %{buildroot}%{_datadir}/%{srcname}/
install -p -m 0644 src/%{srcname}/bootstrap_sh.sh %{buildroot}%{_datadir}/%{srcname}/
install -p -m 0644 src/%{srcname}/bootstrap_fish.fish %{buildroot}%{_datadir}/%{srcname}/
install -p -m 0644 src/%{srcname}/bootstrap_powershell.ps1 %{buildroot}%{_datadir}/%{srcname}/
install -p -m 0644 src/%{srcname}/bootstrap_csh.csh %{buildroot}%{_datadir}/%{srcname}/
install -p -m 0644 src/%{srcname}/bootstrap_csh_fixed.csh %{buildroot}%{_datadir}/%{srcname}/
install -p -m 0644 src/%{srcname}/bootstrap_nushell.nu %{buildroot}%{_datadir}/%{srcname}/

# Install man page
install -d -m 0755 %{buildroot}%{_mandir}/man1
install -p -m 0644 docs/man/%{srcname}.1 %{buildroot}%{_mandir}/man1/

%check
%pyproject_check_import

%files -n python3-%{srcname} -f %{pyproject_files}
%license LICENSE
%doc README.md docs/
%{_bindir}/%{srcname}
%{_datadir}/%{srcname}/
%{_mandir}/man1/%{srcname}.1*

%changelog
* Sat Jan 03 2026 User1995 <userfrom1995@gmail.com> - 0.1.4-1
- Update to version 0.1.4
- Add comprehensive man page for envon command
- Clarify activation usage in documentation
- Improve VIRTUAL_ENV fallback behavior documentation

* Sat Jan 03 2026 User1995 <userfrom1995@gmail.com> - 0.1.3-1
- Update to version 0.1.3
- Use GitHub release tarball as Source0 (fixes MD5sum check errors)
- Comply with Fedora Python Packaging Guidelines
- Use pyproject-rpm-macros for modern Python packaging
- Remove explicit Requires - use automatic dependency generator
- Add %%check section with %%pyproject_check_import
- Use install command with proper permissions for bootstrap files
- Fix URL capitalization
- Add man page for envon command

* Mon Nov 18 2024 User1995 <userfrom1995@gmail.com> - 0.1.1-1
- Initial package