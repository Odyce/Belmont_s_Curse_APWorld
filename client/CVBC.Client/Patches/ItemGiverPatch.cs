using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(ItemGiver), nameof(ItemGiver.GiveItem))]
public static class ItemGiverPatch
{
    static void Prefix(ItemGiver __instance)
    {
        var savable = __instance.GetComponentInParent<SavableEntityBase>();

        // Check if the item is an item in a chest like it's supposed to be in this case
        if (savable == null)
        {
            Plugin.Logger.LogWarning($"[GiveItem] {__instance.name}: SavableEntityBase not found in parents");
            return;
        }

        string id = savable.Id;

        // Fallback if the id is missing, as far as I've seen the guid is always the same
        if (string.IsNullOrEmpty(id))
            id = savable.guid;
        
        CheckTracker.PendingSavedId = id;
        Plugin.Logger.LogInfo($"[GiveItem] source = {id}");
    }

    static void Postfix()
    {
        CheckTracker.PendingSavedId = null;
    }
}
