# linux-galaxyaudio-bin

This package installs the pre-compiled `linux-galaxyaudio` kernel from the GitHub Releases of the [antpln/linux-galaxyaudio](https://github.com/antpln/linux-galaxyaudio) repository.

## Usage

1.  Enter this directory:
    ```bash
    cd linux-galaxyaudio-bin
    ```

2.  (Optional) Update checksums:
    ```bash
    updpkgsums
    ```

3.  Build and install:
    ```bash
    makepkg -si
    ```

This will download the binary packages from GitHub and install them, skipping the compilation step.
