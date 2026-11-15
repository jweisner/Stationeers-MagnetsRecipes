# AGENTS.md

Working notes for anyone (human or agent) changing this mod. What the mod does,
how to install it and its settings are in [README.md](README.md); this file covers
how to work on it.

## Status (2026-11-14)

- **v0.0.1 released**: GitHub release `v0.0.1` and Steam Workshop item
  [3840065472](https://steamcommunity.com/sharedfiles/filedetails/?id=3840065472) (public).
- Tested in single player: charcoal pyrolysis (continuous growth, charcoal out at
  mold open) and carburizing to steel.
- **Not tested**: multiplayer; the recycler output for charcoal; whether
  Stationpedia lists the charcoal recipe; hot hydrogen igniting with leftover oxygen.
- No open task. Next work is whatever the next release needs.

## Layout and build

See the Layout table in the README. In short: `src/` is the plugin
(`MethanePatch.cs` does all the work), `GameData/advancedfurnace.xml` is the one
recipe, `About/` is the LaunchPad metadata and Workshop art, `art/make_art.py`
draws the art.

```bash
./deploy.sh             # build and install into the local mods folder (Proton prefix)
./release.sh            # build dist/MagnetsRecipes-<version>.zip
./release.sh --publish  # also create the GitHub release and verify the download
```

`deploy.sh` is the single source of what ships: `release.sh` zips exactly what it
installs. Add a new file to the mod by adding it to `deploy.sh`.

Art: `python3 art/make_art.py`, then the two `inkscape` commands in its docstring.
`thumb.png` must stay under 1 MB or LaunchPad hides the Workshop button.

## Shipping a new version

1. Bump `<Version>` in `About/About.xml` and `PluginVersion` in `src/Plugin.cs`
   (`release.sh` refuses a mismatch).
2. Replace `<ChangeLog>` in `About/About.xml`; it becomes the Workshop change note.
3. `./deploy.sh`, test in game, commit and push.
4. In game: LaunchPad Workshop list, Magnet's Recipes, **Update**. If the button
   says **Publish**, stop: `<WorkshopHandle>` has been lost and publishing would
   create a duplicate Workshop item.
5. `./release.sh --publish`.

The Workshop upload comes from the local `mods/MagnetsRecipes` folder, not the
repo. After a first publish LaunchPad writes `<WorkshopHandle>` into that local
`About.xml` only; it must be copied into the repo or the next `deploy.sh`
overwrites it. It is in the repo now.

## Identity (do not change)

- ModID `net.pbmagnet.stationeers.MagnetsRecipes`, plugin GUID
  `net.pbmagnet.stationeers.magnetsrecipes`, author Pb_Magnet.
- Changing the ModID makes LaunchPad and every subscriber treat it as a new mod.
  The BepInEx config file is named after the GUID, so changing that resets
  everyone's settings.

## Gotchas

- **Never enable a Workshop copy and a local `mods/` copy at the same time.** The
  furnace patch then runs twice. With a LaunchPad mod pack active, LaunchPad
  1.2.1 skips its duplicate check entirely (`DedupeMods` only applies with no
  pack selected), because packs identify Workshop mods by handle and local mods
  by folder. Keep a dev pack with the local copy and a play pack with the
  Workshop copy.
- **Logs are buffered while the game runs.** Read `BepInEx/LogOutput.log` and
  `Player.log` after quitting. `Player-prev.log` holds the previous session and
  includes plugin lines.
- **Vanilla XML element names look like this mod's old name.** `<FurnaceRecipes>`
  and `<AdvancedFurnaceRecipes>` are the game's own elements; a blanket rename
  must not touch them.
- **Vanilla only ejects one stack per tick** at mold open, so a large carbon bed
  comes out as several stacks in a row.
- Carburizing and pyrolysis need a clean methane atmosphere: charcoal and iron
  ore off-gas CO2 and Pollutant, which blocks deposits until purged. Iron
  **ingots** avoid this for carburizing.

## Design decisions

- Steel comes from carburizing into the vanilla reagent mix, not a new
  iron + methane -> steel recipe, which would be at odds with vanilla's
  Iron 3 : Carbon 1 steel and collided with the vanilla iron recipe.
- Pyrolysis is continuous while the mold is closed, with no cap ("the furnace
  can hold many stacks"). An earlier design made charcoal only at mold open and
  sat doing nothing in the right conditions.
- Carburizing stops at Carbon = Iron so a forgotten furnace overshoots
  recoverably instead of eating methane forever.
- No heat or energy cost: holding the furnace above 1100 K in methane is the
  balance.
- StationeersLaunchPad is a hard requirement; no BepInEx-only install route.

## Inspecting the game

Decompile one type with ilspycmd, e.g.
`ilspycmd -t Assets.Scripts.Objects.Pipes.FurnaceBase -r <game>/rocketstation_Data/Managed <game>/rocketstation_Data/Managed/Assembly-CSharp.dll`.
Keep decompiled output out of the repo.

## Conventions

- Commit and push straight to `main`; no pull requests.
- No AI attribution trailers (`Co-Authored-By` and similar) in commits. The
  README's AI disclosure section is the only mention.
