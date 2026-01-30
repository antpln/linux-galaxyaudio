#!/bin/bash
set -e
echo "Downloading patch from PR #5616..."
curl -L https://github.com/thesofproject/linux/pull/5616.diff -o max98390-sound.patch

# Commented out appending to isolate build failure
# echo "Appending Galaxy Book 2 Pro SE (2-amp) quirk..."
# cat << 'EOF' >> max98390-sound.patch
# diff --git a/sound/hda/codecs/realtek/alc269.c b/sound/hda/codecs/realtek/alc269.c
# ...
# EOF

echo "Done."
