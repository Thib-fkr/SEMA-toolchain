# SEMA SCDG

This directory contains scripts to perform test on the SEMA SCDG part of the SEMA toolchain.

## Structure of this directory

Path between parentheses are meant to be generated and used locally and are ignored by git.

- `(.venv/)` Python virtual environment created by the flake and used to execute SEMA-SCDG
- `(scdg_local/)` Directory containing SEMA-SCDG code meant to be locally executed

## Pre-requisite

The only dependency is to install an implementation of the `Nix` package manager and allow the experimental `flake` feature.

## Downloading and launching SEMA locally

The file `flake.nix` is responsible for downloading and caching the files from the SEMA repository on Github, as well as setting up the test environment.

The command below opens a shell in a python virtual environment, with access to SEMA's files and every dependencies.
```bash
nix develop
```
It perfoms the following actions :
- If run for the first time or if the dependencies have changed
    - Download SEMA from Github
    - Download the specified external dependencies
        - python and some python-packages
        - radare2
    - Compile the samples (as defined in `../samples/flake.nix`)
    - Create a python virtual environment
    - Create an updated version of the `requirements.txt` file, with changes to
        - numpy (removed version specification)
        - scipy (removed version specification)
        - pygraphviz (removed it altogether, as it is installed in previous steps)
- Every time
    - Set some shell environment variables needed for executing SEMA
    - Opens a shell with access to all cached dependencies
    - If needed:
        - Copy sema_scdg code into a local directory `scdg_local`
        - Add write permissions to `scdg_local` (because files in the nix-store are read-only)
        - Apply patches to sema-scdg code if necessary
    - cd into `scdg_local`

### Updating SEMA code
It is sufficient to delete the `scdg_local` directory to have the flake copy the latest version of SEMA scdg in it next time the above-mentioned command is launched.

- If changes have been made to SEMA's python packages dependencies, `devShells.sema_local.buildInputs` and `devShells.sema_local.postVenvCreation` should be the only places to check for potential update.
- If changes have been made to SEMA-SCDG, you may want to check the patches in `devShells.sema_local.postShellHook`

Please note that the only dependencies specified in this flake are the one needed to run simple test on the sema_scdg part of the SEMA toolchain.
If a new external dependency is needed, `devShells.sema_local.packages` is likely to be what you want to try and update first.

## Downloading and launching SEMA on [`manonoreins/sema-scdg`](https://hub.docker.com/r/manonoreins/sema-scdg)'s docker

The file `flake.nix` is responsible for downloading and caching docker, as well as launching a docker instance and connecting a shell session to it.

The command below opens a shell in the docker, where the `Input` directory is `../samples/bin` and the `Output` directory is `./tests-results`.
```bash
nix develop .#sema_docker
```
It perfoms the following actions :
- Download docker
- Compile and cache the samples (as defined in `../samples/flake.nix`)
- Launch the docker instance
