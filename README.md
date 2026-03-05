# Monaspace Frankenstein

A Frankenstein font family that combines different [Monaspace](https://monaspace.githubnext.com/) font families into a single unified family called **Monaspace Frankenstein**. Each style variant (Regular, Bold, Italic, etc.) is actually a different Monaspace family, allowing you to get multiple distinct typefaces through standard font style selection.

## Variant Mapping

All variants have `fsSelection` bit 7 (`USE_TYPO_METRICS`) set.

| Variant              | fsSelection Bits | Source Font          | Weight | usWeightClass |
|----------------------|------------------|----------------------|--------|---------------|
| Regular              | 6                | Monaspace Xenon      | 400    | 400           |
| Bold                 | 5                | Monaspace Krypton    | 400    | 700           |
| Italic               | 0                | Monaspace Radon      | 400    | 400           |
| Underlined           | 1                | Monaspace Neon       | 400    | 400           |
| Bold Italic          | 5, 0             | Monaspace Argon      | 400    | 700           |
| Bold Underlined      | 5, 1             | Monaspace Xenon      | 600    | 700           |
| Italic Underlined    | 0, 1             | Monaspace Krypton    | 600    | 400           |
| Bold Italic Underlined | 5, 0, 1        | Monaspace Radon      | 600    | 700           |

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/)

## Source Fonts

Place these Monaspace variable font TTF files in the project root:

- `Monaspace Argon Var.ttf`
- `Monaspace Krypton Var.ttf`
- `Monaspace Neon Var.ttf`
- `Monaspace Radon Var.ttf`
- `Monaspace Xenon Var.ttf`

These are variable fonts with axes for weight (200-800), width (100-125), and slant (-11 to 0). The build script instantiates them at specific weight values with width=100 and slant=0 to produce static fonts.

## Building

```sh
uv run python3 build_frankenstein.py
```

This produces 8 static TTF files and corresponding TTX files for inspection:

```
MonaspaceFrankenstein-Regular.ttf
MonaspaceFrankenstein-Bold.ttf
MonaspaceFrankenstein-Italic.ttf
MonaspaceFrankenstein-Underlined.ttf
MonaspaceFrankenstein-BoldItalic.ttf
MonaspaceFrankenstein-BoldUnderlined.ttf
MonaspaceFrankenstein-ItalicUnderlined.ttf
MonaspaceFrankenstein-BoldItalicUnderlined.ttf
```

## What the Build Does

1. Loads each source variable font (TTF)
2. Pins all variation axes (`wght`, `wdth`, `slnt`) using `fontTools.varLib.instancer` to create a static instance
3. Removes leftover variable font tables (`fvar`, `gvar`, `avar`, `STAT`, etc.)
4. Sets `OS/2.fsSelection`, `OS/2.usWeightClass`, `head.macStyle`, and `post.italicAngle`
5. Rewrites the `name` table (family name, subfamily, PostScript name, etc.) to "Monaspace Frankenstein"
6. Saves the result as a static TTF and a TTX (XML) for inspection

## Regenerating TTX from TTF

To convert the source variable fonts to TTX for manual inspection:

```sh
uvx fonttools ttx *.ttf
```
