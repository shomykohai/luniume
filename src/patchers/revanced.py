from . import Patch
from utils.utils import run_cli_command
import os

# For more informaton on how this works, you'll have more luck here :3 
# https://github.com/ReVanced/revanced-cli/blob/main/docs/1_usage.md

class RevancedPatch(Patch):
    def should_patch(self) -> bool:
        return self.app.patch_method == "revanced"

    def apply_patch(self) -> None:
        self.app.download()

        rvps = self.app.config.get("rvps", [])
        patches = self.app.config.get("patches", [])
        exclusive = self.app.config.get("exclusive_patches", False)

        if not rvps:
            print(f"[Revanced] No RVP patch files specified for {self.app.name}.")
            return

        apk_path = f"tmp/{self.app.package_name}.apk"
        ## TODO: Decide whether to hardcode this or not
        out_path = f"patched/{self.app.package_name}-revanced.apk"
        os.makedirs(os.path.dirname(out_path), exist_ok=True)

        command = ["revanced-cli", "patch"]

        for rvp in rvps:
            command.append(f"-p=patches/revanced/{rvp}")

        # Allow patches to be either "Patch Name" or a dict with options
        # NOTE: if patches is empty, Revanced cli will just use the defaults
        # https://github.com/ReVanced/revanced-cli/blob/main/docs/1_usage.md#-patch-an-app
        for patch in patches:
            if isinstance(patch, dict) and "name" in patch:
                command.append(f"-e={patch['name']}")
                if "options" in patch and patch["options"]:
                    for key, value in patch["options"].items():
                        if value is None:
                            command.append(f"-O{key}")
                        else:
                            safe_value = str(value).replace('"', '\\"').replace("'", "\\'")
                            command.append(f"-O{key}={safe_value}")
            elif isinstance(patch, str):
                command.append(f"-e={patch}")

        if exclusive:
            command.append("--exclusive")

        command.append(f"-o={out_path}")
        command.append(apk_path)
        command.append("--signer=Luniume")

        # Yeet da keys in!
        if self.is_keystore_valid():
            # Same matter as LSPatch, keystore format are different for the two tools
            if self.keystore.path.endswith(".p12"):
                self.app.keystore.path.replace(".p12", ".bks")
            command.append(f"--keystore={self.keystore.path}")
            command.append(f"--keystore-entry-alias={self.keystore.alias}")
            command.append(f"--keystore-password={self.keystore.password}")
            command.append(f"--keystore-entry-password={self.keystore.password}")
        print(f"[Revanced] Starting patch process for {self.app.name}")
        result = run_cli_command(command)
        if result is not None:
            print(f"[Revanced] Patch applied successfully!")
        else:
            print(f"[Revanced] Failed to apply patch for {self.app.name}")