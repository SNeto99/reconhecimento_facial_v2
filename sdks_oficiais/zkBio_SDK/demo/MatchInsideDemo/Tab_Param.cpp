// Tab_Param.cpp : implementation file
//

#include "stdafx.h"
#include "ZKCameraDemo.h"
#include "Tab_Param.h"
#include "afxdialogex.h"
#include "futil.h"
#include "SettingDlg.h"
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

using namespace rapidjson;
using namespace std;

// Tab_Param dialog

IMPLEMENT_DYNAMIC(Tab_Param, CDialogEx)

Tab_Param::Tab_Param(CWnd* pParent /*=NULL*/)
	: CDialogEx(Tab_Param::IDD, pParent)
{

}

Tab_Param::~Tab_Param()
{
}

void Tab_Param::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}


BEGIN_MESSAGE_MAP(Tab_Param, CDialogEx)
	ON_WM_VSCROLL()
	ON_NOTIFY(UDN_DELTAPOS, IDC_SPIN_DEBUG, &Tab_Param::OnDeltaposSpinDebug)

	ON_CONTROL_RANGE(EN_CHANGE, IDC_EDIT_BLUR, IDC_EDIT_MINYAW, &Tab_Param::OnEnChangeEdit)
	ON_WM_HSCROLL()
END_MESSAGE_MAP()


// Tab_Param message handlers
BOOL Tab_Param::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// Add "About..." menu item to system menu.
	SetDlgItemInt(IDC_EDIT_DEBUG, 0);
	CSpinButtonCtrl* pSpin = (CSpinButtonCtrl *)GetDlgItem(IDC_SPIN_DEBUG);
	pSpin->SetBuddy(GetDlgItem(IDC_EDIT_DEBUG));
	pSpin->SetRange(0, 10);

	SetDlgItemText(IDC_EDIT_THRESHOLD, _T("0.899"));

	SetDlgItemText(IDC_EDIT_LIVENESSTHRESHOLD, _T("0.99"));
	SetDlgItemInt(IDC_EDIT_RECOG_INTERVAL, 1000);
	SetDlgItemInt(IDC_EDIT_ATTR_INTERVAL, 1000);
	SetDlgItemInt(IDC_EDIT_ATT_INTERVAL, 5000);

	CSliderCtrl *pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_BLUR);
	pSlider->SetRange(0, 100, TRUE);
	pSlider->SetPos(30);
	SetDlgItemInt(IDC_EDIT_BLUR, 30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_FRONT);
	pSlider->SetRange(0, 100, TRUE);
	pSlider->SetPos(50);
	SetDlgItemInt(IDC_EDIT_FRONT, 50);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_QUALITY);
	pSlider->SetRange(0, 100, TRUE);
	pSlider->SetPos(30);
	SetDlgItemInt(IDC_EDIT_QUALITY, 30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MAXH);
	pSlider->SetRange(200, 1000, TRUE);
	pSlider->SetPos(400);
	SetDlgItemInt(IDC_EDIT_MAXH, 400);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MINH);
	pSlider->SetRange(0, 200, TRUE);
	pSlider->SetPos(40);
	SetDlgItemInt(IDC_EDIT_MINH, 40);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MAXW);
	pSlider->SetRange(200, 1000, TRUE);
	pSlider->SetPos(400);
	SetDlgItemInt(IDC_EDIT_MAXW, 400);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MINW);
	pSlider->SetRange(0, 200, TRUE);
	pSlider->SetPos(40);
	SetDlgItemInt(IDC_EDIT_MINW, 40);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MAXPITCH);
	pSlider->SetRange(0, 90, TRUE);
	pSlider->SetPos(30);
	SetDlgItemInt(IDC_EDIT_MAXPITCH, 30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MINPITCH);
	pSlider->SetRange(-90, 0, TRUE);
	pSlider->SetPos(-30);
	SetDlgItemInt(IDC_EDIT_MINPITCH, -30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MAXROLL);
	pSlider->SetRange(0, 90, TRUE);
	pSlider->SetPos(30);
	SetDlgItemInt(IDC_EDIT_MAXROLL, 30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MINROLL);
	pSlider->SetRange(-90, 0, TRUE);
	pSlider->SetPos(-30);
	SetDlgItemInt(IDC_EDIT_MINROLL, -30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MAXYAW);
	pSlider->SetRange(0, 90, TRUE);
	pSlider->SetPos(30);
	SetDlgItemInt(IDC_EDIT_MAXYAW, 30);

	pSlider = (CSliderCtrl *)GetDlgItem(IDC_SLIDER_MINYAW);
	pSlider->SetRange(-90, 0, TRUE);
	pSlider->SetPos(-30);
	SetDlgItemInt(IDC_EDIT_MINYAW, -30);

	return TRUE;  // return TRUE  unless you set the focus to a control
}

BOOL Tab_Param::Create(UINT nIDTemplate, CWnd* pParentWnd, CWnd* pParent)
{
	CDialogEx::Create(nIDTemplate, pParentWnd);

	this->pParent = pParent;

	//((CSettingDlg *)pParent)->OnBnClickedBtnGet();

	return TRUE;
}

void Tab_Param::OnDeltaposSpinDebug(NMHDR *pNMHDR, LRESULT *pResult)
{
	LPNMUPDOWN pNMUpDown = reinterpret_cast<LPNMUPDOWN>(pNMHDR);
	// TODO: Add your control notification handler code here

	int value = GetDlgItemInt(IDC_EDIT_DEBUG);
	CString strValue;
 
    if(pNMUpDown->iDelta == 1)                    //如果点击的是Spin中的往上按钮
    {
        if(value < 10)
        {
			SetDlgItemInt(IDC_EDIT_DEBUG, value+1);
        }
    }
    else if(pNMUpDown->iDelta == - 1)    //如果点击的是Spin中往下按钮
    {
		if(value > 0)
		{
			SetDlgItemInt(IDC_EDIT_DEBUG, value-1);
		}
    }

	*pResult = 0;
}

int Tab_Param::SetCommonSettings(char *value)
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	Document document;
	document.Parse(value);

	if (document.HasParseError())
	{
		dlg->ShowInfo(_T("Parse CommonSettings json failed"));
		return -2;
	}

	if(0 == document["status"])
	{
		const Value& data = document["data"];
		string str;
		wstring wstr;
		CString cstr;
		int n;
		float f = 0.0f;

		if(!data.HasMember("commonSettings"))
		{
			return -2;
		}

		((CButton *)GetDlgItem(IDC_CHECK_ATTR_REG))->SetCheck(data["commonSettings"]["attributeRecog"].GetBool());
		
		((CButton *)GetDlgItem(IDC_CHECK_ALG_COUNT))->SetCheck(data["commonSettings"]["countAlgorithm"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_DRAW_TRACK))->SetCheck(data["commonSettings"]["drawTrackRect"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_FACEAE))->SetCheck(data["commonSettings"]["faceAEEnabled"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_RGB_LIVE))->SetCheck(data["commonSettings"]["VLLiveness"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_NIR_LIVE))->SetCheck(data["commonSettings"]["NIRLiveness"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_MASK))->SetCheck(data["commonSettings"]["recogRespirator"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_ATTEND_LOG))->SetCheck(data["commonSettings"]["enableStoreAttendLog"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_STRANGER_ATT_LOG))->SetCheck(data["commonSettings"]["enableStoreStrangerAttLog"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_TRACK_MATCHING))->SetCheck(data["commonSettings"]["isTrackingMatchMode"].GetBool());

		((CButton *)GetDlgItem(IDC_CHECK_STORE_ATT_PHOTO))->SetCheck(data["commonSettings"]["enableStoreAttendPhoto"].GetBool());
		
		n = data["commonSettings"]["debugLevel"].GetInt();
		SetDlgItemInt(IDC_EDIT_DEBUG, n);

		n = data["commonSettings"]["recogInterval"].GetInt();
		SetDlgItemInt(IDC_EDIT_RECOG_INTERVAL, n);

		f = data["commonSettings"]["recogThreshold"].GetFloat();
		cstr.Format(_T("%.2f"), f);
		SetDlgItemText(IDC_EDIT_THRESHOLD, cstr);
		dlg->SetFaceThreshold(f);

		f = data["commonSettings"]["hacknessThreshold"].GetFloat();
		cstr.Format(_T("%.2f"), f);
		SetDlgItemText(IDC_EDIT_LIVENESSTHRESHOLD, cstr);

		n = data["commonSettings"]["attrInterval"].GetInt();
		SetDlgItemInt(IDC_EDIT_ATTR_INTERVAL, n);

		n = data["commonSettings"]["attendInterval"].GetInt();
		SetDlgItemInt(IDC_EDIT_ATT_INTERVAL, n);

		str = data["commonSettings"]["infraredPictureFormat"].GetString();
		((CComboBox *)GetDlgItem(IDC_COMBO_NIR_PIC_FORMAT))->SetCurSel(str == "jpeg" ? 0 : 1);

		str = data["commonSettings"]["attendPhotoQuality"].GetString();
		if("best" == str)
		{
			((CComboBox *)GetDlgItem(IDC_COMBO_PHOTO_QUALITY))->SetCurSel(0);
		}
		else if("good" == str)
		{
			((CComboBox *)GetDlgItem(IDC_COMBO_PHOTO_QUALITY))->SetCurSel(1);
		}
		else
		{
			((CComboBox *)GetDlgItem(IDC_COMBO_PHOTO_QUALITY))->SetCurSel(2);
		}


		return 0;
	}

	return -1;
}

int Tab_Param::GetCommonSettings(char *value, int *len)
{
	/*
	{"status": 0, "detail":"success", "data":{
	   "commonSettings" : {
		  "attrInterval" : 0,
		  "attributeRecog" : "false",
		  "attributeTrack" : "false",
		  "countAlgorithm" : "false",
		  "debugLevel" : 0,
		  "drawTrackRect" : "true",
		  "faceAEEnabled" : "false",
		  "normalLiveness" : "false",
		  "recogBodyTemperature" : "false",
		  "recogInterval" : 1000,
		  "recogRespirator" : "false",
		  "recogThreshold" : 0.40000000596046448,
		  "scoringInterval" : 5,
		  "showBodyTemperatureImg" : "false",
		  "thermalImaging" : "false"
	   }
	}
	}
	*/
	StringBuffer s;
    Writer<StringBuffer> writer(s);
	int ret = 0;
	float f = 0.0f;
	CString cstr;

	writer.StartObject();
	writer.Key("commonSettings");
	writer.StartObject();
	writer.Key("attributeRecog");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_ATTR_REG));
	writer.Key("countAlgorithm");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_ALG_COUNT));
	writer.Key("debugLevel");
	writer.Uint(GetDlgItemInt(IDC_EDIT_DEBUG));
	writer.Key("drawTrackRect");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_DRAW_TRACK));
	writer.Key("faceAEEnabled");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_FACEAE));
	writer.Key("VLLiveness");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_RGB_LIVE));
	writer.Key("NIRLiveness");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_NIR_LIVE));
	writer.Key("recogRespirator");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_MASK));
	writer.Key("enableStoreAttendLog");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_ATTEND_LOG));
	writer.Key("enableStoreStrangerAttLog");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_STRANGER_ATT_LOG));
	writer.Key("isTrackingMatchMode");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_TRACK_MATCHING));
	writer.Key("enableStoreAttendPhoto");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_STORE_ATT_PHOTO));
	
	GetDlgItemText(IDC_EDIT_THRESHOLD, cstr);
	if(!cstr.IsEmpty())
	{
		f = atof(WString2String(cstr.GetBuffer()).c_str());
		if(f > 0 && f <= 1.0)
		{
			writer.Key("recogThreshold");
			writer.Double(f);
		}
	}

	GetDlgItemText(IDC_EDIT_LIVENESSTHRESHOLD, cstr);
	if(!cstr.IsEmpty())
	{
		f = atof(WString2String(cstr.GetBuffer()).c_str());
		if(f > 0 && f <= 1.0)
		{
			writer.Key("hacknessThreshold");
			writer.Double(f);
		}
	}
	writer.Key("recogInterval");
	writer.Uint(GetDlgItemInt(IDC_EDIT_RECOG_INTERVAL));
	writer.Key("attrInterval");
	writer.Uint(GetDlgItemInt(IDC_EDIT_ATTR_INTERVAL));
	writer.Key("attendInterval");
	writer.Uint(GetDlgItemInt(IDC_EDIT_ATT_INTERVAL));
	writer.Key("infraredPictureFormat");
	writer.String(((CComboBox *)GetDlgItem(IDC_COMBO_NIR_PIC_FORMAT))->GetCurSel() == 0 ? "jpeg" : "gray");
	writer.Key("attendPhotoQuality");
	if(0 == ((CComboBox *)GetDlgItem(IDC_COMBO_PHOTO_QUALITY))->GetCurSel())
	{
		writer.String("best");
	}
	else if(1 == ((CComboBox *)GetDlgItem(IDC_COMBO_PHOTO_QUALITY))->GetCurSel())
	{
		writer.String("good");
	}
	else
	{
		writer.String("general");
	}
	writer.EndObject();
	writer.EndObject();

	string str = s.GetString();
	
	if(str.length() <= *len)
	{
		strcpy(value, str.c_str());
		*len = str.length();

		ret = 0;
	}
	else
	{
		ret = -1;
	}

	return ret;
}

int Tab_Param::SetCaptureFilter(char *value)
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	Document document;
	document.Parse(value);

	if (document.HasParseError())
	{
		dlg->ShowInfo(_T("Parse CaptureFilter json failed"));
		return -2;
	}

	if(0 == document["status"])
	{
		const Value& data = document["data"];
		string str;
		wstring wstr;
		int n;

		if(!data.HasMember("captureFilter"))
		{
			return -2;
		}

		n = data["captureFilter"]["blurThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_BLUR, n);

		n = data["captureFilter"]["frontThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_FRONT, n);
		
		n = data["captureFilter"]["scoreThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_QUALITY, n);

		n = data["captureFilter"]["heightMaxValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MAXH, n);

		n = data["captureFilter"]["heightMinValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MINH, n);

		n = data["captureFilter"]["widthMaxValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MAXW, n);

		n = data["captureFilter"]["widthMinValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MINW, n);

		n = data["captureFilter"]["pitchMaxValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MAXPITCH, n);

		n = data["captureFilter"]["pitchMinValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MINPITCH, n);

		n = data["captureFilter"]["rollMaxValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MAXROLL, n);

		n = data["captureFilter"]["rollMinValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MINROLL, n);

		n = data["captureFilter"]["yawMaxValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MAXYAW, n);

		n = data["captureFilter"]["yawMinValue"].GetInt();
		SetDlgItemInt(IDC_EDIT_MINYAW, n);

		return 0;
	}

	return -1;
}

int Tab_Param::GetCaptureFilter(char *value, int *len)
{
	/*
	{"status": 0, "detail":"success", "data":{
	   "captureFilter" : {
		  "blurThreshold" : 30,
		  "frontThreshold" : 50,
		  "heightMaxValue" : 400,
		  "heightMinValue" : 40,
		  "pitchMaxValue" : 30,
		  "pitchMinValue" : -30,
		  "rollMaxValue" : 30,
		  "rollMinValue" : -30,
		  "scoreThreshold" : 30,
		  "widthMaxValue" : 400,
		  "widthMinValue" : 40,
		  "yawMaxValue" : 30,
		  "yawMinValue" : -30
	   }
	}
	}
	*/
	StringBuffer s;
    Writer<StringBuffer> writer(s);
	int ret = 0;

	writer.StartObject();
	writer.Key("captureFilter");
	writer.StartObject();
	writer.Key("blurThreshold");
	writer.Int(GetDlgItemInt(IDC_EDIT_BLUR));
	writer.Key("frontThreshold");
	writer.Int(GetDlgItemInt(IDC_EDIT_FRONT));
	writer.Key("scoreThreshold");
	writer.Int(GetDlgItemInt(IDC_EDIT_QUALITY));
	writer.Key("heightMaxValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MAXH));
	writer.Key("heightMinValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MINH));
	writer.Key("widthMaxValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MAXW));
	writer.Key("widthMinValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MINW));
	writer.Key("pitchMaxValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MAXPITCH));
	writer.Key("pitchMinValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MINPITCH));
	writer.Key("rollMaxValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MAXROLL));
	writer.Key("rollMinValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MINROLL));
	writer.Key("yawMaxValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MAXYAW));
	writer.Key("yawMinValue");
	writer.Int(GetDlgItemInt(IDC_EDIT_MINYAW));
	writer.EndObject();
	writer.EndObject();

	string str = s.GetString();
	
	if(str.length() <= *len)
	{
		strcpy(value, str.c_str());
		*len = str.length();

		ret = 0;
	}
	else
	{
		ret = -1;
	}

	return ret;
}

void Tab_Param::OnEnChangeEdit(UINT nID)
{
	switch(nID)
	{
		case IDC_EDIT_BLUR:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_BLUR))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_FRONT:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_FRONT))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_QUALITY:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_QUALITY))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MAXH:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MAXH))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MINH:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MINH))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MAXW:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MAXW))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MINW:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MINW))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MAXPITCH:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MAXPITCH))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MINPITCH:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MINPITCH))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MAXROLL:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MAXROLL))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MINROLL:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MINROLL))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MAXYAW:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MAXYAW))->SetPos(GetDlgItemInt(nID));
			}
			break;
		case IDC_EDIT_MINYAW:
			{
				((CSliderCtrl*)GetDlgItem(IDC_SLIDER_MINYAW))->SetPos(GetDlgItemInt(nID));
			}
			break;
		default:
			break;
	}
}

void Tab_Param::OnHScroll(UINT nSBCode, UINT nPos, CScrollBar* pScrollBar)
{
	// TODO: Add your message handler code here and/or call default
	if(pScrollBar == GetDlgItem(IDC_SLIDER_BLUR))
	{
		SetDlgItemInt(IDC_EDIT_BLUR, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_FRONT))
	{
		SetDlgItemInt(IDC_EDIT_FRONT, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_QUALITY))
	{
		SetDlgItemInt(IDC_EDIT_QUALITY, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MAXH))
	{
		SetDlgItemInt(IDC_EDIT_MAXH, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MINH))
	{
		SetDlgItemInt(IDC_EDIT_MINH, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MAXW))
	{
		SetDlgItemInt(IDC_EDIT_MAXW, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MINW))
	{
		SetDlgItemInt(IDC_EDIT_MINW, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MAXPITCH))
	{
		SetDlgItemInt(IDC_EDIT_MAXPITCH, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MINPITCH))
	{
		SetDlgItemInt(IDC_EDIT_MINPITCH, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MAXROLL))
	{
		SetDlgItemInt(IDC_EDIT_MAXROLL, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MINROLL))
	{
		SetDlgItemInt(IDC_EDIT_MINROLL, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MAXYAW))
	{
		SetDlgItemInt(IDC_EDIT_MAXYAW, ((CSliderCtrl*)pScrollBar)->GetPos());
	}
	else if(pScrollBar == GetDlgItem(IDC_SLIDER_MINYAW))
	{
		SetDlgItemInt(IDC_EDIT_MINYAW, ((CSliderCtrl*)pScrollBar)->GetPos());
	}

	CDialogEx::OnHScroll(nSBCode, nPos, pScrollBar);
}