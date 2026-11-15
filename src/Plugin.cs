using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;

namespace MagnetsRecipes
{
    [BepInPlugin(PluginGuid, PluginName, PluginVersion)]
    public class Plugin : BaseUnityPlugin
    {
        public const string PluginGuid = "net.pbmagnet.stationeers.magnetsrecipes";
        public const string PluginName = "Magnet's Recipes";
        public const string PluginVersion = "0.0.1";

        internal static ManualLogSource Log = null!;
        internal static ConfigEntry<double> MinTemperatureK = null!;
        internal static ConfigEntry<double> MethanePerCarbon = null!;
        internal static ConfigEntry<float> SecondsPerCarbon = null!;

        private void Awake()
        {
            Log = Logger;
            MinTemperatureK = Config.Bind("Methane", "MinTemperatureK", 1100.0,
                "Minimum Advanced Furnace temperature for methane carburizing and pyrolysis.");
            MethanePerCarbon = Config.Bind("Methane", "MethanePerCarbon", 100.0,
                "Mol of methane consumed per unit of Carbon deposited (releases twice that in H2).");
            SecondsPerCarbon = Config.Bind("Methane", "SecondsPerCarbon", 5f,
                "Seconds between Carbon deposits per furnace.");
            new Harmony(PluginGuid).PatchAll(typeof(Plugin).Assembly);
            Log.LogInfo("Magnet's Recipes loaded");
        }
    }
}
