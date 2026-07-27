# Muse Author Kit

This package is the member-facing Muse toolkit.

It is designed for ACMS members who want to:

- write MuseLang source files
- lint and compile them with MuseLang V1
- install runtime support into the local `muse-game` scaffold
- run the Muse game locally with Evennia
- use the MuseLang V1 VS Code extension

This package is not the full Muse development repository.

If you want to write rooms, objects, verbs, and dialogue in MuseLang and try
them in a local Muse game, you are in the right place.

## Package contents

- `muse-game`: the endorsed local game scaffold
- `examples`: MuseLang V1 example content
- `docs`: MuseLang V1 documentation
  - `MuseLang_V1_README.md`: overview of the MuseLang V1 definition and workflow
  - `MuseLang_author_manual.md`: author-facing language guide
- `vscode`: VS Code support for MuseLang V1
- `packages`: packaged MuseLang wheel files
- `install`: helper install scripts for PowerShell, Windows batch, and Bash

## Windows quick start

The easiest option is:

```bat
.\install\install_muse_author_kit.bat
```

If you prefer PowerShell:

1. Open PowerShell in this `Muse-Author-Kit` folder.
2. Run:

```powershell
.\install\install_muse_author_kit.ps1
```

If PowerShell blocks local scripts on your machine, use:

```powershell
powershell -ExecutionPolicy Bypass -File .\install\install_muse_author_kit.ps1
```

3. When the installer finishes, activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Start the Muse game:

```powershell
cd .\muse-game
evennia migrate
evennia createsuperuser
evennia start
```

5. Open <http://localhost:4001> in a browser, or connect to `localhost` on
   port `4000` with a Telnet or MUD client.

When you are ready to stop the game later:

```powershell
cd .\muse-game
evennia stop
```

Note:

- the install script creates a local Python environment for this kit
- it installs MuseLang from the packaged wheel included in `packages`
- it installs Evennia from Python package indexes, so internet access is still
  needed for the Evennia step unless you arrange an offline mirror
- this kit is meant for authoring and experimenting, not for editing the
  MuseLang compiler itself

## Bash quick start

For macOS, Linux, WSL, or Git Bash:

```bash
chmod +x ./install/install_muse_author_kit.sh
./install/install_muse_author_kit.sh
```

Then:

```bash
source ./.venv/bin/activate
cd ./muse-game
evennia migrate
evennia createsuperuser
evennia start
```

## VS Code

To install the MuseLang V1 VS Code extension:

1. Open VS Code.
2. Run `Developer: Install Extension from Location...`
3. Select:

`vscode\vscode-muselang`

After that, `.muse` and `.muselang` files should open with MuseLang V1 syntax
highlighting and lint support.

## MuseLang workflow

Typical commands from this kit root:

```powershell
muselang lint .\examples\demo_v1.muse
muselang prod .\examples\demo_v1.muse
muselang runtime-install --game-root .\muse-game
muselang doctor --game-root .\muse-game
```

`runtime-install` installs the reusable MuseLang runtime into the Evennia game.
It does not import authored content.

After `muselang prod` has generated the Evennia batch file, start the game and
sign in with an administrator account. Enter this command in the game:

```text
batchcommands demo_v1
```
For your own source file, replace `demo_v1` in both the batch filename and the
`batchcommands` command. For example, compile to
`.\muse-game\world\my_world.ev`, then enter `batchcommands my_world`.

Good starting points in `docs` are `MuseLang_V1_README.md` for the V1 overview
and `MuseLang_author_manual.md` for the author guide.

## Multi-file projects

MuseLang V1 can compile either:

- a single `.muse` file, or
- a folder containing multiple top-level `*.muse` or `*.muselang` files

Example:

```powershell
muselang prod .\examples
```

For multi-file builds:

- files are read in alphabetical order
- ids must still be unique across the whole project
- V1 does not support splitting one room, object, character, or rule across
  multiple files by repeating its id later
