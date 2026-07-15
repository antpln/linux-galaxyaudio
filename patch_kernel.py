#!/usr/bin/env python3
import os
import sys
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: patch_kernel.py <kernel_source_dir>")
        sys.exit(1)
    
    kernel_dir = sys.argv[1]
    print(f"Applying smart kernel patches to: {kernel_dir}")

    # 1. drivers/acpi/scan.c
    scan_path = os.path.join(kernel_dir, "drivers/acpi/scan.c")
    if os.path.exists(scan_path):
        with open(scan_path, "r") as f:
            content = f.read()
        if '{"MAX98390", }' not in content:
            # Look for a place to insert near similar serial bus audio codecs
            pattern = r'(\t+)\{"TXNW2781", \},'
            match = re.search(pattern, content)
            if match:
                indent = match.group(1)
                content = content.replace('{"TXNW2781", },', f'{indent}{{"MAX98390", }},\n{indent}{{"TXNW2781", }},')
            else:
                pattern = r'(\t+)\{"CLSA0100", \},'
                match = re.search(pattern, content)
                if match:
                    indent = match.group(1)
                    content = content.replace('{"CLSA0100", },', f'{indent}{{"MAX98390", }},\n{indent}{{"CLSA0100", }},')
            with open(scan_path, "w") as f:
                f.write(content)
            print("Successfully patched scan.c")
    else:
        print("Warning: drivers/acpi/scan.c not found")

    # 2. drivers/platform/x86/serial-multi-instantiate.c
    smi_path = os.path.join(kernel_dir, "drivers/platform/x86/serial-multi-instantiate.c")
    if os.path.exists(smi_path):
        with open(smi_path, "r") as f:
            content = f.read()
        
        if "max98390_hda" not in content:
            struct_def = """static const struct smi_node max98390_hda = {
	.instances = {
		{ "max98390-hda", IRQ_RESOURCE_NONE, 0 },
		{ "max98390-hda", IRQ_RESOURCE_NONE, 0 },
		{ "max98390-hda", IRQ_RESOURCE_NONE, 0 },
		{ "max98390-hda", IRQ_RESOURCE_NONE, 0 },
		{}
	},
	.bus_type = SMI_I2C,
};

"""
            target = "static const struct acpi_device_id smi_acpi_ids[]"
            if target in content:
                content = content.replace(target, struct_def + target)
            
            # Insert quirk mapping into smi_acpi_ids
            quirk_mapping = '\t{ "MAX98390", (unsigned long)&max98390_hda },\n'
            target_mapping = '\t{ "TXNW2781", (unsigned long)&tas2781_hda },'
            if target_mapping in content:
                content = content.replace(target_mapping, quirk_mapping + target_mapping)
            else:
                target_mapping_fallback = '\t{ "CLSA0100", (unsigned long)&cs35l41_hda },'
                if target_mapping_fallback in content:
                    content = content.replace(target_mapping_fallback, quirk_mapping + target_mapping_fallback)
            
            with open(smi_path, "w") as f:
                f.write(content)
            print("Successfully patched serial-multi-instantiate.c")
    else:
        print("Warning: drivers/platform/x86/serial-multi-instantiate.c not found")

    # 3. sound/soc/codecs/max98390.c
    max_c_path = os.path.join(kernel_dir, "sound/soc/codecs/max98390.c")
    if os.path.exists(max_c_path):
        with open(max_c_path, "r") as f:
            content = f.read()
        if "EXPORT_SYMBOL_GPL(max98390_regmap);" not in content:
            content = content.replace("static const struct regmap_config max98390_regmap =", "const struct regmap_config max98390_regmap =")
            content = content.replace(".cache_type       = REGCACHE_RBTREE,\n};", ".cache_type       = REGCACHE_RBTREE,\n};\nEXPORT_SYMBOL_GPL(max98390_regmap);")
            
            if '"MAX98390"' not in content:
                content = content.replace('{ "MX98390", 0 },', '{ "MAX98390", 0 },\n\t{ "MX98390", 0 },')
            with open(max_c_path, "w") as f:
                f.write(content)
            print("Successfully patched max98390.c")
    else:
        print("Warning: sound/soc/codecs/max98390.c not found")

    # 4. sound/soc/codecs/max98390.h
    max_h_path = os.path.join(kernel_dir, "sound/soc/codecs/max98390.h")
    if os.path.exists(max_h_path):
        with open(max_h_path, "r") as f:
            content = f.read()
        if "extern const struct regmap_config max98390_regmap;" not in content:
            # Insert before final #endif
            pos = content.rfind("#endif")
            if pos != -1:
                content = content[:pos] + "/* Exported for HDA side-codec driver */\nextern const struct regmap_config max98390_regmap;\n\n" + content[pos:]
            with open(max_h_path, "w") as f:
                f.write(content)
            print("Successfully patched max98390.h")
    else:
        print("Warning: sound/soc/codecs/max98390.h not found")

    # 5. sound/hda/codecs/side-codecs/Kconfig
    kconfig_path = os.path.join(kernel_dir, "sound/hda/codecs/side-codecs/Kconfig")
    if os.path.exists(kconfig_path):
        with open(kconfig_path, "r") as f:
            content = f.read()
        if "config SND_HDA_SCODEC_MAX98390" not in content:
            config_text = """
config SND_HDA_SCODEC_MAX98390
	tristate
	select SND_HDA_GENERIC
	select SND_HDA_SCODEC_COMPONENT

config SND_HDA_SCODEC_MAX98390_I2C
	tristate "Build MAX98390 HD-audio side codec support for I2C Bus"
	depends on I2C
	depends on ACPI
	depends on SND_SOC
	select SND_SOC_MAX98390
	select SND_HDA_SCODEC_MAX98390
	help
	  Say Y or M here to include MAX98390 I2C HD-audio side codec support
	  in snd-hda-intel driver, such as ALC298.

comment "Set to Y if you want auto-loading the side codec driver"
	depends on SND_HDA=y && SND_HDA_SCODEC_MAX98390_I2C=m
"""
            with open(kconfig_path, "a") as f:
                f.write(config_text)
            print("Successfully patched side-codecs Kconfig")
    else:
        print("Warning: sound/hda/codecs/side-codecs/Kconfig not found")

    # 6. sound/hda/codecs/side-codecs/Makefile
    makefile_path = os.path.join(kernel_dir, "sound/hda/codecs/side-codecs/Makefile")
    if os.path.exists(makefile_path):
        with open(makefile_path, "r") as f:
            content = f.read()
        if "snd-hda-scodec-max98390" not in content:
            # Insert source-file variables
            target_src = "snd-hda-scodec-tas2781-spi-y :=	tas2781_hda_spi.o"
            max_src = "\nsnd-hda-scodec-max98390-y :=\tmax98390_hda.o max98390_hda_filters.o\nsnd-hda-scodec-max98390-i2c-y := max98390_hda_i2c.o"
            if target_src in content:
                content = content.replace(target_src, target_src + max_src)
            
            # Append targets at the end
            max_objs = "\nobj-$(CONFIG_SND_HDA_SCODEC_MAX98390) += snd-hda-scodec-max98390.o\nobj-$(CONFIG_SND_HDA_SCODEC_MAX98390_I2C) += snd-hda-scodec-max98390-i2c.o\n"
            content += max_objs
            with open(makefile_path, "w") as f:
                f.write(content)
            print("Successfully patched side-codecs Makefile")
    else:
        print("Warning: sound/hda/codecs/side-codecs/Makefile not found")

    # 7. sound/hda/codecs/realtek/alc269.c
    alc_path = os.path.join(kernel_dir, "sound/hda/codecs/realtek/alc269.c")
    if os.path.exists(alc_path):
        with open(alc_path, "r") as f:
            content = f.read()
        
        # 7.1 Helper functions
        if "max98390_fixup_i2c_four" not in content:
            helpers = """static void comp_generic_fixup(struct hda_codec *cdc, int action, const char *bus,
			       const char *hid, const char *match_str, int count);

static void max98390_fixup_i2c_four(struct hda_codec *codec, const struct hda_fixup *fix, int action)
{
	comp_generic_fixup(codec, action, "i2c", "MAX98390", "-%s:00-max98390-hda.%d", 4);
}
static void max98390_fixup_i2c_two(struct hda_codec *codec, const struct hda_fixup *fix, int action) 
{
	comp_generic_fixup(codec, action, "i2c", "MAX98390", "-%s:00-max98390-hda.%d", 2); 
}

"""
            # Insert before the first static void function (global scope, after includes)
            match = re.search(r'^static void\s+\w+\(', content, re.MULTILINE)
            if match:
                span = match.span()
                content = content[:span[0]] + helpers + content[span[0]:]
            else:
                print("Warning: Could not find insertion point for helper functions in alc269.c")

        # 7.2 Enum values
        if "ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS" not in content:
            enums = "\tALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS,\n\tALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS,\n"
            target = "\tALC298_FIXUP_LG_GRAM_STYLE_14,"
            if target in content:
                content = content.replace(target, enums + target)
            else:
                target = "\tALC298_FIXUP_SAMSUNG_AMP_V2_4_AMPS,"
                if target in content:
                    content = content.replace(target, target + "\n" + enums)
                else:
                    print("Warning: Could not find insertion point for enums in alc269.c")

        # 7.3 alc269_fixups table mapping
        if "[ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS]" not in content:
            fixup_defs = """\t[ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS] = {
		.type = HDA_FIXUP_FUNC,
		.v.func = max98390_fixup_i2c_four
	},
	[ALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS] = { 
		.type = HDA_FIXUP_FUNC, 
		.v.func = max98390_fixup_i2c_two, 
		.chained = true, 
		.chain_id = ALC269_FIXUP_HEADSET_MIC, 
	},
"""
            match = re.search(r'\[ALC298_FIXUP_SAMSUNG_AMP_V2_4_AMPS\]\s*=\s*\{[^}]*\},', content)
            if not match:
                match = re.search(r'\[ALC298_FIXUP_SAMSUNG_AMP\]\s*=\s*\{[^}]*\},', content)
            if match:
                span = match.span()
                content = content[:span[1]] + "\n" + fixup_defs + content[span[1]:]
            else:
                print("Warning: Could not find insertion point for fixup definitions in alc269.c")

        # 7.4 alc269_fixup_models
        if "alc298-samsung-max98390-4-amps" not in content:
            model_defs = """\t{.id = ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS, .name = "alc298-samsung-max98390-4-amps"},
	{.id = ALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS, .name = "alc298-samsung-max98390-2-amps"},
"""
            target = '\t{.id = ALC298_FIXUP_SAMSUNG_AMP_V2_4_AMPS, .name = "alc298-samsung-amp-v2-4-amps"},'
            if target in content:
                content = content.replace(target, target + "\n" + model_defs)
            else:
                target = '\t{.id = ALC298_FIXUP_SAMSUNG_AMP, .name = "alc298-samsung-amp"},'
                if target in content:
                    content = content.replace(target, target + "\n" + model_defs)
                else:
                    print("Warning: Could not find insertion point for models in alc269.c")

        # 7.5 alc269_fixup_tbl quirks (Samsung 0x144d block)
        quirks = [
            'SND_PCI_QUIRK(0x144d, 0xca07, "Samsung Galaxy Book4 Pro 14-inch (NP940XGK)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),',
            'SND_PCI_QUIRK(0x144d, 0xc890, "Samsung Galaxy Book4 Pro 16 inch (NP960XGK)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),',
            'SND_PCI_QUIRK(0x144d, 0xc892, "Samsung Galaxy Book4 Pro 360 (NP960QGK)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),',
            'SND_PCI_QUIRK(0x144d, 0xc1d8, "Samsung Galaxy Book4 Ultra (NP960XGL)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),',
            'SND_PCI_QUIRK(0x144d, 0xc1da, "Samsung Galaxy Book5 Pro 360 (NP960QHA)", ALC298_FIXUP_SAMSUNG_MAX98390_4_AMPS),',
            'SND_PCI_QUIRK(0x144d, 0xc896, "Samsung Galaxy Book 2 Pro SE (NP950XGK)", ALC298_FIXUP_SAMSUNG_MAX98390_2_AMPS),'
        ]
        
        tbl_start = content.find("static const struct hda_quirk alc269_fixup_tbl[] = {")
        if tbl_start != -1:
            tbl_end = content.find("};", tbl_start)
            tbl_content = content[tbl_start:tbl_end]
            
            samsung_quirks = re.findall(r'SND_PCI_QUIRK\(0x144d,.*?\),', tbl_content)
            if samsung_quirks:
                # Normalize existing quirks (strip spaces)
                new_samsung_quirks = [q.strip() for q in samsung_quirks]
                
                # Check for duplicates by device ID and add if missing
                for q in quirks:
                    dev_id_match = re.search(r'0x144d,\s*(0x[0-9a-fA-F]+)', q)
                    if dev_id_match:
                        dev_id = dev_id_match.group(1).lower()
                        exists = False
                        for eq in new_samsung_quirks:
                            eq_match = re.search(r'0x144d,\s*(0x[0-9a-fA-F]+)', eq)
                            if eq_match and eq_match.group(1).lower() == dev_id:
                                exists = True
                                break
                        if not exists:
                            new_samsung_quirks.append(q)
                
                # Sort Samsung quirks by device ID
                def get_dev_id(q_str):
                    match = re.search(r'0x144d,\s*(0x[0-9a-fA-F]+)', q_str)
                    if match:
                        return int(match.group(1), 16)
                    return 0
                
                new_samsung_quirks.sort(key=get_dev_id)
                
                # Replace the block
                first_q = samsung_quirks[0]
                last_q = samsung_quirks[-1]
                
                first_idx = tbl_content.find(first_q)
                last_idx = tbl_content.find(last_q) + len(last_q)
                
                new_block = "\n".join("\t" + q for q in new_samsung_quirks)
                
                patched_tbl_content = tbl_content[:first_idx] + new_block + tbl_content[last_idx:]
                content = content[:tbl_start] + patched_tbl_content + content[tbl_end:]
            else:
                print("Warning: Could not find any existing Samsung quirks to hook into")
        else:
            print("Warning: Could not find alc269_fixup_tbl in alc269.c")
            
        with open(alc_path, "w") as f:
            f.write(content)
        print("Successfully patched alc269.c")
    else:
        print("Warning: sound/hda/codecs/realtek/alc269.c not found")

if __name__ == "__main__":
    main()
