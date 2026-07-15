# Maintainer: Your Name <your@email.com>
pkgbase=linux-galaxyaudio
pkgname=(linux-galaxyaudio linux-galaxyaudio-headers)
_pkgname=linux
pkgver=6.19.12
pkgrel=1
pkgdesc='Linux kernel for Samsung Galaxy Book 4 with MAX98390 sound support'
arch=(x86_64)
url="https://github.com/thesofproject/linux/pull/5616"
license=('GPL2')
install=linux-galaxyaudio.install
makedepends=(
  bc kmod libelf cpio perl tar xz
  python
  # standard kernel build deps
  git
)
options=('!strip')

# Kernel.org directory is based on the major version (v6.x, v7.x, ...)
_major="${pkgver%%.*}"

source=(
  "https://cdn.kernel.org/pub/linux/kernel/v${_major}.x/linux-${pkgver}.tar.xz"
  "config"
  "patch_kernel.py"
  "max98390_hda.c"
  "max98390_hda.h"
  "max98390_hda_filters.c"
  "max98390_hda_filters.h"
  "max98390_hda_i2c.c"
)
sha256sums=('ce5c4f1205f9729286b569b037649591555f31ca1e03cc504bd3b70b8e58a8d5'
            'ea0faab7ec127f8510edbb7934fe3060c4a5617c23900e7f049b539c3db579d9'
            '31fc543af1d915590e8b592e9e54f2cabc9a73c5bf0a566f9fe29b4632b001d6'
            '687368e847ec67e43a7de2f48a63b5676e53351c73059a00af124e2bce85ed54'
            '33b223391460e73c521e193b8f877defcd5cd40a71fde046608fac4e67fba2f3'
            'bf075335dd48932a45a5ecffab066fb0d863b8190af678d0d09ff5b3d795859b'
            '462f22b8ae4a41bd77e6956f9b110bb745f77bbc4078961fb46b79ae0bca51f9'
            '8421cd7a024f141eb8910c7689b80417b777d878787f648790a18372651c7467')

prepare() {
  cd "${_pkgname}-${pkgver}"

  echo "Setting version..."
  # scripts/setlocalversion --save-scmversion
  echo "-galaxyaudio" > localversion.10-pkgname

  echo "Applying config..."
  cp "${srcdir}/config" .config

  # Check if user wants to build with only currently loaded modules (huge speedup)
  if [ -f "${srcdir}/localmodconfig" ]; then
    echo "Applying localmodconfig..."
    cp "${srcdir}/localmodconfig" .config
    make localmodconfig
  fi
  
  echo "Applying smart kernel patches..."
  python "${srcdir}/patch_kernel.py" "${srcdir}/${_pkgname}-${pkgver}"

  echo "Copying side-codec source files..."
  mkdir -p "sound/hda/codecs/side-codecs"
  cp "${srcdir}"/max98390_hda* "sound/hda/codecs/side-codecs/"

  echo "Enabling Galaxy Book 4 Sound Configs..."
  scripts/config --module CONFIG_SND_SOC_MAX98390
  scripts/config --module CONFIG_SND_HDA_SCODEC_MAX98390
  scripts/config --module CONFIG_SND_HDA_SCODEC_MAX98390_I2C
  scripts/config --enable CONFIG_SND_HDA_CODEC_REALTEK

  echo "Disabling Debug Info for faster build..."
  scripts/config --disable CONFIG_DEBUG_INFO
  scripts/config --disable CONFIG_DEBUG_INFO_BTF
  scripts/config --disable CONFIG_DEBUG_INFO_DWARF4
  scripts/config --disable CONFIG_DEBUG_INFO_DWARF5
  scripts/config --disable CONFIG_PAHOLE_HAS_SPLIT_BTF
  scripts/config --disable CONFIG_DEBUG_INFO_BTF_MODULES
  scripts/config --disable CONFIG_SLUB_DEBUG
  scripts/config --disable CONFIG_PM_DEBUG
  # Ensure dependencies are met (I2C, etc normally are)

  make olddefconfig
  
  make -s kernelrelease > version
  echo "Prepared $(cat version)"
}

build() {
  cd "${_pkgname}-${pkgver}"
  make all
}

package_linux-galaxyaudio() {
  pkgdesc="The ${pkgdesc} kernel and modules"
  depends=(coreutils kmod initramfs)
  optdepends=('linux-firmware: firmware images needed for some devices')
  provides=(linux)


  cd "${_pkgname}-${pkgver}"
  
  local kernver="$(<version)"
  local modulesdir="${pkgdir}/usr/lib/modules/${kernver}"

  echo "Installing boot image..."
  # systemd-boot / ucode layout or standard /boot?
  # Arch standard: /boot/vmlinuz-linux
  install -Dm644 "$(make -s image_name)" "${pkgdir}/boot/vmlinuz-${pkgbase}"
  
  echo "Installing modules..."
  make INSTALL_MOD_PATH="${pkgdir}/usr" INSTALL_MOD_STRIP=1 modules_install

  # remove build and source links
  rm -f "${modulesdir}"/{source,build}
}

package_linux-galaxyaudio-headers() {
  pkgdesc="Headers and scripts for building modules for the ${pkgdesc} kernel"
  depends=(pahole)

  cd "${_pkgname}-${pkgver}"
  local builddir="${pkgdir}/usr/lib/modules/$(<version)/build"

  echo "Installing build files..."
  install -Dt "${builddir}" -m644 .config Makefile Module.symvers System.map vmlinux
  install -Dt "${builddir}/kernel" -m644 kernel/Makefile
  install -Dt "${builddir}/arch/x86" -m644 arch/x86/Makefile
  cp -t "${builddir}" -a scripts

  # Required headers
  cp -t "${builddir}" -a include
  cp -t "${builddir}/arch/x86" -a arch/x86/include
  install -Dt "${builddir}/arch/x86/kernel" -m644 arch/x86/kernel/asm-offsets.s

  # .objtool
  install -Dt "${builddir}/tools/objtool" tools/objtool/objtool

  # Clean up
  find "${builddir}" -name '.*' -delete
  
  # Strip scripts
  find "${builddir}/scripts" -type f -perm -u+w -print0 | xargs -0 strip 2>/dev/null || true
}
