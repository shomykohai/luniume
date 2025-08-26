{
  description = "";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    frostix = {
      url = "github:shomykohai/frostix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = {
    nixpkgs,
    frostix,
  }: let
    forAllSystems = f: nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed (system: f system);
  in {
    devShells = forAllSystems (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
            android_sdk.accept_license = true;
          };
        };
        frostixPkgs = frostix.packages.${system};
        # From https://github.com/NixOS/nixpkgs/issues/215861#issuecomment-2014663062
        buildToolsVersion = "35.0.0";
        androidComposition = pkgs.androidenv.composeAndroidPackages {
          buildToolsVersions = [buildToolsVersion];
        };
        zipAlignPath = "${androidComposition.androidsdk}/libexec/android-sdk/build-tools/${buildToolsVersion}";
      in {
        default = pkgs.mkShell {
          buildInputs = [
            pkgs.python3
            androidComposition.androidsdk
            # pkgs.androidenv.androidPkgs.tools
            pkgs.curl
            pkgs.jq
            pkgs.apkeditor
            pkgs.openjdk17
            pkgs.revanced-cli
            frostixPkgs.dexpatcher
            frostixPkgs.lspatch
          ];
          shellHook = ''
            export PATH="${zipAlignPath}:$PATH"
          '';
        };
      }
    );
  };
}
