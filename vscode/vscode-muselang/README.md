# MuseLang 3 VS Code Support

This folder contains a lightweight VS Code language extension for MuseLang 3.

It provides:

- file association for `.muse` and `.muselang`;
- TextMate syntax highlighting for the implemented MuseLang 3 profile;
- snippets for common V3 room, object, goal, verb, array, and loop patterns;
- live lint diagnostics powered by the MuseLang 3 CLI.

## Loading It In VS Code

The simplest approach is to load the folder as an unpacked extension:

1. Open VS Code.
2. Run `Developer: Install Extension from Location...`.
3. Select this `vscode/vscode-muselang` folder from the author kit.

After that, `.muse` files should open with MuseLang 3 highlighting.

## Linting

The linter runs:

```text
python -m muselang.cli lint <temporary-source-file>
```

When this extension is used from the author kit, it first looks for `.venv`
inside the opened workspace. That means editor linting normally works after
running the kit installer. You can override the Python executable with the
`muselang.pythonPath` setting.

When this extension is used from the development repository, it can also lint
against `muse-dev/MuseLang/V3/src` directly.

## Notes

The grammar is intentionally lightweight. It helps authors read and edit V3
source, but the command-line linter remains the authority for indentation,
syntax, name resolution, and semantic validation.
