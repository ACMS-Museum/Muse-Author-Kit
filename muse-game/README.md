# muse-game

This folder is the endorsed local Evennia game scaffold for Muse.

It is tracked in the repository so ACMS members start from a consistent
structure, but the mutable runtime state inside this folder is local to each
user. MuseLang tooling operates on this layout when installing runtime helper
modules and when generating content for the game.

## What belongs here

Tracked scaffold content includes:

- game code under `behaviours`, `commands`, `typeclasses`, `web`, and `world`
- configuration modules under `server/conf`
- documentation and helper notes such as this README and `sqlite-utils.md`

Local-only content includes:

- Evennia databases such as `server/evennia.db3`
- logs under `server/logs`
- private settings such as `server/conf/secret_settings.py`
- generated static or media files under `server/.static` and `server/.media`
- any user-specific runtime state created while running the game

## Typical workflow

From the repository root:

```powershell
muselang runtime-install --game-root .\muse-game
muselang doctor --game-root .\muse-game
cd .\muse-game
evennia migrate
evennia createsuperuser
evennia start
```

Open <http://localhost:4001> in a browser, or connect with a Telnet or MUD
client to `localhost` on port `4000`.

To stop the game later, run:

```powershell
evennia stop
```
