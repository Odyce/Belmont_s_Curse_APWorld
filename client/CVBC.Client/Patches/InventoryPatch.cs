using HarmonyLib;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(Inventory), nameof(Inventory.AddItemToInventory), new System.Type[] { typeof(ItemData), typeof(Il2CppSystem.Action<ItemData>), typeof(bool), typeof(bool) })]
public static class InventoryPatch
{
    // THIS WHOLE THING IS A TEST FOR THE PROOF OF CONCEPT
    // It is in no way final, just made for testing as phase 3 intends
    static bool Prefix(Inventory __instance, ItemData itemToAdd, bool fromInit)
    {
        if (fromInit == true)
            return true;
        
        string id = CheckTracker.PendingSavedId;
        if (id == null)
            return true;
        
        CheckTracker.PendingSavedId = null;

        var manager = UnityEngine.Object.FindObjectOfType<ItemsManager>();
        ItemData replacement = null;
        if (manager != null)
            replacement = manager.FindItem("WeaponSpearTier2");
        
        if (replacement == null)
        {
            Plugin.Logger.LogError("[Check] replacement item not found, giving the vanilla item");
            return true;
        }

        Plugin.Logger.LogInfo($"[Check] {id}: blocked {itemToAdd.itemID}, giving {replacement.itemID}");
        __instance.AddItemToInventory(replacement, false);
        return false;
    }
}