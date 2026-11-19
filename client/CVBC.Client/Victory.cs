namespace CVBC.Client;

public static class Victory
{
    // end_goal from slot data: 0 = Bad, 1 = Neutral (Normal), 2 = True, same order as GameEndingState
    public static int Goal = -1;

    public static void OnEndingReached(GameEndingState ending)
    {
        int reached = (int)ending;
        Plugin.Logger.LogInfo($"[Goal] ending reached: {ending} ({reached}), goal is {Goal}");
        if (Goal < 0 || reached < Goal)
            return;

        APState.Set("goal", 1);
        Send();
    }

    // Also called by Sync, so a goal reached while disconnected is sent at the next connection
    public static void Send()
    {
        if (APState.Get("goal") != 1)
            return;
        if (APClient.Session == null || !APClient.Session.Socket.Connected)
        {
            Plugin.Logger.LogWarning("[Goal] not connected, will be sent at the next connection");
            return;
        }
        APClient.Session.SetGoalAchieved();
        Plugin.Logger.LogInfo("[Goal] goal sent to the server!");
    }
}
