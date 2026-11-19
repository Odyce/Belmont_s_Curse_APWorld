namespace CVBC.Client;

public static class Dlc
{
    // The relic given by the paid DLC, and the key of its location in cvbc_data.json
    public const string FamilysGraveId = "Charm_TankOneHit";
    public const string FamilysGraveLocationKey = "item:Charm_TankOneHit";

    static bool freeCheckSent = false;

    // true / false once the game knows, null while BonusContentManager is not ready yet
    public static bool? OwnsFamilysGrave()
    {
        var manager = BonusContentManager._instance;
        if (manager == null || manager.bonusContents == null)
            return null;

        for (int i = 0; i < manager.bonusContents.Count; i++)
        {
            var content = manager.bonusContents[i];
            if (content == null || content.itemIDsUnlocked == null)
                continue;
            for (int j = 0; j < content.itemIDsUnlocked.Length; j++)
            {
                if (content.itemIDsUnlocked[j] == FamilysGraveId)
                    return manager.HasBonusContentUnlocked(content.GetID());
            }
        }
        return null;
    }

    // Without the DLC, the Starting Relic (DLC) location can never be reached: send it for free
    public static void SendFreeCheckIfNeeded()
    {
        if (freeCheckSent)
            return;

        bool? owned = OwnsFamilysGrave();
        if (owned == null)
            return;   // not known yet, retried at the next sync

        freeCheckSent = true;
        Plugin.Logger.LogInfo($"[DLC] Family's Grave DLC owned: {owned}");

        if (owned == false && GameData.Locations.TryGetValue(FamilysGraveLocationKey, out long apLocation))
        {
            Plugin.Logger.LogInfo($"[DLC] DLC not owned, Starting Relic (DLC) sent as a free check (AP location {apLocation})");
            APClient.SendCheck(apLocation);
        }
    }
}
