using BepInEx;
using BepInEx.Logging;
using BepInEx.Unity.IL2CPP;
using HarmonyLib;

namespace CVBC.Client;

[BepInPlugin("odyce.cvbc.client", "CVBC Archipelago Client", "0.1.0")]
public class Plugin : BasePlugin
{
    internal static ManualLogSource Logger;

    public override void Load()
    {
        Logger = Log;
        Logger.LogInfo("CVBC client loaded!");
        new Harmony("odyce.cvbc.client").PatchAll();
        Logger.LogInfo("Patches applied");
    }
}
