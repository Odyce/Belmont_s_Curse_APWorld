using System.Collections.Generic;

namespace CVBC.Client;

static class CheckTracker
{
    public static string PendingSavedId = null;

    // Display subsitution for the cards when getting an item, we need those infos
    public static string DisplayOriginalId = null;
    public static ItemData DisplayReplacement = null;
    
    public static bool GivingFromAP = false;

    public static readonly HashSet<string> ShownAtCheck = new();

    public static long? PendingFragmentLocation = null;

    // Given in the initial inventory (fromInit) at new game, never through a normal pickup
    public static readonly HashSet<string> StartingKeys = new()
    {
        "item:WeaponOneHandedTier1",       // Starting Weapon
        "item:Clue_Doppelganger_FirstCard", // Starting Clue
        "item:CursedFireBall",             // Starting Tarot Card
    };
}
