using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using ZKBioModuleSDKWrapper;

namespace ZKBioModuleDemo
{
    public partial class Form1 : Form
    {
        private bool m_bIsUVCOpened = false;
        private bool m_bIsHIDOpened = false;
        private IntPtr m_vlHandle = IntPtr.Zero;
        private IntPtr m_nirHandle = IntPtr.Zero;
        private IntPtr m_HidHandle = IntPtr.Zero;
        private ZKBioModuleCameraApi.VideoDataCallback m_videoDataCallback = null;
        private ZKBioModuleCameraApi.CustomDataCallback m_customDataCallback = null;
        static int vlParam = 1;
        static int nirParam = 2;
        public static Form1 MainForm = null;
        private int m_vlFrames = 0;
        private int m_nirFrames = 0;
        
        private Thread m_threadVLViewer = null;
        private Thread m_threadNIRViewer = null;
        private bool m_stopGetMatchResult = false;
        private Thread m_threadMatchResult = null;
        private bool m_bStop = false;
        private bool m_bStopHid = false;
        private static bool g_bBioData = false;
        private static bool g_PollMatchResult = false;
        private static bool g_UpgradeImage = false;
        private static bool g_bPollHIDRun = false;
        private Thread m_threadHidHandle = null;

        private static CustomBioData g_CustomBioData;
        private static Queue<Bitmap> g_vlImageList = null;
        private static Queue<Bitmap> g_nirImageList = null;
        private static Queue<CustomBioData> g_customDataQueue = null;
        private static readonly object g_LockVlImage = new object();
        private static readonly object g_LockNIRImage = new object();
        private static readonly object g_LockCustomData = new object();
        private static int m_nImageWidth = 480;
        private static int m_nImageHeight = 640;
        private static bool m_bRegFaceRun = false;
        private static bool m_bRegPalmRun = false;

        static int lastAge = 0;
        static int lastGender = 0;
        static int lastMask = 0;
        static int lastLiveness = 0;
        static int lastLivenessMode = 0;
        static float livenessScore = 0;
        private static String g_register_userId = "";

        BioRect[] GetBioRect(CustomBioData customBioData)
        {
            int bioCnt = 0;

            List<BioData> bioDatas = customBioData.bioDatas;

            for (int i = 0; i < bioDatas.Count; i++)
            {
                if (1 == bioDatas[i].hasTrack)
                {
                    bioCnt++;
                }
            }
            if (0 == bioCnt || 0 == customBioData.width || 0 == customBioData.height)
            {
                return null;
            }
            BioRect[] rect = new BioRect[bioCnt];

            for (int i = 0; i < bioCnt; i++)
            {
                if (1 == bioDatas[i].label && 1 == bioDatas[i].hasTrack)
                {
                    int left = (int)(bioDatas[i].trackData.rect.left * m_nImageWidth / g_CustomBioData.width);
                    int top = (int)(bioDatas[i].trackData.rect.top * m_nImageHeight / g_CustomBioData.height);
                    int right = (int)(bioDatas[i].trackData.rect.right * m_nImageWidth / g_CustomBioData.width);
                    int bottom = (int)(bioDatas[i].trackData.rect.bottom * m_nImageHeight / g_CustomBioData.height);
                    rect[i].point = new POINT[4];
                    rect[i].point[0].x = left;
                    rect[i].point[0].y = top;
                    rect[i].point[1].x = right;
                    rect[i].point[1].y = top;
                    rect[i].point[2].x = right;
                    rect[i].point[2].y = bottom;
                    rect[i].point[3].x = left;
                    rect[i].point[3].y = bottom;
                }
                else if (5 == bioDatas[i].label && 1 == bioDatas[i].hasTrack)
                {
                    for (int j = 0; j < 4; j++)
                    {
                        rect[i].point[j].x = (int)(bioDatas[i].palmInfo.points[j].x * m_nImageWidth / g_CustomBioData.width);
                        rect[i].point[j].y = (int)(bioDatas[i].palmInfo.points[j].y * m_nImageHeight / g_CustomBioData.height);
                    }
                }

            }
            return rect;
        }

        private void showInfo(String info)
        {
            textInfo.BeginInvoke((MethodInvoker)delegate {
                textInfo.Text = info  + "\r\n";
            });
        }

        private void saveToFile(String filename, String text)
        {
            StreamWriter streamw = File.CreateText(filename);
            streamw.WriteLine(text);
            streamw.Close();
        }

        private void saveToFile(String filename, byte[] buffer, int start, int length)
        {
            FileStream fs = new FileStream(filename, FileMode.Create, FileAccess.Write);
            fs.Write(buffer, start, length);
            fs.Flush();
            fs.Close();
        }

        private void getMatchResult()
        {
            while (!m_stopGetMatchResult)
            {
                Thread.Sleep(20);
                bool bHasMatchResult = false;
                int nLabel = 0;
                MatchResult matchResult = new MatchResult();
                if (g_PollMatchResult && m_bIsHIDOpened)
                {
                    String strReuslt = "";
                    int ret = ZKBioModuleHIDApi.pollMatchResult(m_HidHandle, ref strReuslt);
                    if (0 == ret)
                    {
                        List<BioData> bioDatas = CustomDataParse.parseMatchResult(strReuslt);
                        if (null != bioDatas && bioDatas.Count > 0)
                        {
                            bHasMatchResult = true;
                            matchResult = bioDatas[bioDatas.Count - 1].matchResultList[0];
                            nLabel = bioDatas[bioDatas.Count - 1].label;
                        }
                    }

                }
                else if (m_bIsUVCOpened)
                {
                    lock(g_LockCustomData)
                    {
                        if (g_customDataQueue.Count == 0)
                        {
                            continue;
                        }
                        CustomBioData bioData = g_customDataQueue.Dequeue();
                        if (bioData.bioDatas.Count == 0 || bioData.bioDatas[0].matchResultList == null ||
                            bioData.bioDatas[0].matchResultList.Count == 0)
                        {
                            continue;
                        }
                        matchResult = bioData.bioDatas[0].matchResultList[0];
                        nLabel = bioData.bioDatas[0].label;
                    }
                }
                String info = "";
                if (bHasMatchResult)
                {
                    if (matchResult.userId != null && matchResult.userId.Length > 0)
                    {
                        if (1 == nLabel)
                        {
                            info = "Identify face successfully, name: " + matchResult.userId + ",score:" + matchResult.similarity;
                        }
                        else
                        {
                            info = "Identify palm successfully, name: " + matchResult.userId + ",score:" + matchResult.similarity;
                        }
                        picMatchResult.BeginInvoke((MethodInvoker)delegate {
                            picMatchResult.Image = ZKBioModuleDemo.Properties.Resources.correctImage;
                        });
                    }
                    else
                    {
                       
                        if (1 == nLabel)
                        {
                            info = "Identify face fail, score:" + matchResult.similarity;
                        }
                        else
                        {
                            info = "Identify palm fail, score:" + matchResult.similarity;
                        }
                        picMatchResult.BeginInvoke((MethodInvoker)delegate {
                            picMatchResult.Image = ZKBioModuleDemo.Properties.Resources.wrongImage;
                        });
                    }
                    showInfo(info);
                }
            }
        }

        private void registerPalm()
        {

        }

        private void registerFace()
        {
            String userId = g_register_userId;
            int len = 10 * 1024;
            byte[] bufJson = new byte[len];
            int ret = ZKBioModuleHIDApi.manageModuleData(m_HidHandle, (int)HID_ManageType.REG_START, null, bufJson, ref len);
            if (0 == ret)
            {
                String strJson = System.Text.Encoding.UTF8.GetString(bufJson, 0, len);
                int status = 0;
                string detail = "";
                if (!CustomDataParse.parseJson(strJson, ref status, ref detail))              
                {
                    String info = "REG_START failed, parse json failed";
                    showInfo(info);
                    goto exit_register_face;
                }
                if (status != 0)
                {
                    String info = "REG_START failed, status=" + status;
                    showInfo(info);
                    goto exit_register_face;
                }
            }
            else
            {
                String info = "ZKHID_ManageModuleData failed, ret=" + ret;
                showInfo(info);
                goto exit_register_face;
            }
            while(m_bRegFaceRun)
            {
                string json = CustomDataParse.getDetectFaceJson(null, 0, false, true, false);
                len = 10 * 1024;
                bufJson = new byte[len];
                ret = ZKBioModuleHIDApi.manageModuleData(m_HidHandle, (int)HID_ManageType.DETECT_FACE_REG, json, bufJson, ref len);
                if (0 == ret)
                {
                    String strJson = System.Text.Encoding.UTF8.GetString(bufJson, 0, len);
                    FaceDataList faceDataList = new FaceDataList();
                    if (CustomDataParse.parseRegFace(strJson, ref faceDataList))
                    {
                        if (0 != faceDataList.status || faceDataList.list.Count > 1)
                        {
                            for (int i = 0; i < faceDataList.list.Count; i++)
                            {
                                json = CustomDataParse.getDelCacheJson(faceDataList.list[i].cacheId.bioType, faceDataList.list[i].cacheId.id);
                                len = 10 * 1024;
                                bufJson = new byte[len];
                                ZKBioModuleHIDApi.manageModuleData(m_HidHandle, (int)HID_ManageType.DEL_FACE_CACHEID, json, bufJson, ref len);
                            }
                            if (faceDataList.list.Count > 1)
                            {
                                showInfo("Number of faces is greater than 1");
                            }
                            else
                            {
                                showInfo("detect face failed");
                            }
                            continue;
                        }
                        json = CustomDataParse.getAddFaceRegJson(userId, faceDataList.list[0].cacheId.id);
                        len = 10 * 1024;
                        bufJson = new byte[len];
                        ret = ZKBioModuleHIDApi.manageModuleData(m_HidHandle, (int)HID_ManageType.ADD_FACE_REG, json, bufJson, ref len);
                        if (0 == ret)
                        {
                            int status = 0;
                            string detail = "";
                            if (!CustomDataParse.parseJson(strJson, ref status, ref detail))
                            {
                                String info = "Enroll face failed, parse json failed";
                                showInfo(info);
                                break;
                            }
                            if (0 == status)
                            {
                                showInfo("Enroll face successfully");
                                manageUser((int)HID_ManageType.QUERY_STATISTICS, null);
                            }
                            else
                            {
                                String info = "Enroll face failed, ret =" + ret + ", status=" + status;
                                showInfo(info);
                            }
                        }
                        else
                        {
                            String info = "ADD_FACE_REG failed, ret=" + ret;
                            showInfo(info);
                        }
                        break;
                    }
                }
            }

        exit_register_face:
            len = 10 * 1024;
            bufJson = new byte[len];
            ZKBioModuleHIDApi.manageModuleData(m_HidHandle, (int)HID_ManageType.REG_END, null, bufJson, ref len);
            m_bRegFaceRun = false;
        }

        int manageUser(int manageType, String json)
        {
            if (!m_bIsHIDOpened)
            {
                showInfo("Please open HID first");
                return -1;
            }
            byte[] bufJson = null;
            int len = 1024, ret = 0;
            String info = "";
            
            if ((int)HID_ManageType.QUERY_ALL_PERSON == manageType || (int)HID_ManageType.GET_PERSON == manageType || (int)HID_ManageType.EXPORT_ATT_RECORD == manageType)
            {
                len = 2 * 1024 * 1024;
            }
            bufJson = new byte[len];
            ret = ZKBioModuleHIDApi.manageModuleData(m_HidHandle, manageType, json, bufJson, ref len);
            if (0 == ret)
            {
                int status = 0;
                string detail = "";
                String strResult = System.Text.Encoding.UTF8.GetString(bufJson, 0, len);
                if (CustomDataParse.parseJson(strResult, ref status, ref detail))
                {
                    switch (manageType)
                    {
                        case (int)HID_ManageType.ADD_PERSON:
                            if (0 == status)
                            {
                                info = "Add User successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Add User failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.DEL_PERSON:
                            if (0 == status)
                            {
                                info = "Delete User successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Delete User failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.GET_PERSON:
                            if (0 == status)
                            {
                                saveToFile("GET_PERSON.json", strResult);
                                info = "Get User successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Get User failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.CLEAR_PERSON:
                            if (0 == status)
                            {
                                info = "Clear User successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Clear User failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.QUERY_ALL_PERSON:
                            if (0 == status)
                            {
                                saveToFile("GET_PERSON.json", strResult);
                                info = "Get All User successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Get All failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.QUERY_STATISTICS:
                            if (0 == status)
                            {
                                //wsprintf(log, _T("Query Statistics successfully"));
                                Statistics statistics = new Statistics();
                                if (CustomDataParse.parseQueryStatistics(strResult, ref statistics))
                                {
                                    if (0 == statistics.status)
                                    {
                                        textUserNum.BeginInvoke((MethodInvoker)delegate {
                                            textUserNum.Text = statistics.personCount.ToString();
                                        });
                                        textFaceNum.BeginInvoke((MethodInvoker)delegate {
                                            textFaceNum.Text = statistics.faceCount.ToString();
                                        });
                                        textPalmNum.BeginInvoke((MethodInvoker)delegate {
                                            textPalmNum.Text = statistics.palmCount.ToString();
                                        });                                       
                                    }
                                }
                            }
                            else
                            {
                                ret = -100;
                                info = "Query Statistics failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.ADD_FACE:
                            if (0 == status)
                            {
                                info = "Enroll Face successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Enroll Face failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.EXPORT_ATT_RECORD:
                            if (0 == status)
                            {
                                saveToFile("ATT_RECORD.json", strResult);
                                info = "Get att record successfully";
                            }
                            else
                            {
                                ret = -100;
                                info = "Get att record, status=" + status + ",detail=" + detail;
                            }
                            break;
                        case (int)HID_ManageType.CLEAR_ATT_RECORD:
                            if (0 == status)
                            {
                                info = "Clear att record successfully";
                            }
                            else
                            {
                                ret = -100;
                               info = "Clear att record failed, status=" + status + ",detail=" + detail;
                            }
                            break;
                    }
                }
                else
                {
                    info = "parseJson failed, ret=" +  ret;
                }
            }
            else
            {
                info =  "ZKHID_ManageModuleData failed, ret=" + ret;
            }
            showInfo(info);
            return ret;
        }

        public static Bitmap DrawLineInPicture(Bitmap bmp, POINT[] points, Color LineColor, int LineWidth, DashStyle ds)
        {
            Graphics g = Graphics.FromImage(bmp);

            Brush brush = new SolidBrush(LineColor);

            Pen pen = new Pen(brush, LineWidth); 
            pen.DashStyle = ds;
            g.DrawLine(pen, points[0].x, points[0].y, points[1].x, points[1].y);
            g.DrawLine(pen, points[1].x, points[1].y, points[2].x, points[2].y);
            g.DrawLine(pen, points[2].x, points[2].y, points[3].x, points[3].y);
            g.DrawLine(pen, points[3].x, points[3].y, points[0].x, points[0].y);
            g.Dispose();
            return bmp;
        }

        private void PollHIDStatus()
        {
            while(!m_bStopHid)
            {
                Thread.Sleep(500);
                String strText = "Wait for HID to be ready";
                textInfo.BeginInvoke((MethodInvoker)delegate {
                    textInfo.Text = strText;
                });
                String strResult = "";
                int ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.COMMON_CONFIG, ref strResult);
                if (0 == ret)
                {
                    int status = 0;
                    string detail = "";
                    bool bRet = CustomDataParse.parseJson(strResult, ref status, ref detail);
                    if (bRet && 0 == status)
                    {

                        strText = "Hid open success";
                        textInfo.BeginInvoke((MethodInvoker)delegate {
                            textInfo.Text = strText;
                        });
                        break;
                    }
                }
                else
                {
                    strText = "ZKHID_GetConfig failed, ret=" + ret;
                    textInfo.BeginInvoke((MethodInvoker)delegate {
                        textInfo.Text = strText;
                    });
                }
            }
            m_threadHidHandle = null;
            g_bPollHIDRun = false;
        }

        private void UpdateVLViewer()
        {
            while(!m_bStop)
            {
                Thread.Sleep(20);
                Bitmap bitmap = null;
                BioRect[] bioRects = null;
                String strLog = "";
                lock (g_LockCustomData)
                {
                    if (g_bBioData)
                    {
                        bioRects = GetBioRect(g_CustomBioData);
                        int nCount = g_CustomBioData.bioDatas.Count;
                        for (int i = 0; i < nCount; i++)
                        {
                            if (0 == i && 1 == g_CustomBioData.bioDatas[0].label)
                            {
                                String logItem;
                                logItem = "trackId: " + g_CustomBioData.bioDatas[0].trackData.trackId;
                                strLog += logItem;
                                strLog += "\r\n";

                                logItem = "yaw: " + g_CustomBioData.bioDatas[0].trackData.pose.yaw;
                                strLog += logItem;
                                strLog += "\r\n";

                                logItem = "pitch: " + g_CustomBioData.bioDatas[0].trackData.pose.pitch;
                                strLog += logItem;
                                strLog += "\r\n";

                                logItem = "roll: " + g_CustomBioData.bioDatas[0].trackData.pose.roll;
                                strLog += logItem;
                                strLog += "\r\n";
                                if (g_CustomBioData.bioDatas[0].hasAttr == 1)
                                {
                                    logItem = "age: " + g_CustomBioData.bioDatas[0].attribute.age;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "gender: " + (g_CustomBioData.bioDatas[0].attribute.gender == 1 ? "Male" : "Female");
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "mask: " + g_CustomBioData.bioDatas[0].attribute.respirator;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    lastAge = g_CustomBioData.bioDatas[0].attribute.age;
                                    lastGender = g_CustomBioData.bioDatas[0].attribute.gender;
                                    lastMask = g_CustomBioData.bioDatas[0].attribute.respirator;
                                }
                                else
                                {
                                    logItem = "age: " + lastAge;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "gender: " + (lastGender == 1 ? "Male" : "Female");
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "mask:" + lastMask;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                }
                                if (g_CustomBioData.bioDatas[0].hasLiveScore == 1)
                                {
                                    logItem = "liveness: " + g_CustomBioData.bioDatas[0].liveness.liveness;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "livenessScore: " + g_CustomBioData.bioDatas[0].liveness.livenessScore;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "livenessMode:" + g_CustomBioData.bioDatas[0].liveness.livenessMode;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    lastLiveness = g_CustomBioData.bioDatas[0].liveness.liveness;
                                    livenessScore = g_CustomBioData.bioDatas[0].liveness.livenessScore;
                                    lastLivenessMode = g_CustomBioData.bioDatas[0].liveness.livenessMode;
                                }
                                else
                                {
                                    logItem = "liveness: " + lastLiveness;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "livenessScore: " + livenessScore;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                    logItem = "livenessMode: " + lastLivenessMode;
                                    strLog += logItem;
                                    strLog += "\r\n";
                                }
                            }
                        }
                        g_CustomBioData.bioDatas.Clear();
                        g_bBioData = false;
                    }
                }
                if (strLog.Length > 0)
                {
                    textResult.BeginInvoke((MethodInvoker)delegate {
                        textResult.Text = strLog;
                    });
                }
                lock (g_LockVlImage)
                {
                    if (g_vlImageList.Count > 0)
                    {
                        bitmap = g_vlImageList.Dequeue();
                    }
                }
                if (null != bitmap)
                {
                    if (null != bioRects)
                    {
                        int nRectCount = bioRects.Length;
                        for (int i = 0; i < nRectCount; i++)
                        {
                            bitmap = DrawLineInPicture(bitmap, bioRects[i].point, Color.Green, 2, DashStyle.Solid);
                        }
                    }
                    picVL.BeginInvoke((MethodInvoker)delegate {
                        picVL.Image = bitmap;
                    });
                }
            }
        }

        private void UpdateNIRViewer()
        {
            while (!m_bStop)
            {
                Thread.Sleep(20);
                Bitmap bitmap = null;
                lock (g_LockNIRImage)
                {
                    if (g_nirImageList.Count > 0)
                    {
                        bitmap = g_nirImageList.Dequeue();
                    }
                }
                if (null != bitmap)
                {
                    picNIR.BeginInvoke((MethodInvoker)delegate
                    {
                        picNIR.Image = bitmap;
                    });
                }
            }
        }


        public Form1()
        {
            MainForm = this;
            InitializeComponent();
            cmbFps.SelectedIndex = 0;
            cmbResolution.SelectedIndex = 0;

            g_vlImageList = new Queue<Bitmap>();
            g_nirImageList = new Queue<Bitmap>();
            g_customDataQueue = new Queue<CustomBioData>();
            g_CustomBioData = new CustomBioData();
            g_CustomBioData.bioDatas = new List<BioData>();

            g_PollMatchResult = chkboxPollMatchResult.Checked;

            m_stopGetMatchResult = false;
            m_threadMatchResult = new Thread(new ThreadStart(getMatchResult));
            m_threadMatchResult.IsBackground = true;
            m_threadMatchResult.Start();
        }

        private void btnUVCOpen_Click(object sender, EventArgs e)
        {
            if (m_bIsUVCOpened)
            {
                return;
            }
            ZKBioModuleCameraApi.init();
            int nCount = ZKBioModuleCameraApi.getDeviceCount();
            if (nCount < 2)
            {
                textInfo.Text = "No device found";
                return;
            }
            int nFpsSelect = cmbFps.SelectedIndex;
            int nResolutionSelect = cmbResolution.SelectedIndex;
            if (-1 == nFpsSelect || -1 == nResolutionSelect)
            {
                textInfo.Text = "Please select fps and resolution first!";
                return;
            }
            int ret = 0;
            int nType = ZKBioModuleCameraApi.getDeviceType(0);
            int fps = 30;
            if (nFpsSelect == 0)
            {
                fps = 25;
            }
            else if (nFpsSelect == 1)
            {
                fps = 30;
            }
            if (nResolutionSelect == 0)
            {
                m_nImageWidth = 480;
                m_nImageHeight = 640;
            }
            else
            {
                m_nImageWidth = 720;
                m_nImageHeight = 1280;
            }
            picVL.Image = null;
            picNIR.Image = null;
            if (nType == 1)
            {
                ret = ZKBioModuleCameraApi.openDevice(0, m_nImageWidth, m_nImageHeight, fps, ref m_vlHandle);
                ret = ZKBioModuleCameraApi.openDevice(1, m_nImageWidth, m_nImageHeight, fps, ref m_nirHandle);
            }
            else
            {
                ret = ZKBioModuleCameraApi.openDevice(0, m_nImageWidth, m_nImageHeight, fps, ref m_vlHandle);
                ret = ZKBioModuleCameraApi.openDevice(0, m_nImageWidth, m_nImageHeight, fps, ref m_nirHandle);
            }
            if (ret < 0)
            {
                if (null != m_vlHandle)
                {
                    ZKBioModuleCameraApi.closeDevice(m_vlHandle);
                    m_vlHandle = IntPtr.Zero;
                }
                if (null != m_nirHandle)
                {
                    ZKBioModuleCameraApi.closeDevice(m_nirHandle);
                    m_nirHandle = IntPtr.Zero;
                }
                textInfo.Text = "Open camera fail";
                return;
            }
            IntPtr pVlUserParam = new IntPtr(vlParam);
            IntPtr pNirUserParam = new IntPtr(nirParam);
            m_videoDataCallback = new ZKBioModuleCameraApi.VideoDataCallback(OnVideoDataCallback);
            m_customDataCallback = new ZKBioModuleCameraApi.CustomDataCallback(OnCustomDataCallback);
            ZKBioModuleCameraApi.setDataCallback(m_vlHandle, m_videoDataCallback, m_customDataCallback, pVlUserParam);
            ZKBioModuleCameraApi.setDataCallback(m_nirHandle, m_videoDataCallback, null, pNirUserParam);
            m_nirFrames = 0;
            m_vlFrames = 0;
            timer1.Interval = 1000;
            timer1.Enabled = true;
            timer1.Start();

            m_bStop = false;
            m_threadVLViewer = new Thread(new ThreadStart(UpdateVLViewer));
            m_threadVLViewer.IsBackground = true;
            m_threadVLViewer.Start();
            Thread.Sleep(500);
            m_threadNIRViewer = new Thread(new ThreadStart(UpdateNIRViewer));
            m_threadNIRViewer.IsBackground = true;
            m_threadNIRViewer.Start();
            m_bIsUVCOpened = true;
            textInfo.Text = "Open camera success";
        }

        public static Bitmap grayPixels2Bitmap(byte[] grayPixels, int width, int height)
        {
            Bitmap bmp = new Bitmap(width, height, PixelFormat.Format8bppIndexed);
            BitmapData bmpData = bmp.LockBits(new Rectangle(0, 0, width, height),
            ImageLockMode.WriteOnly, PixelFormat.Format8bppIndexed);

            int stride = bmpData.Stride;  // 扫描线的宽度  
            int offset = stride - width;  // 显示宽度与扫描线宽度的间隙  
            IntPtr iptr = bmpData.Scan0;  // 获取bmpData的内存起始位置  
            int scanBytes = stride * height;// 用stride宽度，表示这是内存区域的大小  

            int posScan = 0, posReal = 0;// 分别设置两个位置指针，指向源数组和目标数组  
            byte[] pixelValues = new byte[scanBytes];  //为目标数组分配内存  

            for (int x = 0; x < height; x++)
            {
                for (int y = 0; y < width; y++)
                {
                    pixelValues[posScan++] = grayPixels[posReal++];
                }
                posScan += offset;  //行扫描结束，要将目标位置指针移过那段“间隙”  
            }

            System.Runtime.InteropServices.Marshal.Copy(pixelValues, 0, iptr, scanBytes);
            bmp.UnlockBits(bmpData);  // 解锁内存区域  

            ColorPalette tempPalette;
            using (Bitmap tempBmp = new Bitmap(1, 1, PixelFormat.Format8bppIndexed))
            {
                tempPalette = tempBmp.Palette;
            }
            for (int i = 0; i < 256; i++)
            {
                tempPalette.Entries[i] = Color.FromArgb(i, i, i);
            }
            bmp.Palette = tempPalette;
            return bmp;
        }

        public static Bitmap jpegBuffer2Bitmap(byte[] jpegBuffer, int cbJpegBuffer)
        {
            MemoryStream ms = new MemoryStream(jpegBuffer, 0, cbJpegBuffer);
            return (Bitmap)Image.FromStream(ms);
        }

        public static void OnVideoDataCallback(IntPtr userParam, UVCVedioData data)
        {
            if (data.data_length > 0)
            {
                byte[] managedArray = new byte[data.data_length];
                Marshal.Copy(data.data, managedArray, 0, data.data_length);
                Bitmap bitmap = jpegBuffer2Bitmap(managedArray, data.data_length);
                if (vlParam == userParam.ToInt32())
                {
                    MainForm.m_vlFrames++;
                   lock(g_LockVlImage)
                    {
                        g_vlImageList.Enqueue(bitmap);
                    }
                }
                else
                {
                    MainForm.m_nirFrames++;
                    lock (g_LockNIRImage)
                    {
                        g_nirImageList.Enqueue(bitmap);
                    }
                }
                ZKBioModuleCameraApi.freePointer(data.data);
            }            
        }

        public static void OnCustomDataCallback(IntPtr userParam, UVCCustomData data)
        {
            CustomBioData bioData = new CustomBioData();
            bioData.frame_index = data.frame_index;
            bioData.width = data.width;
            bioData.height = data.height;
            string strJson = Marshal.PtrToStringAnsi(data.customData);
            bioData.bioDatas = CustomDataParse.parse_customData(strJson);
            ZKBioModuleCameraApi.freePointer(data.customData);
            if (bioData.bioDatas.Count == 0)
            {
                return;
            }
            lock(g_LockCustomData)
            {
                if (!g_bBioData)
                {
                    g_CustomBioData.width = bioData.width;
                    g_CustomBioData.height = bioData.height;
                    g_CustomBioData.frame_index = bioData.frame_index;
                    for (int i = 0; i < bioData.bioDatas.Count; i++)
                    {
                        BioData pbio = bioData.bioDatas[i];
                        g_CustomBioData.bioDatas.Add(pbio);
                    }
                    g_bBioData = true;
                }
                if (!g_PollMatchResult)
                {
                    g_customDataQueue.Enqueue(bioData);
                }
                else
                {
                    bioData.bioDatas.Clear();
                }
            }
        }

        private void btnUVCClose_Click(object sender, EventArgs e)
        {
            if (!m_bIsUVCOpened)
            {
                return;
            }
            m_bStop = true;
            m_threadNIRViewer.Join();
            m_threadVLViewer.Join();
            timer1.Stop();
            if (IntPtr.Zero != m_vlHandle)
            {
                ZKBioModuleCameraApi.closeDevice(m_vlHandle);
                m_vlHandle = IntPtr.Zero;
            }
            if (IntPtr.Zero != m_nirHandle)
            {
                ZKBioModuleCameraApi.closeDevice(m_nirHandle);
                m_nirHandle = IntPtr.Zero;
            }
            ZKBioModuleCameraApi.terminate();
            g_CustomBioData.bioDatas.Clear();
            g_customDataQueue.Clear();
            g_vlImageList.Clear();
            g_nirImageList.Clear();
            m_bIsUVCOpened = false;
            textInfo.Text = "Camera closed";
        }

        private void timer1_Tick(object sender, EventArgs e)
        {
            textStatus.Text = "VL:" + m_vlFrames + "fps, NIR:" + m_nirFrames + "fps.";
            m_nirFrames = 0;
            m_vlFrames = 0;
        }

        private void Form1_FormClosing(object sender, FormClosingEventArgs e)
        {
            m_stopGetMatchResult = true;
            m_threadMatchResult.Join();
            if (m_bIsUVCOpened)
            {
                m_bStop = true;
                m_threadNIRViewer.Join();
                m_threadVLViewer.Join();
                timer1.Stop();
                if (IntPtr.Zero != m_vlHandle)
                {
                    ZKBioModuleCameraApi.closeDevice(m_vlHandle);
                    m_vlHandle = IntPtr.Zero;
                }
                if (IntPtr.Zero != m_nirHandle)
                {
                    ZKBioModuleCameraApi.closeDevice(m_nirHandle);
                    m_nirHandle = IntPtr.Zero;
                }
                ZKBioModuleCameraApi.terminate();
                m_bIsUVCOpened = false;
            }
        }

        private void btnHIDOpen_Click(object sender, EventArgs e)
        {
            if (m_bIsHIDOpened)
            {
                return;
            }
            g_bPollHIDRun = false;
            int ret = 0;
            int nDeviceCount = 0;
            ret = ZKBioModuleHIDApi.init();
            if (0 != ret)
            {
                textInfo.Text = "ZKHID_Init failed";
                return;
            }
            ZKBioModuleHIDApi.getDeviceCount(ref nDeviceCount);
            if (nDeviceCount <= 0)
            {
                textInfo.Text = "No device found";
                return;
            }
            ret = ZKBioModuleHIDApi.openDevice(0, ref m_HidHandle);
            if (0 != ret)
            {
                textInfo.Text = "Open HID failed";
                return;
            }
            if (!g_UpgradeImage && !g_bPollHIDRun)
            {
                m_bStopHid = false;
                g_bPollHIDRun = true;
                m_threadHidHandle = new Thread(new ThreadStart(PollHIDStatus));
                m_threadHidHandle.IsBackground = true;
                m_threadHidHandle.Start();
            }
            m_bIsHIDOpened = true;
            return;
        }

        private void btnHIDClose_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                return;
            }
            if (null != m_threadHidHandle)
            {
                m_bStopHid = true;
                g_bPollHIDRun = false;
                m_threadHidHandle.Join();
                m_threadHidHandle = null;
            }
            ZKBioModuleHIDApi.closeDevice(m_HidHandle);
            m_HidHandle = IntPtr.Zero;
            ZKBioModuleHIDApi.terminate();
            m_bIsHIDOpened = false;
            picNIR.Image = ZKBioModuleDemo.Properties.Resources._480x640;
            picVL.Image = ZKBioModuleDemo.Properties.Resources._480x640;
            textInfo.Text = "HID closed";
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String userId = textUserId.Text;
            if (null == userId || userId.Length == 0)
            {
                textInfo.Text = "Please input UserID";
                return;
            }
            String json = CustomDataParse.getAddUserJson(userId, userId);
            int ret = manageUser((int)HID_ManageType.ADD_PERSON, json);
            if (ret == 0)
            {
                manageUser((int)HID_ManageType.QUERY_STATISTICS, null);
            }
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String userId = textUserId.Text;
            if (null == userId || userId.Length == 0)
            {
                textInfo.Text = "Please input UserID";
                return;
            }
            String json = CustomDataParse.getQueryUserJson(userId, true, true);
            manageUser((int)HID_ManageType.GET_PERSON, json);
        }

        private void button3_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String json = CustomDataParse.getQueryAllUserJson();
            manageUser((int)HID_ManageType.QUERY_ALL_PERSON, json);
        }

        private void button4_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String userId = textUserId.Text;
            if (null == userId || userId.Length == 0)
            {
                textInfo.Text = "Please input UserID";
                return;
            }
            String json = CustomDataParse.getDeleteUserJson(userId);
            int ret = manageUser((int)HID_ManageType.DEL_PERSON, json);
            if (ret == 0)
            {
                manageUser((int)HID_ManageType.QUERY_STATISTICS, null);
            }
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            int ret = manageUser((int)HID_ManageType.CLEAR_PERSON, null);
            if (ret == 0)
            {
                manageUser((int)HID_ManageType.QUERY_STATISTICS, null);
            }
        }

        private void button6_Click(object sender, EventArgs e)
        {
            /*
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String userId = textUserId.Text;
            if (null == userId || userId.Length == 0)
            {
                textInfo.Text = "Please input UserID";
                return;
            }
            String json = CustomDataParse.getQueryUserJson(userId, true, true);
            int ret = manageUser((int)HID_ManageType.GET_PERSON, json);
            if (ret != 0)
            {
                textInfo.Text = "Please Add User first";
                return;
            }
            byte[] image = null; // read jpeg file to buffer(width<=720,height<=1280, you can scale the picture to the same scale )
            int size = 0;   //image size
            json = CustomDataParse.getAddFaceJson(userId, image, size);

            ret = manageUser((int)HID_ManageType.ADD_FACE, json);
            if (0 == ret)
            {
                manageUser((int)HID_ManageType.QUERY_STATISTICS, null);
            }
            */
            textInfo.Text = "Not implemented";
        }

        private void button7_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun || m_bRegFaceRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String userId = textUserId.Text;
            if (null == userId || userId.Length == 0)
            {
                textInfo.Text = "Please input UserID";
                return;
            }
            g_register_userId = userId;
            String json = CustomDataParse.getQueryUserJson(userId, true, true);
            int ret = manageUser((int)HID_ManageType.GET_PERSON, json);
            if (ret != 0)
            {
                textInfo.Text = "Please Add User first";
                return;
            }
            m_bRegFaceRun = true;
            Thread thread = new Thread(new ThreadStart(registerFace));
            thread.IsBackground = true;
            thread.Start();
        }

        private void chkboxPollMatchResult_CheckedChanged(object sender, EventArgs e)
        {
            g_PollMatchResult = chkboxPollMatchResult.Checked;
        }

        private void button8_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun || m_bRegPalmRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String userId = textUserId.Text;
            if (null == userId || userId.Length == 0)
            {
                textInfo.Text = "Please input UserID";
                return;
            }
            g_register_userId = userId;
            String json = CustomDataParse.getQueryUserJson(userId, true, true);
            int ret = manageUser((int)HID_ManageType.GET_PERSON, json);
            if (ret != 0)
            {
                textInfo.Text = "Please Add User first";
                return;
            }
            m_bRegPalmRun = true;
            Thread thread = new Thread(new ThreadStart(registerPalm));
            thread.IsBackground = true;
            thread.Start();
        }

        private void button9_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            int len = 1024;
            byte[] bufJson = new byte[len];
            string json = CustomDataParse.getAttRecordCountJson();
            int ret = ZKBioModuleHIDApi.manageModuleData(m_HidHandle, (int)HID_ManageType.ATT_RECORD_COUNT, json, bufJson, ref len);
            if (0 == ret)
            {
                String strJson = System.Text.Encoding.UTF8.GetString(bufJson, 0, len);
                AttRecordCount attRecCount = new AttRecordCount();
                if (CustomDataParse.parseAttRecordCount(strJson, ref attRecCount))
                {
                    if (attRecCount.totalCount > 0)
                    {
                        json = CustomDataParse.getAttRecordJson(1, 20, true);
                        manageUser((int)HID_ManageType.EXPORT_ATT_RECORD, json);
                        textInfo.Text = "Attendance record count=" + attRecCount.totalCount;
                    }
                    else
                    {
                        textInfo.Text = "No att record";
                    }
                }
            }
        }

        private void button10_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            manageUser((int)HID_ManageType.CLEAR_ATT_RECORD, null);
        }

        private void button11_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            String strJson = "";
            String info = "";
            // VL Image
            int ret = ZKBioModuleHIDApi.snapShot(m_HidHandle, (int)HID_SnapShotType.SNAPSHOT_VL, ref strJson);
            // NIR Image
            // int ret = ZKBioModuleHIDApi.snapShot(m_HidHandle, (int)HID_SnapShotType.SNAPSHOT_NIR, ref strJson);
            if (0 == ret)
            {
                SnapShot snapShot = new SnapShot();
                if (CustomDataParse.parseSnapshot(strJson, ref snapShot))
                {
                    if (0 == snapShot.status)
                    {
                        byte[] imageData = Convert.FromBase64String(snapShot.data);
                        if (snapShot.type == "gray")
                        {
                            Bitmap bitmap = grayPixels2Bitmap(imageData, snapShot.width, snapShot.height);
                            bitmap.Save("grayImage.bmp");
                        }else
                        {
                            saveToFile("jpegImage.jpg", imageData, 0, imageData.Length);
                        }
                    }
                    else
                    {
                        info = "SnapShot failed, status=" + snapShot.status;
                    }
                }
                else
                {
                    info = "Parse SnapShot failed";
                }
            }
            else
            {
                info = "SnapShot failed, ret=" + ret;
            }
            showInfo(info);
        }

        private void button12_Click(object sender, EventArgs e)
        {
            if (!m_bIsHIDOpened)
            {
                textInfo.Text = "Hid not opened";
                return;
            }
            if (g_bPollHIDRun)
            {
                textInfo.Text = "Device busy.";
                return;
            }
            DeviceManage deviceManage = new DeviceManage();
            deviceManage.setDeviceHandle(m_HidHandle);
            deviceManage.ShowDialog();
        }
    }
}
