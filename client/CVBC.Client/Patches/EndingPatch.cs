using HarmonyLib;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(GameEndingStateVariableSetter), nameof(GameEndingStateVariableSetter.SetTargetEndingState))]
public static class EndingPatch
{
    static void Prefix(GameEndingStateVariableSetter __instance)
        => Safe.Run("EndingPatch", () => Victory.OnEndingReached(__instance.targetEndingState));
}

// Fallback log: if the credits start without an "ending reached" line before, the hook above is not the right one
[HarmonyPatch(typeof(CreditsViewManager), "Start")]
public static class CreditsPatch
{
    static void Prefix()
        => Safe.Run("CreditsPatch", () => Plugin.Logger.LogInfo("[Goal] credits started"));
}
