using System.Collections.Generic;
using System.IO;
using BepInEx;
using Newtonsoft.Json;

namespace CVBC.Client;

// Small per-seed counters for what the game can't tell us (total EXP given)
public static class APState
{
    static Dictionary<string, int> values = null;
    static string path = null;

    static void EnsureLoaded()
    {
        if (values != null)
            return;
        string dir = Path.Combine(Paths.ConfigPath, "CVBC");
        Directory.CreateDirectory(dir);
        path = Path.Combine(dir, $"{APClient.Session.RoomState.Seed}_{APClient.Session.ConnectionInfo.Slot}.json");
        values = File.Exists(path)
            ? JsonConvert.DeserializeObject<Dictionary<string, int>>(File.ReadAllText(path))
            : new Dictionary<string, int>();
    }

    public static int Get(string key)
    {
        EnsureLoaded();
        return values.TryGetValue(key, out int n) ? n : 0;
    }

    public static void Set(string key, int value)
    {
        EnsureLoaded();
        values[key] = value;
        File.WriteAllText(path, JsonConvert.SerializeObject(values));
    }
}
