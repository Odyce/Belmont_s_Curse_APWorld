using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;

namespace CVBC.Client;

[BepInPlugin("odyce.cvbc.client", "CVBC Archipelago Client", Version)]
public class Plugin : BasePlugin
{

    // Must match WORLD_VERSION in the APWorld (Types.py)
    public const string Version = "0.1.0";
    
    internal static ManualLogSource Logger;

    public override void Load()
    {
        Logger = Log;
        
        string host = Config.Bind("Archipelago", "Server", "localhost:38281", "Server address and port").Value;
        string slot = Config.Bind("Archipelago", "Slot", "Rose", "Your slot name, as written in your YAML").Value;
        string password = Config.Bind("Archipelago", "Password", "", "Room password, empty if none").Value;
        
        Logger.LogInfo("CVBC client loaded!");
        GameData.Load();
        Logger.LogInfo($"{GameData.Locations.Count} locations created, and {GameData.Items.Count} items created");
        
        new Harmony("odyce.cvbc.client").PatchAll();
        Logger.LogInfo("Patches applied");
        
        APClient.Configure(host, slot, password);
        APClient.LoadPending();
        AddComponent<APBehaviour>();
    }
}
