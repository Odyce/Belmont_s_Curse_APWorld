using HarmonyLib;
using Il2CppInterop.Runtime;
using MotherBase.EntityFramework;

namespace CVBC.Client.Patches;

// Heart fragments, step 1: remember which fragment the player interacts with
[HarmonyPatch(typeof(InteractFeature), nameof(InteractFeature.PlayEffect))]
public static class FragmentInteractPatch
{
    static void Prefix(Entity e)
        => Safe.Run("FragmentInteractPatch", () => Body(e));

    private static void Body(Entity e)
    {
        var interactor = e == null ? null : e.GetComponentInChildren<Interactor>();
        var target = interactor == null ? null : interactor.currentInteractionInteractible;
        if (target == null || !target.name.StartsWith("GPE_UpgradeCollectible"))
            return;

        string id = SaveIds.Of(target);
        if (id != null && GameData.Locations.TryGetValue(id, out long apLocation))
            CheckTracker.PendingFragmentLocation = apLocation;
    }
}

// Heart fragments, step 2: block the fragment count increase and send the check instead
[HarmonyPatch(typeof(AffectStatFeature), nameof(AffectStatFeature.PlayEffect))]
public static class FragmentStatPatch
{
    static bool Prefix(AffectStatFeature __instance)
        => Safe.Run("FragmentStatPatch", () => Body(__instance));

    private static bool Body(AffectStatFeature __instance)
    {
        if (CheckTracker.PendingFragmentLocation == null || __instance.targetStat == null)
            return true;

        string stat = __instance.targetStat.GetIl2CppType().Name;
        if (stat != "HealthUpgradeFragmentTotalCount" && stat != "ManaUpgradeFragmentTotalCount")
            return true;

        var reaction = __instance.affectStatReaction;
        Plugin.Logger.LogInfo($"[Diag] fragment reaction: {(reaction == null ? "none" : reaction.GetIl2CppType().Name)}");

        long apLocation = CheckTracker.PendingFragmentLocation.Value;
        CheckTracker.PendingFragmentLocation = null;

        Plugin.Logger.LogInfo($"[Check] fragment: AP location {apLocation}, contains {APClient.Describe(apLocation)}");
        APClient.SendCheck(apLocation);
        return false;
    }
}
