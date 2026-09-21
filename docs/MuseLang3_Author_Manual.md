# MuseLang3 Author Manual

Edition: Implemented profile 0.1

This manual explains how to write, check, compile, and deploy scenarios using
the standalone MuseLang3 implementation.

For an alphabetical description of every implemented language word and
intrinsic function, see `MuseLang3_Keyword_Reference.md`. For exact grammar and
normative semantics, see `MuseLang3_Formal_Syntax.md` and
`MuseLang_spec_v3.md`.

## 1. What MuseLang3 Is

MuseLang3 is for small turn-by-turn games and museum interactions that need
more than static content but do not need a full Python program. It supports
typed command input, scalar and array state, counted `for` loops, arithmetic,
choices made with `if`, reusable routines, interpolation, random values,
scoring, achievements, and movement.

Good MuseLang3 projects include:

- combination locks and code-entry puzzles;
- quizzes and per-player progress;
- dice and chance puzzles;
- resource and score tracking;
- simple control-panel simulations;
- turn-by-turn games such as Lunar Lander;
- shared exhibit state such as power or availability.

Use a Tier 3 Python handler or native client when the experience requires
pathfinding, continuous time, animation, joystick polling, hardware protocols,
network code, AI, or a complex algorithm.

MuseLang3 is the current supported MuseLang release. Use `muselang` for the
latest version or `muselang3`/`MuseLang3` when an explicit V3 command is useful.
There is no `--language` option.

## 2. What Is Implemented Now

Implemented profile 0.1 supports:

- rooms, objects, characters, aliases, descriptions, and scalar or array state;
- goals and achievements;
- typed positional verb arguments;
- local values declared with `let`;
- arithmetic, comparisons, Boolean expressions, and safe functions;
- state owned by the current noun, player, team, scenario, or world;
- object-local routines;
- interpolation in `say` and `hint` strings;
- deterministic random functions;
- conditional statements, counted `for` loops, assignment, movement, registered
  calls, `stop`, and `end`;
- JSON compilation and Evennia batch output;
- a separate installable Evennia runtime.

Not yet implemented are exits, author-defined types and inheritance, rules,
events, dialogue trees, game-time syntax, nested rooms, containers and
supporters as enforced placement relationships, multiline text blocks, and
direct live-world application.

Older MuseLang3 design documents may discuss those broader features. Do not use
them in profile 0.1 source unless they have since appeared in the core language
specification and compiler tests.

## 3. Running MuseLang3

From the ACMS repository root on Windows, use the V3 launcher:

```powershell
.\muse-dev\MuseLang\V3\muselang.bat lint <source>
.\muse-dev\MuseLang\V3\muselang.bat test <source>
.\muse-dev\MuseLang\V3\muselang.bat dev <source>
.\muse-dev\MuseLang\V3\muselang.bat prod <source>
```

`<source>` may be one `.muse` file or a folder containing `.muse` files.

### 3.1 Command Meanings

| Command | Result |
|---|---|
| `lint` | parses and validates without writing a bundle |
| `test` | currently performs the same parse/validation/build checks as lint |
| `dev` | writes a canonical `.muselang.json` bundle |
| `prod` | writes JSON plus an Evennia `.ev` batch file |
| `runtime-install` | installs the V3 Evennia runtime helpers |
| `doctor` | checks the installed V3 runtime against the bundled copy |

Use explicit output paths when needed:

```powershell
.\muse-dev\MuseLang\V3\muselang.bat prod `
  .\world\lander.muse `
  --out .\build\lander.json `
  --batch-out .\build\lander.ev `
  --report .\build\lander-report.json
```

Without `--out`, `dev` and `prod` write next to a file input or inside a folder
input. The default suffixes are `.muselang.json` and `.ev`.

### 3.2 Installing the Package

The project has its own `pyproject.toml`. An editable installation provides the
console commands `muselang`, `muselang3`, and `MuseLang3`:

```powershell
.\.venv\Scripts\python.exe -m pip install -e .\muse-dev\MuseLang\V3
muselang lint .\muse-dev\MuseLang\V3\examples\lunar_lander.muse
```

## 4. Your First Scenario

Create `panel.muse`:

```muse
room laboratory "Laboratory"
  desc "A practical workroom filled with test equipment."

goal panel_started
  desc "Start the test panel."

object test_panel in laboratory from device
  alias "panel"
  state powered = false

  verb power_on
    if this.powered
      say "The panel is already powered."
      stop
    set this.powered = true
    say "The panel lights up."
    achieve panel_started
```

Check it:

```powershell
.\muse-dev\MuseLang\V3\muselang.bat lint .\panel.muse
```

The important shape is:

1. The room begins at the left margin.
2. The object also begins at the left margin.
3. Object properties are indented beneath the object.
4. Verb statements are indented beneath the verb.
5. The body of `if` is indented one level further.

Indent with spaces. Tabs in indentation are errors.

## 5. Files, Comments, and Names

Use UTF-8 text and the `.muse` suffix. Blank lines are ignored. A comment begins
with `#` outside a quoted string:

```muse
# Main exhibit control
object console in gallery from device
  state powered = false  # initial state
```

Choose lowercase IDs that remain easy to type:

```muse
room command_module "Command Module"
object landing_console in command_module from device
```

An ID is how source code refers to something. A quoted display name is what a
player sees. Aliases add other command names:

```muse
object landing_console in command_module from device "Lander Console"
  alias "console" "lander" "flight computer"
```

Aliases may be quoted or single unquoted words. Quote multiword aliases.

## 6. Rooms, Objects, and Characters

### 6.1 Rooms

```muse
room orbit "Command Module"
  desc "The planet fills the lower viewport."
```

Profile 0.1 rooms are flat. Nested-room and exit syntax is not available.

### 6.2 Objects

Every object must name a declared room:

```muse
object lander in orbit from device
```

The optional `from` label records the kind of object. Recognised built-in labels
are `thing`, `device`, `container`, `supporter`, `door`, `key`, and
`portable_item`. These labels do not yet supply inherited properties.

### 6.3 Characters

```muse
character curator in gallery "Museum Curator"
  alias "guide"
```

Characters currently have the same authorable children as other nouns. The
profile does not yet implement dialogue trees or character-specific behaviour.

### 6.4 Descriptions

Use an inline quoted description:

```muse
desc "A battered terminal with yellowed keys."
```

`description` is accepted as the long form. Indented multiline descriptions,
conditional descriptions, and random description blocks are not implemented.

## 7. Declaring State

Object-local state is declared inside a room, object, or character:

```muse
object lander in orbit from device
  state active = false
  state altitude = 1000
  state velocity = 0
  state fuel = 500
  state weather = "clear"
```

Initial values must be literal Booleans, integers, floats, or strings. They
cannot be expressions:

```muse
# Not valid as a declaration
state doubled = 2 * 5
```

Use `this` inside the noun's verbs and routines:

```muse
if this.fuel <= 0
  say "The fuel tank is empty."
```

Named-object state can be read or changed explicitly:

```muse
if lander.active
  set lander.fuel -= 10
```

Object state used through `this` or a named object must first be declared on
that noun. This catches misspellings such as `this.alitutde`.

## 8. Player, Team, Scenario, and World State

Declare non-object defaults at the left margin:

```muse
state player.score = 0
state team.rounds_won = 0
state scenario.turn = 0
state world.exhibit_power = false
```

The scopes mean:

- `player.*`: stored on the current player;
- `team.*`: stored on the player's configured team object;
- `scenario.*`: stored on the object exposing the current verb;
- `game.*`: accepted alias for `scenario.*`;
- `world.*`: stored once for the whole Evennia world;
- `real.*`: read-only current environment values.

Examples:

```muse
set player.score += 10
set team.rounds_won += 1
set scenario.turn += 1
set world.exhibit_power = true
say "The date is {real.date}."
```

The standard adapter exposes `real.now`, `real.date`, and `real.time`. These are
read-only; `set real.time = ...` is rejected.

A `team.*` reference requires trusted runtime setup to place a team object in
the player's `db.muselang_team` field. Without one, reading team state produces
no value and writing it is a safe runtime error.

## 9. Verbs and Typed Input

A verb is a command attached to a noun:

```muse
verb status
  say "Fuel: {this.fuel}."
```

Add typed positional arguments in angle brackets:

```muse
verb thrust <amount:int>
  say "Requested thrust: {amount}."
```

Available types:

| Type | Example input | Result |
|---|---|---|
| `int` | `50` | integer 50 |
| `float` | `12.5` | float 12.5 |
| `number` | `50` or `12.5` | integer or float |
| `word` | `red` | one word |
| `string` | `red alert` | all remaining words |
| `bool` | `true` | Boolean |
| `id` | `lander_1` | one string token |
| `object` | `panel` | resolved accessible object |
| `room` | `gallery` | resolved object; room kind not yet enforced |
| `char` | `curator` | resolved object; character kind not yet enforced |

An omitted type means `word`:

```muse
verb guess <answer>
```

Optional arguments use `?` and must be last:

```muse
verb inspect <detail:word?>
```

A `string` argument must also be last because it consumes the remaining input:

```muse
verb enter_message <message:string>
```

Arguments are read-only. The runtime reports conversion errors before executing
the verb, so invalid input does not change state or consume a random value.

Only simple positional command forms are supported. Do not yet write embedded
grammar words such as:

```muse
# Not implemented
verb give <item> to <recipient>
```

## 10. Expressions

Expressions are available in conditions, assignments, locals, and interpolated
text.

### 10.1 Arithmetic

```muse
let burn = amount * 2
let remaining = this.fuel - burn
let average = total / count
let groups = total // size
let remainder = total % size
```

Arithmetic is numeric. `+` does not join strings.

### 10.2 Comparisons

```muse
amount == 50
amount != 0
amount > 100
amount >= 10
amount < 0
amount <= this.fuel
```

Write range tests explicitly:

```muse
if amount >= 0 and amount <= 100
  say "Accepted."
```

Chained comparisons such as `0 <= amount <= 100` are not supported.

### 10.3 Boolean Operators

```muse
if this.active and this.fuel > 0
  say "Ready."

if not this.active or this.disabled
  say "Unavailable."
```

Precedence is the familiar order: unary operators, multiplication, addition,
comparisons, `and`, then `or`. Use parentheses when that makes intent clearer.

### 10.4 Inventory Predicate

The current inventory predicate is:

```muse
if have badge
  say "The badge is in your inventory."
```

In profile 0.1, `have <object>` must be the complete condition. It cannot yet be
combined directly with `and` or `or`.

## 11. Safe Functions

### Numeric Functions

```muse
let lower = min(a, b)
let upper = max(a, b)
let speed = abs(this.velocity)
let safe_amount = clamp(amount, 0, this.fuel)
let nearest = round(value)
let down = floor(value)
let up = ceil(value)
```

`round()` rounds halves away from zero.

### Random Functions

```muse
let roll = random_int(1, 6)
if random_chance(25)
  say "A warning lamp flickers."
set this.weather = random_choice("clear", "cloudy", "rain")
```

`random_int` includes both endpoints. `random_chance` accepts 0 through 100.
`random_choice` needs at least one value.

Random state is stored on the scenario owner after a successful command. A
runtime failure restores the previous random state. This makes a seeded command
sequence repeatable in the supported runtime.

## 12. Local Variables

Declare temporary values with `let`:

```muse
let burn = clamp(amount, 0, this.fuel)
let lift = burn / 5
```

Locals last only for the current invocation. They are not saved to Evennia.

Reassign an existing local with `set`:

```muse
let bonus = 0
set bonus = 5
```

Do not use `set` to create a local. The compiler rejects unknown local targets.

A local name cannot duplicate an argument, another local in the same block, a
declared noun ID, a state namespace, a Boolean keyword, or a safe function name.

Locals declared inside an `if` branch remain confined to that branch.

## 13. Conditions

Use `if`, optional `elif`, and optional `else`:

```muse
if guess == this.code
  set this.locked = false
  say "The locker clicks open."
elif this.attempts >= 3
  set this.disabled = true
  say "The locker refuses further attempts."
else
  say "The code is rejected."
```

Blocks end by dedenting. Do not write a structural `end` after an `if`.

General `while`, `until`, and `for` loops are deliberately not part of
MuseLang3. Repetition happens when the player enters another command.

## 14. Assignment

Persistent state and locals are changed with `set`:

```muse
set this.active = true
set this.turn += 1
set this.fuel -= burn
set player.score += 10
set world.exhibit_power = false
```

The right side is an expression. `+=` and `-=` require an existing numeric
value. Arguments and `real.*` values cannot be assigned.

## 15. Text and Interpolation

Use `say` for normal output and `hint` for guidance:

```muse
say "The engine fires."
hint "Use THRUST followed by a number from 0 to 100."
```

Insert values or expressions using braces:

```muse
say "Fuel: {this.fuel} units."
say "Impact speed: {abs(this.velocity)} m/s."
say "Score: {player.score}."
```

Use doubled braces for literal braces:

```muse
say "Write a placeholder as {{name}}."
```

Do not embed conditions inside text. Use an ordinary `if`:

```muse
if this.open
  say "The door is open."
else
  say "The door is closed."
```

Output is buffered until the command succeeds. If a later runtime error occurs,
the buffered output is discarded with the command's MuseLang-managed changes.

## 16. Routines

Use a routine to reuse a block that is not itself a player command:

```muse
routine status
  say "Turn: {this.turn}"
  say "Altitude: {this.altitude} m"
  say "Fuel: {this.fuel}"

verb status
  run status
```

You may qualify the owner:

```muse
run this.status
run lander.status
```

Inside `lander.status`, `this` means `lander`.

Routines have no parameters or return values. Keep routine inputs in declared
state, and declare any temporary locals inside the routine. A routine cannot
depend on a particular calling verb's arguments or locals because it is
validated independently.

Routine recursion is rejected. The runtime also stops calls deeper than 32.

## 17. Goals and Achievements

Declare goals at the left margin:

```muse
goal safe_landing
  desc "Land safely on the planet."
```

Award one from a verb:

```muse
achieve safe_landing
```

The goal ID must exist. Achievements are persisted on the current player and
also recorded in the current command's replay information.

MuseLang3 does not have a primitive that ends the shared world. Complete the
scenario by updating state and awarding a goal.

## 18. Movement

Move the player or a declared noun:

```muse
move player to surface
move capsule to laboratory
```

The target and destination must resolve. Profile 0.1 does not yet validate that
the destination is specifically a room or container.

## 19. Stopping a Verb

Use `stop` after rejecting the command:

```muse
if not this.active
  say "The game is not active."
  stop
```

`stop` prevents later statements from running. It is a successful scripted
result: earlier statements and the rejection message are committed.

`end` also returns immediately and exists for integration uses. It does not end
the shared world and normally is not needed in straightforward verbs.

## 20. Calling Tier 3 Behaviour

MuseLang3 can invoke a handler registered by trusted Python runtime code:

```muse
call museum.handlers.activate_relay
```

An unregistered target is a runtime error. Authored code cannot import modules
or call arbitrary Python functions.

External handler effects—hardware operations, network messages, or other
database work—are outside MuseLang3's rollback and replay boundary. Arrange for
the handler to validate first, remain idempotent where practical, and perform
irreversible work only after MuseLang checks have succeeded.

## 21. The Turn-by-Turn Pattern

One successful input verb usually performs one authored turn:

```muse
verb play <choice:int>
  if not this.active
    say "Start the game first."
    stop

  set this.turn += 1
  # Update state for this turn.

  if this.score >= 10
    set this.active = false
    achieve game_won
  else
    run status
```

MuseLang3 does not advance a counter automatically. Put `set this.turn += 1`
only in commands that genuinely consume a turn. A status command, invalid
argument, or rejected command need not advance anything.

## 22. Complete Example: Combination Lock

```muse
room laboratory "Laboratory"

object storage_locker in laboratory from container
  alias "locker"
  state open = false
  state locked = true
  state code = 1977
  state attempts = 0
  state disabled = false

  verb enter <guess:int>
    if this.disabled
      say "The locker refuses further attempts."
      stop

    if not this.locked
      say "The locker is already unlocked."
      stop

    set this.attempts += 1

    if guess == this.code
      set this.locked = false
      set this.open = true
      say "The locker clicks open."
    elif this.attempts >= 3
      set this.disabled = true
      say "The locker emits an angry buzz and refuses further attempts."
    else
      say "The locker rejects the code. Attempts: {this.attempts}."
```

The early `disabled` check matters. Setting `disabled` without checking it on a
later invocation would not actually refuse further attempts.

## 23. Complete Example: Dice Puzzle

```muse
room laboratory "Laboratory"

goal panel_unlocked
  desc "Unlock the test panel."

object test_panel in laboratory from device
  alias "panel"
  state solved = false

  verb press
    if this.solved
      say "The panel is already solved."
      stop

    let roll = random_int(1, 6)
    say "The display rolls a {roll}."

    if roll == 6
      set this.solved = true
      say "The panel unlocks."
      achieve panel_unlocked
    else
      say "Nothing else happens."
```

## 24. Complete Example: Shared Power and Player Score

```muse
state player.score = 0
state world.exhibit_power = false

room gallery "Museum Gallery"

goal quiz_complete
  desc "Answer the exhibit question."

object exhibit_console in gallery from device
  alias "console"

  verb power_on
    set world.exhibit_power = true
    say "Power reaches the shared exhibit."

  verb answer <value:int>
    if value == 8
      set player.score += 1
      say "Correct. Your score is {player.score}."
      achieve quiz_complete
    else
      say "That answer is not correct."
```

Each player gets an independent `player.score`; everyone sees the same
`world.exhibit_power`.

## 25. Lunar Lander

The full turn-by-turn example is:

[examples/lunar_lander.muse](examples/lunar_lander.muse)

It demonstrates:

- typed thrust input;
- range validation and `stop`;
- arithmetic and `clamp`;
- temporary burn and lift values;
- persistent altitude, velocity, fuel, and turn state;
- a reusable status routine;
- interpolated telemetry;
- win and crash goals;
- player movement after a safe landing.

## 26. Errors and Validation

Compiler errors include a file, line, and usually a column:

```text
world/lander.muse:42:5: unknown state reference 'this.alitutde'
```

Common errors include:

### Unknown or Undeclared State

Bad:

```muse
set this.disabled = true
```

when `state disabled = false` was never declared.

### Writing Read-Only State

Bad:

```muse
set real.time = 12
```

### Unknown Local

Bad:

```muse
set bonus = 5
```

without an earlier `let bonus = ...` in the current scope.

### Invalid Argument Layout

Bad:

```muse
verb label <text:string> <colour:word>
```

The `string` argument must be last.

### Recursive Routine

Bad:

```muse
routine again
  run again
```

### Invalid Random Percentage

Bad:

```muse
if random_chance(150)
  say "Impossible percentage."
```

### Unsupported Syntax

Bad in profile 0.1:

```muse
while this.active
  say "Waiting."
```

The compiler rejects general loops.

## 27. Runtime Failure and Rollback

If a runtime error occurs after some MuseLang statements have executed, the
interpreter restores:

- MuseLang-managed state writes;
- moves made through the MuseLang `move` statement;
- achievements added by MuseLang;
- buffered `say` and `hint` output;
- PRNG advancement.

For example, if a verb increments `this.count` and then tries to write
`team.score` when no team owner exists, `this.count` returns to its starting
value and no buffered messages are sent.

This is not a general Evennia database transaction. It does not reverse effects
performed by registered Python handlers, and profile 0.1 does not yet protect a
shared scenario with an optimistic revision lock.

## 28. Determinism and Replay

The standard runtime starts with seed `0` unless trusted setup supplies a
different `muse3/random_seed` on the scenario owner. It persists
`muse3/random_state` after a successful command.

Given the same supported Python runtime, starting state, seed/PRNG state,
command, and external values, the MuseLang portion of a command is repeatable.

The pure runtime exposes a replay record containing final invocation locals
(including bound arguments), random results, mutations, messages, and
achievements. The standard Evennia adapter does not yet save those records
automatically. Python handler effects are not included.

## 29. Compiling and Importing into Evennia

### Step 1: Compile

```powershell
.\muse-dev\MuseLang\V3\muselang.bat prod `
  .\muse-dev\MuseLang\V3\examples\lunar_lander.muse
```

This writes:

- `lunar_lander.muselang.json`
- `lunar_lander.ev`

### Step 2: Install the V3 Runtime

```powershell
.\muse-dev\MuseLang\V3\muselang.bat runtime-install `
  --game-root .\muse-game
```

Check it:

```powershell
.\muse-dev\MuseLang\V3\muselang.bat doctor `
  --game-root .\muse-game
```

The V3 helpers are installed under `muse-game/behaviours/muselang`. This is
separate from the MuseLang V1 runtime.

### Step 3: Import the Batch

Runtime installation does not import authored world content. Place the emitted
`.ev` file where Evennia can find it and, as an Evennia administrator, run the
corresponding `batchcommands <name>` command. The default `.ev` suffix is used
so Evennia module-style names such as `world.minesweeper` work cleanly.

Re-importing the same authored content may create duplicates or conflicts.
Profile 0.1 does not yet provide an idempotent live migration system.

## 30. Testing MuseLang3 Itself

From the repository root:

```powershell
$env:PYTHONPATH = '.\muse-dev\MuseLang\V3\src'
.\.venv\Scripts\python.exe -m unittest discover `
  -s .\muse-dev\MuseLang\V3\tests -v
```

The acceptance suite covers Lunar Lander, combination-lock lockout, dice,
player score, world power, quiz achievements, typed argument errors,
deterministic randomness, PRNG continuation, rollback, recursion rejection,
read-only state, invalid random percentages, and loop rejection.

## 31. Authoring Checklist

Before compiling a scenario, check:

- Every object and character names a declared room.
- Every object state field is declared before it is referenced or assigned.
- Top-level state uses `player`, `team`, `scenario`/`game`, or `world`.
- `real.*` is only read.
- Verb arguments have unique names and trailing `string`/optional layout.
- Locals are declared with `let` before `set` reassigns them.
- Routines do not depend on a caller's local values or call recursively.
- Random percentages stay between 0 and 100.
- A rejected command uses `stop` before turn-consuming statements.
- Turn advancement is explicit and occurs only in the intended verbs.
- Shared state is deliberately placed under `team`, `scenario`, or `world`.
- Per-player progress is deliberately placed under `player`.
- Tier 3 calls are registered and their irreversible effects are understood.
- The source passes `muselang lint`.
- The runtime passes `muselang doctor` before live import.

## 32. Choosing the Right Tier

Use MuseLang3 for current authored Muse content, especially when the interaction
needs calculation, typed input, arrays, random values, routines, or scoped
scenario state and can wait indefinitely between player commands. Use Python or
a native client when the work needs complex data structures, continuous updates,
hardware, network protocols, graphics, AI, or complex algorithms.

The useful boundary is readability: if the MuseLang3 source begins to look like
an awkward substitute for a real program, move that behaviour to Tier 3 and let
MuseLang3 coordinate its meaningful world-state results.
