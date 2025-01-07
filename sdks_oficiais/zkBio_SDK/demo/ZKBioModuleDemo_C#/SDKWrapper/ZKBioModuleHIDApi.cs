using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace ZKBioModuleSDKWrapper
{
    public enum HID_ERRORCODE
    {
         ZKHID_ERROR_NONE = 0,
         ZKHID_ERROR_OPEN = -1,
         ZKHID_ERROR_NOTOPEN = -2,
         ZKHID_ERROR_PARAMETER = -3,
         ZKHID_ERROR_MEMORY = -4,
         ZKHID_ERROR_NO_MEMORY = -5,
         ZKHID_ERROR_SEND_CMD = -6,
         ZKHID_ERROR_READ_TIMEOUT = -7,
         ZKHID_ERROR_SET_CONFIG = -8,
         ZKHID_ERROR_IO = -9,
         ZKHID_ERROR_INVALID_FILE = -10,
         ZKHID_ERROR_INVALID_HEADER	= -11,
         ZKHID_ERROR_CHECKSUM = -12,
         ZKHID_ERROR_LOSS_PACKET = -13,
    }

    public enum HID_ConfigType
    {
        COMMON_CONFIG = 1,
        CAPTURE_FILTER_CONFIG = 2,
        MOTION_DETECT_CONFIG = 3,
        PALM_CONFIG = 4,
        DEVICE_INFORMATION = 5,
        DEVICE_TIME = 6
    }

    public enum HID_SnapShotType
    {
        SNAPSHOT_NIR = 0,
        SNAPSHOT_VL = 1
    }

    public enum HID_SendFileType
    {
        UPGRADE_IMAGE = 0,
        SEND_FILE = 1
    }

    public enum HID_ManageType
    {
        ADD_PERSON = 1,
        DEL_PERSON = 2,
        CLEAR_PERSON = 3,
        GET_PERSON = 4,
        QUERY_ALL_PERSON = 5,
        QUERY_STATISTICS = 6,
        ADD_FACE = 7,
        ADD_FACE_REG = 8,
        DETECT_FACE_REG = 9,
        REG_START = 10,
        REG_END = 11,
        DETECT_PALM_REG = 12,
        ADD_PALM = 13,
        ADD_PALM_REG = 14,
        MERGE_PALM_REG = 15,
        DEL_FACE_CACHEID = 16,
        DEL_PALM_CACHEID = 17,
        ATT_RECORD_COUNT = 18,
        EXPORT_ATT_RECORD = 19,
        CLEAR_ATT_RECORD = 20
    }

    public class ZKBioModuleHIDApi
    {
        [UnmanagedFunctionPointerAttribute(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void SendFileCallback(IntPtr userParam, int progress);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_Init();

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_Terminate();

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_GetCount(ref int count);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_Open(int index, ref IntPtr handle);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_Close(IntPtr handle);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_GetConfig(IntPtr handle, int type, byte[] json, ref int len);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_SetConfig(IntPtr handle, int type, String json);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_RegisterFace(IntPtr handle, String json, byte[] faceData, ref int len);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_RegisterPalm(IntPtr handle, String json, byte[] palmData, ref int len);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_MergePalm(IntPtr handle, byte[] palmData, ref int len);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_SendFile(IntPtr handle, int fileType, String filePath, SendFileCallback sendFileCallback, IntPtr pUserParam);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_SnapShot(IntPtr handle, int snapType, byte[] snapData, ref int len);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_Reboot(IntPtr handle, int mode);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_PollMatchResult(IntPtr handle, byte[] json, ref int len);

        [DllImport("ZKHIDLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKHID_ManageModuleData(IntPtr handle, int type, String json, byte[] result, ref int len);

        public static int init()
        {
            return ZKHID_Init();
        }

        public static int terminate()
        {
            return ZKHID_Terminate();
        }

        public static int getDeviceCount(ref int count)
        {
            return ZKHID_GetCount(ref count);
        }

        public static int openDevice(int index, ref IntPtr handle)
        {
            return ZKHID_Open(index, ref handle);
        }

        public static int closeDevice(IntPtr handle)
        {
            return ZKHID_Close(handle);
        }

        public static int getConfig(IntPtr handle, int type, ref String json)
        {
            byte[] bufData = new byte[2 * 1024];
            int length = 2 * 1024;
            int ret = ZKHID_GetConfig(handle, type, bufData, ref length);
            if (0 == ret)
            {
                json = System.Text.Encoding.UTF8.GetString(bufData, 0, length);
            }
            return ret;
        }

        public static int setConfig(IntPtr handle, int type, String json)
        {
            return ZKHID_SetConfig(handle, type, json);
        }

        public static int registerFace(IntPtr handle, String json, ref String faceData)
        {
            byte[] bufData = new byte[20 * 1024];
            int length = 20 * 1024;
            int ret = ZKHID_RegisterFace(handle, json, bufData, ref length);
            if (0 == ret)
            {
                faceData = System.Text.Encoding.UTF8.GetString(bufData, 0, length);
            }
            return ret;
        }

        public static int registerPalm(IntPtr handle, String json, ref String palmData)
        {
            byte[] bufData = new byte[200 * 1024];
            int length = 200 * 1024;
            int ret = ZKHID_RegisterPalm(handle, json, bufData, ref length);
            if (0 == ret)
            {
                palmData = System.Text.Encoding.UTF8.GetString(bufData, 0, length);
            }
            return ret;
        }

        public static int mergePalm(IntPtr handle, ref String palmData)
        {
            byte[] bufData = new byte[20 * 1024];
            int length = 20 * 1024;
            int ret = ZKHID_MergePalm(handle, bufData, ref length);
            if (0 == ret)
            {
                palmData = System.Text.Encoding.UTF8.GetString(bufData, 0, length);
            }
            return ret;
        }

        public static int sendFile(IntPtr handle, int fileType, String filePath, SendFileCallback sendFileCallback, IntPtr pUserParam)
        {
            return ZKHID_SendFile(handle, fileType, filePath, sendFileCallback, pUserParam);
        }

        public static int snapShot(IntPtr handle, int snapType, ref String snapData)
        {
            byte[] bufData = new byte[2 * 1024 * 1024];
            int length = 2 * 1024 * 1024;
            int ret = ZKHID_SnapShot(handle, snapType, bufData, ref length);
            if (0 == ret)
            {
                snapData = System.Text.Encoding.UTF8.GetString(bufData, 0, length);
            }
            return ret;
        }

        public static int reboot(IntPtr handle, int mode)
        {
            return ZKHID_Reboot(handle, mode);
        }

        public static int pollMatchResult(IntPtr handle, ref String json)
        {
            byte[] bufData = new byte[40 * 1024];
            int length = 40 * 1024;
            int ret = ZKHID_PollMatchResult(handle, bufData, ref length);
            if (0 == ret)
            {
                json = System.Text.Encoding.UTF8.GetString(bufData, 0, length);
            }
            return ret;
        }
 
        public static int manageModuleData(IntPtr handle, int type, String json, byte[] result, ref int len)
        {
            return ZKHID_ManageModuleData(handle, type, json, result, ref len);
        }
    }
}
