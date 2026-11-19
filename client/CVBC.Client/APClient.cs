using System;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using BepInEx;
using System.Collections.Generic;
using Archipelago.MultiClient.Net;
using Archipelago.MultiClient.Net.Enums;
using Archipelago.MultiClient.Net.Models;
using Newtonsoft.Json;

namespace CVBC.Client;

public static class APClient
{
    public static ArchipelagoSession Session = null;

    private static readonly HashSet<long> pendingChecks = new();

    // Set when the seed was generated with another APWorld version, shown on screen
    public static volatile string VersionWarning = null;

    class PendingFile
    {
        public string Seed;
        public List<long> Checks = new();
    }

    static string pendingSeed = null;   // seed the pending checks belong to (last seed we were connected to)

    static string PendingPath => Path.Combine(Paths.ConfigPath, "CVBC", "pending_checks.json");

    public static void LoadPending()
    {
        try
        {
            if (!File.Exists(PendingPath))
                return;
            var file = JsonConvert.DeserializeObject<PendingFile>(File.ReadAllText(PendingPath));
            lock (pendingChecks)
            {
                foreach (long id in file.Checks)
                    pendingChecks.Add(id);
                pendingSeed = file.Seed;
            }
            Plugin.Logger.LogInfo($"[AP] {file.Checks.Count} pending check(s) loaded from disk");
        }
        catch (Exception e)
        {
            Plugin.Logger.LogError($"[AP] could not read the pending checks: {e.Message}");
        }
    }

    // Always called with the pendingChecks lock held
    static void SavePending()
    {
        try
        {
            Directory.CreateDirectory(Path.GetDirectoryName(PendingPath));
            var file = new PendingFile { Seed = pendingSeed, Checks = pendingChecks.ToList() };
            File.WriteAllText(PendingPath, JsonConvert.SerializeObject(file));
        }
        catch (Exception e)
        {
            Plugin.Logger.LogError($"[AP] could not save the pending checks: {e.Message}");
        }
    }

    public static int PendingCount
    {
        get { lock (pendingChecks) return pendingChecks.Count; }
    }

    public static volatile Dictionary<long, ScoutedItemInfo> Scouted = new Dictionary<long, ScoutedItemInfo>();

    // Connection settings, given once by Plugin.Load
    static string host, slot, password;

    // True while a connection attempt runs in the background (only one at a time)
    public static volatile bool Connecting = false;

    public static bool IsConnected
    {
        get
        {
            var session = Session;
            return session != null && session.Socket.Connected;
        }
    }

    public static void Configure(string serverHost, string slotName, string serverPassword)
    {
        host = serverHost;
        slot = slotName;
        password = serverPassword;
    }

    public static void SendCheck(long locationId)
    {
        lock (pendingChecks)
        {
            pendingChecks.Add(locationId);
            SavePending();
        }
        FlushChecks();
    }

    public static void FlushChecks()
    {
        var session = Session;
        if (session == null || !session.Socket.Connected)
            return;

        long[] ids;
        lock (pendingChecks)
        {
            ids = pendingChecks.ToArray();
            pendingChecks.Clear();
            SavePending();
        }
        if (ids.Length == 0)
            return;

        try
        {
            session.Locations.CompleteLocationChecks(ids);
            Plugin.Logger.LogInfo($"[AP] sent {ids.Length} check(s)");
        }
        catch (Exception e)
        {
            // Connection lost while sending: keep them for the next connection
            lock (pendingChecks)
            {
                foreach (long id in ids)
                    pendingChecks.Add(id);
                SavePending();
            }
            Plugin.Logger.LogWarning($"[AP] could not send {ids.Length} check(s), kept for later: {e.Message}");
        }
    }

    // Starts a connection attempt in the background, unless one is already running
    public static void StartConnect()
    {
        if (Connecting)
            return;
        Connecting = true;
        Task.Run(() =>
        {
            try { Connect(); }
            finally { Connecting = false; }
        });
    }

    static void Connect()
    {
        try
        {
            var session = ArchipelagoSessionFactory.CreateSession(host);
            LoginResult result = session.TryConnectAndLogin("Castlevania: Belmont's Curse", slot, ItemsHandlingFlags.AllItems, password: password);

            if (result is LoginSuccessful success)
            {
                Session = session;
                Plugin.Logger.LogInfo($"Connected as {slot} (slot {success.Slot})");
                Victory.Goal = Convert.ToInt32(success.SlotData["end_goal"]);
                Plugin.Logger.LogInfo($"Goald: {Victory.Goal}, Deathlink: {success.SlotData["death_link"]}");

                success.SlotData.TryGetValue("world_version", out object worldVersion);
                if (worldVersion?.ToString() != Plugin.Version)
                {
                    VersionWarning = $"seed made with APWorld {worldVersion ?? "unknown"}, client is {Plugin.Version}";
                    Plugin.Logger.LogWarning($"[AP] version mismatch: {VersionWarning}");
                }
                else
                    VersionWarning = null;

                session.Items.ItemReceived += helper =>
                {
                    ItemSync.NeedsSync = true;
                    ItemSync.Notify = true;
                };

                // Pending checks made for another seed must not be sent to this one
                string seed = session.RoomState.Seed;
                lock (pendingChecks)
                {
                    if (pendingSeed != null && pendingSeed != seed && pendingChecks.Count > 0)
                    {
                        Plugin.Logger.LogWarning($"[AP] {pendingChecks.Count} pending check(s) belong to another seed ({pendingSeed}), discarded");
                        pendingChecks.Clear();
                    }
                    pendingSeed = seed;
                    SavePending();
                }

                ItemSync.NeedsSync = true;
                FlushChecks();

                long[] allLocations = session.Locations.AllLocations.ToArray();
                Scouted = session.Locations.ScoutLocationsAsync(allLocations).GetAwaiter().GetResult();
                Plugin.Logger.LogInfo($"[AP] scouted {Scouted.Count} locations");
            }
            else
            {
                var failure = (LoginFailure)result;
                Plugin.Logger.LogError($"Connection failed: {string.Join(", ", failure.Errors)}");
            }
        }
        catch (Exception e)
        {
            Plugin.Logger.LogError($"Connection error: {e.Message}");
        }
    }

    public static bool IsForMe(ScoutedItemInfo info)
    {
        return info.Player.Slot == Session.ConnectionInfo.Slot;
    }

    public static string Describe(long location)
    {
        if (!Scouted.TryGetValue(location, out ScoutedItemInfo info))
            return "unknown (not scouted)";
        return $"{info.ItemDisplayName} for {info.Player.Name}" + (IsForMe(info) ? " (me)" : "");
    }
}
