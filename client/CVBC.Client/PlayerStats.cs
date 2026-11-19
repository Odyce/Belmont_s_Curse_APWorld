using Il2CppInterop.Runtime;
using MotherBase.EntityFramework;

namespace CVBC.Client;

public static class PlayerStats
{
    public static ExperienceComponent Experience()
    {
        foreach (var xp in UnityEngine.Object.FindObjectsOfType<ExperienceComponent>())
            if (xp.isMcEntity)
                return xp;
        return null;
    }

    public static Entity Player()
    {
        var xp = Experience();
        return xp == null ? null : xp.linkedEntity;
    }

    public static float Get<T>() where T : AFloatStat
    {
        var player = Player();
        var stats = player == null ? null : player.GetComponent<StatsStateComponent>();
        var stat = stats == null ? null : stats.GetStatObject(Il2CppType.Of<T>());
        return stat == null ? -1 : stat.GetFloat(player);
    }

    public static void Dump()
    {
        Plugin.Logger.LogInfo($"[Stats] HP fragments: total {Get<HealthUpgradeFragmentTotalCount>()}, unmerged {Get<HealthUpgradeFragmentUnmergedCount>()}, upgrades {Get<HealthUpgradeCount>()}");
        Plugin.Logger.LogInfo($"[Stats] MP fragments: total {Get<ManaUpgradeFragmentTotalCount>()}, unmerged {Get<ManaUpgradeFragmentUnmergedCount>()}, upgrades {Get<ManaUpgradeCount>()}");
        Plugin.Logger.LogInfo($"[Stats] books: ATK {Get<PowerAttackBonus>()}, DEF {Get<PowerDefenseBonus>()}");
        var xp = Experience();
        if (xp != null)
            Plugin.Logger.LogInfo($"[Stats] level {xp.GetLevel()}, exp {xp.GetExperienceCurrent()} / {xp.GetExperienceMax()}");
    }
}
