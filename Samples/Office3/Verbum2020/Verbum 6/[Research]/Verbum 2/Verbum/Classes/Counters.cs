using System.Text.RegularExpressions;


namespace Datum.Verbum
{
    class Counters
    {
        public static int CountWords(string sDoc)
        {
            MatchCollection collection = Regex.Matches(sDoc, @"[\S]+");
            return collection.Count;
        }
    }
}
