# MuseLang3 Keyword Reference Manual

| Field | Value |
|---|---|
| Edition | Implemented profile 0.1 |
| Language version | 3.0 |

This manual is an alphabetical reference to every keyword, reserved namespace
word, word operator, Boolean literal, and intrinsic function in the implemented
MuseLang3 language. Its organisation follows the spirit of classic Microsoft
BASIC reference manuals: find the word alphabetically, then consult its syntax,
purpose, remarks, examples, and related entries.

For a tutorial introduction, see `MuseLang3_Author_Manual.md`. For normative
runtime semantics, see `MuseLang_spec_v3.md`.

## How to Read an Entry

Notation used in syntax lines:

- `<name>` means an author-supplied item.
- `[item]` means an optional item.
- `...` means the preceding form may be repeated.
- Literal punctuation and keywords appear exactly as written.

Examples are sometimes fragments intended to appear inside the room, object,
routine, or verb shown by their surrounding context.

## Alphabetical Index

| A–C | D–M | N–S | T–Z |
|---|---|---|---|
| `abs` | `desc` | `not` | `team` |
| `achieve` | `description` | `obj` | `this` |
| `alias` | `elif` | `object` | `to` |
| `and` | `else` | `or` | `true` |
| `call` | `end` | `player` | `verb` |
| `ceil` | `false` | `random_chance` | `world` |
| `char` | `floor` | `random_choice` |  |
| `character` | `from` | `random_int` |  |
| `clamp` | `game` | `real` |  |
|  | `goal` | `room` |  |
|  | `have` | `round` |  |
|  | `hint` | `routine` |  |
|  | `if` | `run` |  |
|  | `in` | `say` |  |
|  | `let` | `scenario` |  |
|  | `max` | `set` |  |
|  | `min` | `state` |  |
|  | `move` | `stop` |  |

---

## ABS

**Kind:** Intrinsic numeric function

**Syntax**

```muse
abs(<numeric_expression>)
```

**Purpose**

Returns the non-negative magnitude of a number.

**Remarks**

`abs` accepts exactly one finite integer or floating-point value. Supplying a
Boolean, string, unresolved value, or non-finite number causes a safe runtime
error. It is commonly used when direction is stored in a sign but only speed or
distance magnitude matters.

**Examples**

```muse
let impact_speed = abs(this.velocity)
say "Impact speed: {impact_speed} m/s."
```

```muse
if abs(this.temperature_error) <= 2
  say "Temperature is within tolerance."
```

**See also:** `ceil`, `floor`, `round`, `min`, `max`

---

## ACHIEVE

**Kind:** Statement keyword

**Syntax**

```muse
achieve <goal_id>
```

**Purpose**

Awards a declared goal to the current player.

**Remarks**

The goal must have been declared at top level with `goal`. The runtime persists
the goal ID in the player's `muse3/achievements` state. Re-awarding a goal does
not add a duplicate stored ID. The achievement is included in the command's
MuseLang replay information and is rolled back if the command later fails.

**Examples**

```muse
goal panel_unlocked
  desc "Unlock the test panel."

object panel in laboratory from device
  state solved = false
  verb solve
    set this.solved = true
    achieve panel_unlocked
```

```muse
if abs(this.velocity) <= this.safe_velocity
  achieve safe_landing
  move player to surface
```

**See also:** `goal`, `if`, `player`

---

## ALIAS

**Kind:** Noun declaration keyword

**Syntax**

```muse
alias <alias_value> [<alias_value> ...]
```

**Purpose**

Adds alternative player-facing names to a room, object, or character.

**Remarks**

Write aliases inside the noun block. A one-word alias may be unquoted;
multiword aliases must be quoted. Duplicate aliases on one noun are rejected
case-insensitively. Profile 0.1 does not support `alias` inside a verb block, so
it cannot yet define alternate verb command words.

**Examples**

```muse
object lander_console in orbit from device
  alias console lander
```

```muse
character curator in gallery "Museum Curator"
  alias guide "museum guide"
```

**See also:** `object`, `character`, `room`, `verb`

---

## AND

**Kind:** Boolean word operator

**Syntax**

```muse
<left_expression> and <right_expression>
```

**Purpose**

Produces true only when both operands are truthy.

**Remarks**

`and` evaluates left to right and short-circuits: when the left operand is
false, the right operand is not evaluated. It has higher precedence than `or`
and lower precedence than comparisons. Use parentheses where grouping might be
unclear. The special `have` predicate cannot currently be nested as one operand
of `and`.

**Examples**

```muse
if this.active and this.fuel > 0
  say "The lander is ready."
```

```muse
if amount >= 0 and amount <= 100
  say "Thrust accepted."
```

**See also:** `if`, `not`, `or`, `true`, `false`

---

## CALL

**Kind:** Statement keyword

**Syntax**

```muse
call <registered_target>
```

**Purpose**

Invokes a Tier 3 handler registered by trusted Python runtime code.

**Remarks**

`call` is the escape route for hardware integration, network activity, and
specialised behaviour that does not belong in the bounded language. The target
is conventionally a dotted name. MuseLang3 does not import arbitrary authored
targets; the exact target must exist in the trusted handler registry.

External handler effects are outside MuseLang3 rollback and deterministic
replay. A handler should validate first and be idempotent where practical.

**Examples**

```muse
verb activate
  if not this.enabled
    say "The exhibit is disabled."
    stop
  call museum.handlers.activate_exhibit
```

```muse
verb ring_bell
  call world.hardware.ring_bell
  say "The bell command has been sent."
```

**See also:** `stop`, `verb`

---

## CEIL

**Kind:** Intrinsic numeric function

**Syntax**

```muse
ceil(<numeric_expression>)
```

**Purpose**

Returns the least integer greater than or equal to its argument.

**Remarks**

`ceil` accepts exactly one finite number. For positive values it rounds upward;
for negative values it moves toward positive infinity.

**Examples**

```muse
let crates_needed = ceil(this.parts / this.crate_capacity)
```

```muse
say "Allow {ceil(this.minutes_remaining)} whole minutes."
```

**See also:** `floor`, `round`, `abs`

---

## CHAR

**Kind:** Declaration alias and argument type name

**Syntax**

```muse
char <character_id> in <room_id> [from <type_id>] ["Display Name"]
<name:char>
```

**Purpose**

Provides the short form of `character`; in an argument declaration it requests
an accessible object reference intended to represent a character.

**Remarks**

As a declaration keyword, `char` is exactly synonymous with `character`. As an
argument type, profile 0.1 resolves an accessible object but does not yet
enforce that the resolved object is specifically a character.

**Examples**

```muse
char curator in gallery "Museum Curator"
  alias guide
```

```muse
verb identify <person:char>
  say "The selected person is {person}."
```

**See also:** `character`, `in`, `from`, Appendix A

---

## CHARACTER

**Kind:** Top-level declaration keyword

**Syntax**

```muse
character <character_id> in <room_id> [from <type_id>] ["Display Name"]
```

**Purpose**

Declares a character located in an existing room.

**Remarks**

A character may contain `alias`, `desc`/`description`, local `state`,
`routine`, and `verb` declarations. Dialogue syntax is not implemented in
profile 0.1. The short form is `char`.

**Examples**

```muse
character curator in gallery "Museum Curator"
  desc "The curator is arranging a display."
```

```muse
character technician in laboratory from thing
  state busy = false
  verb status
    say "Technician busy: {this.busy}."
```

**See also:** `char`, `room`, `in`, `from`, `object`

---

## CLAMP

**Kind:** Intrinsic numeric function

**Syntax**

```muse
clamp(<value>, <low>, <high>)
```

**Purpose**

Restricts a value to an inclusive lower and upper bound.

**Remarks**

`clamp` accepts exactly three comparable values. Scenario code normally uses
numbers and supplies a lower bound no greater than the upper bound. The function
returns `low` when the value is below the range, `high` when above it, and the
original value otherwise.

**Examples**

```muse
let burn = clamp(amount, 0, this.fuel)
set this.fuel -= burn
```

```muse
set player.score = clamp(player.score + bonus, 0, 100)
```

**See also:** `min`, `max`, `let`, `set`

---

## DESC

**Kind:** Description declaration keyword

**Syntax**

```muse
desc "<text>"
```

**Purpose**

Assigns inline descriptive text to a room, object, character, or goal.

**Remarks**

`desc` is the short form of `description`. In profile 0.1 the quoted text must
appear on the same physical line. Description interpolation, conditional
descriptions, multiline description blocks, and `desc random` are not
implemented.

**Examples**

```muse
room laboratory "Laboratory"
  desc "A practical workroom filled with test equipment."
```

```muse
goal safe_landing
  desc "Land safely on the planet."
```

**See also:** `description`, `room`, `object`, `character`, `goal`

---

## DESCRIPTION

**Kind:** Description declaration keyword

**Syntax**

```muse
description "<text>"
```

**Purpose**

Provides the long form of `desc`.

**Remarks**

For rooms, objects, and characters, `description` and `desc` are synonyms. Goal
children currently require the short `desc` form in the implemented parser.
The inline-only limitations described under `desc` also apply.

**Examples**

```muse
object terminal in laboratory from device
  description "A battered terminal with yellowed keys."
```

```muse
character guide in gallery
  description "A volunteer wearing an ACMS badge."
```

**See also:** `desc`, `object`, `character`, `room`

---

## ELIF

**Kind:** Conditional statement keyword

**Syntax**

```muse
if <expression>
  <statements>
elif <expression>
  <statements>
[else
  <statements>]
```

**Purpose**

Tests another condition when all preceding `if` or `elif` conditions were
false.

**Remarks**

Any number of `elif` branches may follow an `if`. They must align with the
matching `if`. At most one branch executes: the first whose expression is
truthy. `elif` cannot begin a conditional by itself.

**Examples**

```muse
if guess == this.code
  say "Correct."
elif this.attempts >= 3
  say "No attempts remain."
else
  say "Try again."
```

```muse
if this.temperature > 100
  say "Too hot."
elif this.temperature < 0
  say "Too cold."
else
  say "Temperature is normal."
```

**See also:** `if`, `else`, `and`, `or`, `not`

---

## ELSE

**Kind:** Conditional statement keyword

**Syntax**

```muse
if <expression>
  <statements>
[elif <expression>
  <statements> ...]
else
  <statements>
```

**Purpose**

Provides a fallback branch when every preceding condition is false.

**Remarks**

Only one `else` may occur and it must be last. It has no expression. Align it
with its matching `if`.

**Examples**

```muse
if this.powered
  say "The display glows."
else
  say "The display is dark."
```

```muse
if value == 8
  set player.score += 1
else
  say "That answer is not correct."
```

**See also:** `if`, `elif`

---

## END

**Kind:** Flow-control statement keyword

**Syntax**

```muse
end
```

**Purpose**

Returns immediately from the current MuseLang execution pipeline with the
distinct `ended` result.

**Remarks**

`end` is runtime flow control, not a structural block terminator. Indentation
ends `if`, verb, and routine blocks. Like `stop`, `end` is a successful result:
effects performed before it are committed. It does not end the shared world or
complete a story. Most ordinary verbs should use `stop` for early rejection and
need not use `end`.

**Examples**

```muse
if this.complete
  say "The sequence is already complete."
  end
```

```muse
routine report_once
  say "Report complete."
  end
```

**See also:** `stop`, `if`, `achieve`

---

## FALSE

**Kind:** Boolean literal

**Syntax**

```muse
false
```

**Purpose**

Represents the Boolean value false.

**Remarks**

`false` may initialise state, appear in expressions, and be assigned to state
or locals. It is reserved and cannot be used as an argument or local name.

**Examples**

```muse
state powered = false
state disabled = false
```

```muse
set this.active = false
say "Active: {this.active}."
```

**See also:** `true`, `not`, `and`, `or`, `state`, `set`

---

## FLOOR

**Kind:** Intrinsic numeric function

**Syntax**

```muse
floor(<numeric_expression>)
```

**Purpose**

Returns the greatest integer less than or equal to its argument.

**Remarks**

`floor` accepts exactly one finite number. For negative values it moves toward
negative infinity.

**Examples**

```muse
let full_units = floor(this.resource / this.unit_size)
```

```muse
say "Completed whole hours: {floor(this.elapsed_hours)}."
```

**See also:** `ceil`, `round`, `abs`

---

## FROM

**Kind:** Declaration connective keyword

**Syntax**

```muse
object <id> in <room_id> from <type_id> ["Display Name"]
character <id> in <room_id> from <type_id> ["Display Name"]
```

**Purpose**

Records the type label associated with an object or character.

**Remarks**

Profile 0.1 recognises the built-in labels `thing`, `device`, `container`,
`supporter`, `door`, `key`, and `portable_item`, as well as declared noun IDs.
It records `type_id` in the compiled bundle but does not yet implement
author-defined type blocks or inherited properties.

**Examples**

```muse
object console in gallery from device
```

```muse
character technician in laboratory from thing "Service Technician"
```

**See also:** `object`, `character`, `in`

---

## GAME

**Kind:** Reserved state namespace alias

**Syntax**

```muse
game.<state_name>
```

**Purpose**

Provides an author-friendly alias for the `scenario` state namespace.

**Remarks**

The compiler normalises a top-level `game.*` default to `scenario.*` in the
bundle. At runtime both roots select the current scenario owner, which is the
object exposing the verb in the standard adapter. Prefer `scenario` in new
source when the state describes a puzzle or interaction rather than a whole
game.

**Examples**

```muse
state game.turn = 0
```

```muse
set game.turn += 1
say "Turn: {game.turn}."
```

**See also:** `scenario`, `state`, `this`, `player`, `world`

---

## GOAL

**Kind:** Top-level declaration keyword

**Syntax**

```muse
goal <goal_id>
  [desc "<description>"]
```

**Purpose**

Declares an achievement target that may later be awarded with `achieve`.

**Remarks**

Goal IDs must be unique. A goal may have one optional `desc` child. The long
`description` spelling is not accepted inside a goal in profile 0.1. Declaring
a goal does not automatically award it.

**Examples**

```muse
goal safe_landing
  desc "Land safely on the planet."
```

```muse
goal panel_unlocked

object panel in laboratory from device
  verb solve
    achieve panel_unlocked
```

**See also:** `achieve`, `desc`, `player`

---

## HAVE

**Kind:** Inventory predicate keyword

**Syntax**

```muse
have <object_id>
```

**Purpose**

Tests whether the current player's immediate contents include an object with
the named ID or alias.

**Remarks**

In profile 0.1, `have` must form the complete condition. It cannot yet be used
as one nested term in a larger `and`/`or` expression. The check examines the
player's immediate contents, not recursive contents inside carried containers.

**Examples**

```muse
if have badge
  say "You are carrying the badge."
```

```muse
if have access_key
  set this.locked = false
else
  say "You need the access key."
```

**See also:** `if`, `player`, `and`, `or`

---

## HINT

**Kind:** Text-output statement keyword

**Syntax**

```muse
hint "<interpolated_text>"
```

**Purpose**

Sends guidance text to the current player.

**Remarks**

`hint` accepts the same interpolation syntax as `say`. In profile 0.1 both use
the caller's normal message channel, although the separate opcode permits a
future client or narrator to render hints differently. Output is buffered until
the command succeeds.

**Examples**

```muse
hint "Use THRUST followed by a number from 0 to 100."
```

```muse
hint "Fuel remaining: {this.fuel}."
```

**See also:** `say`, `verb`, `stop`

---

## IF

**Kind:** Conditional statement keyword

**Syntax**

```muse
if <expression>
  <statements>
[elif <expression>
  <statements> ...]
[else
  <statements>]
```

**Purpose**

Executes statements conditionally.

**Remarks**

The first truthy branch executes. Indentation defines each branch. There is no
structural `end if`. Locals declared within a branch remain confined to that
branch. The `have` predicate is accepted as a complete condition.

**Examples**

```muse
if not this.active
  say "The game is not active."
  stop
```

```muse
if roll == 6
  set this.solved = true
  achieve panel_unlocked
else
  say "Nothing else happens."
```

**See also:** `elif`, `else`, `and`, `not`, `or`, `stop`

---

## IN

**Kind:** Declaration connective keyword

**Syntax**

```muse
object <object_id> in <room_id> ...
character <character_id> in <room_id> ...
```

**Purpose**

Names the initial room containing an object or character.

**Remarks**

The room must already be declared somewhere in the combined source document.
Profile 0.1 requires objects and characters to start in rooms. It does not yet
support authored `in` placement inside containers or use `in` as an expression
predicate.

**Examples**

```muse
object test_panel in laboratory from device
```

```muse
character curator in gallery "Museum Curator"
```

**See also:** `object`, `character`, `room`, `from`, `move`, `to`

---

## LET

**Kind:** Local-declaration statement keyword

**Syntax**

```muse
let <local_name> = <expression>
```

**Purpose**

Calculates and stores a temporary value for the current invocation.

**Remarks**

A local is not persisted. It exists within the current verb, routine, or branch
scope. Use `set` to reassign an already declared local. A local cannot shadow an
argument, reserved namespace, Boolean word, intrinsic function, declared noun
ID, or another local in the same scope.

**Examples**

```muse
let burn = clamp(amount, 0, this.fuel)
let lift = burn / 5
```

```muse
let bonus = 0
if player.score >= 10
  set bonus = 5
set player.score += bonus
```

**See also:** `set`, `verb`, `routine`, `if`

---

## MAX

**Kind:** Intrinsic comparison function

**Syntax**

```muse
max(<expression> [, <expression> ...])
```

**Purpose**

Returns the greatest supplied value.

**Remarks**

At least one argument is required. Values must be mutually comparable at
runtime. Numeric use is recommended for scenario calculations.

**Examples**

```muse
let visible_score = max(player.score, 0)
```

```muse
set this.highest_roll = max(this.highest_roll, roll)
```

**See also:** `min`, `clamp`, `abs`

---

## MIN

**Kind:** Intrinsic comparison function

**Syntax**

```muse
min(<expression> [, <expression> ...])
```

**Purpose**

Returns the least supplied value.

**Remarks**

At least one argument is required. Values must be mutually comparable at
runtime. Use `clamp` when both a lower and upper bound must be enforced.

**Examples**

```muse
let burn = min(amount, this.fuel)
```

```muse
set this.lowest_temperature = min(this.lowest_temperature, reading)
```

**See also:** `max`, `clamp`, `abs`

---

## MOVE

**Kind:** Statement keyword

**Syntax**

```muse
move player to <destination_id>
move <noun_id> to <destination_id>
```

**Purpose**

Moves the current player or a declared noun to a resolved destination.

**Remarks**

The source and destination must resolve. Profile 0.1 does not yet enforce that
the destination is specifically a room or container. Movement performed by
this statement is included in MuseLang rollback if a later runtime error occurs.

**Examples**

```muse
move player to surface
```

```muse
move sample_capsule to laboratory
say "The capsule has been returned."
```

**See also:** `to`, `in`, `room`, `player`

---

## NOT

**Kind:** Unary Boolean word operator

**Syntax**

```muse
not <expression>
```

**Purpose**

Reverses the truth value of an expression.

**Remarks**

`not` has higher precedence than multiplication, addition, comparisons,
`and`, and `or`. It is reserved and cannot be used as an argument or local
name.

**Examples**

```muse
if not this.active
  say "The game is stopped."
```

```muse
let unavailable = not world.exhibit_power
```

**See also:** `and`, `or`, `if`, `true`, `false`

---

## OBJ

**Kind:** Top-level declaration alias

**Syntax**

```muse
obj <object_id> in <room_id> [from <type_id>] ["Display Name"]
```

**Purpose**

Provides the short form of `object`.

**Remarks**

`obj` and `object` are exactly synonymous as declaration keywords. The longer
form is usually clearer in manuals and new source.

**Examples**

```muse
obj key in laboratory from key
```

```muse
obj console in gallery from device "Exhibit Console"
  alias panel
```

**See also:** `object`, `in`, `from`

---

## OBJECT

**Kind:** Top-level declaration keyword and argument type name

**Syntax**

```muse
object <object_id> in <room_id> [from <type_id>] ["Display Name"]
<name:object>
```

**Purpose**

Declares a non-character world noun; as an argument type, resolves an accessible
object reference.

**Remarks**

An object may contain aliases, an inline description, local state, routines,
and verbs. Its initial location must be a declared room. Object arguments are
resolved at runtime and make the object available as a value, although most
profile 0.1 statements still identify movement targets statically by ID.

**Examples**

```muse
object lander in orbit from device
  state fuel = 500
```

```muse
verb inspect_target <target:object>
  say "A target was selected."
```

**See also:** `obj`, `character`, `room`, `in`, `from`, Appendix A

---

## OR

**Kind:** Boolean word operator

**Syntax**

```muse
<left_expression> or <right_expression>
```

**Purpose**

Produces true when either operand is truthy.

**Remarks**

`or` evaluates left to right and short-circuits: when the left operand is true,
the right operand is not evaluated. It has lower precedence than `and`. The
special `have` predicate cannot currently be nested as one operand of `or`.

**Examples**

```muse
if this.disabled or not world.exhibit_power
  say "The exhibit is unavailable."
```

```muse
if amount < 0 or amount > 100
  say "Amount must be between 0 and 100."
  stop
```

**See also:** `and`, `not`, `if`, `true`, `false`

---

## PLAYER

**Kind:** Reserved state namespace and movement source

**Syntax**

```muse
player.<state_name>
move player to <destination_id>
```

**Purpose**

Refers to state owned by the current player, or to the player as the source of
a movement statement.

**Remarks**

Declare player defaults at top level. Each player receives an independent
value. The namespace is reserved and cannot be used as an argument or local
name.

**Examples**

```muse
state player.score = 0

verb award
  set player.score += 10
  say "Score: {player.score}."
```

```muse
if this.landed
  move player to surface
```

**See also:** `state`, `scenario`, `team`, `world`, `move`, `achieve`

---

## RANDOM_CHANCE

**Kind:** Intrinsic random function

**Syntax**

```muse
random_chance(<percentage>)
```

**Purpose**

Returns true with the supplied percentage probability.

**Remarks**

The percentage must be numeric and between 0 and 100 inclusive. A constant
outside that range is rejected during validation; a calculated invalid value is
a safe runtime error. The function advances the scenario owner's PRNG only when
it is actually evaluated. Boolean short-circuiting can therefore affect the
random sequence.

**Examples**

```muse
if random_chance(25)
  say "A warning lamp flickers."
```

```muse
let success = random_chance(this.success_percent)
if success
  set this.solved = true
```

**See also:** `random_int`, `random_choice`, `if`, `scenario`

---

## RANDOM_CHOICE

**Kind:** Intrinsic random function

**Syntax**

```muse
random_choice(<expression> [, <expression> ...])
```

**Purpose**

Returns one randomly selected supplied value.

**Remarks**

At least one argument is required. The function chooses uniformly by argument
position. Use scalar values that can be stored or displayed by the scenario.

**Examples**

```muse
set this.weather = random_choice("clear", "cloudy", "rain")
```

```muse
let message_number = random_choice(1, 2, 3)
say "Selected message {message_number}."
```

**See also:** `random_int`, `random_chance`, `set`, `let`

---

## RANDOM_INT

**Kind:** Intrinsic random function

**Syntax**

```muse
random_int(<low>, <high>)
```

**Purpose**

Returns a uniformly selected integer in an inclusive range.

**Remarks**

Both endpoints are converted to integers by the runtime. The low endpoint must
not exceed the high endpoint. The result and changed PRNG state are rolled back
if the command later fails.

**Examples**

```muse
let roll = random_int(1, 6)
say "The die rolls {roll}."
```

```muse
set player.score += random_int(1, 10)
```

**See also:** `random_chance`, `random_choice`, `let`, `set`

---

## REAL

**Kind:** Read-only state namespace

**Syntax**

```muse
real.now
real.date
real.time
```

**Purpose**

Reads the real-world date and time snapshot supplied for the current command.

**Remarks**

The standard Evennia adapter snapshots these three values once when the command
begins. `real.*` cannot be declared or assigned. Using real time makes replay
depend on captured external inputs; profile 0.1 replay records do not yet
persist these values automatically.

**Examples**

```muse
say "Today's date is {real.date}."
```

```muse
say "The command began at {real.time}."
```

**See also:** `world`, `scenario`, `say`, `state`

---

## ROOM

**Kind:** Top-level declaration keyword and argument type name

**Syntax**

```muse
room <room_id> ["Display Name"]
<name:room>
```

**Purpose**

Declares a room; as an argument type, resolves an accessible object intended to
represent a room.

**Remarks**

Rooms are flat in profile 0.1. They may contain aliases, an inline description,
local state, routines, and verbs. Exit and nested-room syntax is not
implemented. A `room` argument currently resolves an accessible object without
enforcing its kind.

**Examples**

```muse
room orbit "Command Module"
  desc "The planet fills the lower viewport."
```

```muse
verb select_room <destination:room>
  say "A destination was selected."
```

**See also:** `object`, `character`, `in`, `move`, Appendix A

---

## ROUND

**Kind:** Intrinsic numeric function

**Syntax**

```muse
round(<numeric_expression>)
```

**Purpose**

Returns the nearest integer.

**Remarks**

Half values round away from zero: `round(2.5)` is 3 and `round(-2.5)` is -3.
This differs from Python's ordinary built-in `round`, which is not exposed
directly. Exactly one finite number is required.

**Examples**

```muse
let displayed_speed = round(abs(this.velocity))
```

```muse
say "Average score: {round(this.total / this.count)}."
```

**See also:** `floor`, `ceil`, `abs`

---

## ROUTINE

**Kind:** Noun child declaration keyword

**Syntax**

```muse
routine <routine_id>
  <statements>
```

**Purpose**

Declares a reusable object-local statement block that is not a player command.

**Remarks**

Routines have no parameters or return values. They are validated independently
and cannot depend on a calling verb's arguments or locals. Use declared state
and routine-local `let` values. Direct and indirect local recursion are rejected;
runtime call depth is also limited to 32.

**Examples**

```muse
routine status
  say "Fuel: {this.fuel}."
  say "Turn: {this.turn}."
```

```muse
routine reset
  set this.score = 0
  set this.turn = 0
```

**See also:** `run`, `verb`, `let`, `this`

---

## RUN

**Kind:** Statement keyword

**Syntax**

```muse
run <routine_id>
run this.<routine_id>
run <noun_id>.<routine_id>
```

**Purpose**

Invokes a declared routine.

**Remarks**

An unqualified call uses the current noun's routine table. A qualified call
binds `this` to the named owner while the routine executes. A `stop` or `end`
inside the routine propagates to the calling program.

**Examples**

```muse
verb status
  run status_report
```

```muse
verb inspect_lander
  run lander.status
```

**See also:** `routine`, `this`, `stop`, `end`

---

## SAY

**Kind:** Text-output statement keyword

**Syntax**

```muse
say "<interpolated_text>"
```

**Purpose**

Sends normal scenario text to the current player.

**Remarks**

Expressions inside `{` and `}` are evaluated and converted to text. Use `{{`
and `}}` for literal braces. Output is buffered until successful command
completion and discarded on a later runtime error. Multiline and `say random`
forms are not implemented.

**Examples**

```muse
say "Fuel: {this.fuel} units."
```

```muse
say "Use braces like this: {{example}}."
```

**See also:** `hint`, `if`, `real`

---

## SCENARIO

**Kind:** Reserved state namespace

**Syntax**

```muse
scenario.<state_name>
```

**Purpose**

Reads or writes state owned by the current scenario context.

**Remarks**

In the standard profile 0.1 Evennia adapter, the object exposing the verb is
the scenario owner. Thus `scenario.*` and `this.*` normally select the same
physical object during an object verb, although they express different author
intent. `game` is an alias. A future scenario-instance service may change the
owner without changing source syntax.

**Examples**

```muse
state scenario.turn = 0
```

```muse
set scenario.turn += 1
say "Scenario turn: {scenario.turn}."
```

**See also:** `game`, `this`, `player`, `team`, `world`, `state`

---

## SET

**Kind:** Assignment statement keyword

**Syntax**

```muse
set <target> = <expression>
set <target> += <expression>
set <target> -= <expression>
```

**Purpose**

Assigns a value to persistent state or reassigns an existing local.

**Remarks**

Qualified targets select state. An unqualified target must name a local already
declared with `let`. Arguments and `real.*` are read-only. `+=` and `-=` require
an existing numeric value. Object state must have been declared before it is
assigned. MuseLang-managed assignments are rolled back on a later runtime error.

**Examples**

```muse
set this.fuel -= burn
set this.turn += 1
```

```muse
let bonus = 0
set bonus = 5
set player.score += bonus
```

**See also:** `state`, `let`, `player`, `scenario`, `world`

---

## STATE

**Kind:** Declaration keyword

**Syntax**

```muse
state <local_state_name> = <literal>
state <writable_namespace>.<state_name> = <literal>
```

**Purpose**

Declares persistent scalar state and its initial value.

**Remarks**

Inside a room, object, or character, use an unqualified state name. At top
level, use `player`, `team`, `game`, `scenario`, or `world`. Initial values must
be literal Booleans, integers, floats, or strings; expressions are not allowed.
Defaults do not overwrite an existing runtime value.

`real` is read-only and cannot be declared. `this` and noun IDs are not valid
top-level declaration roots.

**Examples**

```muse
object lander in orbit from device
  state fuel = 500
  state active = false
```

```muse
state player.score = 0
state world.exhibit_power = false
```

**See also:** `set`, `this`, `player`, `team`, `scenario`, `world`

---

## STOP

**Kind:** Flow-control statement keyword

**Syntax**

```muse
stop
```

**Purpose**

Returns immediately from the current MuseLang program, normally after rejecting
a command.

**Remarks**

Statements after `stop` do not execute. `stop` is a successful scripted result,
so earlier state changes and buffered messages are committed. Place it before
turn-consuming mutations when rejection should leave the scenario unchanged.
A `stop` inside a routine propagates to its caller.

**Examples**

```muse
if not this.active
  say "Start the game first."
  stop
```

```muse
if amount < 0 or amount > 100
  say "Amount must be between 0 and 100."
  stop
set this.turn += 1
```

**See also:** `end`, `if`, `verb`, `run`

---

## TEAM

**Kind:** Reserved state namespace

**Syntax**

```muse
team.<state_name>
```

**Purpose**

Reads or writes state shared by the current player's configured team.

**Remarks**

Trusted runtime setup must assign a team object to the player's
`db.muselang_team` field. Without a team owner, reading produces no value and
writing causes a safe runtime error. Declare team defaults at top level.

**Examples**

```muse
state team.rounds_won = 0
```

```muse
set team.rounds_won += 1
say "Team wins: {team.rounds_won}."
```

**See also:** `player`, `scenario`, `world`, `state`, `set`

---

## THIS

**Kind:** Reserved state namespace and routine-owner word

**Syntax**

```muse
this.<state_name>
run this.<routine_id>
```

**Purpose**

Refers to the noun currently owning the executing verb or routine.

**Remarks**

Inside an ordinary object verb, `this` is that object. In a qualified routine
call such as `run lander.status`, `this` becomes `lander` for the routine.
State named through `this` must have been declared on the owning noun.

**Examples**

```muse
if this.fuel <= 0
  say "The tank is empty."
```

```muse
set this.active = true
run this.status
```

**See also:** `routine`, `run`, `scenario`, `state`, `set`

---

## TO

**Kind:** Movement connective keyword

**Syntax**

```muse
move <source> to <destination_id>
```

**Purpose**

Separates the movement source from its destination.

**Remarks**

`to` is currently used only by `move`. It is not accepted as part of a natural
verb grammar such as `verb give <item> to <recipient>`.

**Examples**

```muse
move player to surface
```

```muse
move capsule to laboratory
```

**See also:** `move`, `in`, `player`, `room`

---

## TRUE

**Kind:** Boolean literal

**Syntax**

```muse
true
```

**Purpose**

Represents the Boolean value true.

**Remarks**

`true` may initialise state, appear in expressions, and be assigned to state or
locals. It is reserved and cannot be used as an argument or local name.

**Examples**

```muse
state locked = true
state visible = true
```

```muse
set this.powered = true
say "Powered: {this.powered}."
```

**See also:** `false`, `not`, `and`, `or`, `state`, `set`

---

## VERB

**Kind:** Noun child declaration keyword

**Syntax**

```muse
verb <verb_name> [<argument_declaration> ...]
  <statements>
```

**Purpose**

Declares a player command attached to a room, object, or character.

**Remarks**

Arguments are positional and read-only. An omitted type means `word`.
Optional and `string` arguments must be last. The standard Evennia adapter
strips an optional target noun from the beginning or end of command arguments
before binding them. Profile 0.1 does not support verb aliases or literal
grammar words between arguments.

**Examples**

```muse
verb status
  say "Fuel: {this.fuel}."
```

```muse
verb thrust <amount:int>
  if amount < 0 or amount > 100
    say "Invalid thrust."
    stop
  set this.fuel -= amount
```

**See also:** `routine`, `let`, `set`, `stop`, Appendix A

---

## WORLD

**Kind:** Reserved state namespace

**Syntax**

```muse
world.<state_name>
```

**Purpose**

Reads or writes state shared by every player and scenario in the Evennia world.

**Remarks**

The standard adapter stores world fields through Evennia `ServerConfig` using
the `muselang.world.` key prefix. Use this scope deliberately: a write by one
player is visible to all. Declare defaults at top level.

**Examples**

```muse
state world.exhibit_power = false
```

```muse
set world.exhibit_power = true
say "Shared exhibit power: {world.exhibit_power}."
```

**See also:** `player`, `team`, `scenario`, `real`, `state`, `set`

---

## Appendix A: Verb Argument Type Specifiers

Type specifiers appear after a colon inside a verb argument declaration. They
are listed alphabetically here. They are not statement keywords.

### BOOL

Accepts exactly `true` or `false` from player input.

```muse
verb enable <value:bool>
  set this.enabled = value
```

```muse
verb set_alarm <active:bool>
  say "Alarm requested: {active}."
```

### CHAR

Resolves an accessible object intended to be a character. Character kind is not
yet enforced.

```muse
verb identify <person:char>
  say "A person was selected."
```

```muse
verb greet_target <target:char?>
  say "Greeting command accepted."
```

### FLOAT

Converts input to a floating-point number.

```muse
verb tune <frequency:float>
  set this.frequency = frequency
```

```muse
verb calibrate <offset:float>
  say "Offset: {offset}."
```

### ID

Accepts one token as an unconverted string identifier.

```muse
verb select <item_id:id>
  say "Selected ID: {item_id}."
```

```muse
verb mode <mode_id:id?>
  say "Mode request received."
```

### INT

Converts input to an integer. Decimal input such as `3.5` is rejected.

```muse
verb thrust <amount:int>
  set this.fuel -= amount
```

```muse
verb answer <value:int>
  if value == 8
    say "Correct."
```

### NUMBER

Converts input to an integer when possible, otherwise to a float when decimal or
exponent notation is present.

```muse
verb add <value:number>
  set this.total += value
```

```muse
verb measure <reading:number>
  say "Reading: {reading}."
```

### OBJECT

Resolves an accessible object of any kind.

```muse
verb inspect_target <target:object>
  say "Target resolved."
```

```muse
verb choose <target:object?>
  say "Choice recorded."
```

### ROOM

Resolves an accessible object intended to be a room. Room kind is not yet
enforced.

```muse
verb destination <place:room>
  say "Destination selected."
```

```muse
verb compare_room <place:room?>
  say "Room comparison requested."
```

### STRING

Consumes all remaining command words and joins them with spaces. It must be the
last argument.

```muse
verb enter_message <message:string>
  say "Message: {message}."
```

```muse
verb label <text:string?>
  say "Label command accepted."
```

### WORD

Accepts one word. This is the default when no type is written.

```muse
verb guess <answer:word>
  say "You guessed {answer}."
```

```muse
verb colour <name>
  say "Colour: {name}."
```

## Appendix B: Symbolic Operators

The following are operators rather than alphabetic keywords:

| Operator | Meaning | Example |
|---|---|---|
| `=` | assignment in `let` and `set` statements | `set this.score = 0` |
| `+=` | numeric compound addition | `set this.turn += 1` |
| `-=` | numeric compound subtraction | `set this.fuel -= burn` |
| `+` | numeric addition | `let total = a + b` |
| `-` | subtraction or unary negation | `let delta = a - b` |
| `*` | multiplication | `let area = width * height` |
| `/` | division | `let average = total / count` |
| `//` | integer/floor division | `let groups = total // size` |
| `%` | modulo | `let remainder = total % size` |
| `==` | equality comparison | `if guess == this.code` |
| `!=` | inequality comparison | `if value != 0` |
| `>` | greater than | `if score > 10` |
| `>=` | greater than or equal | `if score >= 10` |
| `<` | less than | `if amount < 0` |
| `<=` | less than or equal | `if speed <= this.safe_speed` |
| `( )` | expression grouping and function call | `abs(this.velocity)` |
| `{ }` | interpolation inside quoted output | `say "Score: {player.score}."` |
| `{{ }}` | literal interpolation braces | `say "Use {{name}}."` |

## Appendix C: Words Not Implemented in Profile 0.1

The wider MuseLang3 design discusses words such as `type`, `exit`, `rule`,
`before`, `after`, `on`, `time`, `dialogue`, `node`, and `option`. They are not
keywords accepted by the standalone profile 0.1 compiler. General `while`,
`until`, and `for` loops are also deliberately absent.
