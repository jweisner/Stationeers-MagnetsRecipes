using System;
using System.Collections.Generic;
using Assets.Scripts;
using Assets.Scripts.Atmospherics;
using Assets.Scripts.Objects;
using Assets.Scripts.Objects.Pipes;
using HarmonyLib;
using UnityEngine;

namespace FurnaceRecipes
{
    // Recipe XML can consume gas (RequiredMix) but cannot produce it. When one of our methane
    // recipes completes in an Advanced Furnace, add the hydrogen the reaction releases.
    [HarmonyPatch(typeof(FurnaceBase), nameof(FurnaceBase.CreateIngots))]
    internal static class HydrogenPatch
    {
        // Output prefab -> mol H2 released per mol CH4 consumed (CH4 -> C + 2 H2).
        // Keyed on output so vanilla methane recipes (Solid Fuel) are left alone.
        private static readonly Dictionary<string, double> H2PerMethane = new Dictionary<string, double>
        {
            { "ItemCharcoal", 2.0 },
        };

        private static void Prefix(FurnaceBase __instance, out double __state)
        {
            __state = 0.0;
            if (!(__instance is AdvancedFurnace) || __instance.SmelterResult == null)
                return;
            if (!(__instance.SmelterResult is Thing result) || !H2PerMethane.TryGetValue(result.PrefabName, out double ratio))
                return;
            double methanePerOutput = __instance.CurrentRecipe.RequiredMix.Methane;
            if (double.IsNaN(methanePerOutput) || methanePerOutput <= 0.0)
                return;

            int outputs = OutputCount(__instance);
            double wanted = methanePerOutput * outputs;
            double available = __instance.InternalAtmosphere.GasMixture.Methane.Quantity.ToDouble();
            if (available < wanted)
            {
                // Vanilla removal clamps to what is there, so the batch still completes in full.
                Plugin.Log.LogWarning($"{result.PrefabName} x{outputs}: needs {wanted:F1} mol CH4, furnace has {available:F1}; output not reduced");
            }
            double consumed = Math.Min(wanted, available);
            __state = consumed * ratio;
            Plugin.Log.LogInfo($"{result.PrefabName} x{outputs}: CH4 -{consumed:F1} mol, H2 +{__state:F1} mol at {__instance.InternalAtmosphere.Temperature.ToDouble():F0} K");
        }

        private static void Postfix(FurnaceBase __instance, bool __result, double __state)
        {
            if (!__result || __state <= 0.0)
                return;
            AddHydrogen(__instance.InternalAtmosphere, __state);
        }

        // Queued like vanilla's own furnace gas changes, at the furnace's temperature.
        internal static void AddHydrogen(Atmosphere atmosphere, double moles)
        {
            GasMixture hydrogen = GasMixtureHelper.Create();
            hydrogen.Add(new Mole(Chemistry.GasType.Hydrogen, new MoleQuantity(moles), MoleEnergy.Zero));
            hydrogen.TotalEnergy = IdealGas.Energy(hydrogen.HeatCapacity, atmosphere.Temperature);
            AtmosphericEventInstance.CreateAdd(atmosphere, hydrogen);
        }

        // Same arithmetic as FurnaceBase.CreateIngots, which does not expose its output count.
        private static int OutputCount(FurnaceBase furnace)
        {
            int count = (int)(furnace.ReagentMixture.TotalReagents / furnace.RatioMix.TotalReagents);
            float scale = furnace.GetSmelterScale();
            if (scale > 0f)
                count = Mathf.RoundToInt(count * scale);
            return (int)Mathf.Clamp(count, 0f, furnace.SmelterResult.GetMaxQuantity);
        }
    }
}
