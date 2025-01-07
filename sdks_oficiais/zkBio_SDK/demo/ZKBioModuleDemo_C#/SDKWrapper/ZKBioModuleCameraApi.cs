using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace ZKBioModuleSDKWrapper
{

    public struct UVCCustomData
    {
        public UInt64 frame_index;
        public Int32 width;
        public Int32 height;
        public IntPtr customData;
    }

    public struct UVCVedioData
    {
        public Int32 frame_index;
        public Int32 ori_length;
        public Int32 data_length;
        public IntPtr data;
    }


    public class ZKBioModuleCameraApi
    {
        [UnmanagedFunctionPointerAttribute(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void FrameBufferCallback(byte[] data, int size);

        [UnmanagedFunctionPointerAttribute(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void VideoDataCallback(IntPtr userParam, UVCVedioData data);

        [UnmanagedFunctionPointerAttribute(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void CustomDataCallback(IntPtr userParam, UVCCustomData data);

        [UnmanagedFunctionPointerAttribute(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void VideoByteDataCallback(byte[] data, int length, int ori_length, Int32 frame_index);

        [UnmanagedFunctionPointerAttribute(CallingConvention.StdCall, CharSet = CharSet.Ansi)]
        public delegate void CustomByteDataCallback(byte[] data, int length, int face_count, int width, int height, Int32 frame_index);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_Init();

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_Terminate();

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_GetDeviceCount();

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_GetDeviceType(int index);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_OpenDevice(int index, int w, int h, int fps, ref IntPtr handle);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_CloseDevice(IntPtr handle);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_GetCapWidth(IntPtr handle);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_GetCapHeight(IntPtr handle);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_FreePointer(IntPtr ptr);

        [DllImport("ZKCameraLib.dll", CharSet = CharSet.Ansi, CallingConvention = CallingConvention.StdCall)]
        extern static int ZKCamera_SetDataCallback(IntPtr handle, VideoDataCallback videoDataCallback, CustomDataCallback customDataCallback, IntPtr userParam);

        public static int init()
        {
            return ZKCamera_Init();
        }
        public static int terminate()
        {
            return ZKCamera_Terminate();
        }

        public static int getDeviceCount()
        {
            return ZKCamera_GetDeviceCount();
        }

        public static int getDeviceType(int index)
        {
            return ZKCamera_GetDeviceType(index);
        }

        public static int openDevice(int index, int width, int height, int fps, ref IntPtr handle)
        {
            return ZKCamera_OpenDevice(index, width, height, fps, ref handle);
        }

        public static int closeDevice(IntPtr handle)
        {
            return ZKCamera_CloseDevice(handle);
        }

        public static int getCapWidth(IntPtr handle)
        {
            return ZKCamera_GetCapWidth(handle);
        }

        public static int getCapHeight(IntPtr handle)
        {
            return ZKCamera_GetCapHeight(handle);
        }

        public static int freePointer(IntPtr ptr)
        {
            return ZKCamera_FreePointer(ptr);
        }

        public static int setDataCallback(IntPtr handle, VideoDataCallback videoDataCallback, CustomDataCallback customDataCallback, IntPtr userParam)
        {
            return ZKCamera_SetDataCallback(handle, videoDataCallback, customDataCallback, userParam);
        }
    }
}
