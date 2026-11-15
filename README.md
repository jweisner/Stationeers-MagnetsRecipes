# Magnet's Recipes

A Stationeers mod that puts methane to work in the **Advanced Furnace**. Methane is cracked into
carbon and hydrogen (CH4 -> C + 2 H2) in two ways:

- **Charcoal pyrolysis**: a charcoal bed in hot methane keeps growing into more charcoal.
- **Carburizing**: carbon is deposited into molten iron until the mix is ready for vanilla steel.

Both release hydrogen into the furnace. The hard part is keeping the furnace above 1100 K with a
methane atmosphere, which is where the balance comes from.

## Requirements

- [BepInEx 5](https://github.com/BepInEx/BepInEx) (Windows x64 build, also when playing on
  Linux through Proton).
- [StationeersLaunchPad](https://github.com/StationeersLaunchPad/StationeersLaunchPad), which
  loads the mod.

## Installing

1. **Install BepInEx and StationeersLaunchPad** if you have not already, following the
   [StationeersLaunchPad installation guide](https://github.com/StationeersLaunchPad/StationeersLaunchPad#installation).
   You should see the LaunchPad window at the bottom of the game's loading screen.
2. **Download** `MagnetsRecipes-<version>.zip` from the
   [Releases page](https://github.com/jweisner/Stationeers-MagnetsRecipes/releases).
3. **Extract it into your Stationeers mods folder**, so that you end up with a
   `MagnetsRecipes` folder inside it:

   | Platform | Mods folder |
   |---|---|
   | Windows | `Documents\My Games\Stationeers\mods` |
   | Linux (Proton) | `~/.local/share/Steam/steamapps/compatdata/544550/pfx/drive_c/users/steamuser/Documents/My Games/Stationeers/mods` |

   Create the `mods` folder if it does not exist. The result should look like:

   ```
   mods/
     MagnetsRecipes/
       About/About.xml
       GameData/advancedfurnace.xml
       MagnetsRecipes.dll
   ```

4. **Start the game.** LaunchPad loads local mods automatically. To check it is enabled, click
   the LaunchPad window on the loading screen and look for **Magnet's Recipes** in the mod list.

To update, delete the old `MagnetsRecipes` folder and extract the new zip in its place. To
uninstall, delete the folder.

**Multiplayer**: every player and the server need the mod. For a dedicated server, see
LaunchPad's dedicated server instructions (its `Export Mod Package` button bundles your enabled
mods for the server).

## Features

### Charcoal pyrolysis

Put charcoal in the Advanced Furnace and keep the mold closed. While the furnace holds only
carbon, the plugin grows the charcoal bed one unit at a time:

- Every 5 seconds: +1 Carbon, -100 mol methane, +200 mol hydrogen.
- Requires: at least 1 carbon, nothing else in the mix, >= 1100 K, >= 100 mol methane, and a
  clean methane atmosphere (no CO2, N2, etc.).
- No limit: the bed keeps growing as long as methane is supplied.

Open the mold at >= 1100 K and >= 100 kPa to take the bed out as charcoal, one per Carbon. A big
bed comes out as several stacks in a row. Opened colder than that, the mix comes out as slag.

The bed needs a charcoal seed (make the first from Biomass). Smelting charcoal off-gases CO2 and
Pollutant, which stops growth until it is purged from the furnace.

Do not add iron to a growing bed: the mix becomes iron plus carbon and switches to carburizing
below.

### Carburizing iron to steel

There is no new steel recipe. Instead, while the Advanced Furnace holds iron with its mold
closed, the plugin adds carbon to the reagent mix one unit at a time:

- Every 5 seconds: +1 Carbon, -100 mol methane, +200 mol hydrogen.
- Requires: at least 1 iron, nothing but iron and carbon in the mix, >= 1100 K, >= 100 mol
  methane, and a clean methane atmosphere (no CO2, N2, etc.).
- Stops when Carbon equals Iron.

Vanilla steel is Iron 3 : Carbon 1. Watch the furnace (or read its reagents from IC10) and open
the mold when the ratio is right, at vanilla steel's conditions (>= 900 K, >= 1000 kPa). For
example, 3 iron ingots at `Fe 3 C 1` give 4 steel ingots. Miss the window and you get slag,
which a centrifuge turns back into iron ore and charcoal; or add more iron to bring the ratio
back to 3:1.

Feed iron **ingots**: ore off-gases CO2 and Pollutant, which stops carburizing until it is
purged.

## Configuration

`BepInEx/config/ca.weisner.stationeers.magnetsrecipes.cfg`, section `[Methane]`:

| Setting | Default | Meaning |
|---|---|---|
| `MinTemperatureK` | 1100 | Minimum furnace temperature for pyrolysis and carburizing |
| `MethanePerCarbon` | 100 | Mol of methane used per Carbon deposited (H2 released is twice this) |
| `SecondsPerCarbon` | 5 | Seconds between deposits, per furnace |

The temperature and pressure for opening the mold on a charcoal bed are in
`GameData/advancedfurnace.xml`.

## Building from source

Needs the .NET SDK. The project references the game's assemblies from
`~/.local/share/Steam/steamapps/common/Stationeers`; override by setting `StationeersPath` in
the environment.

```bash
./deploy.sh
```

This builds `src/MagnetsRecipes.csproj` and installs `About/`, `GameData/` and
`MagnetsRecipes.dll` into `mods/MagnetsRecipes` in the game's Proton prefix (override the mods
directory with `STATIONEERS_MODS`). Enable **Magnet's Recipes** in LaunchPad's mod list.

Log output goes to `BepInEx/LogOutput.log` (in the game folder) under the `Magnet's Recipes`
source.

### Making a release

Bump `<Version>` in `About/About.xml` and `PluginVersion` in `src/Plugin.cs` (the script checks
they match), commit and push, then:

```bash
./release.sh            # build dist/MagnetsRecipes-<version>.zip only
./release.sh --publish  # also create GitHub release v<version> with the zip attached
```

`--publish` refuses to run with uncommitted changes, unpushed commits, or an existing release
for that version, and checks the uploaded zip actually downloads.

## Layout

| Path | Contents |
|---|---|
| `About/About.xml` | Mod metadata |
| `GameData/advancedfurnace.xml` | Turns a grown carbon bed into charcoal when the mold opens |
| `src/MethanePatch.cs` | Cracks methane into carbon and hydrogen: pyrolysis and carburizing |
| `src/Plugin.cs` | BepInEx entry point and config |
| `deploy.sh` | Build and install into the local mods folder |
| `release.sh` | Build the release zip, optionally publish a GitHub release |
