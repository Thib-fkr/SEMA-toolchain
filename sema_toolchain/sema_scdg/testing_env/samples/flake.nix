{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    # nixpkgs-unstable.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
      in {
        devShells = rec {

          samples_dev = pkgs.mkShell {
            name = "samples_dev";
            src = ./.;

            packages = [
              pkgs.zig
              pkgs.zls
            ];

            shellHook = ''
              echo "[+] Entering dev shell..."
              fish
            '';
          };

          default = samples_dev;
        };

        packages = rec {
          zig-compile = pkgs.stdenv.mkDerivation {
            name = "zig-compile";
            src = ./.;

            buildInputs = [
              pkgs.zig
            ];

            # Execute the computations in a temporary directory
            buildPhase = ''
              runHook preBuild

              # Create a directory to receive cache files with correct permissions
              mkdir -p zig-cache

              # Set the zig env variables to point to this new directory
              ZIG_GLOBAL_CACHE_DIR="$PWD/zig-cache"
              export ZIG_GLOBAL_CACHE_DIR

              ZIG_LOCAL_CACHE_DIR="$PWD/zig-cache"
              export ZIG_LOCAL_CACHE_DIR

              zig build install

              runHook postBuild
            '';

            # Install the result in ./result
            installPhase = ''
              runHook preInstall

              mkdir -p $out/bin
              cp zig-out/bin/* $out/bin

              runHook postInstall
            '';
          };

          default = zig-compile;
        };
    });
}
