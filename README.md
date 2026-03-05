# Monaspace Frankenstein

A Frankenstein font family that combines different [Monaspace](https://monaspace.githubnext.com/) font families into a single unified family called **Monaspace Frankenstein**. Each style variant (Regular, Bold, Italic, Bold Italic) is actually a different Monaspace family, allowing you to get multiple distinct typefaces through standard font style selection.

## Why?

Editors like VS Code and Cursor let you assign `fontStyle` per syntax scope via `editor.tokenColorCustomizations`. By mapping each style to a different Monaspace family, you can visually distinguish keywords, comments, functions, and regular code — each rendered in a completely different typeface.

## Variant Mapping

All variants have `fsSelection` bit 7 (`USE_TYPO_METRICS`) set.

| fontStyle         | Font Variant | Source Font       | Instance | usWeightClass |
| ----------------- | ------------ | ----------------- | -------- | ------------- |
| _(regular)_       | Regular      | Monaspace Xenon   | 400      | 400           |
| **bold**          | Bold         | Monaspace Krypton | 400      | 700           |
| _italic_          | Italic       | Monaspace Radon   | 400      | 400           |
| **_bold italic_** | Bold Italic  | Monaspace Argon   | 400      | 700           |

The build also produces Underlined variants (using `fsSelection` bit 1) for completeness, but VS Code/Cursor render `underline` as a text decoration rather than selecting a font variant, so these are not usable for font differentiation in practice.

### Additional variants (not usable in VS Code/Cursor)

| Variant                | Source Font       | Instance | usWeightClass |
| ---------------------- | ----------------- | -------- | ------------- |
| Underlined             | Monaspace Neon    | 400      | 400           |
| Bold Underlined        | Monaspace Xenon   | 600      | 700           |
| Italic Underlined      | Monaspace Krypton | 600      | 400           |
| Bold Italic Underlined | Monaspace Radon   | 600      | 700           |

## Installation

Download and install the TTF files from this repo:

- `MonaspaceFrankenstein-Regular.ttf`
- `MonaspaceFrankenstein-Bold.ttf`
- `MonaspaceFrankenstein-Italic.ttf`
- `MonaspaceFrankenstein-BoldItalic.ttf`

The additional Underlined variants are also included if your application can make use of them.

## Building from Source

To rebuild the fonts yourself, you need [uv](https://docs.astral.sh/uv/) and the [Monaspace](https://monaspace.githubnext.com/) variable font TTFs placed in the project root:

```text
Monaspace Argon Var.ttf
Monaspace Krypton Var.ttf
Monaspace Neon Var.ttf
Monaspace Radon Var.ttf
Monaspace Xenon Var.ttf
```

Then run:

```sh
uv run build_frankenstein.py
```

## VS Code / Cursor Setup

Set the editor font family:

```json
"editor.fontFamily": "'Monaspace Frankenstein'"
```

Then add `textMateRules` to assign different typefaces to different syntax scopes:

```json
"editor.tokenColorCustomizations": {
  "textMateRules": [
    {
      "name": "Comments → Radon (italic)",
      "scope": "comment, punctuation.definition.comment",
      "settings": { "fontStyle": "italic" }
    },
    {
      "name": "Keywords → Krypton (bold)",
      "scope": "keyword, storage.type, storage.modifier, keyword.operator.expression, keyword.operator.new, variable.language.this, variable.language.self, variable.language.super",
      "settings": { "fontStyle": "bold" }
    },
    {
      "name": "Functions → Argon (bold italic)",
      "scope": "entity.name.function, support.function, meta.function-call entity.name.function, support.method",
      "settings": { "fontStyle": "bold italic" }
    }
  ]
}
```

Everything not matched by a rule renders in the default Regular style (Xenon).

## How the Build Works

1. Loads each source variable font (TTF)
2. Pins all variation axes (`wght`, `wdth`, `slnt`) using `fontTools.varLib.instancer` to create a static instance
3. Removes leftover variable font tables (`fvar`, `gvar`, `avar`, `STAT`, etc.)
4. Sets `OS/2.fsSelection`, `OS/2.usWeightClass`, `head.macStyle`, and `post.italicAngle`
5. Rewrites the `name` table (family name, subfamily, PostScript name, etc.) to "Monaspace Frankenstein"
6. Saves the result as a static TTF and a TTX (XML) for inspection
