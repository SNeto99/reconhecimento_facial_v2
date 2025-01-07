using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Text;
using System.Windows.Forms;
using ZKBioModuleSDKWrapper;

namespace ZKBioModuleDemo
{
    public partial class DeviceManage : Form
    {
        IntPtr m_HidHandle = IntPtr.Zero;

        public void setDeviceHandle(IntPtr handle)
        {
            m_HidHandle = handle;
        }

        

        public DeviceManage()
        {
            InitializeComponent();
        }

        private void button6_Click(object sender, EventArgs e)
        {
            if (IntPtr.Zero == m_HidHandle)
            {
                MessageBox.Show("Device not connect!");
                return;
            }
            if (tabControl1.SelectedIndex == 0)
            {
                int ret = 0;
                String strResult = "";
                ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.DEVICE_INFORMATION, ref strResult);
                if (0 == ret)
                {
                    SetDeviceInfo(strResult);
                    texttabInfo.Text = "GetConfig successfully";
                }
                else
                {
                    texttabInfo.Text = "GetConfig fail, ret=" + ret;
                }
            }
            else if (tabControl1.SelectedIndex == 1)
            {
                int ret = 0;
                String strResult = "";
                ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.COMMON_CONFIG, ref strResult);
                if (0 == ret)
                {
                    SetCommonSettings(strResult);
                    texttabInfo.Text = "GetConfig successfully";
                }
                else
                {
                    texttabInfo.Text = "GetConfig fail, ret=" + ret;
                }
                strResult = "";
                ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.CAPTURE_FILTER_CONFIG, ref strResult);
                if (0 == ret)
                {
                    SetCaptureFilter(strResult);
                    texttabInfo.Text = "GetConfig successfully";
                }
                else
                {
                    texttabInfo.Text = "GetConfig fail, ret=" + ret;
                }
            }
            else
            {
                int ret = 0;
                String strResult = "";
                ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.MOTION_DETECT_CONFIG, ref strResult);
                if (0 == ret)
                {
                    SetMotionDetection(strResult);
                    texttabInfo.Text = "GetConfig successfully";
                }
                else
                {
                    texttabInfo.Text = "GetConfig fail, ret=" + ret;
                }
                strResult = "";
                ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.PALM_CONFIG, ref strResult);
                if (0 == ret)
                {
                    SetPalmSettings(strResult);
                    texttabInfo.Text = "GetConfig successfully";
                }
                else
                {
                    texttabInfo.Text = "GetConfig fail, ret=" + ret;
                }
            }
        }

        private void SetDeviceInfo(String json)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                texttabInfo.Text = "Parse DeviceInfo json failed";
                return;
            }

            String detail = jObject["detail"].ToString();
            if (detail.Equals("success"))
            {
                JObject data = (JObject)jObject["data"];
                if (!data.ContainsKey("deviceInfo"))
                {
                    texttabInfo.Text = "No deviceInfo item";
                    return;
                }

                JObject deviceInfo = (JObject)data["deviceInfo"];

                if (deviceInfo.ContainsKey("gSDK_VERSION"))
                {
                    textSDKVersion.Text = deviceInfo["gSDK_VERSION"].ToString();
                }

                if (deviceInfo.ContainsKey("app"))
                {
                    textApp.Text = deviceInfo["app"].ToString();
                }

                if (deviceInfo.ContainsKey("sn"))
                {
                    textSn.Text = deviceInfo["sn"].ToString();
                }

                if (deviceInfo.ContainsKey("hidVer"))
                {
                    textHidVer.Text = deviceInfo["hidVer"].ToString();  
                }

                if (deviceInfo.ContainsKey("firmVer"))
                {
                    textfirmVer.Text = deviceInfo["firmVer"].ToString();
                }

                if (deviceInfo.ContainsKey("cpID"))
                {
                    textcpID.Text = deviceInfo["cpID"].ToString();
                }
            }
        }

        private void SetCommonSettings(String json)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                texttabInfo.Text = "Parse CommonSettings json failed";
                return;
            }
            int status = int.Parse(jObject["status"].ToString());
            if (0 == status)
            {
                JObject data = (JObject)jObject["data"];

                if (!data.ContainsKey("commonSettings"))
                {
                    return;
                }
                checkAttrReg.Checked = bool.Parse(data["commonSettings"]["attributeRecog"].ToString());
                checkAlgCount.Checked = bool.Parse(data["commonSettings"]["countAlgorithm"].ToString());
                checkDrawTrack.Checked = bool.Parse(data["commonSettings"]["drawTrackRect"].ToString());
                checkFaceAE.Checked = bool.Parse(data["commonSettings"]["faceAEEnabled"].ToString());
                checkVLLiveness.Checked = bool.Parse(data["commonSettings"]["VLLiveness"].ToString());
                checkNIRLiveNess.Checked = bool.Parse(data["commonSettings"]["NIRLiveness"].ToString());
                checkMask.Checked = bool.Parse(data["commonSettings"]["recogRespirator"].ToString());
                checkAttlog.Checked = bool.Parse(data["commonSettings"]["enableStoreAttendLog"].ToString());
                checkStrangerAttLog.Checked = bool.Parse(data["commonSettings"]["enableStoreStrangerAttLog"].ToString());
                checkTrackMatchMode.Checked = bool.Parse(data["commonSettings"]["isTrackingMatchMode"].ToString());
                checkStoreAttPhoto.Checked = bool.Parse(data["commonSettings"]["enableStoreAttendPhoto"].ToString());
                
                int debugLevel = int.Parse(data["commonSettings"]["debugLevel"].ToString());
                nudDebugLevel.Value = debugLevel;
                

                textRecigThreshold.Text = data["commonSettings"]["recogThreshold"].ToString();
                textLivenessThreshold.Text = data["commonSettings"]["hacknessThreshold"].ToString();
                textRecogInterval.Text = data["commonSettings"]["recogInterval"].ToString();

                textAttrInterval.Text = data["commonSettings"]["attrInterval"].ToString();
                textAttendInterval.Text = data["commonSettings"]["attendInterval"].ToString();

                String format = data["commonSettings"]["infraredPictureFormat"].ToString();
                if (format.Equals("jpeg"))
                {
                    cmbNIRPicFormat.SelectedIndex = 0;
                }
                else
                {
                    cmbNIRPicFormat.SelectedIndex = 1;
                }

                String qualityLevel = data["commonSettings"]["attendPhotoQuality"].ToString();
                if (qualityLevel.Equals("best"))
                {
                    cmbAttPicQuality.SelectedIndex = 0;
                }
                else if (qualityLevel.Equals("best"))
                {
                    cmbAttPicQuality.SelectedIndex = 1;
                }
                else
                {
                    cmbAttPicQuality.SelectedIndex = 2;
                }
            }
        }

        private void SetCaptureFilter(string json)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                texttabInfo.Text = "Parse CaptureFilter json failed";
                return;
            }

            int status = int.Parse(jObject["status"].ToString());
            if (0 == status)
            {
                JObject data = (JObject)jObject["data"];

                if (!data.ContainsKey("captureFilter"))
                {
                    return;
                }

                textBlur.Text = data["captureFilter"]["blurThreshold"].ToString();
                textFrontThreshold.Text = data["captureFilter"]["frontThreshold"].ToString();
                textQuality.Text = data["captureFilter"]["scoreThreshold"].ToString();
                textMaxHeight.Text = data["captureFilter"]["heightMaxValue"].ToString();
                textMinHeight.Text = data["captureFilter"]["heightMinValue"].ToString();
                textMaxWidth.Text = data["captureFilter"]["widthMaxValue"].ToString();
                textMinWidth.Text = data["captureFilter"]["widthMinValue"].ToString();
                textMaxPitch.Text = data["captureFilter"]["pitchMaxValue"].ToString();
                textMinPitch.Text = data["captureFilter"]["pitchMinValue"].ToString();
                textMaxRoll.Text = data["captureFilter"]["rollMaxValue"].ToString();
                textMinRoll.Text = data["captureFilter"]["rollMinValue"].ToString();
                textMaxYaw.Text = data["captureFilter"]["yawMaxValue"].ToString();
                textMinYaw.Text = data["captureFilter"]["yawMinValue"].ToString();
            }
        }

        private void SetMotionDetection(String json)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                texttabInfo.Text = "Parse MotionDetection json failed";
                return;
            }
            String detail = jObject["detail"].ToString();
            if (detail.Equals("success"))
            {
                JObject data = (JObject)jObject["data"];
                if (!data.ContainsKey("MotionDetectionSetting"))
                {
                    return;
                }
                textBrightnessThreshold.Text = data["MotionDetectionSetting"]["brightnessThreshold"].ToString();
                checkmotionDetectFunOn.Checked = bool.Parse(data["MotionDetectionSetting"]["motionDetectFunOn"].ToString());
                textIdleTimeout.Text = data["MotionDetectionSetting"]["idleTimeOutMS"].ToString();
                textsensitivityThreshold.Text = data["MotionDetectionSetting"]["sensitivityThreshold"].ToString();
            }
        }

        private void SetPalmSettings(String json)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                texttabInfo.Text = "Parse PalmSetting json failed";
                return;
            }


            String detail = jObject["detail"].ToString();
            if (detail.Equals("success"))
            {
                JObject data = (JObject)jObject["data"];
                if (!data.ContainsKey("PALMSetting"))
                {
                    return;
                }
                checkpalmFunOn.Checked = bool.Parse(data["PALMSetting"]["palmFunOn"].ToString());
                String state = data["PALMSetting"]["palmRunState"].ToString();
                if (state.Equals("match"))
                {
                    cmbpalmRunState.SelectedIndex = 0;
                }
                else
                {
                    cmbpalmRunState.SelectedIndex = 1;
                }

                textPalmWidth.Text = data["PALMSetting"]["palmSupportWidth"].ToString();
                textPalmHeight.Text = data["PALMSetting"]["palmSupportHeight"].ToString();

                textPalmImageQuality.Text = data["PALMSetting"]["imageQualityThreshold"].ToString();
                textPalmTemplateQuality.Text = data["PALMSetting"]["templateQualityThreshold"].ToString();

                if (((JObject)data["PALMSetting"]).ContainsKey("palmIdentifyThreshold"))
                {
                    textPalmThreshold.Text = data["PALMSetting"]["palmIdentifyThreshold"].ToString();
                }
            }
        }

        private void trackBulr_Scroll(object sender, EventArgs e)
        {
            textBlur.Text = trackBulr.Value.ToString();
        }

        private void textBlur_TextChanged(object sender, EventArgs e)
        {
            trackBulr.Value = int.Parse(textBlur.Text);
        }

        private void trackFront_Scroll(object sender, EventArgs e)
        {
            textFrontThreshold.Text = trackFront.Value.ToString();
        }

        private void textFrontThreshold_TextChanged(object sender, EventArgs e)
        {
            trackFront.Value = int.Parse(textFrontThreshold.Text);
        }

        private void trackQuality_Scroll(object sender, EventArgs e)
        {
            textQuality.Text = trackQuality.Value.ToString();
        }

        private void textQuality_TextChanged(object sender, EventArgs e)
        {
            trackQuality.Value = int.Parse(textQuality.Text.ToString());
        }

        private void trackMaxHeight_Scroll(object sender, EventArgs e)
        {
            textMaxHeight.Text = trackMaxHeight.Value.ToString();
        }

        private void textMaxHeight_TextChanged(object sender, EventArgs e)
        {
            trackMaxHeight.Value = int.Parse(textMaxHeight.Text.ToString());
        }

        private void trackMinHeight_Scroll(object sender, EventArgs e)
        {
            textMinHeight.Text = trackMinHeight.Value.ToString();
        }

        private void textMinHeight_TextChanged(object sender, EventArgs e)
        {
            trackMinHeight.Value = int.Parse(textMinHeight.Text.ToString());
        }

        private void trackMaxWidth_Scroll(object sender, EventArgs e)
        {
            textMaxWidth.Text = trackMaxWidth.Value.ToString();
        }

        private void textMaxWidth_TextChanged(object sender, EventArgs e)
        {
            trackMaxWidth.Value = int.Parse(textMaxWidth.Text.ToString());
        }

        private void trackMinWidth_Scroll(object sender, EventArgs e)
        {
            textMinWidth.Text = trackMinWidth.Value.ToString();
        }

        private void textMinWidth_TextChanged(object sender, EventArgs e)
        {
            trackMinWidth.Value = int.Parse(textMinWidth.Text.ToString());
        }

        private void trackMaxPitch_Scroll(object sender, EventArgs e)
        {
            textMaxPitch.Text = trackMaxPitch.Value.ToString();
        }

        private void textMaxPitch_TextChanged(object sender, EventArgs e)
        {
            trackMaxPitch.Value = int.Parse(textMaxPitch.Text.ToString());
        }

        private void trackMinPitch_Scroll(object sender, EventArgs e)
        {
            textMinPitch.Text = trackMinPitch.Value.ToString();
        }

        private void textMinPitch_TextChanged(object sender, EventArgs e)
        {
            trackMinPitch.Value = int.Parse(textMinPitch.Text.ToString());
        }

        private void trackMaxRoll_Scroll(object sender, EventArgs e)
        {
            textMaxRoll.Text = trackMaxRoll.Value.ToString();
        }

        private void textMaxRoll_TextChanged(object sender, EventArgs e)
        {
            trackMaxRoll.Value = int.Parse(textMaxRoll.Text.ToString());
        }

        private void trackMinRoll_Scroll(object sender, EventArgs e)
        {
            textMinRoll.Text = trackMinRoll.Value.ToString();
        }

        private void textMinRoll_TextChanged(object sender, EventArgs e)
        {
            trackMinRoll.Value = int.Parse(textMinRoll.Text.ToString());
        }

        private void trackMaxYaw_Scroll(object sender, EventArgs e)
        {
            textMaxYaw.Text = trackMaxYaw.Value.ToString();
        }

        private void textMaxYaw_TextChanged(object sender, EventArgs e)
        {
            trackMaxYaw.Value = int.Parse(textMaxYaw.Text.ToString());
        }

        private void trackMinYaw_Scroll(object sender, EventArgs e)
        {
            textMinYaw.Text = trackMinYaw.Value.ToString();
        }

        private void textMinYaw_TextChanged(object sender, EventArgs e)
        {
            trackMinYaw.Value = int.Parse(textMinYaw.Text.ToString());
        }

        private void button5_Click(object sender, EventArgs e)
        {
            if (IntPtr.Zero == m_HidHandle)
            {
                MessageBox.Show("Device not connect!");
                return;
            }
            int ret = ZKBioModuleHIDApi.reboot(m_HidHandle, 0);
            if (0 == ret)
            {
                texttabInfo.Text = "Reboot successfully";
            }
            else
            {
                texttabInfo.Text = "Reboot failed";
            }
        }

        private void button8_Click(object sender, EventArgs e)
        {
            if (IntPtr.Zero == m_HidHandle)
            {
                MessageBox.Show("Device not connect!");
                return;
            }
            String localTimeStr = DateTime.Now.ToLocalTime().ToString("yyyy-MM-dd HH:mm:ss");
            string json = CustomDataParse.getSyncTimeJson(localTimeStr);
            int ret = ZKBioModuleHIDApi.setConfig(m_HidHandle, (int)HID_ConfigType.DEVICE_TIME, json);
            if (0 == ret)
            {
                texttabInfo.Text = "Sync time successfully";
            }
            else
            {
                texttabInfo.Text = "Sync time failed, ret=" + ret;
            }
        }

        private void button9_Click(object sender, EventArgs e)
        {
            if (IntPtr.Zero == m_HidHandle)
            {
                MessageBox.Show("Device not connect!");
                return;
            }
            String strResult = "";
            int ret = ZKBioModuleHIDApi.getConfig(m_HidHandle, (int)HID_ConfigType.DEVICE_TIME, ref strResult);
            if (0 == ret)
            {
                int status = 0;
                string detail = "", sysTime = "";
                if (CustomDataParse.parseDeviceTime(strResult, ref status, ref detail, ref sysTime))
                {
                    textDeviceTime.Text = sysTime;
                }
                else
                {
                    texttabInfo.Text = "Get time failed, status=" + status;
                }
            }
            else
            {
                texttabInfo.Text = "Get time failed, ret=" + ret;
            }
        }

        private void button7_Click(object sender, EventArgs e)
        {
            if (IntPtr.Zero == m_HidHandle)
            {
                MessageBox.Show("Device not connect!");
                return;
            }
            if (tabControl1.SelectedIndex == 1)
            {
                // commonsetting
                {
                    String json = "{\r\n" +
                                  "\"commonSettings\" : {\r\n " +
                                  "\"NIRLiveness\" : true,\r\n" +
                                  "\"VLLiveness\" : true,\r\n" +
                                  "\"attendInterval\" : 5000,\r\n" +
                                  "\"attendPhotoQuality\" : \"general\",\r\n" +
                                  "\"attrInterval\" : 0,\r\n" +
                                  "\"attributeRecog\" : true,\r\n" +
                                  "\"countAlgorithm\" : false,\r\n" +
                                  "\"debugLevel\" : 0,\r\n" +
                                  "\"drawTrackRect\" : false,\r\n" +
                                  "\"enableStoreAttendLog\" : true,\r\n" +
                                  "\"enableStoreAttendPhoto\" : false,\r\n" +
                                  "\"enableStoreStrangerAttLog\" : false,\r\n" +
                                  "\"faceAEEnabled\" : true,\r\n" +
                                  "\"hacknessThreshold\" : 0.99000000953674316,\r\n" +
                                  "\"infraredPictureFormat\" : \"jpeg\",\r\n" +
                                  "\"isTrackingMatchMode\" : true,\r\n" +
                                  "\"recogInterval\" : 1000,\r\n" +
                                  "\"recogRespirator\" : false,\r\n" +
                                  "\"recogThreshold\" : 0.89999997615814209,\r\n" +
                                  "\"scoringInterval\" : 3\r\n" +
                                  "}\r\n" +
                                  "}";

                    int ret = ZKBioModuleHIDApi.setConfig(m_HidHandle, (int)HID_ConfigType.COMMON_CONFIG, json);
                    if (0 == ret)
                    {
                        texttabInfo.Text = "SetConfig successfully";
                    }
                    else
                    {
                        texttabInfo.Text = "SetConfig failed, ret=" + ret;
                    }
                }
                {
                    // GetCaptureFilter
                    String json = "{\r\n" +
                                  "\"captureFilter\" : {\r\n" +
                                  "\"blurThreshold\" : 30,\r\n" +
                                  "\"frontThreshold\" : 50,\r\n" +
                                  "\"heightMaxValue\" : 400,\r\n" +
                                  "\"heightMinValue\" : 40,\r\n" +
                                  "\"pitchMaxValue\" : 30,\r\n" +
                                  "\"pitchMinValue\" : -90,\r\n" +
                                  "\"rollMaxValue\" : 30,\r\n" +
                                  "\"rollMinValue\" : -90,\r\n" +
                                  "\"scoreThreshold\" : 30,\r\n" +
                                  "\"widthMaxValue\" : 400,\r\n" +
                                  "\"widthMinValue\" : 40,\r\n" +
                                  "\"yawMaxValue\" : 46,\r\n" +
                                  "\"yawMinValue\" : -90\r\n" +
                                  "}\r\n" +
                                  "}";
                    int ret = ZKBioModuleHIDApi.setConfig(m_HidHandle, (int)HID_ConfigType.CAPTURE_FILTER_CONFIG, json);
                    if (0 == ret)
                    {
                        texttabInfo.Text = "SetConfig successfully";
                    }
                    else
                    {
                        texttabInfo.Text = "SetConfig failed, ret=" + ret;
                    }
                }
            }
            else if (tabControl1.SelectedIndex == 2)
            {
                {
                    // MotionDetection
                    String json = "{\r\n" + 
                                "\"MotionDetectionSetting\" : {\r\n" +
                                "\"brightnessThreshold\" : 0,\r\n" +
                                "\"idleTimeOutMS\" : 0,\r\n" +
                                "\"motionDetectFunOn\" : false,\r\n" +
                                "\"sensitivityThreshold\" : 0\r\n" +
                                "}\r\n" +
                                 "}";
                    int ret = ZKBioModuleHIDApi.setConfig(m_HidHandle, (int)HID_ConfigType.MOTION_DETECT_CONFIG, json);
                    if (0 == ret)
                    {
                        texttabInfo.Text = "SetConfig successfully";
                    }
                    else
                    {
                        texttabInfo.Text = "SetConfig failed, ret=" + ret;
                    }
                }
                {
                    // Palm setting
                    String json = "{\r\n" +
                                "\"PALMSetting\" : {\r\n " +
                                "\"imageQualityThreshold\" : 0,\r\n " +
                                "\"palmFunOn\" : false,\r\n " +
                                "\"palmIdentifyThreshold\" : 0,\r\n " +
                                "\"palmRunState\" : \"enroll\",\r\n " +
                                "\"palmSupportHeight\" : 1280,\r\n " +
                                "\"palmSupportWidth\" : 720,\r\n " +
                                "\"templateQualityThreshold\" : 0\r\n " +
                                 "}\r\n" + 
                                 "}";
                    int ret = ZKBioModuleHIDApi.setConfig(m_HidHandle, (int)HID_ConfigType.PALM_CONFIG, json);
                    if (0 == ret)
                    {
                        texttabInfo.Text = "SetConfig successfully";
                    }
                    else
                    {
                        texttabInfo.Text = "SetConfig failed, ret=" + ret;
                    }
                }
            }
        }
    }
}
