using HarmonyLib;
using System.Collections.Generic;
using Newtonsoft.Json.Linq;

namespace CVBC.Client;

static class GameData
{
    public static Dictionary<string, long> Locations = new();
    public static Dictionary<long, JObject> Items = new();
    public static Dictionary<string, List<string>> Progressive = new();

    public static void Load()
    {
        string dir = System.IO.Path.GetDirectoryName(typeof(Plugin).Assembly.Location);
        string path = System.IO.Path.Combine(dir, "cvbc_data.json");

        var root = JObject.Parse(System.IO.File.ReadAllText(path));

        foreach (var prop in ((JObject)root["locations"]).Properties())
            Locations[prop.Name] = (long)prop.Value;
        
        foreach (var prop in ((JObject)root["items"]).Properties())
            Items[long.Parse(prop.Name)] = (JObject)prop.Value;
        
        foreach (var prop in ((JObject)root["progressive"]).Properties())
            Progressive[prop.Name] = prop.Value.ToObject<List<string>>();
    }
}
