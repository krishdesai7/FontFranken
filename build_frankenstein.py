#!./venv/bin/python
"""Build Monaspace Frankenstein font family from Monaspace variable fonts.

Creates 8 static font files by instantiating specific weights from different
Monaspace font families, uniting them under the "Monaspace Frankenstein" family name.
"""

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import _n_a_m_e, G_D_E_F_
from fontTools.varLib.instancer import instantiateVariableFont, OverlapMode
from pathlib import Path
from enum import IntFlag
from dataclasses import dataclass
from typing import Final, Literal, Protocol, cast
import numpy as np

FAMILY_NAME: Final[Literal["Monaspace Frankenstein"]] = "Monaspace Frankenstein"
ROOT: Final[Path] = Path(__file__).parent
SRC_DIR: Final[Path] = ROOT / "fonts" / "Monaspace"
TTF_DIR: Final[Path] = ROOT / "fonts" / "Frankenstein" / "TTF"
TTX_DIR: Final[Path] = ROOT / "fonts" / "Frankenstein" / "TTX"

class FsSelection(IntFlag):
    """OS/2.fsSelection flags."""
    __value__: np.ubyte
    ITALIC = 1 << 0
    UNDERSCORE = 1 << 1
    BOLD = 1 << 5
    REGULAR = 1 << 6
    USE_TYPO_METRICS = 1 << 7

class MacStyle(IntFlag):
    """head.macStyle flags."""
    __value__: np.ubyte
    BOLD = 1 << 0
    ITALIC = 1 << 1
    UNDERLINE = 1 << 2

@dataclass
class Variant:
    source_file: Final[Literal[
        "Monaspace Xenon Var.ttf",
        "Monaspace Krypton Var.ttf",
        "Monaspace Radon Var.ttf",
        "Monaspace Neon Var.ttf",
        "Monaspace Argon Var.ttf",
    ]]
    weight_value: int
    subfamily: str
    fs_mask: FsSelection
    mac_mask: MacStyle
    weight_class: int

VARIANTS: list[Variant] = [
    # 1. Regular = Xenon Regular
    Variant(
        "Monaspace Xenon Var.ttf",
        400,
        "Regular",
        FsSelection.REGULAR | FsSelection.USE_TYPO_METRICS,
        MacStyle(0),
        400,
    ),
    # 2. Bold = Krypton Regular
    Variant(
        "Monaspace Krypton Var.ttf",
        400,
        "Bold",
        FsSelection.BOLD | FsSelection.USE_TYPO_METRICS,
        MacStyle.BOLD,
        700,
    ),
    # 3. Italic = Radon Regular
    Variant(
        "Monaspace Radon Var.ttf",
        400,
        "Italic",
        FsSelection.ITALIC | FsSelection.USE_TYPO_METRICS,
        MacStyle.ITALIC,
        400,
    ),
    # 4. Underlined = Neon Regular
    Variant(
        "Monaspace Neon Var.ttf",
        400,
        "Underlined",
        FsSelection.UNDERSCORE | FsSelection.USE_TYPO_METRICS,
        MacStyle.UNDERLINE,
        400,
    ),
    # 5. Bold Italic = Argon Regular
    Variant(
        "Monaspace Argon Var.ttf",
        400,
        "Bold Italic",
        FsSelection.BOLD | FsSelection.ITALIC | FsSelection.USE_TYPO_METRICS,
        MacStyle.BOLD | MacStyle.ITALIC,
        700,
    ),
    # 6. Bold Underlined = Xenon SemiBold
    Variant(
        "Monaspace Xenon Var.ttf",
        600,
        "Bold Underlined",
        FsSelection.BOLD | FsSelection.UNDERSCORE | FsSelection.USE_TYPO_METRICS,
        MacStyle.BOLD | MacStyle.UNDERLINE,
        700,
    ),
    # 7. Italic Underlined = Krypton SemiBold
    Variant(
        "Monaspace Krypton Var.ttf",
        600,
        "Italic Underlined",
        FsSelection.ITALIC | FsSelection.UNDERSCORE | FsSelection.USE_TYPO_METRICS,
        MacStyle.ITALIC | MacStyle.UNDERLINE,
        400,
    ),
    # 8. Bold Italic Underlined = Radon SemiBold
    Variant(
        "Monaspace Radon Var.ttf",
        600,
        "Bold Italic Underlined",
        FsSelection.BOLD | FsSelection.ITALIC | FsSelection.UNDERSCORE | FsSelection.USE_TYPO_METRICS,
        MacStyle.BOLD | MacStyle.ITALIC | MacStyle.UNDERLINE,
        700,
    ),
]

def set_name_record(name_table: _n_a_m_e.table__n_a_m_e,
                    name_id: int,
                    value: str,
                    platform_ids: list[tuple[int, int, int]] | None = None) -> None:
    """Set a name record across all platforms, or specific ones."""
    if platform_ids is None:
        for record in name_table.names:
            if record.nameID == name_id:
                record.string = value
        return

    for plat_id, enc_id, lang_id in platform_ids:
        name_table.setName(value, name_id, plat_id, enc_id, lang_id)


def update_name_table(font: TTFont, subfamily_name: str) -> None:
    """Update the name table for the Frankenstein family."""
    name: _n_a_m_e.table__n_a_m_e = font["name"]

    ps_subfamily: str = subfamily_name.replace(" ", "")
    ps_name: str = f"MonaspaceFrankenstein-{ps_subfamily}"
    full_name: str = f"{FAMILY_NAME} {subfamily_name}"

    # Collect all platform/encoding/language combos present in the font
    platforms: set[tuple[int, int, int]] = set()
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
    # Rebuild nameID 3: Unique font identifier
    for plat_id, enc_id, lang_id in platforms:
        name.setName(ps_name, 3, plat_id, enc_id, lang_id)

def build_variant(v: Variant) -> str:
    """Build one variant of the Frankenstein font."""
    print(f"\tBuilding {v.subfamily} from {v.source_file} @ wght={v.weight_value}.")

    font = TTFont(SRC_DIR / v.source_file)

    # Instantiate: pin weight, width=100, slant=0 to create a static font
    instantiateVariableFont(
        font, {
            "wght": v.weight_value,
            "wdth": 100,
            "slnt": 0,
        },
        inplace=True,
        overlap=OverlapMode.KEEP_AND_SET_FLAGS,
    )

    # Remove any leftover variable font tables
    for tag in ["fvar", "gvar", "avar", "cvar", "STAT", "HVAR", "VVAR", "MVAR"]:
        if tag in font:
            del font[tag]

    # Clean GDEF if it has no useful data after instantiation
    if "GDEF" in font:
        gdef: G_D_E_F_.table_G_D_E_F_ = font["GDEF"].table
        has_data: bool = any([
            getattr(gdef, "GlyphClassDef", None),
            getattr(gdef, "AttachList", None),
            getattr(gdef, "LigCaretList", None),
            getattr(gdef, "MarkAttachClassDef", None),
            getattr(gdef, "MarkGlyphSetsDef", None),
        ])
        if not has_data:
            del font["GDEF"]

    # Update OS/2 table
    class OS2Table(Protocol):
        fsSelection: FsSelection
        usWeightClass: int
    os2: OS2Table = cast(OS2Table, font["OS/2"])
    os2.fsSelection = v.fs_mask
    os2.usWeightClass = v.weight_class

    # Update head table
    class HeadTable(Protocol):
        macStyle: MacStyle
    head: HeadTable = cast(HeadTable, font["head"])
    head.macStyle = v.mac_mask

    # Update name table
    update_name_table(font, v.subfamily)

    # Set italic angle for italic variants
    class PostTable(Protocol):
        italicAngle: float
    post: PostTable = cast(PostTable, font["post"])
    if v.fs_mask & FsSelection.ITALIC:
        post.italicAngle = -12.0
    else:
        post.italicAngle = 0.0

    # Output filename
    safe_subfamily: str = v.subfamily.replace(" ", "")
    out_name: str = f"MonaspaceFrankenstein-{safe_subfamily}.ttf"
    out_path: Path = TTF_DIR / out_name
    font.save(out_path)
    print(f"\t-> fonts/Frankenstein/TTF/{out_name}")

    # Also generate TTX for inspection
    font.saveXML(TTX_DIR / f"MonaspaceFrankenstein-{safe_subfamily}.ttx",
        writeVersion=True,
        quiet=True,
        tables=None,
        skipTables=None,
        splitTables=False,
        splitGlyphs=False,
        disassembleInstructions=False,
        bitmapGlyphDataFormat="raw",
    )

    font.close()
    return out_name


def main():
    print(f"Building {FAMILY_NAME}.")
    print()

    TTF_DIR.mkdir(parents=True, exist_ok=True)
    TTX_DIR.mkdir(parents=True, exist_ok=True)

    outputs: list[str] = [build_variant(v) for v in VARIANTS]

    print()
    print("Generated files:")
    for f in outputs:
        print(f"\t{f}")

if __name__ == "__main__":
    main()
