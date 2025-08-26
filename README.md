# 🌙 Luniume

Luniume is an automatic declarative patcher for android apps, powered by Revanced and LSPatch.

# Installation

- [Arch Linux](#installing-on-arch-linux)
- [NixOS](#installing-on-nixos)


## Installing on Arch Linux

Install the dependencies
```sh
$ (sudo) pacman -S  python python-pip python-pipenv git jdk17-openjdk
$ yay -S revanced-cli-bin 
```

Download LSPatch from [here](https://github.com/JingMatrix/LSPatch)
Then make a wrapper script to bin (or alias it to run the jar file)
```sh
$ sudo cp lspatch.jar /usr/lib/lspatch/
$ sudo tee /usr/bin/lspatch <<EOF
#!/bin/sh
exec java -jar /usr/lib/lspatch/lspatch.jar "\$@"
EOF
$ sudo chmod +x /usr/bin/lspatch
```

Finally clone the repo:
```sh
$ git clone https://github.com/shomykohai/luniume
```

## Installing on NixOS

Clone the repo and enter into the nix shell
```sh
$ git clone https://github.com/shomykohai/luniume
$ nix develop
```

Now edit `config.json` at your will and run
```sh
$ ./bulk_patch.sh
```

# Usage

1. Configure your own keystore running the `keystore.sh` bash script (you can skip this and use the default keystore instead)

```sh
$ scripts/keystore.sh
# The script will prompt the following questions
Keystore name (e.g. mykeystore) [mykeystore]:
Keystore password (must be at least 6 characters): testpassword
Keystore alias (e.g. key0) [key0]:
Distinguished Name (e.g. CN=Android,O=Test,C=US) [CN=Luniume,O=Luniume]:
Creating PKCS keystore...
```

2. Edit `config.json` as you like

```json
{
    # These are the apps that the bulk_patch.sh script will automatically patch
    "bulk_patch_apps": [
        "instagram",
        "youtube",
        "ytmusic"
    ],
    # Change if you want to use your custom keystore
    "keystore": {
        "name": "luniume",
        "alias": "key0"
    }
}
```

3. Run the patch script.

```sh
$ ./bulk_patch.sh
```

To use with a custom keystore, make sure you changed your keystore configuration in `config.json`, then run:
```sh
$ ./bulk_patch.sh --use-custom-keystore --ks-password=<yourkeystorepassword>
```

You can also test with the default test keystore, the password is `luniumedefaultpassword`.
It is suggested you make your own keystore.

All the patched apks will be in the `patched` directory

## Customizing the patches:

By default, luniume uses the patches found in [patches.json](patches/patches.json).

You can change revanced and lspatch patches there.
For revanced, modify the config as following:

```json
{
    "revanced": {
        "patches": {
            "url": "https://github.com/ReVanced/revanced-patches",
            "version": "latest"
        },
        "patches-rvx": {
            "url": "https://github.com/inotia00/revanced-patches",
            "version": "latest"
        },
        # Make sure the patches are in the release tab
        "myrevanced-patches": {
            "url": "https://github.com/<username>/revanced-patches",
            "version": "latest"
        }
    },
...
```

Then download them automatically with the following command:
```sh
$ scripts/download_patches.sh
```

Or manually add them under [here](patches/revanced/) if you cannot get them from github releases.

--- 
For LSPatch, add patches to `patches.json` only if you're embedding the patch.
Example:

```json
    "lspatch": {
        "instaeclipse": {
            "version": "v0.4.3",
            "url": "https://github.com/ReSo7200/InstaEclipse/releases/download/v0.4.3/InstaEclipse.0.4.3.apk",
            "hash": "sha256-X6N48rz5WX8ikXZcVwyT1YUjPtctWCo+Tb5/2oxBlp4="
        }
    },
```

The hash is a sha256 in SRI format.

---

Now, we can make/change an app by creating/editing the patch file under [apps](/apps/)

Example:
```
{
    "app_name": "Instagram",
    "package_name": "com.instagram.android",
    "source": "apkmirror", # Available sources are currently apkmirror, github
    "download_url": "https://www.apkmirror.com/apk/instagram/instagram-instagram/instagram",
    "version": "394.0.0.38.81",
    "patch_method": "lspatch", # either lspatch or revanced
    "embedded": false, # lspatch only
    "split": true, # If the downloaded apk is split (xapk or apkm), set this to true
    "patches": []
}
```

The availble options are the following

| Option        | Type        | Description                                                    |
| ------------- | ----------- | -------------------------------------------------------------- |
| app_name      | string      | Name of the application                           |
| package_name  | string      | Package name (e.g. com.instagram.android)                             |
| source        | string      | Either `github` or `apkmirror`                                 |
| download_url  | string      | Url of the apk. (APKMirror only)                               |
| asset_name    | string      | Name of the file to download on `github` (wildcards are allowed) |
| repo          | string      | Repository, e.g. owner/repo                                    |
| version       | string      | Version number or tag of the release                           |
| patch_method  | string      | Method used to patch the apk (either `revanced` or `lspatch`)  |
| split         | boolean     | If the apk is a split one (xapk or apkm). Will automatically merge into a single apk.         |
| embedded      | boolean     | Whether to inject the patch directly into the apk or allow managing through LSPatch Manager (LSPatch only)              |
| rvps          | string array| Which revanced patches under [patches/revanced](/patches/revanced/) to use for patching (Revanced only) |
| exclusive_patches | boolean | Whether to use default patches, or only use the patches declared below in patches | 
| patches       | string array| Patches to apply by name. For LSPatch, use the name in `patches.json`. For Revanced, use the patch name.                    |


### Changing patches options (Revanced)

You can configure revanced patches the following way:

```json
# youtube.json
{
    ..
    "patches": [
        "Force original audio",
        "Video quality",
        {
            "name": "Theme",
            "options": {
                "Dark theme background color": "#00000000",
                "Light theme background color": "#FFFFFFFF"
            }
        },
        "SponsorBlock"
    ]
}
```


# License

Luniume is licensed under the GNU Affero General Public License v3 (AGPL-3.0), see [LICENSE](LICENSE) for details.