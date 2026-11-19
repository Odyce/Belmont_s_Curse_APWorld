using System.IO;
using Archipelago.MultiClient.Net.Enums;
using Archipelago.MultiClient.Net.Models;
using UnityEngine;
using Il2CppInterop.Runtime.InteropTypes;

namespace CVBC.Client;

public class APCardText
{
    public string Name;
    public string Description;
    public string Lore;
}

public static class APCard
{
    // Only these item types have an acquisition card (see ItemAcquisitionGlobalController)
    public static bool HasAcquisitionCard(ItemData item)
    {
        if (item == null)
            return false;
        return item.TryCast<WeaponItemData>() != null
            || item.TryCast<SpellItemData>() != null
            || item.TryCast<VaniaMoveItemData>() != null
            || item.TryCast<CharmItemData>() != null
            || item.TryCast<QuestItemData>() != null;
    }


    // Lich's Mark: borrowed only for its card layout, never given
    public const string PlaceholderId = "Charm_ReduceSpellManaCostSpam";
    public const string ImageFile = "Illustration_20261018_1.png";

    public static APCardText Pending = null;
    public static APCardText Shown = null;
    public static InventoryItemDisplayBase CurrentDisplay = null;

    static Sprite sprite = null;

    public static APCardText TextFor(ScoutedItemInfo info)
    {
        bool progression = (info.Flags & ItemFlags.Advancement) != 0;
        return new APCardText
        {
            Name = info.ItemDisplayName,
            Description = APClient.IsForMe(info) ? "For you" : $"For {info.Player.Name} ({info.ItemGame})",
            Lore = progression ? "Archipelago item - Progression" : "Archipelago item",
        };
    }

    public static void ApplyText(UILocalizedString s)
    {
        if (Shown == null || s == null || s.textDisplay == null)
            return;
        switch (s.gameObject.name)
        {
            case "ItemName": s.textDisplay.text = Shown.Name; break;
            case "ItemDescription_Gameplay": s.textDisplay.text = Shown.Description; break;
            case "ItemDescription_Lore": s.textDisplay.text = Shown.Lore; break;
        }
    }

    public static Sprite GetSprite()
    {
        if (sprite != null)
            return sprite;

        string path = Path.Combine(Path.GetDirectoryName(typeof(Plugin).Assembly.Location), ImageFile);
        if (!File.Exists(path))
        {
            Plugin.Logger.LogWarning($"[APCard] {ImageFile} not found next to the DLL");
            return null;
        }

        var texture = new Texture2D(2, 2);
        if (!ImageConversion.LoadImage(texture, File.ReadAllBytes(path)))
        {
            Plugin.Logger.LogWarning($"[APCard] could not read {ImageFile}");
            return null;
        }
        texture.hideFlags = HideFlags.HideAndDontSave;

        sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f));
        sprite.hideFlags = HideFlags.HideAndDontSave;
        return sprite;
    }
}
