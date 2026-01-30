#!/bin/bash
set -e

PATCH_FILE="max98390-sound.patch"
UPSTREAM_URL="https://github.com/thesofproject/linux/pull/5616.diff"

echo "Downloading patch from PR #5616..."
# Download to temp file first
curl -L "$UPSTREAM_URL" -o "${PATCH_FILE}.tmp"

# Ensure the downloaded patch ends with a newline
if [ -n "$(tail -c 1 "${PATCH_FILE}.tmp")" ]; then
    echo "" >> "${PATCH_FILE}.tmp"
fi

echo "Appending Galaxy Book 2 Pro SE (2-amp) quirk..."
cat << 'EOF' >> "${PATCH_FILE}.tmp"
diff --git a/sound/hda/codecs/realtek/alc269.c b/sound/hda/codecs/realtek/alc269.c
index c44a774672a737..d55b885783b848 100644
--- a/sound/hda/codecs/realtek/alc269.c
+++ b/sound/hda/codecs/realtek/alc269.c
@@ -2994,6 +2994,11 @@ static void max98390_fixup_i2c_four(struct hda_codec *codec, const struct hda_fixup *fix, int action)
 	comp_generic_fixup(codec, action, "i2c", "MAX98390", "-%s:00-max98390-hda.%d", 4);
 }
 
+static void max98390_fixup_i2c_two(struct hda_codec *codec, const struct hda_fixup *fix, int action)
+{
+	comp_generic_fixup(codec, action, "i2c", "MAX98390", "-%s:00-max98390-hda.%d", 2);
+}
+
 static void alc287_fixup_legion_16achg6_speakers(struct hda_codec *cdc, const struct hda_fixup *fix,
 						 int action)
 {
@@ -3684,6 +3689,7 @@ enum {
 	ALC298_FIXUP_SAMSUNG_AMP_V2_2_AMPS,
 	ALC298_FIXUP_SAMSUNG_AMP_V2_4_AMPS,
 	ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS,
+	ALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS,
 	ALC298_FIXUP_SAMSUNG_HEADPHONE_VERY_QUIET,
 	ALC256_FIXUP_SAMSUNG_HEADPHONE_VERY_QUIET,
 	ALC295_FIXUP_ASUS_MIC_NO_PRESENCE,
@@ -5364,6 +5370,10 @@ static const struct hda_fixup alc269_fixups[] = {
 		.type = HDA_FIXUP_FUNC,
 		.v.func = max98390_fixup_i2c_four
 	},
+	[ALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS] = {
+		.type = HDA_FIXUP_FUNC,
+		.v.func = max98390_fixup_i2c_two,
+		.chained = true, 
+		.chain_id = ALC269_FIXUP_HEADSET_MIC,
+	},
 	[ALC298_FIXUP_SAMSUNG_HEADPHONE_VERY_QUIET] = {
 		.type = HDA_FIXUP_VERBS,
 		.v.verbs = (const struct hda_verb[]) {
@@ -6990,6 +7000,7 @@ static const struct hda_quirk alc269_fixup_tbl[] = {
 	SND_PCI_QUIRK(0x144d, 0xc892, "Samsung Galaxy Book4 Pro 360 (NP960QGK)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),
 	SND_PCI_QUIRK(0x144d, 0xc1d8, "Samsung Galaxy Book4 Ultra (NP960XGL)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),
 	SND_PCI_QUIRK(0x144d, 0xc1da, "Samsung Galaxy Book5 Pro 360 (NP960QHA)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),
+	SND_PCI_QUIRK(0x144d, 0xc896, "Samsung Galaxy Book 2 Pro SE (NP950XGK)", ALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS),
 	SND_PCI_QUIRK(0x144d, 0xc868, "Samsung Galaxy Book2 Pro (NP930XED)", ALC298_FIXUP_SAMSUNG_AMP),
 	SND_PCI_QUIRK(0x144d, 0xc870, "Samsung Galaxy Book2 Pro (NP950XED)", ALC298_FIXUP_SAMSUNG_AMP_V2_2_AMPS),
 	SND_PCI_QUIRK(0x144d, 0xc872, "Samsung Galaxy Book2 Pro (NP950XEE)", ALC298_FIXUP_SAMSUNG_AMP_V2_2_AMPS),
EOF

mv "${PATCH_FILE}.tmp" "$PATCH_FILE"
echo "Done. Patch generated at $PATCH_FILE"
