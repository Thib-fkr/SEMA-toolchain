{
  description = "Nix flake for testing the SEMA SCDG tool";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
        pythonPackages = pkgs.python312Packages;
      in
      {
        devShells.default = pkgs.mkShell {
          name = "sema_scdg";
          src = null;

          nativeBuildInputs = with pkgs; [
            pkg-config
          ];

          # Python modules dependencies
          buildInputs = with pythonPackages; [
            # Needed for installing the requirements
            setuptools
            wheel
            venvShellHook
            distutils

            # Additional dependencies that won't install normally
            pygraphviz
            z3
          ];

          # Binary packages made available in the shell
          packages = with pythonPackages; [
            pkgs.radare2
          ];

          venvDir = ".venv";

          postVenv = ''
            unset SOURCE_DATE_EPOCH
          '';

          postShellHook = ''
            unset SOURCE_DATE_EPOCH
            unset LD_PRELOAD

            PYTHONPATH=$PWD/$venvDir/${python.sitePackages}:$PYTHONPATH
            export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc.lib]}
          '';
        };
      });
}

# Once in the shell:

#  To install the packages, do:
# `pip install -U pip`
# `pip install -r requirements.txt`

# Then you can run the program as explained in the README etc...
