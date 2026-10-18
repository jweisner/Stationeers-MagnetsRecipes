using System.Runtime.CompilerServices;
using Assets.Scripts;
using Assets.Scripts.Atmospherics;
using Assets.Scripts.Objects.Pipes;
using HarmonyLib;
using Reagents;

namespace FurnaceRecipes
{
    // Methane carburizing in the Advanced Furnace. While the furnace holds iron (and optionally
    // carbon, e.g. from charcoal) in a hot, pure methane atmosphere, deposit carbon into its
    // reagent mix one whole unit at a time: CH4 -> C + 2 H2.
    // Steel itself comes from the vanilla recipe (Iron 0.75 + Carbon 0.25) when the player opens
    // the mold at the right ratio. Whole units matter: vanilla matches the ratio exactly.
    [HarmonyPatch(typeof(DeviceInputOutputImportExport), nameof(DeviceInputOutputImportExport.OnServerTick))]
    internal static class CarburizingPatch
    {
        private const double Epsilon = 1e-6;

        private static readonly ConditionalWeakTable<AdvancedFurnace, StrongBox<float>> Timers =
            new ConditionalWeakTable<AdvancedFurnace, StrongBox<float>>();

        private static void Postfix(DeviceInputOutputImportExport __instance, float deltaTime)
        {
            if (!(__instance is AdvancedFurnace furnace) || !GameManager.RunSimulation || !furnace.IsStructureCompleted)
                return;

            StrongBox<float> timer = Timers.GetOrCreateValue(furnace);
            timer.Value += deltaTime;
            if (timer.Value < Plugin.SecondsPerCarbon.Value)
                return;
            timer.Value = 0f;

            if (!CanCarburize(furnace, out double iron, out double carbon))
                return;

            double methane = Plugin.MethanePerCarbon.Value;
            Atmosphere atmosphere = furnace.InternalAtmosphere;
            GasMixture removed = GasMixtureHelper.Create();
            removed.Add(new Mole(Chemistry.GasType.Methane, new MoleQuantity(methane), MoleEnergy.Zero));
            removed.TotalEnergy = IdealGas.Energy(removed.HeatCapacity, atmosphere.Temperature);
            AtmosphericEventInstance.CreateRemove(atmosphere, removed);
            HydrogenPatch.AddHydrogen(atmosphere, methane * 2.0);

            ReagentMixture mix = furnace.ReagentMixture;
            mix.Set(mix.Carbon.ReagentId, carbon + 1.0);
            Plugin.Log.LogInfo($"Carburizing: Fe {iron:F0} C {carbon + 1.0:F0} (CH4 -{methane:F0}, H2 +{methane * 2.0:F0} mol)");
        }

        private static bool CanCarburize(AdvancedFurnace furnace, out double iron, out double carbon)
        {
            ReagentMixture mix = furnace.ReagentMixture;
            iron = mix.Iron.Quantity;
            carbon = mix.Carbon.Quantity;

            // Mix must be iron, plus any carbon, and nothing else.
            if (iron < 1.0 || mix.TotalReagents - iron - carbon > Epsilon)
                return false;
            // Safety cap: stop at Carbon = Iron, well past steel's 3:1, so a forgotten furnace
            // overshoots recoverably instead of eating methane forever.
            if (carbon + 1.0 > iron + Epsilon)
                return false;

            Atmosphere atmosphere = furnace.InternalAtmosphere;
            if (atmosphere == null || atmosphere.Temperature.ToDouble() < Plugin.MinTemperatureK.Value)
                return false;
            GasMixture gas = atmosphere.GasMixture;
            if (gas.Methane.Quantity.ToDouble() < Plugin.MethanePerCarbon.Value)
                return false;
            // Same gases vanilla's Rule="Pure" checks (MoleMixture.Contains). Hydrogen is allowed.
            return IsZero(gas.Oxygen) && IsZero(gas.Nitrogen) && IsZero(gas.CarbonDioxide) &&
                   IsZero(gas.Pollutant) && IsZero(gas.Water) && IsZero(gas.PollutedWater);
        }

        private static bool IsZero(Mole mole) => Chemistry.IsMolecularlyZero(mole.Quantity);
    }
}
