using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Windows.Forms;
using DevExpress.XtraRichEdit;
using System.Linq.Expressions;

namespace RichEditControlEventViewer
{
    public class RichEditEventHooker
    {
        #region Fields
        string eventName;
        Form1 owner;
        Delegate handler;
        #endregion

        public RichEditEventHooker(string eventName, Form1 owner)
        {
            this.eventName = eventName;
            this.owner = owner;
        }

        #region Properties
        public string Name { get { return eventName; } }
        protected virtual string MethodName { get { return "InitializeEventLogger"; } }
        #endregion

        #region CreateEventProxy
        Delegate CreateEventProxy(EventInfo eInfo)
        {
            Type eventHandlerType = eInfo.EventHandlerType;
            MethodInfo mInfo = eventHandlerType.GetMethod("Invoke");
            MethodInfo loggerMethodInfo = typeof(Form1).GetMethod(MethodName, BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Instance | BindingFlags.Static);
            ParameterInfo[] pInfo = mInfo.GetParameters();
            ParameterExpression eventSender = Expression.Parameter(typeof(object), "sender");
            ParameterExpression eventArgs = Expression.Parameter(pInfo[1].ParameterType, "args");
            return Expression.Lambda(eventHandlerType, Expression.Call(Expression.Constant(owner), loggerMethodInfo, Expression.Constant(eventName), eventSender, eventArgs), eventSender, eventArgs).Compile();
        }
        #endregion

        public bool HookEvent(RichEditControl control)
        {
            Type controlType = typeof(RichEditControl);
            EventInfo eInfo = controlType.GetEvent(eventName);

            //if (eventName.Contains("Draw")) return false;

            if (handler == null)
                handler = CreateEventProxy(eInfo);

            try
            {
                eInfo.AddEventHandler(control, handler);
            }
            catch (ArgumentException e)
            {
                MessageBox.Show(e.Message, "Cannot hook an event", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return false;
            }
            return true;
        }

        public void UnhookEvent(RichEditControl control)
        {
            if (handler != null)
            {
                Type controlType = typeof(RichEditControl);
                EventInfo eInfo = controlType.GetEvent(eventName);
                eInfo.RemoveEventHandler(control, handler);
            }
        }
    }
}
