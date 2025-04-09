{pkgs}: {
  deps = [
    pkgs.sqlite
    pkgs.rustc
    pkgs.pkg-config
    pkgs.openssl
    pkgs.libiconv
    pkgs.cargo
    pkgs.libxcrypt
    pkgs.postgresql
    pkgs.bash
    pkgs.glibcLocales
  ];
}
