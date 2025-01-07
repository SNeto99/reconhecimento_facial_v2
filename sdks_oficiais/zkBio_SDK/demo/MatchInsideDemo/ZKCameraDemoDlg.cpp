
// ZKCameraDemoDlg.cpp : implementation file
//

#include "stdafx.h"
#include "ZKCameraDemo.h"
#include "ZKCameraDemoDlg.h"
#include "afxdialogex.h"
#include <initguid.h>
#include <dbt.h>
#include "usbiodef.h"
#include "futil.h"

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

#include "base64.h"
#include "ZKCameraLib.h"
#include "ZKHIDLib.h"
#include <gdiplus.h>


using namespace std;
using namespace rapidjson;

#ifdef _DEBUG
#define new DEBUG_NEW
#endif

#define PALM_REG_TEMPLATELEN	8844
#define MATCH_TIMES	5

bool breg = false;
CRITICAL_SECTION videoLock;
CRITICAL_SECTION nirVideoLock;
CRITICAL_SECTION customLock;
queue<VideoData> videoDataQueue;
queue<CustomBioData> customDataQueue;
VideoData gVideoData;
VideoData gNIRVideoData;
CustomBioData gCustomBioData;
bool bVideoData = false;
bool bNIRVideoData = false;
bool bBioData = false;
int gImageWidth = 0;
int gImageHeight = 0;
HANDLE faceHandle = NULL;
HANDLE palmHandle = NULL;
HANDLE nirHandle = NULL;
HANDLE vlHandle = NULL;
HANDLE hidHandle = NULL;
#define QUEUE_SIZE	30
int gUSBDetached = 0;
bool bUvcOpen = false;;
bool bHidOpen = false;
bool bReplugged = 0;
int vlParam = 1;
int nirParam =2;
float faceThreshold = 0.75f;
int palmThreshold = 576;
int gNIRFrames = 0, gVLFrames = 0;
bool gPollMatchResult = false;
bool gUpgradeImage = false;

void enqueueVideoData(VideoData data)
{
	EnterCriticalSection(&videoLock);

	if(!bVideoData)
	{
		gVideoData.frame_index = data.frame_index;
		gVideoData.ori_length = data.ori_length;
		gVideoData.data_length = data.data_length;
		gVideoData.data = (unsigned char *)malloc(gVideoData.data_length);
		memcpy(gVideoData.data, data.data, gVideoData.data_length);
		_ASSERTE(_CrtCheckMemory());
		bVideoData = true;
	}

	videoDataQueue.push(data);
	if(videoDataQueue.size() > QUEUE_SIZE)
	{
		VideoData data2 = videoDataQueue.front();
		videoDataQueue.pop();
		ZKCamera_FreePointer(data2.data);
	}
	LeaveCriticalSection(&videoLock);
}

void clearVideoDataQueue()
{
	EnterCriticalSection(&videoLock);
	while (!videoDataQueue.empty())
	{
		VideoData vdata = videoDataQueue.front();
		ZKCamera_FreePointer(vdata.data);
		videoDataQueue.pop();
	}
	LeaveCriticalSection(&videoLock);
}

void clearCustomDataQueue()
{
	EnterCriticalSection(&customLock);
	while (!customDataQueue.empty())
	{
		CustomBioData data = customDataQueue.front();

		clearCustomDataVector(data.bioDatas);

		customDataQueue.pop();
	}
	LeaveCriticalSection(&customLock);
}

void __stdcall onGetVideoData(void *pUserParam, VideoData data)
{
	int userParam = *((int *)pUserParam);

	if(1 == userParam)
	{
		gVLFrames++;
		enqueueVideoData(data);
	}
	else
	{
		EnterCriticalSection(&nirVideoLock);
		gNIRFrames++;
		if(bNIRVideoData)
		{
			ZKCamera_FreePointer(gNIRVideoData.data);
			gNIRVideoData = data;
		}
		if(!bNIRVideoData)
		{
			gNIRVideoData = data;
			bNIRVideoData = true;
		}
		LeaveCriticalSection(&nirVideoLock);
	}
}

void __stdcall onGetCustomData(void *pUserParam, CustomData data)
{
	cout << "custom data - " << data.frame_index << " " << data.width << " " << data.height;
	wchar_t log[128] = {0}; 
	bool bFound = false;

	CustomBioData bioData;
	memset(&bioData, 0, sizeof(CustomBioData));
	bioData.frame_index = data.frame_index;
	bioData.width = data.width;
	bioData.height = data.height;

	bioData.bioDatas = parse_customData(data.customData);

	ZKCamera_FreePointer(data.customData);
	if(bioData.bioDatas.size() < 1)
	{
		OutputDebugString(L"No data\n");
		return;
	}

#if 1
	EnterCriticalSection(&customLock);
	if(!bBioData)
	{
		gCustomBioData.width = bioData.width;
		gCustomBioData.height = bioData.height;
		gCustomBioData.frame_index = bioData.frame_index;
		for(int i = 0; i < bioData.bioDatas.size(); i++)
		{
			PBioData pbio = new BioData(*bioData.bioDatas[i]);
			gCustomBioData.bioDatas.push_back(pbio);
		}
		bBioData = true;
	}
	if(!gPollMatchResult)
	{
		customDataQueue.push(bioData);
	}
	else
	{
		clearCustomDataVector(bioData.bioDatas);
	}
	LeaveCriticalSection(&customLock);
#endif
#if 0
	while (!videoDataQueue.empty())
	{
		VideoData vdata = videoDataQueue.front();
		if(vdata.frame_index == data.frame_index)
		{
			SaveToFile("face.jpg", vdata.data, vdata.data_length);
			bFound = true;
		}
		ZKCamera_FreePointer(vdata.data);
		videoDataQueue.pop();
		if(bFound)
		{
			break;
		}
	}
#endif
}

// CAboutDlg dialog used for App About

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// Dialog Data
	enum { IDD = IDD_ABOUTBOX };

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support

// Implementation
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(CAboutDlg::IDD)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CZKCameraDemoDlg dialog




CZKCameraDemoDlg::CZKCameraDemoDlg(CWnd* pParent /*=NULL*/)
	: CDialogEx(CZKCameraDemoDlg::IDD, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);

	bRegPalm = false;
	m_bRegPalmRun = false;
	m_bRegFaceRun = false;
	m_bPollHIDRun = false;
	m_hViewHandle = NULL;
	m_hMatchHandle = NULL;
	m_hRegPalmHandle = NULL;
	m_hRegFaceHandle = NULL;
	m_hPollHIDHandle = NULL;
	bgr = NULL;
	vlHandle = NULL;
	nirHandle = NULL;
	hidHandle = NULL;
}

void CZKCameraDemoDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CZKCameraDemoDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDC_BTN_OPEN, &CZKCameraDemoDlg::OnBnClickedBtnOpen)
	ON_BN_CLICKED(IDC_BTN_CLOSE, &CZKCameraDemoDlg::OnBnClickedBtnClose)
	ON_WM_CLOSE()
	ON_BN_CLICKED(IDC_BTN_OPEN_HID, &CZKCameraDemoDlg::OnBnClickedBtnOpenHid)
	ON_BN_CLICKED(IDC_BTN_CLOSE_HID, &CZKCameraDemoDlg::OnBnClickedBtnCloseHid)
	ON_BN_CLICKED(IDC_BTN_REG, &CZKCameraDemoDlg::OnBnClickedBtnReg)
	ON_BN_CLICKED(IDC_BTN_DEVICEMANAGE, &CZKCameraDemoDlg::OnBnClickedBtnDevicemanage)
	ON_BN_CLICKED(IDC_BTN_SNAPSHOT, &CZKCameraDemoDlg::OnBnClickedBtnSnapshot)
	ON_BN_CLICKED(IDC_BTN_CLEAR, &CZKCameraDemoDlg::OnBnClickedBtnClear)
	ON_BN_CLICKED(IDC_BTN_LOCALREGPALM, &CZKCameraDemoDlg::OnBnClickedBtnLocalregpalm)
	ON_BN_CLICKED(IDC_BTN_DELUSER, &CZKCameraDemoDlg::OnBnClickedBtnDeluser)
	ON_WM_DEVICECHANGE()
	ON_MESSAGE(WM_DEVICEATTACH, OnDeviceAttach)
	ON_BN_CLICKED(IDC_BTN_ADDUSER, &CZKCameraDemoDlg::OnBnClickedBtnAdduser)
	ON_BN_CLICKED(IDC_BTN_GETALLUSER, &CZKCameraDemoDlg::OnBnClickedBtnGetalluser)
	ON_BN_CLICKED(IDC_BTN_REGFROMFILE, &CZKCameraDemoDlg::OnBnClickedBtnRegfromfile)
	ON_BN_CLICKED(IDC_BTN_GETUSER, &CZKCameraDemoDlg::OnBnClickedBtnGetuser)
	ON_WM_SIZE()
	ON_WM_TIMER()
	ON_BN_CLICKED(IDC_CHECK_POLLMATCHRESULT, &CZKCameraDemoDlg::OnBnClickedCheckPollmatchresult)
	ON_BN_CLICKED(IDC_BTN_CLEAR_ATT_RECORD, &CZKCameraDemoDlg::OnBnClickedBtnClearAttRecord)
	ON_BN_CLICKED(IDC_BTN_GET_ATT_RECORD, &CZKCameraDemoDlg::OnBnClickedBtnGetAttRecord)
END_MESSAGE_MAP()


// CZKCameraDemoDlg message handlers

BOOL CZKCameraDemoDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon

	SetTimer(1, 1000, 0);

	RECT mRect;
	GetClientRect(&mRect);

	int nParts[3] = { 150, 600, -1 };
	mStatusBar = new CStatusBarCtrl;
	mStatusBar->Create(WS_VISIBLE | CBRS_BOTTOM, mRect, this, 0);
	mStatusBar->SetParts(3, nParts);
	mStatusBar->SetText(TEXT("VL: 0fps NIR: 0fps"), 0, 0);
	mStatusBar->ShowWindow(SW_SHOW);

	// TODO: Add extra initialization here
	CComboBox *com = (CComboBox *)GetDlgItem(IDC_COMBO_RESOLUTION);
	com->SetCurSel(1);

	((CComboBox *)GetDlgItem(IDC_COMBO_FPS))->SetCurSel(0);

	InitializeCriticalSection(&videoLock);
	InitializeCriticalSection(&nirVideoLock);
	InitializeCriticalSection(&customLock);

	ReadIniFloat(_T("Parameter"), _T("faceThreshold"), faceThreshold, 0.75);
	ReadIniInt(_T("Parameter"), _T("palmThreshold"), palmThreshold, 576);

	settingDlg.Create(IDD_SETTING_DIALOG, this);

	DEV_BROADCAST_DEVICEINTERFACE broadcastInterface;
	broadcastInterface.dbcc_size = sizeof(DEV_BROADCAST_DEVICEINTERFACE);
	broadcastInterface.dbcc_devicetype = DBT_DEVTYP_DEVICEINTERFACE;
	memcpy(&(broadcastInterface.dbcc_classguid), &(GUID_CLASS_USB_DEVICE), sizeof(struct _GUID));
	mNotifyDevHandle = RegisterDeviceNotification(this->m_hWnd, &broadcastInterface, DEVICE_NOTIFY_WINDOW_HANDLE);
	memcpy(&(broadcastInterface.dbcc_classguid), &(GUID_CLASS_USBHUB), sizeof(struct _GUID));
	mNotifyHubHandle = RegisterDeviceNotification(this->m_hWnd, &broadcastInterface, DEVICE_NOTIFY_WINDOW_HANDLE);

	m_bMatchRun = true;
	m_hMatchHandle = CreateThread(NULL, 0,                      // use default stack size  
	MatchThread,       // thread function name
	this,          // argument to thread function 
	0,                      // use default creation flags 
	NULL);   // returns the thread identifier

	EnableControl(false);

	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CZKCameraDemoDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CZKCameraDemoDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

// The system calls this function to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CZKCameraDemoDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}

BOOL CZKCameraDemoDlg::PreTranslateMessage(MSG* pMsg)
{
    if(pMsg->message==WM_KEYDOWN && (pMsg->wParam==VK_ESCAPE || pMsg->wParam==VK_RETURN))
        return TRUE;
    else
        return CDialog::PreTranslateMessage(pMsg);
}

void CZKCameraDemoDlg::updateView(unsigned char* raw, int w, int h)
{
	CRect cRect;
	CWnd *item = GetDlgItem(IDC_STATIC_IMAGE);
	CDC *cdc = item->GetDC();
	item->GetClientRect(&cRect);
	SetStretchBltMode(cdc->m_hDC, STRETCH_HALFTONE);
	CString str;
	wchar_t wlog[128] = {0};
	char log[1024] = {0};
	float coef = 1.0;
	int offset_x = 0, offset_y = 0;

	CImage	*cim = new CImage();
	cim->Create(w, h, 24);
	for(int i = 0; i < h; i++)
	{
		memcpy(cim->GetPixelAddress(0, i), raw + w * 3 * i, w*3);
	}

	if (w > cRect.Width() || h > cRect.Height())
	{
		coef = ((float)h / w) > ((float)cRect.Height() / cRect.Width()) ? (float)h / cRect.Height() : (float)w / cRect.Width();
		offset_x = (cRect.Width() - w / coef) / 2;
		offset_y = (cRect.Height() - h / coef) / 2;
		cRect.MoveToXY(offset_x, offset_y);
		cRect.right = cRect.left + w / coef;
		cRect.bottom = cRect.top + h / coef;
	}

	cim->StretchBlt(cdc->m_hDC, cRect.left, cRect.top, cRect.Width(), cRect.Height(), 0, 0, w, h, SRCCOPY);

	BioRect *rect = NULL;
	int count = 0;
	static int lastAge = 0, lastGender = 0, lastMask = 0, lastLiveness = 0, lastLivenessMode = 0;
	static float livenessScore = 0;
	EnterCriticalSection(&customLock);
	if(bBioData)
	{
		count = gCustomBioData.bioDatas.size();
		rect = GetBioRect(gCustomBioData);
		memset(log, 0, sizeof(log));
		
		for(int i = 0; i < count; i ++)
		{
			if(0 == i && 1 == gCustomBioData.bioDatas[0]->label)
			{
				sprintf(log, "trackId: %d\r\n", gCustomBioData.bioDatas[0]->trackData.trackId);
				sprintf(log, "%syaw: %.2f\r\n", log, gCustomBioData.bioDatas[0]->trackData.pose.yaw);
				sprintf(log, "%spitch: %.2f\r\n", log, gCustomBioData.bioDatas[0]->trackData.pose.pitch);
				sprintf(log, "%sroll: %.2f\r\n", log, gCustomBioData.bioDatas[0]->trackData.pose.roll);
				if(gCustomBioData.bioDatas[0]->hasAttr)
				{
					sprintf(log, "%sage: %d\r\n", log, gCustomBioData.bioDatas[0]->attribute.age);
					sprintf(log, "%sgender: %s\r\n", log, gCustomBioData.bioDatas[0]->attribute.gender == 1 ? "Male": "Female");
					sprintf(log, "%smask: %d\r\n", log, gCustomBioData.bioDatas[0]->attribute.respirator);

					lastAge = gCustomBioData.bioDatas[0]->attribute.age;
					lastGender = gCustomBioData.bioDatas[0]->attribute.gender;
					lastMask = gCustomBioData.bioDatas[0]->attribute.respirator;
				}
				else
				{
					sprintf(log, "%sage: %d\r\n", log, lastAge);
					sprintf(log, "%sgender: %s\r\n", log, lastGender == 1 ? "Male": "Female");
					sprintf(log, "%smask: %d\r\n", log, lastMask);
				}
				if(gCustomBioData.bioDatas[0]->hasLiveScore)
				{
					sprintf(log, "%sliveness: %d\r\n", log, gCustomBioData.bioDatas[0]->liveness.liveness);
					sprintf(log, "%slivenessScore: %.2f\r\n", log, gCustomBioData.bioDatas[0]->liveness.livenessScore);
					sprintf(log, "%slivenessMode: %d\r\n", log, gCustomBioData.bioDatas[0]->liveness.livenessMode);

					lastLiveness = gCustomBioData.bioDatas[0]->liveness.liveness;
					livenessScore = gCustomBioData.bioDatas[0]->liveness.livenessScore;
					lastLivenessMode = gCustomBioData.bioDatas[0]->liveness.livenessMode;
				}
				else
				{
					sprintf(log, "%sliveness: %d\r\n", log, lastLiveness);
					sprintf(log, "%slivenessScore: %.2f\r\n", log, livenessScore);
					sprintf(log, "%slivenessMode: %d\r\n", log, lastLivenessMode);
				}
				str.Append(String2WString(log).c_str());
				SetDlgItemText(IDC_EDIT_RESULT, str);
			}
		}
		clearCustomDataVector(gCustomBioData.bioDatas);

		bBioData = false;
	}
	LeaveCriticalSection(&customLock);

	COLORREF color;
	if(1)
	{
		color = RGB(0, 255, 0);
	}
	else
	{
		color = RGB(255, 0, 0);
	}
	CPen pen(PS_SOLID, 1, color);
	cdc->SelectObject(&pen);

	if(rect)
	{
		for(int i = 0; i < count; i++)
		{
			for(int j = 0; j < 4; j++)
			{
				rect[i].point[j].x /= coef;
				rect[i].point[j].x += offset_x;
				rect[i].point[j].y /= coef;
				rect[i].point[j].y += offset_y;
			}
			cdc->MoveTo(rect[i].point[3]);
			for (int j = 0; j < 4; j++)
			{
				cdc->LineTo(rect[i].point[j]);
			}
		}

		delete []rect;
		rect = NULL;
	}
	DeleteObject(pen);
	ReleaseDC(cdc);
	cim->Destroy();
	delete cim;
	cim = NULL;
}

void CZKCameraDemoDlg::updateNIRView(unsigned char* raw, int w, int h)
{
	CRect cRect;
	CWnd *item = GetDlgItem(IDC_STATIC_NIRIMAGE);
	CDC *cdc = item->GetDC();
	item->GetClientRect(&cRect);
	SetStretchBltMode(cdc->m_hDC, STRETCH_HALFTONE);
	CString str;
	wchar_t wlog[128] = {0};
	char log[1024] = {0};
	float coef = 1.0;
	int offset_x = 0, offset_y = 0;

	CImage	*cim = new CImage();
	cim->Create(w, h, 24);
	for(int i = 0; i < h; i++)
	{
		memcpy(cim->GetPixelAddress(0, i), raw + w * 3 * i, w*3);
	}

	if (w > cRect.Width() || h > cRect.Height())
	{
		coef = ((float)h / w) > ((float)cRect.Height() / cRect.Width()) ? (float)h / cRect.Height() : (float)w / cRect.Width();
		offset_x = (cRect.Width() - w / coef) / 2;
		offset_y = (cRect.Height() - h / coef) / 2;
		cRect.MoveToXY(offset_x, offset_y);
		cRect.right = cRect.left + w / coef;
		cRect.bottom = cRect.top + h / coef;
	}

	cim->StretchBlt(cdc->m_hDC, cRect.left, cRect.top, cRect.Width(), cRect.Height(), 0, 0, w, h, SRCCOPY);

	ReleaseDC(cdc);
	cim->Destroy();
	delete cim;
	cim = NULL;
}

BioRect* CZKCameraDemoDlg::GetBioRect(CustomBioData customBioData)
{
	BioRect *rect = NULL;
	int bioCnt = 0;

	vector<PBioData> bioDatas = customBioData.bioDatas;

	for(int i = 0; i < bioDatas.size(); i++)
	{
		if(1 == bioDatas[i]->hasTrack)
		{
			bioCnt++;
		}
	}
	if(0 == bioCnt || 0 == customBioData.width || 0 == customBioData.height)
	{
		return NULL;
	}
	rect = new BioRect[bioCnt];

	for(int i = 0; i < bioCnt; i++)
	{
		if(1 == bioDatas[i]->label && 1 == bioDatas[i]->hasTrack)
		{
			int left = bioDatas[i]->trackData.rect.left * gImageWidth / gCustomBioData.width;
			int top = bioDatas[i]->trackData.rect.top * gImageHeight / gCustomBioData.height;
			int right = bioDatas[i]->trackData.rect.right * gImageWidth / gCustomBioData.width;
			int bottom = bioDatas[i]->trackData.rect.bottom * gImageHeight / gCustomBioData.height;
			rect[i].point[0].x = left;
			rect[i].point[0].y = top;
			rect[i].point[1].x = right;
			rect[i].point[1].y = top;
			rect[i].point[2].x = right;
			rect[i].point[2].y = bottom;
			rect[i].point[3].x = left;
			rect[i].point[3].y = bottom;
		}
		else if(5 == bioDatas[i]->label && 1 == bioDatas[i]->hasTrack)
		{
			for(int j = 0; j < 4; j++)
			{
				rect[i].point[j].x = bioDatas[i]->palmInfo.points[j].x * gImageWidth / gCustomBioData.width;
				rect[i].point[j].y = bioDatas[i]->palmInfo.points[j].y * gImageWidth / gCustomBioData.width;
			}
		}

	}

	return rect;
}

DWORD WINAPI CZKCameraDemoDlg::ViewThread(LPVOID lpParam)
{
	cout << "view thread started" << endl;
	CZKCameraDemoDlg* dlg = (CZKCameraDemoDlg*)lpParam;
	wchar_t log[128] = {0};
	int count = 0, len = 0, w = 0, h = 0;
	int bgrSize = gImageWidth*gImageHeight*3;

	while(dlg->m_bViewRun)
	{
		Sleep(20);

		EnterCriticalSection(&videoLock);
		if(!bVideoData)
		{
			LeaveCriticalSection(&videoLock);
			continue;
		}
		bVideoData = false;
		if (gVideoData.data_length != gVideoData.ori_length)
		{
			wsprintf(log, L"error video data len %d %d %d\n", gVideoData.frame_index, gVideoData.data_length, gVideoData.ori_length);
			OutputDebugString(log);
			free(gVideoData.data);
			LeaveCriticalSection(&videoLock);
			continue;
		}
		int size = gVideoData.data_length;
		
		len = jpeg2bgr(gVideoData.data, size, dlg->bgr, &bgrSize, &w, &h);
		if(len != gImageWidth*gImageHeight*3)
		{
			wsprintf(log, _T("Decode jpeg len=%d, w=%d, h=%d\n"), len, w, h);
			OutputDebugString(log);
			free(gVideoData.data);
			LeaveCriticalSection(&videoLock);
			continue;
		}
		dlg->updateView(dlg->bgr, w, h);
		free(gVideoData.data);
		LeaveCriticalSection(&videoLock);
	}
	clearVideoDataQueue();
	cout << "view thread stoped" << endl;
	return 0;
}

DWORD WINAPI CZKCameraDemoDlg::NIRViewThread(LPVOID lpParam)
{
	cout << "view thread started" << endl;
	CZKCameraDemoDlg* dlg = (CZKCameraDemoDlg*)lpParam;
	wchar_t log[128] = {0};
	int count = 0, len = 0, w = 0, h = 0;
	int bgrSize = gImageWidth*gImageHeight*3;

	while(dlg->m_bViewRun)
	{
		Sleep(20);

		EnterCriticalSection(&nirVideoLock);
		if(!bNIRVideoData)
		{
			LeaveCriticalSection(&nirVideoLock);
			continue;
		}
		bNIRVideoData = false;
		if (gNIRVideoData.data_length != gNIRVideoData.ori_length)
		{
			wsprintf(log, L"error video data len %d %d %d\n", gNIRVideoData.frame_index, gNIRVideoData.data_length, gNIRVideoData.ori_length);
			OutputDebugString(log);
			ZKCamera_FreePointer(gNIRVideoData.data);
			LeaveCriticalSection(&nirVideoLock);
			continue;
		}
		int size = gNIRVideoData.data_length;
		
		len = jpeg2bgr(gNIRVideoData.data, size, dlg->nirImage, &bgrSize, &w, &h);
		if(len != gImageWidth*gImageHeight*3)
		{
			wsprintf(log, _T("Decode jpeg len=%d, w=%d, h=%d\n"), len, w, h);
			OutputDebugString(log);
			ZKCamera_FreePointer(gNIRVideoData.data);
			LeaveCriticalSection(&nirVideoLock);
			continue;
		}
		dlg->updateNIRView(dlg->nirImage, w, h);
		ZKCamera_FreePointer(gNIRVideoData.data);
		LeaveCriticalSection(&nirVideoLock);
	}
	cout << "view thread stoped" << endl;
	return 0;
}

DWORD WINAPI CZKCameraDemoDlg::MatchThread(LPVOID lpParam)
{
	cout << "match thread started" << endl;
	CZKCameraDemoDlg* dlg = (CZKCameraDemoDlg*)lpParam;
	char log[1024] = {0};
	float fScore = 0.0f;
	int nScore = 0.0f;
	float verTemplate[256] = {0};
	int ret = 0;
	int nTick = 0;
	char *json = (char *)malloc(40*1024);
	int len = 0;

	PMatchResult pMatchResult;
	bool bHasMatchResult = false;
	int label = 0;

	while (dlg->m_bMatchRun)
	{
		Sleep(20);

		if(gPollMatchResult)
		{
			if(!bHidOpen)
			{
				continue;
			}
			len = 40*1024;
			ret = ZKHID_PollMatchResult(hidHandle, json, &len);
			if(0 == ret)
			{
				vector<PBioData> bioDataList = parseMatchResult(json);
				if(bioDataList.size() > 0)
				{
					bHasMatchResult = true;
					pMatchResult = new MatchResult(*bioDataList[bioDataList.size()-1]->matchResultList[0]);
					label = bioDataList[bioDataList.size()-1]->label;

					clearCustomDataVector(bioDataList);
				}
			}
		}
		else if(bUvcOpen)
		{
			EnterCriticalSection(&customLock);
			if(customDataQueue.empty())
			{
				LeaveCriticalSection(&customLock);
				continue;
			}
			CustomBioData bioData = customDataQueue.front();
			customDataQueue.pop();

			if(0 == bioData.bioDatas.size())
			{
				LeaveCriticalSection(&customLock);
				continue;
			}
			if(0 == bioData.bioDatas[0]->matchResultList.size())
			{
				clearCustomDataVector(bioData.bioDatas);
				LeaveCriticalSection(&customLock);
				continue;
			}
			LeaveCriticalSection(&customLock);

			bHasMatchResult = true;
			pMatchResult = new MatchResult(*bioData.bioDatas[0]->matchResultList[0]);
			label = bioData.bioDatas[0]->label;

			clearCustomDataVector(bioData.bioDatas);
		}

		if(bHasMatchResult)
		{
			memset(log, 0, sizeof(log));

			if(!pMatchResult->userId.empty())
			{
				if(1 == label)
				{
					sprintf(log, "Identify face successfully, name: %s, score: %.2f", pMatchResult->userId.c_str(), pMatchResult->similarity);
				}
				else
				{
					sprintf(log, "Identify palm successfully, name: %s, score: %d", pMatchResult->userId.c_str(), (int)pMatchResult->similarity);
				}
			}
			else
			{
				if(1 == label)
				{
					sprintf(log, "Identify face failed, score: %.2f", pMatchResult->similarity);
				}
				else
				{
					sprintf(log, "Identify palm failed, score: %d", (int)pMatchResult->similarity);
				}
			}
			dlg->SetDlgItemText(IDC_STATIC_INFO, String2WString(log).c_str());

			delete pMatchResult;
			bHasMatchResult = false;
		}
	}
	clearCustomDataQueue();
	cout << "match thread stoped" << endl;
	return 0;
}

void CZKCameraDemoDlg::OnBnClickedBtnOpen()
{
	CComboBox *com = (CComboBox *)GetDlgItem(IDC_COMBO_RESOLUTION);

	if(bUvcOpen)
		return;
	ZKCamera_Init();

	int nCount = ZKCamera_GetDeviceCount();
	if(nCount < 2)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("No device found"));
		return;
	}
	int index = 0;
	int sel_w = -1, sel_h = -1, sel_fps = -1;
	CString str;
	com->GetWindowTextW(str);

	vector<std::wstring> s1 = split_wstring(str.GetBuffer(), L'*');
	if (s1.size() == 2){
		sel_w = stoi(s1[0].c_str());
		sel_h = stoi(s1[1].c_str());
		cout << "select resolution: " << sel_w << sel_h;
	}

	int ret = 0;

	int type = ZKCamera_GetDeviceType(0);

	((CComboBox *)GetDlgItem(IDC_COMBO_FPS))->GetWindowTextW(str);
	sel_fps = stoi(str.GetBuffer());

	if(1 == type)
	{
		ret = ZKCamera_OpenDevice(0, sel_w, sel_h, sel_fps, &vlHandle);
		ret = ZKCamera_OpenDevice(1, sel_w, sel_h, sel_fps, &nirHandle);
	}
	else
	{
		ret = ZKCamera_OpenDevice(0, sel_w, sel_h, sel_fps, &nirHandle);
		ret = ZKCamera_OpenDevice(1, sel_w, sel_h, sel_fps, &vlHandle);
	}

	if (ret < 0){
		SetDlgItemText(IDC_STATIC_INFO, _T("Open camera failed"));
	}
	else{

		ZKCamera_SetDataCallback(vlHandle, onGetVideoData, onGetCustomData, &vlParam);
		ZKCamera_SetDataCallback(nirHandle, onGetVideoData, NULL, &nirParam);
		SetDlgItemText(IDC_STATIC_INFO, _T("Camera opened"));
		bUvcOpen = true;
		gImageWidth = ZKCamera_GetCapWidth(vlHandle);
		gImageHeight = ZKCamera_GetCapHeight(vlHandle);

		bgr = (unsigned char *)malloc(gImageWidth*gImageHeight*3);
		nirImage = (unsigned char *)malloc(gImageWidth*gImageHeight*3);

		m_bViewRun = true;
		m_hViewHandle = CreateThread(NULL, 0,                      // use default stack size  
		ViewThread,       // thread function name
		this,          // argument to thread function 
		0,                      // use default creation flags 
		NULL);   // returns the thread identifier

		m_hNIRViewHandle = CreateThread(NULL, 0,                      // use default stack size  
		NIRViewThread,       // thread function name
		this,          // argument to thread function 
		0,                      // use default creation flags 
		NULL);   // returns the thread identifier
	}
}


void CZKCameraDemoDlg::OnBnClickedBtnClose()
{
	if (!bUvcOpen)
		return;

	ZKCamera_CloseDevice(nirHandle);
	ZKCamera_CloseDevice(vlHandle);
	ZKCamera_Terminate();
	nirHandle = NULL;
	vlHandle = NULL;
	m_bViewRun = false;
	KillThread(m_hViewHandle);
	KillThread(m_hNIRViewHandle);
	bUvcOpen = false;
	if(bgr)
	{
		free(bgr);
		bgr = NULL;
	}
	if(nirImage)
	{
		free(nirImage);
		nirImage = NULL;
	}
	clearCustomDataVector(gCustomBioData.bioDatas);
	SetDlgItemText(IDC_STATIC_INFO, _T("Camera closed"));
	((CStatic *)GetDlgItem(IDC_STATIC_IMAGE))->SetBitmap((HBITMAP)::LoadImage(AfxGetInstanceHandle(), MAKEINTRESOURCE(IDB_BITMAP_BG), IMAGE_BITMAP,0,0,LR_CREATEDIBSECTION));
	((CStatic *)GetDlgItem(IDC_STATIC_NIRIMAGE))->SetBitmap((HBITMAP)::LoadImage(AfxGetInstanceHandle(), MAKEINTRESOURCE(IDB_BITMAP_BG), IMAGE_BITMAP,0,0,LR_CREATEDIBSECTION));
}


void CZKCameraDemoDlg::OnClose()
{
	// TODO: Add your message handler code here and/or call default
	OnBnClickedBtnClose();
	m_bMatchRun = false;
	KillThread(m_hMatchHandle);
	OnBnClickedBtnCloseHid();
	DeleteCriticalSection(&videoLock);
	DeleteCriticalSection(&nirVideoLock);
	DeleteCriticalSection(&customLock);

	delete mStatusBar;

	CDialogEx::OnClose();
}


void CZKCameraDemoDlg::OnBnClickedBtnOpenHid()
{
	if(bHidOpen)
	{
		return;
	}

	int ret = 0, count = 0;
	ret = ZKHID_Init();
	if(0 != ret)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("ZKHID_Init failed"));
		return;
	}
	ZKHID_GetCount(&count);
	if(count <= 0)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("No device found"));
		return;
	}

	ret = ZKHID_Open(0, &hidHandle);
	if(0 == ret)
	{
		bHidOpen = true;
		if(!gUpgradeImage && !m_bPollHIDRun)
		{
			m_bPollHIDRun = true;
			m_hPollHIDHandle = CreateThread(NULL, 0,                      // use default stack size  
			PollHIDStatusThread,       // thread function name
			this,          // argument to thread function 
			0,                      // use default creation flags 
			NULL);   // returns the thread identifier
		}
	}
	else
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Open HID failed"));
		return;
	}
}


void CZKCameraDemoDlg::OnBnClickedBtnCloseHid()
{
	if(m_bPollHIDRun)
	{
		m_bPollHIDRun = false;
		KillThread(m_hPollHIDHandle);
	}
	if(bHidOpen)
	{
		if(m_bRegPalmRun)
		{
			OnBnClickedBtnLocalregpalm();
		}
		if(m_bRegFaceRun)
		{
			OnBnClickedBtnReg();
		}
		ZKHID_Close(hidHandle);
		ZKHID_Terminate();
		hidHandle = NULL;
		bHidOpen = false;
		GetDlgItem(IDC_CHECK_POLLMATCHRESULT)->EnableWindow(FALSE);
		SetDlgItemText(IDC_STATIC_INFO, _T("HID Closed"));
		SetDlgItemText(IDC_EDIT_USERCNT, _T(""));
		SetDlgItemText(IDC_EDIT_FACECNT, _T(""));
		SetDlgItemText(IDC_EDIT_PALMCNT, _T(""));

		EnableControl(false);
	}
}

void CZKCameraDemoDlg::OnBnClickedBtnReg()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	wchar_t log[128] = {0};
	CString str;
	GetDlgItemText(IDC_EDIT_USERID, str);
	if(str.IsEmpty())
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please input UserID"));
		return;
	}

	string userid = WString2String(str.GetBuffer());
	string json = getQueryUserJson((char *)userid.c_str(), true, true);
	int ret = 0;

	ret = ManageUser(GET_PERSON, (char *)json.c_str());
	if(0 != ret)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please Add User first"));
		return;
	}

	if(!m_bRegFaceRun)
	{
		m_bRegFaceRun = true;
		m_hRegFaceHandle = CreateThread(NULL, 0,                      // use default stack size  
		RegFaceThread,       // thread function name
		this,          // argument to thread function 
		0,                      // use default creation flags 
		NULL);   // returns the thread identifier
		SetDlgItemText(IDC_BTN_REG, _T("End"));
	}
	else
	{
		m_bRegFaceRun = false;
		KillThread(m_hRegFaceHandle);
		SetDlgItemText(IDC_BTN_REG, _T("Enroll Face"));
	}
}

void CZKCameraDemoDlg::OnBnClickedBtnDevicemanage()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}
	/*settingDlg.CenterWindow(GetDesktopWindow());
	settingDlg.ShowWindow(TRUE);*/
	RECT rect;
	int	xLeft, yTop;
	settingDlg.GetWindowRect(&rect);  
	xLeft = GetSystemMetrics(SM_CXFULLSCREEN)-(rect.right-rect.left);
	yTop = (GetSystemMetrics(SM_CYFULLSCREEN)-(rect.bottom-rect.top))/2;
	settingDlg.SetWindowPos(NULL, xLeft, yTop, -1, -1, SWP_NOSIZE | SWP_NOZORDER);
	settingDlg.SetWindowPos(NULL, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE);
	settingDlg.ShowWindow(TRUE);
}

HANDLE CZKCameraDemoDlg::GetHidHandle()
{
	return hidHandle;
}

bool CZKCameraDemoDlg::GetUSBStatus()
{
	return bReplugged;
}

void CZKCameraDemoDlg::ResetUSBStatus()
{
	bReplugged = 0;
}

void CZKCameraDemoDlg::SetFaceThreshold(float threshold)
{
	faceThreshold = threshold;
	WriteIniFloat(_T("Parameter"), _T("faceThreshold"), faceThreshold);
}

void CZKCameraDemoDlg::SetPalmThreshold(int threshold)
{
	palmThreshold = threshold;
	WriteIniInt(_T("Parameter"), _T("palmThreshold"), palmThreshold);
}

void CZKCameraDemoDlg::SetDeviceMode(bool bUpgradeImage)
{
	gUpgradeImage = bUpgradeImage;
}

void CZKCameraDemoDlg::OnBnClickedBtnSnapshot()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}
	wchar_t wc[128] = {0};
	int len = 2*1024*1024;
	char *buffer = (char *)malloc(len);
	int ret = 0;
	int nTick = GetTickCount();
	static int snapType = SNAPSHOT_NIR;
	ret = ZKHID_SnapShot(hidHandle, snapType++%2, buffer, &len);
	nTick = GetTickCount()-nTick;
	if(0 == ret)
	{
		SnapShot snapShot;
		ret = parseSnapshot(buffer, &snapShot);

		if(0 == ret)
		{
			if(0 == snapShot.status)
			{
				char timeStr[24] = {0};
				char fname[MAX_PATH];
				SYSTEMTIME stLocal;
				GetLocalTime(&stLocal);
				sprintf(timeStr, "%4d%02d%02d%02d%02d%02d%d", stLocal.wYear, stLocal.wMonth, stLocal.wDay, stLocal.wHour, stLocal.wMinute, stLocal.wSecond, stLocal.wMilliseconds);
				string image = base64_decode(snapShot.data);
				if(snapShot.type == "gray")
				{
					sprintf(fname, "%s.bmp", timeStr);
					WriteBitmap((unsigned char *)image.c_str(), snapShot.width, snapShot.height, fname);
				}
				else
				{
					sprintf(fname, "%s.jpg", timeStr);
					SaveToFile(fname, (void *)image.c_str(), image.size());
				}

				wsprintf(wc, _T("SnapShot successfully, time=%dms"), nTick);
				SetDlgItemText(IDC_STATIC_INFO, wc);
			}
			else
			{
				wsprintf(wc, _T("SnapShot failed, status=%d"), snapShot.status);
				SetDlgItemText(IDC_STATIC_INFO, wc);
			}
		}
		else
		{
			wsprintf(wc, _T("Parse SnapShot failed, ret=%d"), ret);
			SetDlgItemText(IDC_STATIC_INFO, wc);
		}
	}
	else
	{
		wsprintf(wc, _T("SnapShot failed, ret=%d"), ret);
		SetDlgItemText(IDC_STATIC_INFO, wc);
	}

	free(buffer);
}

void CZKCameraDemoDlg::OnBnClickedBtnClear()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	int ret = ManageUser(CLEAR_PERSON, NULL);
	if(0 == ret)
	{
		ManageUser(QUERY_STATISTICS, NULL);
	}
}

int CZKCameraDemoDlg::KillThread(HANDLE &thread)
{
	DWORD dwRet = 0;
	int flag = 0;
	MSG msg;
	while(TRUE)
	{
		if(NULL == thread)
		{
			break;
		}
		dwRet = WaitForSingleObject(thread, 500);
		switch(dwRet)
		{
		case WAIT_OBJECT_0:
		case WAIT_FAILED:
			flag = 1;
			break;
		case WAIT_TIMEOUT:
			PeekMessage(&msg, NULL, 0, 0, PM_NOREMOVE);
			continue;
		default:
			break; // unexpected failure
		}
		if(1 == flag)
		{
			break;
		}
	}

	if(thread)
	{
		CloseHandle(thread);
		thread = NULL;
	}

	return 0;
}

DWORD WINAPI CZKCameraDemoDlg::RegFaceThread(LPVOID lpParam)
{
	cout << "reg face thread started" << endl;
	CZKCameraDemoDlg* dlg = (CZKCameraDemoDlg*)lpParam;

	CString str;
	wchar_t log[128] = {0};
	dlg->GetDlgItemText(IDC_EDIT_USERID, str);
	string userid = WString2String(str.GetBuffer());
	int index = 0, size = 0, len = 0, ret = 0, nTick = 0, status = 0;
	string detail;

	len = 10*1024;
	char *result = (char *)malloc(len);

	ret = ZKHID_ManageModuleData(hidHandle, REG_START, NULL, result, &len);
		
	if(0 == ret)
	{
		ret = parseJson(result, &status, detail);
		if(0 != ret)
		{
			wsprintf(log, _T("Parse json failed, ret=%d"), ret);
			dlg->SetDlgItemText(IDC_STATIC_INFO, log);
			goto EXIT;
		}
		if(0 != status)
		{
			wsprintf(log, _T("REG_START failed, status=%d"), status);
			dlg->SetDlgItemText(IDC_STATIC_INFO, log);
			goto EXIT;
		}
	}
	else
	{
		wsprintf(log, _T("ZKHID_ManageModuleData failed, ret=%d"), ret);
		dlg->SetDlgItemText(IDC_STATIC_INFO, log);
		goto EXIT;
	}
	while (dlg->m_bRegFaceRun)
	{
		string json = getDetectFaceJson(NULL, 0, false, true, false);

		len = 10*1024;
		ret = ZKHID_ManageModuleData(hidHandle, DETECT_FACE_REG, (char *)json.c_str(), result, &len);
		if(0 == ret)
		{
			FaceDataList faceDataList;
			ret = parseRegFace(result, &faceDataList);
			if(0 == ret)
			{
				if(0 != faceDataList.status || faceDataList.list.size() > 1)
				{
					for(int i = 0; i < faceDataList.list.size(); i++)
					{
						json = getDelCacheJson(faceDataList.list[i]->cacheId.bioType, faceDataList.list[i]->cacheId.id);
						len = 10*1024;
						ZKHID_ManageModuleData(hidHandle, DEL_FACE_CACHEID, (char *)json.c_str(), result, &len);
						delete faceDataList.list[i];
					}
					if(faceDataList.list.size() > 1)
					{
						dlg->SetDlgItemText(IDC_STATIC_INFO, _T("Number of faces is greater than 1"));
					}
					else
					{
						dlg->SetDlgItemText(IDC_STATIC_INFO, _T("detect face failed"));
					}
					continue;
				}

				json = getAddFaceRegJson((char *)userid.c_str(), faceDataList.list[0]->cacheId.id);
				for(int i = 0; i < faceDataList.list.size(); i++)
				{
					delete faceDataList.list[i];
				}
				
				len = 10*1024;
				ret = ZKHID_ManageModuleData(hidHandle, ADD_FACE_REG, (char *)json.c_str(), result, &len);
				if(0 == ret)
				{
					ret = parseJson(result, &status, detail);
					if(0 == ret && 0 == status)
					{
						dlg->SetDlgItemText(IDC_STATIC_INFO, _T("Enroll face successfully"));

						dlg->ManageUser(QUERY_STATISTICS, NULL);
					}
					else
					{
						wsprintf(log, _T("Enroll face failed, ret=%d, status=%d, detail=%s"), ret, status, String2WString(detail).c_str());
						dlg->SetDlgItemText(IDC_STATIC_INFO, log);
					}
					break;
				}
				else
				{
					wsprintf(log, _T("ADD_FACE_REG failed, ret=%d"), ret);
					dlg->SetDlgItemText(IDC_STATIC_INFO, log);
					break;
				}
			}
			else
			{
				wsprintf(log, _T("parseRegFace failed, ret=%d"), ret);
				dlg->SetDlgItemText(IDC_STATIC_INFO, log);
			}
		}
		else
		{
			wsprintf(log, _T("DETECT_FACE_REG failed, ret=%d"), ret);
			dlg->SetDlgItemText(IDC_STATIC_INFO, log);
		}

		Sleep(10);	
	}
		

EXIT:

	len = 10*1024;
	ZKHID_ManageModuleData(hidHandle, REG_END, NULL, result, &len);

	free(result);
	if(dlg->m_bRegFaceRun)
	{
		dlg->m_bRegFaceRun = false;
		CloseHandle(dlg->m_hRegFaceHandle);
		dlg->m_hRegFaceHandle = NULL;
		dlg->SetDlgItemText(IDC_BTN_REG, _T("Enroll Face"));
	}
		
	cout << "reg face thread stoped" << endl;
	return 0;
}


DWORD WINAPI CZKCameraDemoDlg::RegPalmThread(LPVOID lpParam)
{
	cout << "reg palm thread started" << endl;
	CZKCameraDemoDlg* dlg = (CZKCameraDemoDlg*)lpParam;

	CString str;
	wchar_t log[128] = {0};
	dlg->GetDlgItemText(IDC_EDIT_USERID, str);
	string userid = WString2String(str.GetBuffer());
	int index = 0, size = 0, len = 0, ret = 0, nTick = 0, status = 0, cacheId[5] = {0};
	string detail;

	len = 20*1024;
	char *result = (char *)malloc(len);

	ret = ZKHID_ManageModuleData(hidHandle, REG_START, NULL, result, &len);
		
	if(0 == ret)
	{
		ret = parseJson(result, &status, detail);
		if(0 != ret)
		{
			wsprintf(log, _T("Parse json failed, ret=%d"), ret);
			dlg->SetDlgItemText(IDC_STATIC_INFO, log);
			goto EXIT;
		}
		if(0 != status)
		{
			wsprintf(log, _T("REG_START failed, status=%d"), status);
			dlg->SetDlgItemText(IDC_STATIC_INFO, log);
			goto EXIT;
		}
	}
	else
	{
		wsprintf(log, _T("ZKHID_ManageModuleData failed, ret=%d"), ret);
		dlg->SetDlgItemText(IDC_STATIC_INFO, log);
		goto EXIT;
	}
	while (dlg->m_bRegPalmRun)
	{
		string json = getDetectPalmJson(NULL, 0, 0, false, true, false);

		len = 20*1024;
		ret = ZKHID_ManageModuleData(hidHandle, DETECT_PALM_REG, (char *)json.c_str(), result, &len);
		if(0 == ret)
		{
			PalmDetectInfoList palmDetectInfoList;
			ret = parseDetectPalm(result, &palmDetectInfoList);
			if(0 == ret)
			{
				if(0 != palmDetectInfoList.status || palmDetectInfoList.list.size() > 1)
				{
					for(int i = 0; i < palmDetectInfoList.list.size(); i++)
					{
						json = getDelCacheJson(palmDetectInfoList.list[i]->cacheId.bioType, palmDetectInfoList.list[i]->cacheId.id);
						len = 20*1024;
						ZKHID_ManageModuleData(hidHandle, DEL_PALM_CACHEID, (char *)json.c_str(), result, &len);
						delete palmDetectInfoList.list[i];
					}
					if(palmDetectInfoList.list.size() > 1)
					{
						dlg->SetDlgItemText(IDC_STATIC_INFO, _T("Number of palms is greater than 1"));
					}
					else
					{
						dlg->SetDlgItemText(IDC_STATIC_INFO, _T("detect palm failed"));
					}
					continue;
				}
				cacheId[index++] = palmDetectInfoList.list[0]->cacheId.id;
				for(int i = 0; i < palmDetectInfoList.list.size(); i++)
				{
					delete palmDetectInfoList.list[i];
				}
				
				if(5 == index)
				{
					json = getPalmMergeRegJson(true, cacheId, 5);
					len = 20*1024;
					ret = ZKHID_ManageModuleData(hidHandle, MERGE_PALM_REG, (char *)json.c_str(), result, &len);
					if(0 == ret)
					{
						PalmRegInfo palmRegInfo;
						ret = parseRegPalm(result, &palmRegInfo);
						if(0 == ret)
						{
							if(0 != palmRegInfo.status)
							{
								dlg->SetDlgItemText(IDC_STATIC_INFO, _T("Merge templates failed"));
								goto EXIT;
							}
							json = getAddPalmRegJson((char *)userid.c_str(), palmRegInfo.cacheId.id);
							len = 20*1024;
							ret = ZKHID_ManageModuleData(hidHandle, ADD_PALM_REG, (char *)json.c_str(), result, &len);
							if(0 == ret)
							{
								ret = parseJson(result, &status, detail);
								if(0 == ret && 0 == status)
								{
									dlg->SetDlgItemText(IDC_STATIC_INFO, _T("Enroll palm successfully"));

									dlg->ManageUser(QUERY_STATISTICS, NULL);
								}
								else
								{
									wsprintf(log, _T("Enroll palm failed, ret=%d, status=%d, detail=%s"), ret, status, String2WString(detail).c_str());
									dlg->SetDlgItemText(IDC_STATIC_INFO, log);
								}
								break;
							}
							else
							{
								wsprintf(log, _T("ADD_PALM_REG failed, ret=%d"), ret);
								dlg->SetDlgItemText(IDC_STATIC_INFO, log);
								break;
							}
						}
						else
						{
							wsprintf(log, _T(" parse parseRegPalm failed, ret=%d"), ret);
							dlg->SetDlgItemText(IDC_STATIC_INFO, log);
						}
					}
					else
					{
						wsprintf(log, _T("parse MERGE_PALM_REG failed, ret=%d"), ret);
						dlg->SetDlgItemText(IDC_STATIC_INFO, log);
						break;
					}
				}
				else
				{
					wsprintf(log, _T("Left %d times"), 5-index);
					dlg->SetDlgItemText(IDC_STATIC_INFO, log);
				}
			}
			else
			{
				wsprintf(log, _T("parseDetectPalm failed, ret=%d"), ret);
				dlg->SetDlgItemText(IDC_STATIC_INFO, log);
			}
		}
		else
		{
			wsprintf(log, _T("DETECT_PALM_REG failed, ret=%d"), ret);
			dlg->SetDlgItemText(IDC_STATIC_INFO, log);
		}

		Sleep(10);	
	}
		

EXIT:

	len = 20*1024;
	ZKHID_ManageModuleData(hidHandle, REG_END, NULL, result, &len);

	free(result);
	if(dlg->m_bRegPalmRun)
	{
		dlg->m_bRegPalmRun = false;
		CloseHandle(dlg->m_hRegPalmHandle);
		dlg->m_hRegPalmHandle = NULL;
		dlg->SetDlgItemText(IDC_BTN_LOCALREGPALM, _T("Enroll Palm"));
	}
		
	cout << "reg palm thread stoped" << endl;
	return 0;
}

DWORD WINAPI CZKCameraDemoDlg::PollHIDStatusThread(LPVOID lpParam)
{
	CZKCameraDemoDlg* dlg = (CZKCameraDemoDlg*)lpParam;

	wchar_t wc[64] = {0};

	while(!gUpgradeImage && dlg->m_bPollHIDRun)
	{
		dlg->SetDlgItemText(IDC_STATIC_INFO, _T("Wait for HID to be ready"));
		char json[1024] = {0};
		int len = 1024;
		int ret = ZKHID_GetConfig(hidHandle, COMMON_CONFIG, json, &len);
		if(0 == ret)
		{
			int status = 0;
			string detail;
			ret = parseJson(json, &status, detail);
			if(0 == ret && 0 == status)
			{				
				dlg->ManageUser(QUERY_STATISTICS, NULL);
				dlg->EnableControl(true);
				dlg->SetDlgItemText(IDC_STATIC_INFO, _T("HID opened"));
				break;
			}
		}
		else
		{
			wsprintf(wc, L"ZKHID_GetConfig failed, ret=%d", ret);
			dlg->SetDlgItemText(IDC_STATIC_INFO, wc);
		}

		Sleep(500);
	}

	dlg->m_bPollHIDRun = false;
	CloseHandle(dlg->m_hPollHIDHandle);
	dlg->m_hPollHIDHandle = NULL;

	return 0;
}

void CZKCameraDemoDlg::OnBnClickedBtnLocalregpalm()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	wchar_t log[128] = {0};
	CString str;
	GetDlgItemText(IDC_EDIT_USERID, str);
	if(str.IsEmpty())
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please input UserID"));
		return;
	}

	string userid = WString2String(str.GetBuffer());
	string json = getQueryUserJson((char *)userid.c_str(), true, true);
	int ret = 0;

	ret = ManageUser(GET_PERSON, (char *)json.c_str());
	if(0 != ret)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please Add User first"));
		return;
	}

	if(!m_bRegPalmRun)
	{
		m_bRegPalmRun = true;
		m_hRegPalmHandle = CreateThread(NULL, 0,                      // use default stack size  
		RegPalmThread,       // thread function name
		this,          // argument to thread function 
		0,                      // use default creation flags 
		NULL);   // returns the thread identifier
		SetDlgItemText(IDC_BTN_LOCALREGPALM, _T("End"));
		SetDlgItemText(IDC_STATIC_INFO, _T("Please place your palm 5 times"));
	}
	else
	{
		m_bRegPalmRun = false;
		KillThread(m_hRegPalmHandle);
		SetDlgItemText(IDC_BTN_LOCALREGPALM, _T("Enroll Palm"));
	}
}

void CZKCameraDemoDlg::OnBnClickedBtnDeluser()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}
	CString str;
	GetDlgItemText(IDC_EDIT_USERID, str);
	if(str.IsEmpty())
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please input UserID"));
		return;
	}

	string userid = WString2String(str.GetBuffer());
	string json = getDeleteUserJson((char *)userid.c_str());

	int ret = ManageUser(DEL_PERSON, (char *)json.c_str());
	if(0 == ret)
	{
		ManageUser(QUERY_STATISTICS, NULL);
	}
}

BOOL CZKCameraDemoDlg::OnDeviceChange( UINT nEventType, DWORD_PTR dwData )
{
	UINT Event = nEventType;
	PDEV_BROADCAST_HDR pHDR = (PDEV_BROADCAST_HDR)dwData;
	PDEV_BROADCAST_DEVICEINTERFACE pBDI = (PDEV_BROADCAST_DEVICEINTERFACE)dwData;

	TRACE("nEventType = 0x%08X %s\n", nEventType, nEventType == DBT_DEVICEARRIVAL ? "DBT_DEVICEARRIVAL" : nEventType == DBT_DEVICEREMOVECOMPLETE ? "DBT_DEVICEREMOVECOMPLETE" : "unknow");

	switch(nEventType)
	{
		case DBT_DEVNODES_CHANGED:
			break;
		case DBT_DEVICEARRIVAL:
			{
				switch(pHDR->dbch_devicetype)
				{
				case DBT_DEVTYP_DEVICEINTERFACE:
					{
						wstring str = _wcsupr(pBDI->dbcc_name);
						if(find_wstring(str, _T("VID_1B55&PID_0504")) || find_wstring(str, _T("VID_1B55&PID_0505")) || find_wstring(str, _T("VID_1B55&PID_0103"))
							|| find_wstring(str, _T("VID_1D6B&PID_0102")) || find_wstring(str, _T("VID_1D6B&PID_0103")))
						{
							::PostMessage(GetSafeHwnd(), WM_DEVICEATTACH, 1, 0);
						}
					}			
					break;
				default:
					break;
				}
			}	
			break;
		case DBT_DEVICEREMOVECOMPLETE:
			{
				switch(pHDR->dbch_devicetype)
				{
				case DBT_DEVTYP_DEVICEINTERFACE:
					{
						wstring str = _wcsupr(pBDI->dbcc_name);
						if(find_wstring(str, _T("VID_1B55&PID_0504")) || find_wstring(str, _T("VID_1B55&PID_0505")) || find_wstring(str, _T("VID_1B55&PID_0103"))
							|| find_wstring(str, _T("VID_1D6B&PID_0102")) || find_wstring(str, _T("VID_1D6B&PID_0103")))
						{
							::PostMessage(GetSafeHwnd(), WM_DEVICEATTACH, 0, 0);
						}
					}
					break;
				default:
					break;
				}
			}
			break;
		default:
			break;
	}

	return true;
}

LRESULT CZKCameraDemoDlg::OnDeviceAttach(WPARAM wParam,LPARAM lParam)
{
	char timeStr[24] = {0};
	char log[128] = {0};
	getCurrentTime(timeStr);
	if(0 == wParam)
	{
		sprintf(log, "%s DEVICE REMOVE\n", timeStr);
		AppendToFile("usb.log", log, strlen(log));
		if(bHidOpen)
		{
			OnBnClickedBtnCloseHid();
			gUSBDetached = 1;
		}
		if(bUvcOpen)
		{
			OnBnClickedBtnClose();
		}
	}
	else
	{
		sprintf(log, "%s DEVICE ARRIVAL\n", timeStr);
		AppendToFile("usb.log", log, strlen(log));

		if(1 == gUSBDetached)
		{
			gUSBDetached = 0;
			bReplugged = 1;
		}

		int nTick = GetTickCount();
		while(!bHidOpen && (GetTickCount()-nTick) < 5000)
		{
			OnBnClickedBtnOpenHid();
			Sleep(100);
		}
		nTick = GetTickCount();
		while(!bUvcOpen && (GetTickCount()-nTick) < 1000)
		{
			OnBnClickedBtnOpen();
			Sleep(100);
		}
	}
	return 0;
}

void CZKCameraDemoDlg::OnBnClickedBtnAdduser()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}
	CString str;
	GetDlgItemText(IDC_EDIT_USERID, str);
	if(str.IsEmpty())
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please input UserID"));
		return;
	}

	string userid = WString2String(str.GetBuffer());
	string json = getAddUserJson((char *)userid.c_str(), (char *)userid.c_str());
	
	int ret = ManageUser(ADD_PERSON, (char *)json.c_str());
	if(0 == ret)
	{
		ManageUser(QUERY_STATISTICS, NULL);
	}
}


void CZKCameraDemoDlg::OnBnClickedBtnGetalluser()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	string json = getQueryAllUserJson();
	
	ManageUser(QUERY_ALL_PERSON, (char *)json.c_str());
}

int CZKCameraDemoDlg::ManageUser(int manageType, char *json)
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return -1;
	}

	wchar_t log[128] = {0};
	int len = 1024, ret = 0;

	if(QUERY_ALL_PERSON == manageType || GET_PERSON == manageType || EXPORT_ATT_RECORD == manageType)
	{
		len = 2*1024*1024;
	}
	char *result = (char *)malloc(len);
	ret = ZKHID_ManageModuleData(hidHandle, manageType, json, result, &len);
	if(0 == ret)
	{
		int status = 0;
		string detail;
		ret = parseJson(result, &status, detail);
		if(0 == ret)
		{
			switch(manageType)
			{
			case ADD_PERSON:
				if(0 == status)
				{
					wsprintf(log, _T("Add User successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Add User failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case DEL_PERSON:
				if(0 == status)
				{
					wsprintf(log, _T("Delete User successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Delete User failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case GET_PERSON:
				if(0 == status)
				{
					SaveToFile("GET_PERSON.json", result, len);
					wsprintf(log, _T("Get User successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Get User failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case CLEAR_PERSON:
				if(0 == status)
				{
					wsprintf(log, _T("Clear User successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Clear User failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case QUERY_ALL_PERSON:
				if(0 == status)
				{
					SaveToFile("QUERY_ALL_PERSON.json", result, len);
					wsprintf(log, _T("Get All User successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Get All failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case QUERY_STATISTICS:
				if(0 == status)
				{
					//wsprintf(log, _T("Query Statistics successfully"));
					Statistics statistics;
					ret = parseQueryStatistics(result, &statistics);
					if(0 == ret)
					{
						if(0 == statistics.status)
						{
							SetDlgItemInt(IDC_EDIT_USERCNT, statistics.personCount);
							SetDlgItemInt(IDC_EDIT_FACECNT, statistics.faceCount);
							SetDlgItemInt(IDC_EDIT_PALMCNT, statistics.palmCount);
						}
					}
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Query Statistics failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
					SetDlgItemText(IDC_STATIC_INFO, log);
				}
				break;
			case ADD_FACE:
				if(0 == status)
				{
					wsprintf(log, _T("Enroll Face successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Enroll Face failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case EXPORT_ATT_RECORD:
				if(0 == status)
				{
					SaveToFile("ATT_RECORD.json", result, len);
					wsprintf(log, _T("Get att record successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Get att record, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			case CLEAR_ATT_RECORD:
				if(0 == status)
				{
					wsprintf(log, _T("Clear att record successfully"));
				}
				else
				{
					ret = -100;
					wsprintf(log, _T("Clear att record failed, status=%d, detail=%s"), status, String2WString(detail).c_str());
				}
				SetDlgItemText(IDC_STATIC_INFO, log);
				break;
			}
		}
		else
		{
			wsprintf(log, _T("parseJson failed, ret=%d"), ret);
			SetDlgItemText(IDC_STATIC_INFO, log);
		}
	}
	else
	{
		wsprintf(log, _T("ZKHID_ManageModuleData failed, ret=%d"), ret);
		SetDlgItemText(IDC_STATIC_INFO, log);
	}
	free(result);
	return ret;
}

void CZKCameraDemoDlg::OnBnClickedBtnRegfromfile()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	CString str;
	GetDlgItemText(IDC_EDIT_USERID, str);
	if(str.IsEmpty())
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please input UserID"));
		return;
	}

	string userid = WString2String(str.GetBuffer());
	string json = getQueryUserJson((char *)userid.c_str(), true, true);
	int ret = 0;

	ret = ManageUser(GET_PERSON, (char *)json.c_str());
	if(0 != ret)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please Add User first"));
		return;
	}

	CFileDialog fileDlg(TRUE, L"", NULL, OFN_HIDEREADONLY | OFN_OVERWRITEPROMPT, L"img(*.jpg)|*.jpg||"); 
	if(fileDlg.DoModal() == IDOK)
	{
		int size = 0;
		unsigned char *image = NULL;
		CImage srcImage;
		ret = srcImage.Load(fileDlg.GetPathName().GetBuffer());
		if(0 != ret)
		{
			SetDlgItemText(IDC_STATIC_INFO, _T("Load file failed"));
			return;
		}
		
		if(srcImage.GetWidth() > 720 || srcImage.GetHeight() > 1280)
		{
			CImage dstImage;
			float scaleWidth = (float)srcImage.GetWidth() / 720;
			float scaleHeight = (float)srcImage.GetHeight() / 1280;
			float coef = scaleWidth > scaleHeight ? scaleWidth : scaleHeight;

			CreateStretchImage(&srcImage, &dstImage, srcImage.GetWidth()/coef, srcImage.GetHeight()/coef);
			if(dstImage.IsNull())
			{
				srcImage.Destroy();
				SetDlgItemText(IDC_STATIC_INFO, _T("Stretch image failed"));
				return;
			}

			bool bret = save_img(dstImage, NULL, &size);
			if(!bret)
			{
				srcImage.Destroy();
				dstImage.Destroy();

				SetDlgItemText(IDC_STATIC_INFO, _T("Get JPEG stream failed"));
				return;
			}
			image = (unsigned char *)malloc(size);
			bret = save_img(dstImage, image, &size);
			dstImage.Destroy();
			if(!bret)
			{
				srcImage.Destroy();
				free(image);
				image = NULL;
				SetDlgItemText(IDC_STATIC_INFO, _T("Get JPEG stream failed"));
				return;
			}
		}
		else
		{
			image = LoadFile(WString2String(fileDlg.GetPathName().GetBuffer()).c_str(), &size);
		}
		srcImage.Destroy();
		if(image)
		{
			string json = getAddFaceJson((char *)userid.c_str(), image, size);

			ret = ManageUser(ADD_FACE, (char *)json.c_str());
			if(0 == ret)
			{
				ManageUser(QUERY_STATISTICS, NULL);
			}

			free(image);
			image = NULL;
		}
	}
}

void CZKCameraDemoDlg::OnBnClickedBtnGetuser()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}
	CString str;
	GetDlgItemText(IDC_EDIT_USERID, str);
	if(str.IsEmpty())
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please input UserID"));
		return;
	}

	string userid = WString2String(str.GetBuffer());
	string json = getQueryUserJson((char *)userid.c_str(), true, true);

	ManageUser(GET_PERSON, (char *)json.c_str());
}


void CZKCameraDemoDlg::OnSize(UINT nType, int cx, int cy)
{
	CDialogEx::OnSize(nType, cx, cy);

	if(IsWindowVisible())
	{
		CRect rect;

		GetClientRect(&rect);
		mStatusBar->MoveWindow(rect.left, rect.top, rect.Width(), rect.Height(), true);
	}
}


void CZKCameraDemoDlg::OnTimer(UINT_PTR nIDEvent)
{
	// TODO: Add your message handler code here and/or call default
	switch(nIDEvent)
	{
	case 1:
		{
			CString str;

			str.Format(TEXT("VL: %dfps NIR: %dfps"), gVLFrames, gNIRFrames);
			mStatusBar->SetText(str, 0, 0);

			gVLFrames = 0;
			gNIRFrames = 0;
		}
		break;
	}

	CDialogEx::OnTimer(nIDEvent);
}


void CZKCameraDemoDlg::OnBnClickedCheckPollmatchresult()
{
	// TODO: Add your control notification handler code here
	gPollMatchResult = BST_UNCHECKED == IsDlgButtonChecked(IDC_CHECK_POLLMATCHRESULT) ? false : true;
}


void CZKCameraDemoDlg::OnBnClickedBtnClearAttRecord()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	ManageUser(CLEAR_ATT_RECORD, NULL);
}


void CZKCameraDemoDlg::OnBnClickedBtnGetAttRecord()
{
	if(!bHidOpen)
	{
		SetDlgItemText(IDC_STATIC_INFO, _T("Please open HID first"));
		return;
	}

	wchar_t wc[64] = {0};
	int len = 1024;
	char *result = (char *)malloc(len);
	string json = getAttRecordCountJson();
	int ret = ZKHID_ManageModuleData(hidHandle, ATT_RECORD_COUNT, (char *)json.c_str(), result, &len);
	if(0 == ret)
	{
		AttRecordCount attRecCount;
		ret = parseAttRecordCount(result, &attRecCount);
		if(0 == ret)
		{
			if(attRecCount.totalCount > 0)
			{
				json = getAttRecordJson(1, 20, true);
				ManageUser(EXPORT_ATT_RECORD, (char *)json.c_str());
				wsprintf(wc, _T("Attendance record count=%d"), attRecCount.totalCount);
				SetDlgItemText(IDC_STATIC_INFO, wc);
			}
			else
			{
				SetDlgItemText(IDC_STATIC_INFO, _T("No att record"));
			}
		}
		else
		{
			SetDlgItemText(IDC_STATIC_INFO, _T("Parse att record count failed"));
		}
	}
	free(result);
}

void CZKCameraDemoDlg::EnableControl(bool bEnable)
{
	GetDlgItem(IDC_BTN_ADDUSER)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_GETUSER)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_GETALLUSER)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_DELUSER)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_CLEAR)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_REGFROMFILE)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_REG)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_LOCALREGPALM)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_GET_ATT_RECORD)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_CLEAR_ATT_RECORD)->EnableWindow(bEnable);
	GetDlgItem(IDC_BTN_SNAPSHOT)->EnableWindow(bEnable);
	//GetDlgItem(IDC_BTN_DEVICEMANAGE)->EnableWindow(bEnable);
	GetDlgItem(IDC_CHECK_POLLMATCHRESULT)->EnableWindow(bEnable);
}