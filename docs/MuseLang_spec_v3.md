# MuseLang3 Language Specification

| Field | Value |
|---|---|
| Status | Implemented profile 0.1 |
| Language version | 3.0 |
| Bundle schema | 3 |
| Runtime API | 3 |

## 1. Purpose and Scope

MuseLang3 is a small, standalone language for authoring modest turn-by-turn
games, puzzles, scored interactions, and museum-machine scenarios. A player
command supplies one invocation of an authored verb. Persistent state carries
the scenario between invocations, so general loops are unnecessary.

MuseLang3 is the Tier 2 scenario language in the Muse authoring model:

- MuseLang V1 is the separate Tier 1 content-authoring project.
- MuseLang3 is the Tier 2 bounded scenario-scripting project.
- Python handlers and native clients provide Tier 3 behaviour.

MuseLang3 does not share a compiler or version switch with MuseLang V1. Its
package is `muselang`; its console commands are `muselang` and `MuseLang3`.

The companion `MuseLang3_Keyword_Reference.md` provides the alphabetical user
reference, while `MuseLang3_Author_Manual.md` provides the tutorial guide.

The current implementation covers the scenario scripting core. The older V2
design material also describes types, exits, rules, events, dialogue, nested
rooms, and game-time declarations. Those features are not part of implemented
profile 0.1 and must not be assumed to compile.

## 2. Design Principles

1. Source remains readable by volunteers and non-professional programmers.
2. Authored code cannot execute arbitrary Python expressions.
3. Expressions compile to a restricted structured AST.
4. Runtime behaviour comes from standard interpreters over versioned metadata.
5. Scalar state and explicit cases are preferred to general data structures.
6. Player commands provide repetition; general loops are excluded.
7. Routine recursion is excluded and runtime call depth is bounded.
8. Random behaviour can be deterministic and replayed.
9. A failed command rolls back MuseLang-managed effects.
10. Complex algorithms, real-time activity, hardware protocols, and custom
    external effects remain Tier 3 responsibilities.

## 3. Source Files and Layout

MuseLang3 source files use the `.muse` suffix and UTF-8 text. A single file or a
folder tree of files may be compiled. Folder input is discovered recursively
and combined in sorted path order before validation.

The language is line-oriented and indentation-sensitive:

- top-level declarations begin at the left margin;
- child declarations and statements are indented with spaces;
- tabs in indentation are errors;
- a block ends when indentation returns to its parent level;
- blank lines are ignored;
- `#` begins a comment outside a quoted string.

Example:

```muse
room laboratory "Laboratory"

object panel in laboratory from device
  state powered = false

  verb power_on
    set this.powered = true
    say "The panel comes to life."
```

## 4. Lexical Values

### 4.1 Identifiers

Identifiers begin with an ASCII letter or underscore and continue with letters,
digits, underscores, or hyphens. Lowercase `snake_case` is recommended.

Identifiers are case-sensitive in source. Runtime command and object matching
is case-insensitive.

### 4.2 Strings

Strings are enclosed in double quotes. Python-style quoted-string escapes for
quotes and backslashes are accepted by the current parser.

```muse
desc "A label reads \"READY\"."
```

### 4.3 Scalar Literals

The implemented scalar literal types are:

- Boolean: `true`, `false`
- Integer: `0`, `42`, `1977`
- Floating point: `3.5`, `0.25`
- String: `"clear"`, `"suspicious"`

State declarations require a scalar literal. Expressions are permitted when a
statement executes, but not as initial state values.

## 5. Top-Level Declarations

Implemented profile 0.1 accepts:

```text
room
object / obj
character / char
goal
state <namespace>.<name>
```

No other top-level declaration is currently accepted.

## 6. Rooms

Syntax:

```muse
room <room_id> ["Display Name"]
```

Example:

```muse
room orbit "Command Module"
  desc "The planet fills the lower viewport."
```

A room may contain the common noun children defined in section 9: aliases,
description, state, routines, and verbs.

Nested-room syntax and exit declarations are not implemented in profile 0.1.

## 7. Objects and Characters

Syntax:

```muse
object <object_id> in <room_id> [from <type_id>] ["Display Name"]
character <character_id> in <room_id> [from <type_id>] ["Display Name"]
```

The short forms `obj` and `char` are accepted.

Examples:

```muse
object lander in orbit from device
character curator in gallery "Museum Curator"
```

The location must name a declared room. The optional `from` value must name a
known built-in type label or a declared noun. Profile 0.1 recognises these
built-in labels for validation:

```text
thing device container supporter door key portable_item
```

Profile 0.1 records `type_id` in the bundle but does not implement author-defined
type declarations or property inheritance.

## 8. Goals

Syntax:

```muse
goal <goal_id>
  desc "Goal description."
```

The description is optional. Goals are awarded with `achieve`:

```muse
achieve safe_landing
```

The goal must be declared. At runtime, achieved goal IDs are persisted in the
current player's `muse3/achievements` state and included in replay records.

## 9. Common Noun Children

Rooms, objects, and characters may contain these declarations:

### 9.1 Aliases

```muse
alias "console" "flight computer"
```

Several aliases may appear on one line. Duplicate aliases on the same noun are
errors, compared case-insensitively.

### 9.2 Description

```muse
desc "A brushed metal panel with a dark display."
description "The long keyword is also accepted."
```

Only the inline quoted form is implemented. Dynamic description blocks and
random description alternatives are future features.

### 9.3 Local Object State

```muse
state active = false
state fuel = 500
state weather = "clear"
```

The state name is unqualified inside a noun. It is later accessed through
`this.<name>` or `<noun_id>.<name>`.

### 9.4 Routines and Verbs

Routines and verbs are defined in sections 11 and 12.

## 10. State Namespaces

State references have an explicit owner:

| Reference | Runtime owner | Sharing |
|---|---|---|
| `this.name` | noun executing the routine or verb | depends on noun |
| `object_id.name` | named world noun | shared with that noun |
| `player.name` | current player | private to player |
| `team.name` | current player's configured team object | shared by team |
| `scenario.name` | current scenario owner | scoped to scenario owner |
| `game.name` | alias of `scenario.name` | scoped to scenario owner |
| `world.name` | Evennia server configuration | shared by whole world |
| `real.name` | invocation-time environment snapshot | read-only |

In the standard Evennia adapter, the object exposing the verb is the scenario
owner. Consequently, `scenario.*` is object-scoped in profile 0.1. A later
scenario-instance service may provide a different owner without changing the
language syntax.

Top-level declarations establish defaults for non-object namespaces:

```muse
state player.score = 0
state team.rounds_won = 0
state scenario.turn = 0
state world.exhibit_power = false
```

Permitted top-level roots are `player`, `team`, `game`, `scenario`, and `world`.
`game` is normalised to `scenario` in compiled metadata. Defaults are applied
only when the target field does not already exist.

`real.*` values are read-only. The standard adapter exposes:

```text
real.now
real.date
real.time
```

They are snapshotted once at command invocation.

## 11. Verb Arguments

Syntax:

```muse
verb <verb_name> [<argument> ...]
```

Argument syntax:

```text
<name>
<name:type>
<name?>
<name:type?>
```

Supported types:

| Type | Conversion |
|---|---|
| `int` | integer |
| `float` | floating-point number |
| `number` | integer or floating-point number |
| `string` | all remaining words, joined with spaces |
| `word` | one word; default when type is omitted |
| `bool` | `true` or `false` |
| `object` | resolved accessible object |
| `room` | resolved accessible object; category is not yet enforced |
| `char` | resolved accessible object; category is not yet enforced |
| `id` | one unconverted identifier-like word |

Example:

```muse
verb thrust <amount:int>
  if amount < 0 or amount > 100
    say "Thrust must be between 0 and 100."
    stop
```

Arguments are read-only local values. Optional arguments and `string` arguments
must be last. Quoted command input is tokenised as one value. Conversion errors
occur before the program begins and cause no state or random changes.

Profile 0.1 supports positional arguments only. Natural multi-part command
grammars such as `give <item> to <recipient>` are not implemented.

## 12. Routines

Routines are object-local reusable statement blocks that are not player
commands:

```muse
routine status
  say "Turn: {this.turn}"
  say "Fuel: {this.fuel}"
```

They are invoked with:

```muse
run status
run this.status
run lander.status
```

`run status` uses the current noun's routine table. Qualified calls bind `this`
to the named owner.

Routine parameters and return values are not implemented. A routine should use
persistent state and locals that it declares itself; compile-time validation
does not allow a routine to depend on a particular calling verb's arguments or
locals.

Direct and indirect local routine recursion are compile-time errors. Runtime
call depth is limited to 32 as a second safety boundary.

## 13. Local Variables

Syntax:

```muse
let <name> = <expression>
```

Example:

```muse
let burn = clamp(amount, 0, this.fuel)
let lift = burn / 5
```

A local exists only during the current verb or routine invocation. It is not
persisted. `set` may reassign an existing local:

```muse
let bonus = 0
set bonus = 5
```

Locals cannot shadow arguments, namespace roots, safe built-ins, reserved
Boolean words, another local in the same block, or a declared noun ID. Branch
locals do not become available after the branch.

## 14. Expressions

Expressions may be used in `let`, `set`, `if`, `elif`, and interpolation.

### 14.1 Primary Expressions

- scalar literals;
- local and argument references;
- state references;
- parentheses;
- safe function calls;
- the standalone `have <object_id>` predicate.

The `have` predicate is presently accepted only when it forms the complete
expression, not as one term inside a larger Boolean expression.

### 14.2 Operators

Precedence from highest to lowest:

1. Parentheses, references, and function calls.
2. Unary `not` and unary `-`.
3. `*`, `/`, `//`, `%`.
4. `+`, `-`.
5. `==`, `!=`, `>`, `>=`, `<`, `<=`.
6. `and`.
7. `or`.

Boolean `and` and `or` short-circuit from left to right. Chained comparisons
such as `0 < amount < 100` are not implemented; write two comparisons joined
with `and`.

Arithmetic operators require finite numeric operands. `+` is numeric addition,
not string concatenation. Division or modulo by zero is a safe runtime error and
causes the MuseLang-managed command effects to roll back.

## 15. Safe Built-in Functions

| Function | Meaning |
|---|---|
| `min(a, ...)` | minimum value |
| `max(a, ...)` | maximum value |
| `abs(x)` | absolute value |
| `clamp(x, low, high)` | inclusive range clamp |
| `round(x)` | nearest integer, halves away from zero |
| `floor(x)` | next integer downward |
| `ceil(x)` | next integer upward |
| `random_int(low, high)` | inclusive integer choice |
| `random_chance(percent)` | Boolean percentage test, 0 through 100 |
| `random_choice(a, ...)` | choose one supplied scalar value |

Built-in arity is checked statically where possible. Random calls use the
scenario owner's persisted PRNG state.

## 16. String Interpolation

Quoted `say` and `hint` text may contain expressions in braces:

```muse
say "Turn: {this.turn}"
say "Impact speed: {abs(this.velocity)} m/s"
say "Player score: {player.score}"
```

Use doubled braces for literal braces:

```muse
say "Use braces like this: {{example}}."
```

Unmatched or empty interpolation braces are compile-time errors. Conditional
text inside a string is not supported; use an ordinary `if` statement.

## 17. Statements

### 17.1 Conditional Statements

```muse
if <expression>
  <statements>
elif <expression>
  <statements>
else
  <statements>
```

`elif` and `else` are optional. The first truthy branch executes.

### 17.2 Assignment

```muse
set <target> = <expression>
set <target> += <expression>
set <target> -= <expression>
```

Qualified targets mutate persistent state. Unqualified targets must name an
existing local. Arguments and `real.*` are read-only. Object state accessed by
`this.*` or a noun ID must have been declared on that noun.

Compound assignment requires an existing numeric value.

### 17.3 Text Output

```muse
say "Normal message."
hint "Guidance message."
```

Both currently use the caller's normal message channel. Output is buffered
until successful completion of the command.

### 17.4 Routine Invocation

```muse
run status
run lander.status
```

### 17.5 Movement

```muse
move player to surface
move sample_capsule to laboratory
```

The object and destination must resolve. The destination currently needs only
to be a declared noun; category validation is not yet enforced.

### 17.6 Achievements

```muse
achieve panel_unlocked
```

### 17.7 Flow Control

`stop` returns immediately from the current program and is normally used to
reject a command. `end` also returns immediately and is retained as a distinct
runtime result for integration contexts. Neither terminates the shared world.

### 17.8 Registered Tier 3 Calls

```muse
call museum.handlers.activate_relay
```

The target must have been explicitly registered by trusted Python code. The
runtime does not dynamically import arbitrary source targets.

Effects performed inside a registered Python handler are external to the
MuseLang transaction and cannot in general be rolled back or deterministically
replayed. Handlers should validate before producing irreversible effects.

## 18. Turn Lifecycle and Transactions

MuseLang3 does not increment turns automatically. An author advances a turn by
changing state in the appropriate successful verb:

```muse
set this.turn += 1
```

A standard command invocation proceeds as follows:

1. Establish caller, noun, scenario, team, world, and real-value owners.
2. Parse and convert typed arguments.
3. Snapshot MuseLang-managed state, movement, achievements, output, and PRNG.
4. Execute the structured statement program.
5. Commit buffered output and persist the ending PRNG state on success.
6. Restore the starting MuseLang-managed effects on a runtime failure.

`stop` and `end` are successful control-flow results; they do not cause
rollback. Invalid argument conversion and runtime exceptions do.

The transaction is an application-level interpreter transaction, not a general
database transaction. Concurrent commands against one shared scenario owner
are not revision-locked in profile 0.1. Tier 3 handler side effects are outside
the rollback boundary.

## 19. Determinism and Replay

The runtime uses Python's version-dependent `random.Random` implementation with
a stored state per scenario owner. Profile 0.1 therefore provides repeatability
within the supported Python runtime, but does not yet promise a language-level
PRNG algorithm stable across all future Python versions.

The initial seed defaults to `0` unless trusted runtime configuration supplies
the scenario owner's `muse3/random_seed`. After each successful command, the
Evennia adapter writes `muse3/random_state` on the scenario owner.

The runtime can produce an in-memory replay record containing:

- verb and final invocation locals, including bound arguments;
- starting seed;
- random results;
- MuseLang-managed mutations and moves;
- messages;
- achieved goals.

Replay records are not yet persisted automatically by the Evennia adapter and
do not capture Tier 3 handler effects.

## 20. Compilation and Runtime Artifacts

The compiler emits canonical JSON with:

```json
{
  "language_version": "3.0",
  "bundle_schema": 3,
  "runtime_api": 3
}
```

Expressions, templates, statements, routine bodies, verb arguments, defaults,
and source locations are stored as structured metadata. No authored Python
source is generated.

`prod` additionally emits an Evennia batch file. The batch file creates the
implemented rooms, objects, and characters; writes state and scenario metadata
to the `muse3` attribute category; and attaches
`behaviours.muselang.scenario_verbs.ScenarioVerbCmdSet`.

The reusable runtime is installed under:

```text
<game-root>/behaviours/muselang
```

Compiling and runtime installation do not import the authored batch content.
An Evennia administrator must run the emitted batch file separately.

## 21. Validation Requirements

Profile 0.1 validates at least:

1. duplicate noun and goal IDs;
2. unknown room locations and type labels;
3. duplicate noun aliases;
4. duplicate routines and verbs;
5. unknown or misplaced argument types;
6. duplicate or reserved argument and local names;
7. use of undeclared locals and object state;
8. assignment to arguments or `real.*`;
9. unknown namespace roots, goals, routine owners, and routines;
10. direct and indirect local routine recursion;
11. safe built-in arity;
12. statically invalid `random_chance` percentages;
13. malformed or disallowed expression AST forms;
14. unmatched and empty interpolation braces;
15. invalid movement references.

Errors include a source path, line, and column where available.

## 22. Implemented Non-Goals

Profile 0.1 deliberately excludes:

- `while`, `until`, and other unbounded general loops;
- maps, comprehensions, and user-defined data structures;
- arbitrary Python syntax or `eval`;
- recursive routines;
- routine parameters and return values;
- free-form command grammars;
- native-client or real-time update loops;
- hardware and network protocol syntax;
- imports and modules in authored source.

## 23. Planned but Not Implemented in Profile 0.1

The wider MuseLang3 design discusses the following. They remain future work:

- author-defined types and inheritance;
- exits, nested rooms, containers, supporters, and parts as enforced world
  relationships;
- portable and visible properties;
- rules, before rules, after rules, and lifecycle events;
- game-time declarations, durations, timers, and automatic turns;
- dialogue trees, options, hotkeys, and topics;
- random description blocks and multiline text blocks;
- tags, conditional descriptions, and curated verb enforcement;
- direct live-world apply and migration tooling;
- persistent replay journals and optimistic concurrency control.

These items remain useful design direction, but documentation and authored
content must distinguish them from implemented syntax.

## 24. Acceptance Scenarios

The implemented language is verified against:

1. a combination lock with typed numeric input and a persistent attempt limit;
2. a dice puzzle using deterministic random values;
3. a per-player score counter;
4. a shared world power switch;
5. a turn-by-turn Lunar Lander using arithmetic, locals, routines, movement,
   interpolation, and goals;
6. a per-player quiz with achievement persistence;
7. rollback after a later runtime failure;
8. PRNG continuation across command contexts;
9. rejection of loops, recursion, invalid random percentages, read-only writes,
   and undeclared state.

Runnable examples are provided in `V3/examples`.
