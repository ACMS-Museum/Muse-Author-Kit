# Muse

Muse is an ACMS project for building interactive, text-based museum worlds.
Visitors can explore rooms, examine exhibits, talk to characters, solve simple
puzzles, and eventually connect from web browsers, ordinary MUD clients, or
real vintage terminals.

You do not need to be an experienced programmer to experiment with Muse.
World content can be written in **MuseLang**, a small, readable language made
for describing rooms, objects, actions, and conversations.

## What is in this repository?

Muse currently has three main parts:

1. **MuseLang** turns a `.muse` text file into data and Evennia import commands.
2. **Muse Game** runs the interactive world using the
   [Evennia](https://www.evennia.com/) game server.
3. **Adapters** explore connections between Muse and physical serial terminals.

The basic flow is:

```text
MuseLang source
      |
      v
MuseLang compiler
      |
      v
JSON bundle + Evennia batch file
      |
      v
Muse runtime on Evennia
      |
      v
Browser, Telnet client, or terminal adapter
```

## Project status

Muse is under active development.

- **MuseLang 1.0** has a working compiler, validator, Evennia runtime, and
  demonstration world.
- **MuseLang 2.0** is currently a separate specification and design project.
- V1 imports create a world in an Evennia database, but they do **not** merge
  changes safely into an existing live world.
- The included demonstration should therefore be imported into a new,
  disposable, or otherwise empty database.

The V1 system is ready for ACMS members to run, inspect, and modify.

## Local versus tracked content

This repository contains both canonical project source and an endorsed local
game scaffold.

- `muse-dev/MuseLang/V1` is the source of truth for the MuseLang compiler and
  the runtime template files copied into a game.
- `muse-dev/MuseLang/V2` holds design and specification work for the next
  language version.
- `muse-game` is a tracked scaffold for the expected Evennia game layout used
  by MuseLang tooling.
- Runtime state inside `muse-game`, such as databases, logs, generated static
  files, and private settings, is local machine state and is not treated as
  canonical project source.

## Repository guide

| Location | Purpose |
| --- | --- |
| [`muse-game`](muse-game) | Endorsed local Evennia game scaffold used by MuseLang tooling |
| [`muse-dev/MuseLang/V1`](muse-dev/MuseLang/V1) | Working MuseLang 1.0 compiler, examples, tests, and documentation |
| [`muse-dev/MuseLang/V2`](muse-dev/MuseLang/V2) | MuseLang 2.0 design documents |
| [`muse-dev/MuseLang/V1/vscode-muselang`](muse-dev/MuseLang/V1/vscode-muselang) | Visual Studio Code support for MuseLang V1 |
| [`muse-dev/pi_adapters`](muse-dev/pi_adapters) | Raspberry Pi, Telnet, and serial-terminal experiments |
| [`muse-dev/Evennia`](muse-dev/Evennia) | Notes about the Evennia system |

## Quick start on Windows

These instructions assume Windows PowerShell. Muse is currently tested with
Python 3.12, but the package accepts Python 3.11 or newer.

### 1. Install the prerequisites

Install:

- [Git](https://git-scm.com/downloads)
- [Python](https://www.python.org/downloads/) 3.11 or newer

When installing Python on Windows, select the option to add Python to `PATH`.

### 2. Download Muse

Open PowerShell and run:

```powershell
git clone https://github.com/pdr0663/acms.git
cd acms
```

### 3. Create a private Python environment

A virtual environment keeps Muse's Python packages separate from the rest of
your computer.

```powershell
py -3.12 -m venv .\.venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools
```

If your Python command is not `py -3.12`, use the installed command shown by:

```powershell
py --list
```

### 4. Install Evennia and MuseLang

```powershell
python -m pip install evennia
python -m pip install -e .\muse-dev\MuseLang\V1
```

The `-e` means "editable." Changes made to the MuseLang Python source are used
without reinstalling the package.

### 5. Install the Muse runtime into the game

From the repository root:

```powershell
muselang runtime-install --game-root .\muse-game
muselang doctor --game-root .\muse-game
```

MuseLang V1 can compile either a single source file or a folder containing
multiple top-level `*.muse` or `*.muselang` files. That makes it possible for
several authors to keep separate content files and then compile the whole
project together.

The doctor should report:

```text
"healthy": true
```

### 6. Prepare and start the game

```powershell
cd .\muse-game
evennia migrate
evennia createsuperuser
evennia start
```

Choose a username and password when prompted. This creates the administrator
account you will use for the demonstration.

Open <http://localhost:4001> in a browser and sign in. A Telnet/MUD client can
instead connect to `localhost` on port `4000`.

To stop Muse later, run this from the `muse-game` directory:

```powershell
evennia stop
```

### Linux and macOS

The overall process is the same. Create and activate the environment with:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Then use the same `pip`, `muselang`, and `evennia` commands, replacing Windows
backslashes with forward slashes.

## Import and play the demonstration

The repository includes a compiled demonstration called `demo_v1`.

After signing in with the administrator account, enter this command in the
game:

```text
batchcommands demo_v1
```

The import creates a museum workshop, a maintenance panel, a screwdriver, a
badge, and a curator. When the import finishes, try:

```text
look
examine panel
open panel
get badge
talk curator
talk curator h
get screwdriver
use screwdriver on panel
open panel
```

The first attempt to open the panel is blocked. Using the screwdriver changes
the panel's stored state, so later commands see that it is open.

## A first look at MuseLang

MuseLang uses indentation to show which details belong to an object.

```text
room workshop "Museum Workshop"
  desc "A workbench stands beneath rows of vintage equipment."

obj panel in workshop "Maintenance Panel"
  alias hatch
  state open = false

  verb examine
    say "The panel is held shut by two screws."

  verb open
    if panel.open
      say "The panel is already open."
    else
      say "The screws prevent it from opening."
```

This defines:

- a room named `workshop`;
- an object named `panel`;
- an alternative name, `hatch`;
- a piece of state called `open`; and
- two commands that a visitor can use.

The full example is
[`demo_v1.muse`](muse-dev/MuseLang/V1/examples/demo_v1.muse).

## Make your own small world

Start by copying the demonstration:

```powershell
cd .\muse-dev\MuseLang\V1
Copy-Item .\examples\demo_v1.muse .\examples\my_world.muse
```

Edit `my_world.muse` in a text editor, then check it:

```powershell
muselang test .\examples\my_world.muse
```

Compile it into a JSON bundle and an Evennia batch file:

```powershell
muselang prod .\examples\my_world.muse `
  --out .\examples\my_world.json `
  --batch-out ..\..\..\muse-game\world\my_world.ev
```

From inside the running game, an administrator can then use:

```text
batchcommands my_world
```

### Important import warning

MuseLang 1.0 does not yet reconcile authored changes with objects already in a
live database. Re-importing the same world can create duplicates or conflicts.
Use a clean demonstration database while learning and keep backups of any
world data you care about.

## Documentation

Good starting points are:

- [MuseLang 1.0 Tinkerer Guide](muse-dev/MuseLang/V1/V1_TINKERER_GUIDE.md)
- [MuseLang Author Manual](muse-dev/MuseLang/V1/MuseLang_author_manual.md)
- [MuseLang 1.0 specification](muse-dev/MuseLang/V1/MuseLang_spec.md)
- [Compiler specification](muse-dev/MuseLang/V1/MuseLang_compiler_spec.md)
- [Runtime specification](muse-dev/MuseLang/V1/MuseLang_runtime_spec.md)
- [MuseLang 2.0 documents](muse-dev/MuseLang/V2)

## Member distribution

If you want ACMS members to author MuseLang content without working directly in
the compiler source tree, use the member kit under [member-kit](member-kit).
That builder assembles a shareable `Muse-Author-Kit` package containing:

- the `muse-game` scaffold
- MuseLang V1 author documentation
- example content
- the MuseLang V1 VS Code extension
- a packaged MuseLang wheel for installation

## Running the tests

From the repository root with the virtual environment active:

```powershell
python -m unittest discover -s .\muse-dev\MuseLang\V1\tests -v
```

The tests cover lexing, parsing, validation, bundle generation, runtime
conditions and actions, and runtime installation.

## Getting involved

Useful contributions include:

- trying the demonstration and reporting confusing steps;
- writing a small room, exhibit, character, or conversation;
- improving beginner documentation;
- adding tests for unusual authoring mistakes;
- experimenting with the serial-terminal adapters; and
- reviewing the MuseLang 2.0 design.

For code changes, create a branch, keep each change focused, run the tests, and
open a pull request. Bugs and suggestions can be recorded in the repository's
GitHub issue tracker.

This is an ACMS development project. Contribution and licensing arrangements
should be confirmed with the project maintainers before redistributing the
software outside ACMS.
