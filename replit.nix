{pkgs}: {
  deps = [
    pkgs.libxcrypt
    pkgs.postgresql
    pkgs.bash
    pkgs.glibcLocales
  ];
}
