# SABBATICAL ARCADE LAUNCHER

Created by gleeson.

## What is it?

This Godot 4 project is a game launcher for the Sabbatical Gallery Arcade. It is inspired by the [Mixed-Media-Bundle-Launcher](https://github.com/cis-ash/MM-Bundle-Launcher).

It's not quite done yet!

## How To Add Games

The launcher will look for a `'/games/'` folder in the same directory, where it expects a folder for 
each game.

```
SabbyLauncher
┣━ games
┃ ┣━ game 1
┃ ┣━ game 2
┃ ┣━ game 3
┃ ┗━ ...
┗━ SabbyLauncher.exe
```
Each game folder must include the following files:
- `arcade.json`. The data to be displayed in the carousel.
- `cover.png`. The image to be displayed in the carousel.

## arcade.json

This holds data about the game so that it the launcher knows how to display and start it.
Refer to this template:

```json
{
  "name": "{Game Title}",
  "author": "{Author}",
  "description": "{Description}",
  "cover": "cover.png",
  "type": "exe",
  "link": "game.exe",
}
```

- `type` can either be:
  - `"exe"` : Game is a native application.
  - `"web"` : Game is launched in a browser. `link` must be a valid URL.
  - Other types are not yet supported.

- `link` and `cover` are relative paths to the following files:
  - `link`: the actual game executable (`"game.exe"` -> `"../games/game_title/game.exe"`
  - `cover`: the display image (`"cover.png"` -> `"../games/game_title/cover.png"`)

## Notes
- I attempted to track process_ids for launched games, so that they can be remotely killed by the
launcher. Godot has barebones methods to do this, but doesn't support apps that might start
more than process (which most seem to do).

- 