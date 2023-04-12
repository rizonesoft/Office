using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Rizonesoft.Office.Verbum.Classes
{
    using System;
    using System.Collections.Generic;
    using System.IO;
    using System.Linq;

    public class CustomWordNet
    {
        private readonly string _wordNetDatabasePath;

        public CustomWordNet(string wordNetDatabasePath)
        {
            _wordNetDatabasePath = wordNetDatabasePath;
        }

        public List<string> GetSynonyms(string word)
        {
            List<string> synonyms = new List<string>();

            string indexFilePath = Path.Combine(_wordNetDatabasePath, "index.noun");
            string dataFilePath = Path.Combine(_wordNetDatabasePath, "data.noun");

            using var indexReader = new StreamReader(indexFilePath);
            string line;
            while ((line = indexReader.ReadLine()) != null)
            {
                if (!line.StartsWith(word)) continue;

                string[] parts = line.Split(' ', StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length < 4) continue;

                int pointerCount = int.Parse(parts[2]);
                int[] synsetOffsets = parts.Skip(4 + pointerCount).Select(int.Parse).ToArray();

                using var dataReader = new StreamReader(dataFilePath);
                foreach (int offset in synsetOffsets)
                {
                    dataReader.BaseStream.Seek(offset, SeekOrigin.Begin);

                    string synsetData = dataReader.ReadLine();
                    string[] synsetParts = synsetData.Split(' ', StringSplitOptions.RemoveEmptyEntries);

                    int wordCount = Convert.ToInt32(synsetParts[3], 16);
                    for (int i = 0; i < wordCount; i++)
                    {
                        string synonym = synsetParts[4 + i * 2];
                        if (!synonym.Equals(word, StringComparison.OrdinalIgnoreCase))
                        {
                            synonyms.Add(synonym.Replace('_', ' '));
                        }
                    }
                }
                break;
            }
            return synonyms.Distinct().ToList();
        }
    }
}
