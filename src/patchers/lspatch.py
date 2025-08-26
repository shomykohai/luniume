from . import Patch
from utils.utils import get_global_patches, download_file, run_cli_command, sri_hash
import os

class LSPatch(Patch):
    def should_patch(self) -> bool:
        return self.app.patch_method == "lspatch"
    
    def apply_patch(self) -> None:
        self.app.download()
        if self.app.config.get("embedded", False):
            print(f"[LSPatch] Downloading patches for {self.app.name}")
            to_apply: List[str] = []
            global_patches = get_global_patches()
            for patch in self.app.patches:
                patch_info: Dict = global_patches.get("lspatch", {}).get(patch, {})

                if not patch_info:
                    print(f"[LSPatch] Patch {patch} not found in global patches.")
                    continue
                
                patch_url: str = patch_info.get("url", "")
                if not patch_url:
                    print(f"[LSPatch] No URL found for patch {patch}.")
                    continue
                
                dest = os.path.join("patches/lspatch", f"{patch}.apk")
                print(f"[LSPatch] Downloading {patch} from {patch_url}")
                if not download_file(patch_url, dest):
                    print(f"[LSPatch] Failed to download {patch}.")
                    continue
                    
                print(f"[LSPatch] Verifying SRI hash for {patch}")
                patch_hash = sri_hash(dest)
                print(f"[LSPatch] Expected hash: {patch_info['hash']}")
                print(f"[LSPatch] SRI hash for {dest}: {patch_hash}")
                if patch_hash != patch_info["hash"]:
                    print(f"[LSPatch] SRI hash mismatch for {patch_name}! Expected {patch_info['hash']}, got {patch_hash}")
                    continue
                
                to_apply.append(dest)

            print(f"[LSPatch] Embedding patch for {self.app.name}")
            additional_args = ["-m", *to_apply]



            
        else:
            print(f"[LSPatch] Patching {self.app.name} for usage with Manager.")
            additional_args = ["--manager", "--injectdex"]
        

        command = ["lspatch", "-v", "-l",  "2", "-f", "-o", "patched"]
        
        if self.is_keystore_valid():
            # LSPatch expects a p12 keystore, not bks
            if self.keystore.path.endswith(".bks"):
                self.app.keystore.path.replace(".bks", ".p12")
            command.extend([
                "-k", self.keystore.path,
                self.keystore.password,
                self.keystore.alias,
                self.keystore.password
            ])
        
        command.extend(additional_args)
        # This has to be at the end
        command.append(f"tmp/{self.app.package_name}.apk")
        print(command)
        result = run_cli_command(command)
        if result is not None:
            print(f"[LSPatch] Patch applied successfully!")
        else:
            print(f"[LSPatch] Failed to apply patch for {self.app.name}")
