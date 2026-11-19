using System;

namespace CVBC.Client;

// Every Harmony patch runs through here: an exception is logged, never thrown back into the game
public static class Safe
{
    public static void Run(string where, Action action)
    {
        try { action(); }
        catch (Exception e) { Plugin.Logger.LogError($"[{where}] {e}"); }
    }

    // For prefixes returning bool: on error, let the game run its original code
    public static bool Run(string where, Func<bool> prefix)
    {
        try { return prefix(); }
        catch (Exception e)
        {
            Plugin.Logger.LogError($"[{where}] {e}");
            return true;
        }
    }
}