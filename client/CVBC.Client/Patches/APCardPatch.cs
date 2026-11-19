using HarmonyLib;

namespace CVBC.Client.Patches;

[HarmonyPatch(typeof(InventoryItemDisplayBase), nameof(InventoryItemDisplayBase.SetItemToDisplay))]
public static class APCardDisplayPatch
{
    static void Postfix(InventoryItemDisplayBase __instance, ItemData item)
        => Safe.Run("APCardDisplayPatch", () => Body(__instance, item));

    private static void Body(InventoryItemDisplayBase __instance, ItemData item)
    {
        if (item != null && item.itemID == APCard.PlaceholderId && APCard.Pending != null)
        {
            APCard.Shown = APCard.Pending;
            APCard.Pending = null;
            APCard.CurrentDisplay = __instance;

            APCard.ApplyText(__instance.itemNameText);
            APCard.ApplyText(__instance.itemDescriptionText);
            APCard.ApplyText(__instance.itemSecondaryDescritpionText);

            var sprite = APCard.GetSprite();
            if (sprite != null && __instance.itemIconImage != null)
                __instance.itemIconImage.sprite = sprite;

            Plugin.Logger.LogInfo($"[APCard] showing {APCard.Shown.Name}");
        }
        else if (APCard.CurrentDisplay != null && __instance.Pointer == APCard.CurrentDisplay.Pointer)
        {
            // Same card reused for a real item: back to normal
            APCard.Shown = null;
            APCard.CurrentDisplay = null;
        }
    }
}

[HarmonyPatch(typeof(UILocalizedString), nameof(UILocalizedString.UpdateString))]
public static class APCardTextPatch
{
    static void Postfix(UILocalizedString __instance)
        => Safe.Run("APCardTextPatch", () => Body(__instance));

    private static void Body(UILocalizedString __instance)
    {
        if (APCard.Shown == null || APCard.CurrentDisplay == null)
            return;
        if (!__instance.transform.IsChildOf(APCard.CurrentDisplay.transform))
            return;
        APCard.ApplyText(__instance);
    }
}

[HarmonyPatch(typeof(ItemAcquisitionController), nameof(ItemAcquisitionController.TryQuickEquip))]
public static class APCardQuickEquipPatch
{
    static bool Prefix(ItemAcquisitionController __instance)
        => Safe.Run("APCardQuickEquipPatch", () => Body(__instance));

    private static bool Body(ItemAcquisitionController __instance)
    {
        if (APCard.CurrentDisplay == null)
            return true;
        return __instance.gameObject.Pointer != APCard.CurrentDisplay.gameObject.Pointer;
    }
}
