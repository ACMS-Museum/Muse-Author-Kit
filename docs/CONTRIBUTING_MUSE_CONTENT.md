# Contributing Muse Content

Muse content is written in `.muse` files and tested locally before it is shared
with the ACMS Muse maintainers.

## Recommended workflow

1. Choose or create a `.muse` source file.
2. Run `muselang lint` before committing changes.
3. Run `muselang prod` to generate a local bundle and Evennia batch file.
4. Import the batch file into a clean local Muse game.
5. Play through the changed rooms, objects, verbs, and goals.
6. Submit the `.muse` source and a short description of the intended visitor
   experience.

Generated `.json` and `.ev` files are local build outputs unless a maintainer
has specifically asked for them.

## File organization

- Keep separate exhibits, rooms, or scenarios in separate source files where
  possible.
- Use clear lowercase IDs with underscores, such as `radio_room` or
  `power_panel`.
- Keep IDs stable after other content begins referring to them.
- Prefer small, playable changes over large untested submissions.

## Review expectations

Content review should check:

- the source compiles without errors;
- the scenario can be imported into a clean local game;
- verbs, hints, goals, and state changes are playable;
- names and descriptions fit the agreed Muse setting;
- no local machine paths, private notes, generated state, or test-only artifacts
  are included.

The fictional setting will evolve through maintainers and recruited authors, so
canon questions should be captured in review notes rather than hidden in source
comments.
