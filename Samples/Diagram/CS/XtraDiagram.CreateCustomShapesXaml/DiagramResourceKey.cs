using System;
using System.Linq;
using System.Windows;
using DevExpress.Diagram.Core;

namespace XtraDiagram.CreateCustomShapes {
    public class ShapeKey : ResourceKey, IOrderedKey {
        [ThreadStatic]
        static int idCore;
        readonly int id;
        readonly string resourceKey;

        public int Id { get { return id; } }
        public string ResourceKey { get { return resourceKey; } }
        public override System.Reflection.Assembly Assembly {
            get { return null; }
        }

        public ShapeKey(string resourceKey) {
            this.id = idCore++;
            this.resourceKey = resourceKey;
        }
    }
}
