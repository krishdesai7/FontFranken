#!/usr/bin/env python3
"""Build Monaspace Frankenstein font family from Monaspace variable fonts.

Creates 8 static font files by instantiating specific weights from different
Monaspace font families, rebranding them all as "Monaspace Frankenstein".
"""

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathlib import Path

FAMILY_NAME = "Monaspace Frankenstein"
DIR = Path(__file__).parent

# fsSelection bit definitions
BIT_ITALIC = 0
BIT_UNDERSCORE = 1
BIT_BOLD = 5
BIT_REGULAR = 6
BIT_USE_TYPO_METRICS = 7

# macStyle bit definitions
MAC_BOLD = 0
MAC_ITALIC = 1
MAC_UNDERLINE = 2

# Variant definitions: (source_font, weight_value, subfamily_name, fsSelection_bits, mac_style_bits, weight_class)
VARIANTS = [
    # 1. Regular = Xenon Regular
    ("Monaspace Xenon Var.ttf", 400, "Regular",
     [BIT_REGULAR, BIT_USE_TYPO_METRICS], [], 400),
    # 2. Bold = Krypton Regular
    ("Monaspace Krypton Var.ttf", 400, "Bold",
     [BIT_BOLD, BIT_USE_TYPO_METRICS], [MAC_BOLD], 700),
    # 3. Italic = Radon Regular
    ("Monaspace Radon Var.ttf", 400, "Italic",
     [BIT_ITALIC, BIT_USE_TYPO_METRICS], [MAC_ITALIC], 400),
    # 4. Underlined = Neon Regular  (fsSelection bit 1)
    ("Monaspace Neon Var.ttf", 400, "Underlined",
     [BIT_UNDERSCORE, BIT_USE_TYPO_METRICS], [MAC_UNDERLINE], 400),
    # 5. Bold Italic = Argon Regular
    ("Monaspace Argon Var.ttf", 400, "Bold Italic",
     [BIT_BOLD, BIT_ITALIC, BIT_USE_TYPO_METRICS], [MAC_BOLD, MAC_ITALIC], 700),
    # 6. Bold Underlined = Xenon SemiBold
    ("Monaspace Xenon Var.ttf", 600, "Bold Underlined",
     [BIT_BOLD, BIT_UNDERSCORE, BIT_USE_TYPO_METRICS], [MAC_BOLD, MAC_UNDERLINE], 700),
    # 7. Italic Underlined = Krypton SemiBold
    ("Monaspace Krypton Var.ttf", 600, "Italic Underlined",
     [BIT_ITALIC, BIT_UNDERSCORE, BIT_USE_TYPO_METRICS], [MAC_ITALIC, MAC_UNDERLINE], 400),
    # 8. Bold Italic Underlined = Radon SemiBold
    ("Monaspace Radon Var.ttf", 600, "Bold Italic Underlined",
     [BIT_BOLD, BIT_ITALIC, BIT_UNDERSCORE, BIT_USE_TYPO_METRICS],
     [MAC_BOLD, MAC_ITALIC, MAC_UNDERLINE], 700),
]


def bits_to_value(bits):
    """Convert a list of bit positions to an integer value."""
    val = 0
    for b in bits:
        val |= (1 << b)
    return val


def set_name_record(name_table, name_id, value, platform_ids=None):
    """Set a name record across all platforms, or specific ones."""
    if platform_ids is None:
        # Update all existing records with this nameID
        for record in name_table.names:
            if record.nameID == name_id:
                record.string = value
        return

    for plat_id, enc_id, lang_id in platform_ids:
        name_table.setName(value, name_id, plat_id, enc_id, lang_id)


def update_name_table(font, subfamily_name):
    """Update the name table for the Frankenstein family."""
    name = font["name"]

    ps_subfamily = subfamily_name.replace(" ", "")
    ps_name = f"MonaspaceFrankenstein-{ps_subfamily}"
    full_name = f"{FAMILY_NAME} {subfamily_name}"

    # Collect all platform/encoding/language combos present in the font
    platforms = set()
    for record in name.names:
        platforms.add((record.platformID, record.platEncID, record.langID))

    for plat_id, enc_id, lang_id in platforms:
        # nameID 1: Font Family name
        name.setName(FAMILY_NAME, 1, plat_id, enc_id, lang_id)
        # nameID 2: Font Subfamily name
        name.setName(subfamily_name, 2, plat_id, enc_id, lang_id)
        # nameID 4: Full font name
        name.setName(full_name, 4, plat_id, enc_id, lang_id)
        # nameID 6: PostScript name
        name.setName(ps_name, 6, plat_id, enc_id, lang_id)
        # nameID 16: Typographic Family name (preferred family)
        name.setName(FAMILY_NAME, 16, plat_id, enc_id, lang_id)
        # nameID 17: Typographic Subfamily name (preferred subfamily)
        name.setName(subfamily_name, 17, plat_id, enc_id, lang_id)

    # Remove nameIDs that reference the original font identity
    # nameID 3: Unique font identifier - rebuild it
    for plat_id, enc_id, lang_id in platforms:
        name.setName(ps_name, 3, plat_id, enc_id, lang_id)

    # Remove any stale version-specific or trademark records that reference old names
    # Keep nameID 0 (copyright), 5 (version), 7 (trademark), etc. as-is
    # but update nameID 10 (description) and 11 (vendor URL) if present


def build_variant(source_file, weight, subfamily, fs_bits, mac_bits, weight_class):
    """Build one variant of the Frankenstein font."""
    print(f"  Building {subfamily} from {source_file} @ wght={weight}...")

    font = TTFont(DIR / source_file)

    # Instantiate: pin weight, width=100, slant=0 to create a static font
    instantiateVariableFont(
        font, {"wght": weight, "wdth": 100, "slnt": 0},
        inplace=True, overlap=OverlapMode.KEEP_AND_SET_FLAGS,
    )

    # Remove any leftover variable font tables
    for tag in ["fvar", "gvar", "avar", "cvar", "STAT", "HVAR", "VVAR", "MVAR"]:
        if tag in font:
            del font[tag]
    # Clean GDEF if it has no useful data after instantiation
    if "GDEF" in font:
        gdef = font["GDEF"].table
        has_data = any([
            getattr(gdef, "GlyphClassDef", None),
            getattr(gdef, "AttachList", None),
            getattr(gdef, "LigCaretList", None),
            getattr(gdef, "MarkAttachClassDef", None),
            getattr(gdef, "MarkGlyphSetsDef", None),
        ])
        if not has_data:
            del font["GDEF"]

    # Update OS/2 table
    os2 = font["OS/2"]
    os2.fsSelection = bits_to_value(fs_bits)
    os2.usWeightClass = weight_class

    # Update head table
    head = font["head"]
    head.macStyle = bits_to_value(mac_bits)

    # Update name table
    update_name_table(font, subfamily)

    # Set italic angle for italic variants
    post = font["post"]
    if BIT_ITALIC in fs_bits:
        post.italicAngle = -12.0
    else:
        post.italicAngle = 0.0

    # Output filename
    safe_subfamily = subfamily.replace(" ", "")
    out_name = f"MonaspaceFrankenstein-{safe_subfamily}.ttf"
    out_path = DIR / out_name
    font.save(out_path)
    print(f"    -> {out_name}")

    # Also generate TTX for inspection
    font.saveXML(out_path.with_suffix(".ttx"))

    font.close()
    return out_name


def main():
    print(f"Building {FAMILY_NAME} font family...")
    print()

    outputs = []
    for source, weight, subfamily, fs_bits, mac_bits, wc in VARIANTS:
        out = build_variant(source, weight, subfamily, fs_bits, mac_bits, wc)
        outputs.append(out)

    print()
    print("Done! Generated files:")
    for f in outputs:
        print(f"  {f}")


if __name__ == "__main__":
    main()
