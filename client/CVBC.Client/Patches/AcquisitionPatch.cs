using HarmonyLib;
using Il2CppInterop.Runtime.InteropTypes.Arrays;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(ItemAcquisitionGlobalController), nameof(ItemAcquisitionGlobalController.OpenAcquisitionForItems))]
public static class AcquisitionPatch
{
    static void Prefix(Il2CppReferenceArray<ItemData> itemData)
        => Safe.Run("AcquisitionPatch", () => Body(itemData));

    private static void Body(Il2CppReferenceArray<ItemData> itemData)
    {
        if (CheckTracker.DisplayOriginalId == null || itemData == null)
            return;

        bool swapped = false;
        if (CheckTracker.DisplayReplacement != null)
        {
            for (int k = 0; k < itemData.Length; k++)
            {
                var item = itemData[k];
                if (item != null && item.itemID == CheckTracker.DisplayOriginalId)
                {
                    itemData[k] = CheckTracker.DisplayReplacement;
                    swapped = true;
                    Plugin.Logger.LogInfo($"[Display] card {item.itemID} became {CheckTracker.DisplayReplacement.itemID}");
                }
            }
        }
        if (!swapped)
            APCard.Pending = null;

        CheckTracker.DisplayOriginalId = null;
        CheckTracker.DisplayReplacement = null;
    }
}
