using BepInEx;
using BepInEx.Configuration;
using BepInEx.Logging;
using HarmonyLib;

namespace FurnaceRecipes
{
    [BepInPlugin(PluginGuid, PluginName, PluginVersion)]
    public class Plugin : BaseUnityPlugin
    {
        public const string PluginGuid = "ca.weisner.stationeers.furnacerecipes";
        public const string PluginName = "Furnace Recipes";
        public const string PluginVersion = "0.0.1";

        internal static ManualLogSource Log = null!;
        internal static ConfigEntry<double> MinTemperatureK = null!;
        internal static ConfigEntry<double> MethanePerCarbon = null!;
        internal static ConfigEntry<float> SecondsPerCarbon = null!;

        private void Awake()
        {
            Log = Logger;
            MinTemperatureK = Config.Bind("Carburizing", "MinTemperatureK", 1100.0,
                "Minimum Advanced Furnace temperature for methane carburizing.");
            MethanePerCarbon = Config.Bind("Carburizing", "MethanePerCarbon", 100.0,
                "Mol of methane consumed per unit of Carbon deposited (releases twice that in H2).");
            SecondsPerCarbon = Config.Bind("Carburizing", "SecondsPerCarbon", 5f,
                "Seconds between Carbon deposits per furnace.");
            new Harmony(PluginGuid).PatchAll(typeof(Plugin).Assembly);
            Log.LogInfo("Furnace Recipes loaded");
        }
    }
}
