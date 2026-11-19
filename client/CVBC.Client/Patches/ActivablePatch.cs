using HarmonyLib;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(GPE_ActivableEntity), nameof(GPE_ActivableEntity.Activate))]
public static class ActivablePatch
{
    static bool Prefix(GPE_ActivableEntity __instance)
        => Safe.Run("ActivablePatch", () => Body(__instance));

    private static bool Body(GPE_ActivableEntity __instance)
    {
        // Chests keep their own path (ItemGiver -> InventoryPatch), with the card display
        if (__instance.GetComponentInChildren<ItemGiver>(true) != null)
            return true;

        string id = SaveIds.Of(__instance);
        if (id == null || !GameData.Locations.TryGetValue(id, out long apLocation))
            return true;

        Plugin.Logger.LogInfo($"[Check] {__instance.name} ({id}): AP location {apLocation}, contains {APClient.Describe(apLocation)}");
        APClient.SendCheck(apLocation);

        // Activated (saved, final visuals) without the reward action
        __instance.InstantActivate();
        return false;
    }
}
