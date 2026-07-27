# MuseLang V1 VSCode Support

This folder contains a minimal VSCode language extension for MuseLang V1.

It provides:

- file association for `.muse` and `.muselang`
- TextMate syntax highlighting
- basic editor settings such as `#` comments and quote pairing
- live lint diagnostics powered by the MuseLang V1 CLI

## Loading it in VSCode

The simplest approach is to load the folder as an unpacked extension:

1. Open VSCode.
2. Run `Developer: Install Extension from Location...`.
3. Select this `V1/vscode-muselang` folder.

After that, `.muse` files should open with MuseLang V1 highlighting.

The linter expects access to a Python executable and the MuseLang V1 source tree in this repository. In this workspace it finds that automatically when you open the repo root.

## Packaging as `.vsix`

A `.vsix` file is the packaged form of a VSCode extension. It is just the extension plus metadata zipped into a distributable archive that VSCode can install.

Typical flow:

1. develop the extension in a folder like this one
2. package it into a `.vsix`
3. install that `.vsix` into VSCode or share it with other authors

With the standard VSCode tooling, that is usually done with `vsce package` or `npx @vscode/vsce package`.

## Notes

The grammar is intentionally lightweight. It highlights the core MuseLang V1 surface syntax, but it does not try to fully validate indentation structure or semantic rules.
