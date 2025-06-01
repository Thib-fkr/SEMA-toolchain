{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs";
    flake-utils.url = "github:numtide/flake-utils";
    sema = {
        # nix flake update sema
        url = "github:csvl/SEMA";
        flake = false;
    };
    samples = {
      url = "path:./../samples";
    };
  };
  outputs = { self, nixpkgs, flake-utils, sema, samples, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };
        python = pkgs.python312;
        pythonPackages = pkgs.python312Packages;
      in {

        # Shell for locally testing SEMA
        devShells = rec {
          sema_local = pkgs.mkShell {
            name = "sema_scdg";
            src = null;

            scdg = "${sema}/sema_toolchain/sema_scdg";
            samples = samples.packages.${system}.default;

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
            packages = [
                pkgs.radare2
            ];

            venvDir = ".venv";

            # Runs when the virtual environment is created
            # Here it replaces lines of broken packages in 'sema_scdg/requirements.txt'
            postVenvCreation = ''
                unset SOURCE_DATE_EPOCH

                cp ${sema}/sema_toolchain/sema_scdg/requirements.txt .
                sed -i 's/numpy==.*$/numpy/' requirements.txt
                sed -i 's/scipy==.*$/scipy/' requirements.txt
                sed -i 's/pygraphviz==.*$//' requirements.txt
                pip install -r requirements.txt
                rm -f requirements.txt

                sed -i 's//and\ irsb.next.tag\ ==\ \"Iex_Const\"/' $venvDir/lib/python3.12/site-packages/angr/engines/vex/heavy/heavy.py
            '';

            # Runs in the virtual environment
            postShellHook = ''
                unset SOURCE_DATE_EPOCH
                unset LD_PRELOAD

                PYTHONPATH=$PWD/$venvDir/${python.sitePackages}:$PYTHONPATH
                export LD_LIBRARY_PATH=${pkgs.lib.makeLibraryPath [pkgs.stdenv.cc.cc.lib]}

                # Apply modification to make SemaSCDG.py directly runable
                if [ ! -d $PWD/scdg_local/ ]; then

                  # Create a local copy and give it execution permission
                  echo "[+] Copying scdg to local directory"
                  mkdir -p scdg_local
                  cp -r $scdg scdg_local
                  chmod u+w -R scdg_local

                  # Create directories to store binaries to analyze
                  mkdir -p scdg_local/sema_scdg/application/database/malware-win
                  mkdir -p scdg_local/sema_scdg/application/database/malware-lin
                  mkdir -p scdg_local/sema_scdg/application/database/malware-any

                  # Apply various patches
                  sed -i 's/call_sim.custom_simproc_windows/call_sim.sim_proc/' scdg_local/sema_scdg/application/plugin/PluginHooks.py # Patch missing custom simproc in hook plugin while prod not fixed
                fi
                # Add new sim procedures
                cp new_files/win/* scdg_local/sema_scdg/application/procedures/windows/custom_package/

                cd scdg_local/sema_scdg/application
            '';
          };

          sema_docker = pkgs.mkShell {
            name = "sema_scdg_docker";
            src = ./.;

            packages = [
              pkgs.docker
            ];

            shellHook = ''
                sudo ${pkgs.docker}/bin/docker run --rm --name="sema-scdg" \
                -v ${samples}/bin/:/sema-scdg/application/database/Binaries \
                -v $PWD/tests_results/:/sema-scdg/application/database/SCDG \
                -p 5001:5001 -it manonoreins/sema-scdg bash
            '';
          };

          default = sema_local;
        };
    });
}
