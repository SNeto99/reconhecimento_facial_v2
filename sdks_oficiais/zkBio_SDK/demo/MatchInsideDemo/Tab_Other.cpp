// Tab_Other.cpp : implementation file
//

#include "stdafx.h"
#include "ZKCameraDemo.h"
#include "Tab_Other.h"
#include "afxdialogex.h"
#include "SettingDlg.h"
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

using namespace rapidjson;
using namespace std;

// Tab_Other dialog

IMPLEMENT_DYNAMIC(Tab_Other, CDialogEx)

Tab_Other::Tab_Other(CWnd* pParent /*=NULL*/)
	: CDialogEx(Tab_Other::IDD, pParent)
{

}

Tab_Other::~Tab_Other()
{
}

void Tab_Other::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}


BEGIN_MESSAGE_MAP(Tab_Other, CDialogEx)
END_MESSAGE_MAP()


// Tab_Other message handlers
BOOL Tab_Other::Create(UINT nIDTemplate, CWnd* pParentWnd, CWnd* pParent)
{
	CDialogEx::Create(nIDTemplate, pParentWnd);

	this->pParent = pParent;

	return TRUE;
}

int Tab_Other::SetMotionDetection(char *value)
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	Document document;
	document.Parse(value);

	if (document.HasParseError())
	{
		dlg->ShowInfo(_T("Parse MotionDetection json failed"));
		return -2;
	}

	const Value& detail = document["detail"];
	if(strstr(detail.GetString(), "success"))
	{
		const Value& data = document["data"];
		string str;
		wstring wstr;
		int n;

		if(!data.HasMember("MotionDetectionSetting"))
		{
			return -2;
		}

		n = data["MotionDetectionSetting"]["brightnessThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_BRIGHTNESS, n);

		((CButton *)GetDlgItem(IDC_CHECK_MOTIONFUN))->SetCheck(data["MotionDetectionSetting"]["motionDetectFunOn"].GetBool());
		
		n = data["MotionDetectionSetting"]["idleTimeOutMS"].GetInt();
		SetDlgItemInt(IDC_EDIT_TIMEOUT, n);

		n = data["MotionDetectionSetting"]["sensitivityThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_SENSITIVITY, n);

		return 0;
	}

	return -1;
}

int Tab_Other::GetMotionDetection(char *value, int *len)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);
	int ret = 0, n = 0;

	writer.StartObject();
	writer.Key("MotionDetectionSetting");
	writer.StartObject();
	writer.Key("motionDetectFunOn");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_MOTIONFUN));
	writer.Key("brightnessThreshold");
	writer.Uint(GetDlgItemInt(IDC_EDIT_BRIGHTNESS));
	writer.Key("idleTimeOutMS");
	writer.Uint(GetDlgItemInt(IDC_EDIT_TIMEOUT));
	writer.Key("sensitivityThreshold");
	writer.Uint(GetDlgItemInt(IDC_EDIT_SENSITIVITY));
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

int Tab_Other::SetPalmSettings(char *value)
{
	CSettingDlg *dlg = (CSettingDlg *)this->pParent;
	Document document;
	document.Parse(value);

	if (document.HasParseError())
	{
		dlg->ShowInfo(_T("Parse MotionDetection json failed"));
		return -2;
	}

	const Value& detail = document["detail"];
	if(strstr(detail.GetString(), "success"))
	{
		const Value& data = document["data"];
		string str;
		wstring wstr;
		int n;

		if(!data.HasMember("PALMSetting"))
		{
			return -2;
		}

		((CButton *)GetDlgItem(IDC_CHECK_PALMFUN))->SetCheck(data["PALMSetting"]["palmFunOn"].GetBool());

		str = data["PALMSetting"]["palmRunState"].GetString();
		((CComboBox *)GetDlgItem(IDC_COMBO_STATUS))->SetCurSel(str == "match" ? 0 : 1);
		
		n = data["PALMSetting"]["palmSupportWidth"].GetInt();
		SetDlgItemInt(IDC_EDIT_PALMW, n);

		n = data["PALMSetting"]["palmSupportHeight"].GetInt();
		SetDlgItemInt(IDC_EDIT_PALMH, n);

		n = data["PALMSetting"]["imageQualityThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_IMAGE_QUALITY, n);

		n = data["PALMSetting"]["templateQualityThreshold"].GetInt();
		SetDlgItemInt(IDC_EDIT_TEMPLATE_QUALITY, n);

		if(data["PALMSetting"].HasMember("palmIdentifyThreshold"))
		{
			n = data["PALMSetting"]["palmIdentifyThreshold"].GetInt();
			SetDlgItemInt(IDC_EDIT_THRESHOLD, n);
			dlg->SetPalmThreshold(n);
		}

		return 0;
	}

	return -1;
}

int Tab_Other::GetPalmSettings(char *value, int *len)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);
	int ret = 0, n = 0;

	writer.StartObject();
	writer.Key("PALMSetting");
	writer.StartObject();
	writer.Key("palmFunOn");
	writer.Bool(IsDlgButtonChecked(IDC_CHECK_PALMFUN));
	writer.Key("palmRunState");
	n = ((CComboBox *)GetDlgItem(IDC_COMBO_STATUS))->GetCurSel();
	writer.String(n == 0 ? "match" : "enroll");
	writer.Key("palmSupportWidth");
	writer.Uint(GetDlgItemInt(IDC_EDIT_PALMW));
	writer.Key("palmSupportHeight");
	writer.Uint(GetDlgItemInt(IDC_EDIT_PALMH));
	writer.Key("imageQualityThreshold");
	writer.Uint(GetDlgItemInt(IDC_EDIT_IMAGE_QUALITY));
	writer.Key("templateQualityThreshold");
	writer.Uint(GetDlgItemInt(IDC_EDIT_TEMPLATE_QUALITY));
	writer.Key("palmIdentifyThreshold");
	writer.Uint(GetDlgItemInt(IDC_EDIT_THRESHOLD));
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