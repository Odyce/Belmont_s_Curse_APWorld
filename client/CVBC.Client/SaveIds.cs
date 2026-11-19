namespace CVBC.Client;

public static class SaveIds
{
    public static string Of(UnityEngine.Component c)
    {
        if (c == null)
            return null;
        var savable = c.GetComponentInParent<SavableEntityBase>();
        if (savable == null)
            return null;
        return string.IsNullOrEmpty(savable.Id) ? savable.guid : savable.Id;
    }
}
