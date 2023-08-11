#pragma warning disable CS1591

namespace Rizonesoft.Office.Utilities
{
    public static class ActionsManager
    {
        public static void ExecuteAction(Actions action)
        {
            switch (action)
            {
                case Actions.ShowMessageOne:
                    MessageBox.Show("Message One");
                    break;
                case Actions.ShowMessageTwo:
                    MessageBox.Show("Message Two");
                    break;
                default:
                    throw new ArgumentOutOfRangeException(nameof(action), action, null);
            }
        }
    }
}
