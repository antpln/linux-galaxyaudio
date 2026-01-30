# linux-galaxybook4

Arch Linux kernel for Samsung Galaxy Book 4/5 (and some GB2) with sound support.
Based on [PR #5616](https://github.com/thesofproject/linux/pull/5616) by The SOF Project.

## Install

Add to `/etc/pacman.conf`:
```ini
[linux-galaxyaudio]
SigLevel = Optional TrustAll
Server = https://<YOUR_GITHUB_USERNAME>.github.io/linux-galaxyaudio/$arch
```

Run:
```bash
sudo pacman -Sy linux-galaxyaudio linux-galaxyaudio-headers
```

## Supported Models
- Galaxy Book 4 Pro / Pro 360 / Ultra
- Galaxy Book 5 Pro 360
- Galaxy Book 2 Pro SE (via included 2-amp quirk)
