using System;
using UnityEngine;

namespace CVBC.Client;

public class APBehaviour : MonoBehaviour
{
    // Reconnection: first attempt right away, then 5 s, 10 s, 20 s... up to 60 s between attempts
    static float nextAttempt = 0f;
    static float retryDelay = 5f;
    static bool wasConnected = false;

    static void KeepConnected()
    {
        float now = Time.realtimeSinceStartup;

        if (APClient.IsConnected)
        {
            if (!wasConnected)
            {
                wasConnected = true;
                retryDelay = 5f;
            }
            return;
        }

        if (wasConnected)
        {
            wasConnected = false;
            nextAttempt = now;
            Plugin.Logger.LogWarning("[AP] connection lost, trying to reconnect");
        }

        if (!APClient.Connecting && now >= nextAttempt)
        {
            APClient.StartConnect();
            nextAttempt = now + retryDelay;
            retryDelay = Math.Min(retryDelay * 2f, 60f);
        }
    }


    // Required by IL2CPP: Unity creates the C# object around an existing native object
    public APBehaviour(IntPtr ptr) : base(ptr) { }

    public void Update()
    {
        try
        {
            KeepConnected();
            if (ItemSync.NeedsSync)
                ItemSync.Sync();
            ItemSync.TryShowCards();
        }
        catch (Exception e)
        {
            Plugin.Logger.LogError($"[AP] Update error: {e}");
        }
    }

    // Small AP status line, bottom-left of the screen
    public void OnGUI()
    {
        try
        {
            string text = APClient.IsConnected ? "AP: connected" : "AP: disconnected, reconnecting...";
            int pending = APClient.PendingCount;
            if (pending > 0)
                text += $"  |  {pending} check(s) waiting to be sent";
            if (APClient.VersionWarning != null)
                text += $"  |  Version mismatch: {APClient.VersionWarning}";

            GUI.color = APClient.IsConnected && APClient.VersionWarning == null ? Color.white : Color.yellow;
            GUI.Label(new Rect(10, Screen.height - 30, 1200, 25), text);
        }
        catch (Exception e)
        {
            Plugin.Logger.LogError($"[AP] OnGUI error: {e}");
        }
    }
}
