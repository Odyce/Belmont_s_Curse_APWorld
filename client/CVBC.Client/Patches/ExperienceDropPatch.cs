using HarmonyLib;
using MotherBase.EntityFramework;

namespace CVBC.Client.Patches;

// EXP statues: block the experience balls dropped by a statue that is a location
[HarmonyPatch(typeof(ExperienceLootData), nameof(ExperienceLootData.Drop))]
public static class ExperienceDropPatch
{
    static bool Prefix(Entity droppingEntity)
        => Safe.Run("ExperienceDropPatch", () => Body(droppingEntity));

    private static bool Body(Entity droppingEntity)
    {
        string id = SaveIds.Of(droppingEntity);
        if (id == null || !GameData.Locations.TryGetValue(id, out long apLocation))
            return true;

        APClient.SendCheck(apLocation);
        Plugin.Logger.LogInfo($"[Check] {id}: blocked experience drop");
        return false;
    }
}
