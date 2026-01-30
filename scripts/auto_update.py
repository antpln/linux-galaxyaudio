import os
import re
import sys
import json
import urllib.request
import subprocess

def get_arch_version():
    try:
        url = "https://archlinux.org/packages/core/x86_64/linux/json"
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            return data['pkgver']
    except Exception as e:
        print(f"Error fetching Arch version: {e}")
        sys.exit(1)

def get_current_version(pkgbuild_path):
    with open(pkgbuild_path, 'r') as f:
        content = f.read()
        match = re.search(r'^pkgver=(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1)
    return None

def update_pkgbuild(path, new_ver):
    with open(path, 'r') as f:
        content = f.read()
    
    # Update pkgver
    content = re.sub(r'^pkgver=.*$', f'pkgver={new_ver}', content, flags=re.MULTILINE)
    # Reset pkgrel to 1
    content = re.sub(r'^pkgrel=.*$', 'pkgrel=1', content, flags=re.MULTILINE)
    
    with open(path, 'w') as f:
        f.write(content)

def main():
    arch_ver = get_arch_version()
    current_ver = get_current_version('PKGBUILD')
    
    print(f"Arch Version: {arch_ver}")
    print(f"Current Version: {current_ver}")
    
    # Simple semantic version comparison could be better but string equality is a safe start
    if arch_ver != current_ver:
        print(f"Update detected: {current_ver} -> {arch_ver}")
        
        # Update Main PKGBUILD
        update_pkgbuild('PKGBUILD', arch_ver)
        
        # Update Bin PKGBUILD
        update_pkgbuild('linux-galaxyaudio-bin/PKGBUILD', arch_ver)
        
        # Run generate-patch.sh to ensure patch is up to date (it downloads from URL)
        print("Regenerating patch...")
        subprocess.run(['bash', 'scripts/generate-patch.sh'], check=True)
        
        # Update checksums for Main PKGBUILD
        # Note: This requires updpkgsums to be installed (pacman-contrib)
        print("Updating checksums...")
        try:
            subprocess.run(['updpkgsums'], check=True)
        except subprocess.CalledProcessError:
            print("Error running updpkgsums. Make sure pacman-contrib is installed.")
            sys.exit(1)
            
        # Set output for GitHub Actions
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write(f"updated=true\n")
                f.write(f"version={arch_ver}\n")
    else:
        print("No update needed.")
        if 'GITHUB_OUTPUT' in os.environ:
            with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
                f.write("updated=false\n")

if __name__ == "__main__":
    main()
