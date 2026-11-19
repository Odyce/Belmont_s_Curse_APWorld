using System.Collections.Generic;
using System.Linq;
using BepInEx.Logging;
using HarmonyLib;
using Newtonsoft.Json.Linq;
using Il2CppInterop.Runtime.InteropTypes.Arrays;

namespace CVBC.Client;

public static class ItemSync
{
    public static volatile bool NeedsSync = false;
    public static volatile bool Notify = false;
    public static Inventory PlayerInventory = null;

    static readonly List<ItemData> pendingCards = new();

    static string lastReason = null;

    public static ItemData FindGameItem(string gameId)
    {
        var manager = UnityEngine.Object.FindObjectOfType<ItemsManager>();
        if (manager == null)
            return null;
        return manager.FindItem(gameId);
    }

    public static string NextGameIdFor(long apItemId)
    {
        if (!GameData.Items.TryGetValue(apItemId, out JObject data))
            return null;

        string gameId = (string)data["game_id"];
        string group = (string)data["progressive_group"];
        if (gameId != null || group == null)
            return gameId;

        // Progressive item: the next tier is the number of copies already received
        int owned = 0;
        foreach (var info in APClient.Session.Items.AllItemsReceived)
        {
            if (GameData.Items.TryGetValue(info.ItemId, out JObject other)
                && (string)other["game_id"] == null
                && (string)other["progressive_group"] == group)
                owned++;
        }

        var tiers = GameData.Progressive[group];
        return owned < tiers.Count ? tiers[owned] : null;
    }

    static void LogReason(string reason)
    {
        if (reason == lastReason)
            return;
        lastReason = reason;
        Plugin.Logger.LogInfo($"[AP] cards: {reason}");
    }

    static bool CanShowCards()
    {
        if (UnityEngine.Object.FindObjectOfType<GameMenuManager>() != null)
        {
            LogReason("waiting (GameMenuManager open)");
            return false;
        }
        if (UnityEngine.Object.FindObjectOfType<PauseMenuManager>() != null)
        {
            LogReason("waiting (PauseMenuManager open)");
            return false;
        }
        LogReason("free");
        return true;
    }

    public static void TryShowCards()
    {
        if (pendingCards.Count == 0 || !CanShowCards())
            return;
        if (ShowCards(pendingCards))
        {
            Plugin.Logger.LogInfo($"[AP] showed {pendingCards.Count} card(s)");
            pendingCards.Clear();
        }
        else
            LogReason("no acquisition controller");
    }

    public static void ClearPendingCards()
    {
        pendingCards.Clear();
        CheckTracker.ShownAtCheck.Clear();
    }

    static bool ShowCards(List<ItemData> items)
    {
        var controller = ItemAcquisitionGlobalController.GetInstance();
        if (controller == null)
            return false;
        controller.OpenAcquisitionForItems(new Il2CppReferenceArray<ItemData>(items.ToArray()));
        return true;
    }

    public static ItemData Give(ItemsManager manager, string gameId, string name)
    {
        if (PlayerInventory.HasItemInInventory(gameId))
            return null;
        
        ItemData item = manager.FindItem(gameId);

        if (item == null)
        {
            Plugin.Logger.LogWarning($"Item {name} not found, cannot give it to player");
            return null;
        }
        
        CheckTracker.GivingFromAP = true;
        try 
        { 
            PlayerInventory.AddItemToInventory(item, false); 
        }
        finally 
        { 
            CheckTracker.GivingFromAP = false; 
        }
        Plugin.Logger.LogInfo($"[AP] received {name}");
        return item;
    }

    public static void Sync()
    {
        if (APClient.Session != null)
            Victory.Send();
        
        if (APClient.Session == null || PlayerInventory == null)
            return;
        
        var manager = UnityEngine.Object.FindObjectOfType<ItemsManager>();
        var given = new List<ItemData>();

        if (manager == null)
            return;
        
        Dlc.SendFreeCheckIfNeeded();
        NeedsSync = false;

        var received = APClient.Session.Items.AllItemsReceived.ToArray();
        var progressiveCounter = new Dictionary<string, int>();
        var statItems = new Dictionary<string, int>();

        foreach (var info in received)
        {
            if (!GameData.Items.TryGetValue(info.ItemId, out JObject data))
                continue;

            string gameId = (string)data["game_id"];
            string group = (string)data["progressive_group"];

            if (gameId == null && group != null)
            {
                progressiveCounter.TryGetValue(group, out int n);
                progressiveCounter[group] = n + 1;
                if (n < GameData.Progressive[group].Count)
                    gameId = GameData.Progressive[group][n];
            }

            if (gameId == null && group == null)
            {
                string itemName = (string)data["name"];
                statItems.TryGetValue(itemName, out int count);
                statItems[itemName] = count + 1;
                continue;
            }

            if (gameId == null)
                continue;
            
            // Without the DLC, the game would take the relic back anyway
            if (gameId == Dlc.FamilysGraveId && Dlc.OwnsFamilysGrave() == false)
                continue;
            
            ItemData item = Give(manager, gameId, (string)data["name"]);
            if (item != null && !CheckTracker.ShownAtCheck.Remove(item.itemID) && APCard.HasAcquisitionCard(item))
                given.Add(item);
        }

        StatItems.Apply(statItems);
        
        if (given.Count > 0 && Notify)
        {
            pendingCards.AddRange(given);
            Plugin.Logger.LogInfo($"[AP] {given.Count} card(s) queued");
        }
        Notify = false;
        PlayerStats.Dump();
    }
}
