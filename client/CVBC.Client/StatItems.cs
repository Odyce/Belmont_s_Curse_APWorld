using System;
using System.Collections.Generic;
using static AffectStatHealthUpgradeCountReaction;
using static AffectStatManaUpgradeCountReaction;

namespace CVBC.Client;

public static class StatItems
{
    // received: AP item name -> number of copies received
    public static void Apply(Dictionary<string, int> received)
    {
        var player = PlayerStats.Player();
        if (player == null)
            return;

        TopUp<HealthUpgradeFragmentTotalCount>("Brave Heart Fragment", received,
            () => new AffectStatHealthUpgradeCountReaction(HealthAdaptationType.KeepHealthRatio));
        TopUp<ManaUpgradeFragmentTotalCount>("Wise Heart Fragment", received,
            () => new AffectStatManaUpgradeCountReaction(ManaAdaptationType.KeepManaRatio));
        TopUp<PowerAttackBonus>("ATK Book", received, null);
        TopUp<PowerDefenseBonus>("DEF Book", received, null);

        GiveExperience(received);
    }

    static void TopUp<T>(string itemName, Dictionary<string, int> received, Func<AffectStatReaction> reaction)
        where T : AFloatStat, new()
    {
        received.TryGetValue(itemName, out int wanted);
        int current = (int)PlayerStats.Get<T>();
        if (current < 0)
        {
            Plugin.Logger.LogWarning($"[AP] stat for {itemName} not found, will retry on next sync");
            return;
        }

        for (int i = current; i < wanted; i++)
        {
            var parameters = new AffectStatParameters();
            parameters.targetStat = new T();
            parameters.affectType = AffectStatType.IncrementOne;
            parameters.affectStatReaction = reaction == null ? null : reaction();
            AffectStatFeature.AffectStat(PlayerStats.Player(), parameters);
            Plugin.Logger.LogInfo($"[AP] received {itemName} ({i + 1}/{wanted})");
        }
    }

    static void GiveExperience(Dictionary<string, int> received)
    {
        int wanted = 0;
        foreach (var pair in received)
            if (pair.Key.StartsWith("Experience Statue ") && int.TryParse(pair.Key.Substring(18), out int amount))
                wanted += amount * pair.Value;

        int given = APState.Get("experience");
        if (wanted <= given)
            return;

        var xp = PlayerStats.Experience();
        if (xp == null)
            return;
        xp.IncrementCurrentExperience(PlayerStats.Player(), wanted - given);
        APState.Set("experience", wanted);
        Plugin.Logger.LogInfo($"[AP] received {wanted - given} experience");
    }
}
