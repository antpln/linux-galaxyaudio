# linux-galaxyaudio

[![Build](https://github.com/antpln/linux-galaxyaudio/actions/workflows/build.yml/badge.svg)](https://github.com/antpln/linux-galaxyaudio/actions/workflows/build.yml)
[![AUR](https://img.shields.io/aur/version/linux-galaxyaudio)](https://aur.archlinux.org/packages/linux-galaxyaudio)

Arch Linux kernel with sound support for Samsung Galaxy Book 4/5 (and some GB2).

Based on [thesofproject/linux#5616](https://github.com/thesofproject/linux/pull/5616).

## Install

### From AUR

```bash
yay -S linux-galaxyaudio
```

### From GitHub Releases

Download the latest `.pkg.tar.zst` from [Releases](https://github.com/antpln/linux-galaxyaudio/releases) and install:

```bash
sudo pacman -U linux-galaxyaudio-*.pkg.tar.zst
```

## Supported Models

| Model | Status |
|-------|--------|
| Galaxy Book 4 Pro | ✅ |
| Galaxy Book 4 Pro 360 | ✅ |
| Galaxy Book 4 Ultra | ✅ |
| Galaxy Book 5 Pro 360 | ✅ |
| Galaxy Book 2 Pro SE | ✅ |

## Build Locally

```bash
git clone https://github.com/antpln/linux-galaxyaudio.git
cd linux-galaxyaudio
makepkg -si
```

## How It Works

1. GitHub Actions checks daily for new Arch Linux kernel versions
2. If new version found: updates PKGBUILD, builds, and creates a release
3. AUR is automatically updated on each release

## License

GPL-2.0
