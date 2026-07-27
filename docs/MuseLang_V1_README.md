# MuseLang

This folder is the home of MuseLang, the author-facing language for Muse world content.

MuseLang is intended to stand on its own as the public authoring and compilation path for game content.

Current documents:

- [MuseLang_spec.md](MuseLang_spec.md)
- [MuseLang_compiler_spec.md](MuseLang_compiler_spec.md)
- [MuseLang_runtime_spec.md](MuseLang_runtime_spec.md)
- [MuseLang_author_manual.md](MuseLang_author_manual.md)

Current implementation:

- Python package under [src/muselang](src/muselang)
- CLI entry point `muselang`
- parser and validator for core MuseLang syntax
- indentation-aware lexer and token-based parser
- name resolution and versioned V1 intermediate representation
- bundle generation for compiled MuseLang content
- `test`, `dev`, and `prod` mode scaffolding

Current CLI shape:

```text
muselang runtime-install [--language 1.0] [--game-root muse-game]
muselang doctor [--language 1.0] [--game-root muse-game]
muselang test <source.muse|source-folder> [--language 1.0]
muselang dev <source.muse|source-folder> [--language 1.0] [--live-json snapshot.json] [--out bundle.json]
muselang prod <source.muse|source-folder> [--language 1.0] [--live-json snapshot.json] [--out bundle.json] [--batch-out world.ev]
```

Current status:

- `runtime-install` installs the bundled MuseLang runtime helper modules into a target game
- `doctor` verifies that the target game has the expected MuseLang runtime helper modules
- `test` parses and validates a MuseLang source file or a folder of source files
- `dev` parses, validates, writes the compiled bundle by default, and compares against an optional live snapshot JSON file
- `prod` parses, validates, writes a compiled bundle, and emits an Evennia batch file
- direct live Evennia apply is still not wired yet

Multi-file project support:

- if the source path is a file, MuseLang behaves as before
- if the source path is a folder, MuseLang compiles all top-level `*.muse` and
  `*.muselang` files in alphabetical filename order
- duplicate ids across files are rejected during validation
- V1 does not support reopening the same room, object, character, or rule
  across multiple files; each id must still be defined once
- default output names for folder builds are written back into that folder as
  `<foldername>.muselang.json` and `<foldername>.muselang.ev`

Recommended workflow:

1. Run `muselang runtime-install` once for a game root.
2. Run `muselang doctor` to confirm the runtime is installed.
3. Use `muselang test`, `dev`, and `prod` for normal content work.

Collaborative workflow example:

```text
museum-project/
  01_rooms.muse
  02_objects.muse
  03_dialogue.muse
```

Then compile the whole folder:

```powershell
muselang prod .\museum-project
```

Planned contents of this folder:

- MuseLang documentation
- MuseLang compiler implementation
- MuseLang runtime implementation
- MuseLang tests and examples
