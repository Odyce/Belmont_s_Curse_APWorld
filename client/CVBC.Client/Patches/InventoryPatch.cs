using HarmonyLib;
using Archipelago.MultiClient.Net.Models;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(Inventory), nameof(Inventory.AddItemToInventory), new System.Type[] { typeof(ItemData), typeof(Il2CppSystem.Action<ItemData>), typeof(bool), typeof(bool) })]
public static class InventoryPatch
{
    static bool Prefix(Inventory __instance, ItemData itemToAdd, bool fromInit)
        => Safe.Run("InventoryPatch", () => Body(__instance, itemToAdd, fromInit));
    private static bool Body(Inventory __instance, ItemData itemToAdd, bool fromInit)
    {
        if (fromInit == true)
        {
            ItemSync.PlayerInventory = __instance;
            ItemSync.Notify = false;
            ItemSync.NeedsSync = true;
            ItemSync.ClearPendingCards();
            string startKey = "item:" + itemToAdd.itemID;
            if (CheckTracker.StartingKeys.Contains(startKey) && GameData.Locations.TryGetValue(startKey, out long startLocation))
            {
                Plugin.Logger.LogInfo($"[Check] starting item {itemToAdd.itemID}: AP location {startLocation}");
                APClient.SendCheck(startLocation);
            }
            return true;
        }
        
        if (CheckTracker.GivingFromAP)
            return true;
        
        string key = CheckTracker.PendingSavedId;
        
        if (key == null || !GameData.Locations.ContainsKey(key))
            key = "item:" + itemToAdd.itemID;

        if (GameData.Locations.TryGetValue(key, out long apLocation))
        {
            Plugin.Logger.LogInfo($"[Check] AP location {apLocation}");
            Plugin.Logger.LogInfo($"[Check] contains {APClient.Describe(apLocation)}");
        }
        else
        {
            if (CheckTracker.PendingSavedId != null)
                Plugin.Logger.LogWarning($"[Check] {key} is not in cvbc_data.json");
            return true;
        }
        
        CheckTracker.DisplayOriginalId = itemToAdd.itemID;
        CheckTracker.DisplayReplacement = null;
        APCard.Pending = null;

        if (APClient.Scouted.TryGetValue(apLocation, out ScoutedItemInfo info))
        {
            if (APClient.IsForMe(info))
            {
                string gameId = ItemSync.NextGameIdFor(info.ItemId);
                ItemData real = gameId == null ? null : ItemSync.FindGameItem(gameId);
                if (APCard.HasAcquisitionCard(real))
                {
                    CheckTracker.DisplayReplacement = real;
                    CheckTracker.ShownAtCheck.Add(real.itemID);
                }
            }

            // Foreign item, or own item without a game card: AP card
            // Will be improved in later versions
            if (CheckTracker.DisplayReplacement == null)
            {
                CheckTracker.DisplayReplacement = ItemSync.FindGameItem(APCard.PlaceholderId);
                APCard.Pending = APCard.TextFor(info);
            }
        }

        CheckTracker.PendingSavedId = null;
        APClient.SendCheck(apLocation);
        Plugin.Logger.LogInfo($"[Check] {key}: blocked {itemToAdd.itemID}");

        return false;
    }
}
