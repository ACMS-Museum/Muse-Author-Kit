# MuseLang 3

MuseLang 3 is the current supported MuseLang implementation. It is a
separate project from `MuseLang/V1`: it has its own Python package, executable,
bundle schema, runtime API, tests, launcher, and Evennia runtime directory.

Current project version: 3.0.0. Compiled source reports language version 3.0,
bundle schema 3, and runtime API 3.

## Documentation

- `MuseLang_spec_v3.md`: normative implemented language and runtime semantics.
- `MuseLang3_Author_Manual.md`: task-oriented authoring and deployment guide.
- `MuseLang3_Keyword_Reference.md`: alphabetical, BASIC-manual-style reference
  to every implemented keyword and intrinsic function, with examples.
- `MuseLang3_Keyword_Reference.html`: self-contained browser edition with a
  clickable alphabetical index and linked cross-references.
- `MuseLang3_Formal_Syntax.md`: parser-facing grammar for profile 0.1.
- `MuseLang3_Scenario_Scripting_Extensions.md`: original extension rationale,
  now incorporated into the core specification.
- `MuseLang_Tier_Model_White_Paper.docx` in the parent directory: Tier 1/2/3
  design boundary.

## Commands

From the repository root on Windows:

```powershell
.\muse-dev\MuseLang\V3\muselang.bat lint .\muse-dev\MuseLang\V3\examples\lunar_lander.muse
.\muse-dev\MuseLang\V3\muselang.bat dev .\muse-dev\MuseLang\V3\examples\lunar_lander.muse
.\muse-dev\MuseLang\V3\muselang.bat prod .\muse-dev\MuseLang\V3\examples\lunar_lander.muse
.\muse-dev\MuseLang\V3\muselang.bat runtime-install --game-root .\muse-game
```

The installable console commands are `muselang`, `muselang3`, and `MuseLang3`.
`muselang` is always the current supported MuseLang release; versioned commands
identify historical or explicit versions.

`dev` writes a `.muselang.json` bundle. `prod` writes that JSON bundle plus an
Evennia `.ev` batch file. `runtime-install` installs the V3 runtime to
`behaviours/muselang`, separate from the V1 `behaviours/common` runtime.

## Implemented scenario profile

The initial implementation supports:

- rooms, objects, characters, goals, descriptions, aliases, and literal state;
- `object ... in ... from ...` construction;
- typed positional verb arguments;
- `let`, arithmetic, comparison, Boolean expressions, and safe built-ins;
- namespaced `player`, `team`, `scenario`/`game`, `world`, `this`, named-object,
  and read-only `real` state;
- routines and bounded routine call depth, with recursion rejected at compile time;
- string interpolation with escaped braces;
- deterministic random functions with persisted PRNG state;
- `if`/`elif`/`else`, `set`, `say`, `hint`, `run`, `move`, `achieve`, `stop`,
  `end`, and registered Tier 3 calls;
- transactional command execution and replay records.

General `while` and `until` loops are deliberately not part of MuseLang3.

The wider design's exits, author-defined types/inheritance, rules, events,
dialogue, time declarations, nested rooms, and direct live application are not
implemented in profile 0.1. See the core specification for the exact current
surface and runtime limitations.

## Tests

```powershell
$env:PYTHONPATH = '.\muse-dev\MuseLang\V3\src'
.\.venv\Scripts\python.exe -m unittest discover -s .\muse-dev\MuseLang\V3\tests -v
```
