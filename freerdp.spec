# Can be rebuilt with OpenH264 support enabled by passing # "--with=openh264"
# to mock/rpmbuild; or by globally setting the following variable:

#global _with_openh264 1

# Momentarily disable GSS support
# https://github.com/FreeRDP/FreeRDP/issues/4348
#global _with_gss 1

# Disable server support in RHEL
# https://bugzilla.redhat.com/show_bug.cgi?id=1639165
%if 0%{?fedora} || 0%{?rhel} >= 10
%global _with_server 1
%endif

# Disable support for missing codecs in RHEL
%{!?rhel:%global _with_soxr 1}
%if 0%{?fedora} || 0%{?rhel} >= 8
%global _with_lame 1
%endif
%if 0%{?fedora} >= 39
%global _with_ffmpeg 1
%endif

%global prerel  beta2
Name:           freerdp3
Version:        3.0.0
Release:        %{prerel}%{?dist}
Epoch:          3
Summary:        Free implementation of the Remote Desktop Protocol (RDP)
License:        ASL 2.0
URL:            http://www.freerdp.com/

Source0:        https://github.com/FreeRDP/FreeRDP/archive/refs/tags/%{version}-%{prerel}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  alsa-lib-devel
BuildRequires:  cmake >= 2.8
BuildRequires:  cups-devel
BuildRequires:  gsm-devel
%{?_with_lame:BuildRequires:  lame-devel}
BuildRequires:  libicu-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libX11-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXdamage-devel
BuildRequires:  libXext-devel
BuildRequires:  libXi-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libxkbfile-devel
BuildRequires:  libXrandr-devel
%{?_with_server:BuildRequires:  libXtst-devel}
BuildRequires:  libXv-devel
%{?_with_openh264:BuildRequires:  openh264-devel}
%{?_with_x264:BuildRequires:  x264-devel}
%{?_with_server:BuildRequires:  pam-devel}
BuildRequires:  xmlto
BuildRequires:  zlib-devel
BuildRequires:  multilib-rpm-config

BuildRequires:  pkgconfig(cairo)
%{?_with_gss:BuildRequires:  pkgconfig(krb5) >= 1.13}
BuildRequires:  pkgconfig(libpcsclite)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(libusb-1.0)
BuildRequires:  pkgconfig(openssl)
%{?_with_soxr:BuildRequires:  pkgconfig(soxr)}
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(xkbcommon)

%{?_with_ffmpeg:
BuildRequires:  pkgconfig(libavcodec) >= 57.48.101
BuildRequires:  pkgconfig(libavutil)
}

BuildRequires:  pkcs11-helper-devel
BuildRequires:  libswscale-free-devel
BuildRequires:  fuse3-devel
BuildRequires:  cjson-devel

Provides:       xfreerdp3 = %{?epoch}:%{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       libwinpr3%{?_isa} = %{?epoch}:%{version}-%{release}

%description
The xfreerdp & wlfreerdp Remote Desktop Protocol (RDP) clients from the FreeRDP
project.

xfreerdp & wlfreerdp can connect to RDP servers such as Microsoft Windows
machines, xrdp and VirtualBox.

%package        libs
Summary:        Core libraries implementing the RDP protocol
Requires:       libwinpr3%{?_isa} = %{?epoch}:%{version}-%{release}
Obsoletes:      %{name}-plugins < 1:1.1.0
Provides:       %{name}-plugins = %{?epoch}:%{version}-%{release}
%description    libs
libfreerdp-core can be embedded in applications.

libfreerdp-channels and libfreerdp-kbd might be convenient to use in X
applications together with libfreerdp-core.

libfreerdp-core can be extended with plugins handling RDP channels.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       pkgconfig
Requires:       cmake >= 2.8

%description    devel
The %{name}-devel package contains libraries and header files for developing
applications that use %{name}-libs.

%{?_with_server:
%package        server
Summary:        Server support for %{name}
Requires:       libwinpr%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       %{name}-libs%{?_isa} = %{?epoch}:%{version}-%{release}

%description    server
The %{name}-server package contains servers which can export a desktop via
the RDP protocol.
}

%package -n     libwinpr3
Summary:        Windows Portable Runtime
Provides:       %{name}-libwinpr = %{?epoch}:%{version}-%{release}
Obsoletes:      %{name}-libwinpr < 1:1.2.0

%description -n libwinpr3
WinPR provides API compatibility for applications targeting non-Windows
environments. When on Windows, the original native API is being used instead of
the equivalent WinPR implementation, without having to modify the code using it.

%package -n     libwinpr3-devel
Summary:        Windows Portable Runtime development files
Requires:       libwinpr%{?_isa} = %{?epoch}:%{version}-%{release}
Requires:       pkgconfig
Requires:       cmake >= 2.8

%description -n libwinpr3-devel
The %{name}-libwinpr-devel package contains libraries and header files for
developing applications that use %{name}-libwinpr.

%prep
%autosetup -n FreeRDP-%{version}-%{prerel}

# Rpmlint fixes
find . -name "*.h" -exec chmod 664 {} \;
find . -name "*.c" -exec chmod 664 {} \;

%build
%cmake %{?_cmake_skip_rpath} \
    -DCMAKE_INSTALL_LIBDIR:PATH=%{_lib} \
    -DWITH_ALSA=ON \
    -DWITH_CAIRO=ON \
    -DWITH_CUPS=ON \
    -DWITH_CHANNELS=ON -DBUILTIN_CHANNELS=OFF \
    -DWITH_CLIENT=ON \
    -DWITH_DIRECTFB=OFF \
    -DWITH_DSP_FFMPEG=%{?_with_ffmpeg:ON}%{?!_with_ffmpeg:OFF} \
    -DWITH_FFMPEG=%{?_with_ffmpeg:ON}%{?!_with_ffmpeg:OFF} \
    -DWITH_GSM=ON \
    -DWITH_GSSAPI=%{?_with_gss:ON}%{?!_with_gss:OFF} \
    -DWITH_ICU=ON \
    -DWITH_IPP=OFF \
    -DWITH_JPEG=ON \
    -DWITH_LAME=%{?_with_lame:ON}%{?!_with_lame:OFF} \
    -DWITH_MANPAGES=ON \
    -DWITH_OPENH264=%{?_with_openh264:ON}%{?!_with_openh264:OFF} \
    -DWITH_OPENSSL=ON \
    -DWITH_PCSC=ON \
    -DWITH_PULSE=ON \
    -DWITH_SERVER=%{?_with_server:ON}%{?!_with_server:OFF} \
    -DWITH_SERVER_INTERFACE=%{?_with_server:ON}%{?!_with_server:OFF} \
    -DWITH_SHADOW_X11=%{?_with_server:ON}%{?!_with_server:OFF} \
    -DWITH_SHADOW_MAC=%{?_with_server:ON}%{?!_with_server:OFF} \
    -DWITH_SOXR=%{?_with_soxr:ON}%{?!_with_soxr:OFF} \
    -DWITH_WAYLAND=ON \
    -DWITH_X11=ON \
    -DWITH_XCURSOR=ON \
    -DWITH_XEXT=ON \
    -DWITH_XKBFILE=ON \
    -DWITH_XI=ON \
    -DWITH_XINERAMA=ON \
    -DWITH_XRENDER=ON \
    -DWITH_XTEST=%{?_with_server:ON}%{?!_with_server:OFF} \
    -DWITH_XV=ON \
    -DWITH_ZLIB=ON \
%ifarch x86_64
    -DWITH_SSE2=ON \
    -DWITH_VAAPI=%{?_with_ffmpeg:ON}%{?!_with_ffmpeg:OFF} \
%else
    -DWITH_SSE2=OFF \
%endif
%ifarch armv7hl
    -DARM_FP_ABI=hard \
    -DWITH_NEON=OFF \
%endif
%ifarch armv7hnl
    -DARM_FP_ABI=hard \
    -DWITH_NEON=ON \
%endif
%ifarch armv5tel armv6l armv7l
    -DARM_FP_ABI=soft \
    -DWITH_NEON=OFF \
%endif
    %{nil}

%cmake_build

%install
%cmake_install

find %{buildroot} -name "*.a" -delete

for f in winpr-hash winpr-makecert wlfreerdp xfreerdp sfreerdp sfreerdp-server; do
    mv %{buildroot}/%{_bindir}/$f %{buildroot}/%{_bindir}/${f}3
done

for f in winpr-hash winpr-makecert wlfreerdp xfreerdp; do
    mv %{buildroot}/%{_mandir}/man1/$f.1.gz %{buildroot}/%{_mandir}/man1/${f}3.1.gz
done

mv %{buildroot}/%{_mandir}/man7/wlog.7.gz %{buildroot}/%{_mandir}/man7/wlog3.7.gz

%multilib_fix_c_header --file %{_includedir}/freerdp3/freerdp/build-config.h

%files
%{_bindir}/winpr-hash3
%{_bindir}/winpr-makecert3
%{_bindir}/wlfreerdp3
%{_bindir}/xfreerdp3
%{_bindir}/sfreerdp3
%{_bindir}/sfreerdp-server3
%{_mandir}/man1/winpr-hash3.1*
%{_mandir}/man1/winpr-makecert3.1*
%{_mandir}/man1/wlfreerdp3.1*
%{_mandir}/man1/xfreerdp3.1*

%files libs
%license LICENSE
%doc README.md ChangeLog
%{_libdir}/freerdp3/
%{_libdir}/libfreerdp-client3.so.*
%{?_with_server:
%{_libdir}/libfreerdp-server3.so.*
%{_libdir}/libfreerdp-shadow3.so.*
%{_libdir}/libfreerdp-shadow-subsystem3.so.*
%{_libdir}/libfreerdp-server-proxy3.so.*
}
%{_libdir}/libfreerdp3.so.*
%{_libdir}/libuwac0.so.*
%{_libdir}/librdtk0.so.*
%{_mandir}/man7/wlog3.*

%files devel
%{_includedir}/freerdp3
%{_includedir}/uwac0
%{_includedir}/rdtk0
%{_libdir}/cmake/FreeRDP3
%{_libdir}/cmake/FreeRDP-Client3
%{?_with_server:
%{_libdir}/cmake/FreeRDP-Server3
%{_libdir}/cmake/FreeRDP-Shadow3
%{_libdir}/cmake/FreeRDP-Proxy3
}
%{_libdir}/cmake/uwac0
%{_libdir}/cmake/rdtk0
%{_libdir}/libfreerdp-client3.so
%{?_with_server:
%{_libdir}/libfreerdp-server3.so
%{_libdir}/libfreerdp-shadow3.so
%{_libdir}/libfreerdp-shadow-subsystem3.so
%{_libdir}/libfreerdp-server-proxy3.so
}
%{_libdir}/libfreerdp3.so
%{_libdir}/libuwac0.so
%{_libdir}/librdtk0.so
%{_libdir}/pkgconfig/freerdp3.pc
%{_libdir}/pkgconfig/freerdp-client3.pc
%{?_with_server:
%{_libdir}/pkgconfig/freerdp-server3.pc
%{_libdir}/pkgconfig/freerdp-shadow3.pc
%{_libdir}/pkgconfig/freerdp-server-proxy3.pc
}
%{_libdir}/pkgconfig/uwac0.pc
%{_libdir}/pkgconfig/rdtk0.pc

%{?_with_server:
%files server
%{_bindir}/freerdp-proxy
%{_bindir}/freerdp-shadow-cli
%{_mandir}/man1/freerdp-shadow-cli.1*
}

%files -n libwinpr3
%license LICENSE
%doc README.md ChangeLog
%{_libdir}/libwinpr3.so.*
%{_libdir}/libwinpr-tools3.so.*

%files -n libwinpr3-devel
%{_libdir}/cmake/WinPR3
%{_includedir}/winpr3
%{_libdir}/libwinpr3.so
%{_libdir}/libwinpr-tools3.so
%{_libdir}/pkgconfig/winpr3.pc
%{_libdir}/pkgconfig/winpr-tools3.pc

%changelog
* Wed Aug 9 2023 Nicholas Kudriavtsev <nkudriavtsev@gmail.com> - 3:3.0.0-beta2-1
- Change epoch to 3
- Rename package and execution files to freerdp3 to prevent conflict with v2
  (not so with devel packages)

* Sun Aug 6 2023 Nicholas Kudriavtsev <nkudriavtsev@gmail.com> - 2:3.0.0-beta2-1
- Update to 3.0.0-beta2
- Remove the patch included in version 3.0.0

* Wed Jul 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.10.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Tue Jul 11 2023 František Zatloukal <fzatlouk@redhat.com> - 2:2.10.0-3
- Rebuilt for ICU 73.2

* Thu May 11 2023 Ondrej Holy <oholy@redhat.com> - 2:2.10.0-2
- Enable recommended FFmpeg support.

* Tue Feb 21 2023 Ondrej Holy <oholy@redhat.com> - 2:2.10.0-1
- Update to 2.10.0.

* Thu Jan 19 2023 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.9.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_38_Mass_Rebuild

* Sat Dec 31 2022 Pete Walter <pwalter@fedoraproject.org> - 2:2.9.0-2
- Rebuild for ICU 72

* Wed Nov 30 2022 Ondrej Holy <oholy@redhat.com> - 2:2.9.0-1
- Update to 2.9.0 (CVE-2022-39316, CVE-2022-39317, CVE-2022-39318,
CVE-2022-39319, CVE-2022-39320, CVE-2022-41877, CVE-2022-39347).

* Mon Nov 14 2022 Ondrej Holy <oholy@redhat.com> - 2:2.8.1-1
- Update to 2.8.1 (CVE-2022-39282, CVE-2022-39283).

* Mon Aug 15 2022 Simone Caronni <negativo17@gmail.com> - 2:2.8.0-1
- Update to 2.8.0.

* Wed Aug 03 2022 Ondrej Holy <oholy@redhat.com> - 2:2.7.0-4
- Enable server support in ELN.

* Mon Aug 01 2022 Frantisek Zatloukal <fzatlouk@redhat.com> - 2:2.7.0-3
- Rebuilt for ICU 71.1

* Thu Jul 21 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.7.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_37_Mass_Rebuild

* Mon Apr 25 2022 Ondrej Holy <oholy@redhat.com> - 2:2.7.0-1
- Update to 2.7.0.

* Fri Mar 11 2022 Ondrej Holy <oholy@redhat.com> - 2:2.6.1-1
- Update to 2.6.1.

* Thu Feb 03 2022 Ondrej Holy <oholy@redhat.com> - 2:2.5.0-1
- Update to 2.5.0.

* Thu Jan 20 2022 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.4.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_36_Mass_Rebuild

* Fri Nov 26 2021 Ondrej Holy <oholy@redhat.com> - 2:2.4.1-2
- Fix datatype mismatch / big-endian breakage
- Load legacy provider when initializing OpenSSL 3.0

* Wed Nov 10 2021 Ondrej Holy <oholy@redhat.com> - 2:2.4.1-1
- Update to 2.4.1 (CVE-2021-41159, CVE-2021-41160).

* Tue Sep 14 2021 Sahana Prasad <sahana@redhat.com> - 2:2.4.0-3
- Rebuilt with OpenSSL 3.0.0

* Wed Aug 11 2021 Ondrej Holy <oholy@redhat.com> - 2:2.4.0-2
- Preparation for OpenSSL 3.0

* Thu Jul 29 2021 Ondrej Holy <oholy@redhat.com> - 2:2.4.0-1
- Update to 2.4.0.

* Wed Jul 21 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.3.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Wed May 19 2021 Pete Walter <pwalter@fedoraproject.org> - 2:2.3.2-2
- Rebuild for ICU 69

* Thu Apr 15 2021 Simone Caronni <negativo17@gmail.com> - 2:2.3.2-1
- Update to 2.3.2.

* Tue Mar 23 2021 Simone Caronni <negativo17@gmail.com> - 2:2.2.0-6
- Explicitly enable Cairo support (#1938393).

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.2.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Aug 11 2020 Ondrej Holy <oholy@redhat.com> - 2:2.2.0-4
- Use %%cmake_ macros to fix out-of-source builds (#1863586)

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.2.0-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.2.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu Jul 23 2020 Simone Caronni <negativo17@gmail.com> - 2:2.2.0-1
- Update to 2.2.0.

* Tue Jun 30 2020 Simone Caronni <negativo17@gmail.com> - 2:2.1.2-1
- Update to 2.1.2.

* Thu May 21 2020 Ondrej Holy <oholy@redhat.com> - 2:2.1.1-1
- Update to 2.1.1.

* Fri May 15 2020 Ondrej Holy <oholy@redhat.com> - 2:2.1.0-1
- Update to 2.1.0 (#1833540).

* Fri May 15 2020 Pete Walter <pwalter@fedoraproject.org> - 2:2.0.0-57.20200207git245fc60
- Rebuild for ICU 67

* Fri Feb 07 2020 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-56.20200207git245fc60
- Update to latest snapshot.

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-55.20190820git6015229
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Fri Nov 01 2019 Pete Walter <pwalter@fedoraproject.org> - 2:2.0.0-54.20190820git6015229
- Rebuild for ICU 65

* Tue Aug 20 2019 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-53.20190820git6015229
- Update to latest snapshot.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-52.20190918git5e672d4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sun Jul 21 2019 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-51.20190918git5e672d4
- Update to latest snapshot.

* Sat May 18 2019 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-50.20190517gitb907324
- Update to latest snapshot.

* Wed Mar 06 2019 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-49.20190304git435872b
- Fix for GFX color depth (Windows 10).

* Thu Feb 28 2019 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-48.20190228gitce386c8
- Update to latest snapshot post rc4.
- CVE-2018-1000852 (#1661642).

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-47.rc4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Nov 29 2018 Ondrej Holy <oholy@redhat.com> - 2:2.0.0-47.rc4
- Update to 2.0.0-rc4

* Mon Oct 15 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-46.20181008git00af869
- Enable Xtest option (#1559606).

* Mon Oct 15 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-45.20181008git00af869
- Update to last snapshot post 2.0.0-rc3.

* Mon Aug 20 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-44.rc3
- Update SPEC file.

* Sat Aug 04 2018 Mike DePaulo <mikedep333@fedoraproject.org> - 2:2.0.0-43.20180801.rc3
- Update to 2.0.0-rc3

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-42.20180405gita9ecd6a
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Apr 09 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-41.20180405gita9ecd6a
- Update to latest snapshot.

* Wed Mar 21 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-40.20180320gitde83f4d
- Add PAM support (fixes freerdp-shadow-cli). Thanks Paolo Zeppegno.
- Update to latest snapshot.

* Thu Mar 15 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-39.20180314gitf8baeb7
- Update to latest snapshot.
- Fixes connection to RDP servers with the latest Microsoft patches:
  https://github.com/FreeRDP/FreeRDP/issues/4449

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-38.20180115git8f52c7e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Jan 18 2018 Karsten Hopp <karsten@redhat.com> - 2.0.0-37git}
- use versioned build requirement on pkgconfig(openssl) to prevent using
  compat-openssl10-devel instead of openssl-devel

* Tue Jan 16 2018 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-36.20180115git8f52c7e
- Update to latest snapshot.
- Make GSS support optional and disable it for now (#1534094 and FreeRDP #4348,
  #1435, #4363).

* Wed Dec 20 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-35.20171220gitbfe8359
- Update to latest snapshot post 2.0.0rc1.

* Mon Sep 11 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-34.20170831git3b83526
- Update to latest snapshot.
- Trim changelog.

* Mon Aug 07 2017 Björn Esser <besser82@fedoraproject.org> - 2:2.0.0-33.20170724gitf8c9f43
- Rebuilt for AutoReq cmake-filesystem

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-32.20170724gitf8c9f43
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-31.20170724gitf8c9f43
- Update to latest snapshot, Talos security fixes.

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-30.20170710gitf580bea
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 12 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-29.20170710gitf580bea
- Update to latest snapshot.

* Mon Jun 26 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-28.20170623git9904c32
- Update to latest snapshot.

* Mon May 15 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-27.20170512gitb1df835
- Update to latest snapshot.

* Thu Apr 20 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-26.20170419gitbfcf8e7
- Update to latest 2.0 snapshot.

* Thu Apr 13 2017 Orion Poplawski <orion@cora.nwra.com> - 2:2.0.0-25.20170317git8c68761
- Install tools via make install

* Wed Mar 22 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-24.20170317git8c68761
- Update to latest snapshot.

* Mon Mar 06 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-23.20170302git210de68
- Remove shared libxfreerdp-client shared library.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-22.20170302git210de68
- Move libxfreerdp-client shared object into devel subpackage.

* Thu Mar 02 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-21.20170302git210de68
- Update to latest snapshot.
- Update build requirements, tune build options.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2:2.0.0-20.20161228git90877f5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Mon Jan 09 2017 Simone Caronni <negativo17@gmail.com> - 2:2.0.0-19.20161228git90877f5
- Update to latest snapshot.
