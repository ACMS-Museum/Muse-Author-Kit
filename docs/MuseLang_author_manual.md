# MuseLang Author Manual

This guide is for content authors who want to create rooms, objects, characters, interactions, and dialogue in MuseLang without writing Python.

If you are looking for the formal language definition, see [MuseLang_spec.md](MuseLang_spec.md).
If you are looking for compiler and runtime details, see [MuseLang_compiler_spec.md](MuseLang_compiler_spec.md).

## What This Language Is For

MuseLang is a small authoring language for world content.

You use it to:

- create rooms
- place objects and characters
- add descriptions and aliases
- define verbs like `examine`, `open`, `scan`, or `talk`
- add simple conditions like `if have badge`
- write branching dialogue with menu choices

You do not normally use it to write raw Python. Complex runtime behavior should be handled by pre-written game code.

## Mental Model

Think of the language as describing three things:

1. What exists in the world.
2. What the player can do with it.
3. What happens when the player does it.

Example:

```text
obj panel in showroom
  desc "A brushed metal maintenance panel."

  verb examine
    say "The panel is scratched and slightly loose."

  verb open
    if panel.locked
      say "The panel is locked."
    else
      set panel.open = true
      say "You open the panel."
```

## Basic File Shape

Macro files are line-oriented. Indentation matters.

Top-level lines define things such as rooms, objects, and characters. Indented lines define their details.

If you are teaching MuseLang to a new author, you can use `object` instead of `obj`, `character` instead of `char`, and `description` instead of `desc`. `desc`, `say`, and `hint` can also continue over indented quoted lines.

Example:

```text
room showroom "ACMS Museum Showroom"

obj panel in showroom
  desc "A brushed metal maintenance panel."

char guard in showroom
  desc "A tired security guard watches the corridor."
```

MuseLang V1 can also compile a folder of source files together. This is useful
when several authors want to contribute content to one world without editing
the same file.

Example project folder:

```text
museum-project/
  01_rooms.muse
  02_objects.muse
  03_dialogue.muse
```

Compile the folder with:

```powershell
muselang prod .\museum-project
```

Folder compilation rules:

- MuseLang reads top-level `*.muse` and `*.muselang` files in alphabetical
  filename order
- all files are merged into one logical compilation unit
- ids must still be unique across the whole project
- V1 does not support splitting one room, object, character, or rule across
  multiple files by repeating its id later
- default outputs are written into the folder as
  `<foldername>.muselang.json` and `<foldername>.muselang.ev`

## Terse Syntax Summary

MuseLang is block-based and indentation-sensitive.

Top-level forms:

```text
room <id> "<display name>"
obj <id> in <room_id> ["<display name>"]
object <id> in <room_id> ["<display name>"]
char <id> in <room_id> ["<display name>"]
character <id> in <room_id> ["<display name>"]
rule <verb> <object_id> on <target_id>
rule <verb> <object_id> to <target_id>
```

Common child lines:

```text
alias <alias> [<alias> ...]
Aliases appear on a line by themselves. Multi-word aliases must be written in double quotes.
desc "<text>" or description "<text>"
desc / description followed by one or more indented quoted lines
tag <token>
state <name> = <value>
portable true|false
verb <verb_name>
  alias <alias> [<alias> ...]
dialogue <node_id>
node <node_id>
exit <exit_id> to <destination_room_id>
```

Common action lines:

```text
say "<text>"
say followed by one or more indented quoted lines
hint "<text>"
hint followed by one or more indented quoted lines
set <target> = <value>
move <object_id> to <location_id>
give <object_id> to <character_id>
goto <node_id>
call <python_path>
end
```

If you are teaching MuseLang to a new author, you can use `object` instead of `obj`, `character` instead of `char`, and `description` instead of `desc`. The shorter forms are still accepted later.

Condition syntax:

```text
if <condition>
elif <condition>
else
```

Conditions use infix boolean logic:

```text
have badge
panel.locked
not panel.open
have badge and not guard.alert
(have badge or have permit) and not guard.alert
speech >= 4
```

Dialogue option syntax:

```text
option <option_id> "<label>" -> <node_id>
option <option_id> "<label>" if <condition> -> <node_id>
```

Hotkeys are marked inside option text:

```text
option inspect "I'm here to <i>nspect the machine." -> allow_entry
```

## Rooms

Use `room` to create a room.

Syntax:

```text
room <id> "<display name>"
```

Example:

```text
room showroom "ACMS Museum Showroom"
  desc "Rows of old equipment sit under fluorescent lights."
  alias museum "display room"
```

Useful room properties:

- `desc "<text>"` or `description "<text>"`
- `desc` / `description` followed by one or more indented quoted lines
- `alias <alias> [<alias> ...]`
- Aliases appear on a line by themselves. Multi-word aliases must be written in double quotes.
- `tag <token>`
- `state <name> = <value>`

## Room Exits

Exits are authored inside the room they leave from.

Syntax:

```text
exit <exit_id> to <destination_room_id>
```

Example:

```text
room laboratory "Laboratory"
  exit showroom to showroom
```

The first `showroom` is the exit id and the default command players use. The second `showroom` is the destination room id. If the exit needs aliases, add them under the exit on separate `alias` lines.

## Objects

Use `obj` to create an object in a room.

Syntax:

```text
obj <id> in <room_id>
obj <id> in <room_id> "<display name>"
```

Example:

```text
obj panel in showroom "maintenance panel"
  alias hatch "maintenance hatch"
  desc "A brushed metal maintenance panel."
  state locked = true
  state open = false
```

Useful object properties:

- `alias <alias> [<alias> ...]`
- Aliases appear on a line by themselves. Multi-word aliases must be written in double quotes.
- `desc "<text>"`
- `tag <token>`
- `state <name> = <value>`
- `portable true`
- `portable false`

## Characters

Use `char` to create a character in a room.

Syntax:

```text
char <id> in <room_id>
char <id> in <room_id> "<display name>"
```

Example:

```text
char guard in showroom
  desc "A tired security guard watches the corridor."
  state alert = false
```

Characters can have normal verbs and dialogue.

## Descriptions, Aliases, Tags, and State

These are the most common child lines you will write.

Example:

```text
obj badge in showroom
  alias pass
  alias permit
  desc "A laminated visitor badge."
  tag security
  state valid = true
```

Use them like this:

- `alias` gives extra names players might try
- `desc` is the object's description
- `tag` is a simple label for categorization
- `state` stores flags or values used by rules and dialogue

## Verbs

Verbs define what a player can do with a room, object, or character.

Example:

```text
obj terminal in showroom
  verb examine
    say "An old terminal with a green phosphor display."

  verb read
    say "The boot screen says ACMS TERM MONITOR."
```

### Simple One-Line Verbs

If the verb only says one thing, you can write it on one line:

```text
verb examine say "An old terminal with a green phosphor display."
```

### Verb Aliases

You can give a verb extra names:

```text
verb scan
  alias analyse inspect
  say "The machine hums quietly."
```

This is useful when players might try similar words.

## Common Verb Ideas

You do not need to use every verb. Give each thing only the verbs that make sense.

Common verbs include:

- `examine`
- `read`
- `talk`
- `greet`
- `ask`
- `take`
- `open`
- `close`
- `use`
- `scan`
- `repair`

Examples:

```text
obj spanner in workshop
  verb examine
    say "A magnetic spanner with worn insulation."

  verb take
    say "You pick up the spanner."

obj robot in workshop
  verb scan
    say "Power low. Left actuator misaligned."

  verb repair
    say "You are not sure where to begin."
```

## Conditions

Conditions let you say that something only happens when certain facts are true.

Example:

```text
verb open
  if panel.locked
    say "The panel is locked."
  else
    set panel.open = true
    say "You open the panel."
```

### Useful Condition Forms

Examples:

```text
if have badge
if panel.locked
if not panel.open
if have badge and not guard.alert
if (have badge or have permit) and not guard.alert
```

Supported boolean words:

- `not`
- `and`
- `or`

Parentheses are allowed and can make logic easier to read.

## Actions

Inside verbs, rules, and dialogue nodes, you usually write actions.

Common actions:

- `say "<text>"`
- `hint "<text>"`
- `set <target> = <value>`
- `goto <node_id>`
- `end`
- `call <python_path>`

Example:

```text
verb unlock
  if have badge
    set panel.locked = false
    say "You release the lock."
  else
    hint "You may need some kind of access badge."
```

## Setting State

Use `set` to change the world state.

Examples:

```text
set panel.open = true
set panel.locked = false
set guard.cleared_you = true
set robot.repaired = true
```

Keep state names simple and descriptive.

Good examples:

- `locked`
- `open`
- `cleared_you`
- `repaired`
- `alert`

## Rules

Use `rule` when the action involves more than one thing, or when the logic is shared.

Example:

```text
rule use screwdriver on panel
  if panel.locked
    say "The panel is locked."
  else
    set panel.open = true
    say "You loosen the screws and open the panel."
```

Another example:

```text
rule give badge to guard
  say "The guard studies the badge and nods."
  set guard.cleared_you = true
```

Think of `rule` as a place for actions like:

- `use X on Y`
- `give X to Y`
- shared machine logic

## Dialogue

Dialogue is used for guided conversations, usually with characters.

Players still use normal verbs such as `talk guard`, but the `talk` behavior can open a dialogue tree.

### Basic Dialogue

Example:

```text
char guard in showroom
  dialogue start
    say "State your business."
    option inspect "I'm here to <i>nspect the machine." if have badge -> allow_entry
    option leave "<n>ever mind." -> end_leave

  node allow_entry
    say "All right, go on through."
    set guard.cleared_you = true
    end

  node end_leave
    say "Move along, then."
    end
```

### Dialogue Parts

A dialogue usually has:

- a starting node
- one or more named follow-up nodes
- NPC text with `say`
- player options with `option`
- actions like `set`, `goto`, or `end`

### Dialogue Entry Point

Use:

```text
dialogue start
```

This means the conversation begins at node `start`.

### Extra Dialogue Nodes

Use:

```text
node <node_id>
```

Example:

```text
node denied
  say "No badge, no entry."
  end
```

## Dialogue Options

Options define what the player can choose to say or do during a conversation.

Syntax:

```text
option <option_id> "<label>" -> <node_id>
option <option_id> "<label>" if <condition> -> <node_id>
```

Example:

```text
option inspect "I'm here to <i>nspect the machine." if have badge -> allow_entry
option bluff "The chief sent me." if speech >= 4 -> bluff_entry
option leave "<n>ever mind." -> end_leave
```

### Option ID

The first word after `option` is the internal option name.

Example:

```text
option inspect "I'm here to <i>nspect the machine." -> allow_entry
```

Here, `inspect` is the internal ID.

This is used by the system. It is not the visible text.

### Hotkey Markup

Use angle brackets inside the option text to mark a hotkey letter:

```text
"I'm here to <i>nspect the machine."
"<n>ever mind."
```

This tells the system what letter the player can type.

So:

```text
option inspect "I'm here to <i>nspect the machine." -> allow_entry
```

may be shown to the player as:

```text
[i] I'm here to inspect the machine.
```

Try to make each hotkey unique within one dialogue node.

## Guided and Hidden Choices

You can make a choice appear only when its condition is true.

Example:

```text
option inspect "I'm here to <i>nspect the machine." if have badge -> allow_entry
option bluff "The chief sent me." if speech >= 4 -> bluff_entry
option leave "<n>ever mind." -> end_leave
```

This lets you write:

- visible choices for everyone
- special choices for players who meet certain conditions

## Dialogue with Condition Routing

Sometimes a node should automatically branch based on state.

Example:

```text
node inspect_request
  if have badge
    goto allow_entry
  elif guard.bribed
    goto reluctant_entry
  else
    goto denied
```

This is useful when the player has already made a choice, and now the game needs to decide the outcome.

## Hints

Hints gently guide the player.

Example:

```text
verb repair
  if have spanner
    say "You tighten the actuator bracket."
    set robot.repaired = true
  else
    hint "You may need a suitable tool."
```

Hints are especially useful when:

- an object is interactive but blocked
- the player is missing a key item
- a dialogue option is meant to be discovered

## Calling Hand-Written Python

Most content should stay in MuseLang. If something is too special or too complex, call pre-written Python.

Example:

```text
verb activate
  call muse.behaviours.areas.reactor.activate_sequence
```

Use this sparingly. Prefer normal `if`, `say`, `set`, and dialogue blocks when they are enough.

## A Small Complete Example

This example shows a room, an object, and a character with dialogue.

```text
room showroom "ACMS Museum Showroom"
  desc "Rows of old equipment sit under fluorescent lights."

obj panel in showroom "maintenance panel"
  alias hatch
  desc "A brushed metal maintenance panel."
  state locked = true
  state open = false

  verb examine
    say "The panel is scratched and slightly loose."

  verb open
    if panel.locked
      say "The panel is locked."
    else
      set panel.open = true
      say "You open the panel."

char guard in showroom
  desc "A tired security guard watches the corridor."
  state alert = false
  state cleared_you = false

  verb examine
    say "His badge is polished, but his expression is not."

  dialogue start
    say "State your business."
    option inspect "I'm here to <i>nspect the machine." if have badge -> allow_entry
    option leave "<n>ever mind." -> end_leave

  node allow_entry
    say "All right, go on through."
    set guard.cleared_you = true
    end

  node end_leave
    say "Move along, then."
    end
```

## Writing Style Tips

These habits make content easier to maintain:

- Keep IDs short, stable, and lowercase.
- Keep display names natural and readable.
- Use one concept per state flag.
- Prefer small verbs over giant blocks.
- Use dialogue for guided conversations, not for every interaction.
- Use `hint` when the player is likely to get stuck.
- Reuse familiar verbs like `examine`, `talk`, `scan`, and `open`.

## Common Mistakes

### Misaligned Indentation

Bad:

```text
obj panel in showroom
 desc "A panel."
```

Good:

```text
obj panel in showroom
  desc "A panel."
```

### Referring to Something That Does Not Exist

Bad:

```text
obj panel in showroom
  verb open
    set hatch.open = true
```

if there is no object or state called `hatch`.

Good:

```text
obj panel in showroom
  verb open
    set panel.open = true
```

### Duplicate Hotkeys in One Dialogue Node

Bad:

```text
option inspect "I'm here to <i>nspect the machine." -> allow_entry
option inquire "Can I <i>nquire about access?" -> ask_access
```

Good:

```text
option inspect "I'm here to <i>nspect the machine." -> allow_entry
option inquire "Can I <q>uestion the access rules?" -> ask_access
```

### Too Much Logic in One Place

Bad:

- one huge dialogue node with everything in it
- one huge verb doing many unrelated things

Better:

- split dialogue into named nodes
- split logic into separate verbs or rules

## Recommended First Steps for New Authors

If you are learning the language, practice in this order:

1. Write one room.
2. Add one object with `desc` and `examine`.
3. Add one blocked verb with `if` and `say`.
4. Add one character with a tiny dialogue tree.
5. Add one item-gated option like `if have badge`.

That sequence teaches most of the language quickly.

## Quick Reference

Top-level blocks:

- `room`
- `obj` or `object`
- `char` or `character`
- `rule`

Common child lines:

- `desc` or `description`
- `alias`
- `tag`
- `state`
- `verb`
- `dialogue`
- `node`
- `exit`

Common control lines:

- `if`
- `elif`
- `else`
- `goto`
- `end`

Common actions:

- `say`
- `hint`
- `set`
- `call`

Dialogue lines:

- `option`

## Final Advice

Start simple.

If an interaction can be expressed as:

- a short description
- a small `if`/`else`
- one or two state changes
- a short dialogue tree

then it probably belongs in MuseLang.

If it needs deep game logic, unusual parsing, or lots of custom rules, keep the content in MuseLang and let pre-written Python handle the hard part.
