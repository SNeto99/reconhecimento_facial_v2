#ifdef WIN32
#include "stdafx.h"
#endif
#include<iostream>
#include <vector>
#include <sstream>
#include <string>
#include <iostream>
#include <queue>
#include <map>

using namespace std;

//人脸关键点(暂时未启用)
struct Landmark{
    int count;               //landmark数量
    string data;			 //landmark坐标

	Landmark()
	{
		count = 0;
		data = "";
	}
};

//人脸角度
struct FacePose {
    float yaw;
    float pitch;
    float roll;

	FacePose()
	{
		yaw = 0;
		pitch = 0;
		roll = 0;
	}
};

#ifndef WIN32
struct RECT
{
    long    left;
    long    top;
    long    right;
    long    bottom;
};
struct POINT
{
    long  x;
    long  y;
};
#endif

struct TrackData{
	int trackId;           //人脸跟踪id
	float blur;            //模糊度
    Landmark landmark;     //关键点
    FacePose pose;         //人脸角度
    RECT rect;             //人脸框
    string snap_type;      //抓拍类型，"enter", "leave", "single", "timing"

	TrackData()
	{
		trackId = 0;
		blur = 0;
		snap_type = "";
	}
};

//质量分与活体数据
struct LiveData {
    float livenessScore;             //活体分数
    int liveness;                    //活体状态值
    int livenessMode;                //活体模式,"ir","rgb"
    long irFrameId;                  //红外帧索引
    float quality;                   //质量

	LiveData()
	{
		livenessScore = 0.0;
		liveness = 0;
		livenessMode = 0;
		irFrameId = 0;
		quality = 0.0;
	}
};

//人脸属性
struct Attribute {
    int age;             //年龄
    int beauty;          //颜值
    int cap;             //帽子
    int expression;      //表情
    int eye;             //闭眼
    int gender;          //性别,[1,男][2，女]
    int glasses;         //眼镜
    int mouth;           //张嘴
    int mustache;        //是否有胡子
    int respirator;      //口罩
    int skinColor;       //肤色
    int smile;           //微笑

	Attribute()
	{
		this->age = 0;
		this->beauty = 0;
		this->cap = 0;
		this->expression = 0;
		this->eye = 0;
		this->gender = 0;
		this->glasses = 0;
		this->mouth = 0;
		this->mustache = 0;
		this->respirator = 0;
		this->skinColor = 0;
		this->smile = 0;
	}
};

struct FaceFeature {
    string verTemplate;
    int size;

	FaceFeature()
	{
		size = 0;
		verTemplate = "";
	}
};

struct PalmInfo 
{
	POINT points[4];
	int imageQuality;
	int templateQuality;

	PalmInfo()
	{
		imageQuality = 0;
		templateQuality = 0;
	}
};

struct PalmFeature {
    string verTemplate;
	string preRegTemplate;
    int verTemplateSize;
	int preRegTemplateSize;

	PalmFeature()
	{
		verTemplateSize = 0;
		preRegTemplateSize = 0;
		verTemplate = "";
		preRegTemplate = "";
	}
};

typedef struct MatchResult
{
	string groupId;
	string name;
	string personId;
	string userId;
	float similarity;

	MatchResult()
	{
		this->groupId = "";
		this->name = "";
		this->personId = "";
		this->userId = "";
		this->similarity = 0;
	}

	MatchResult(MatchResult &matchResult)
	{
		this->groupId = matchResult.groupId;
		this->name = matchResult.name;
		this->personId = matchResult.personId;
		this->userId = matchResult.userId;
		this->similarity = matchResult.similarity;
	}
}*PMatchResult;

typedef struct BioData{
	//是否包含特征向量 0:n 1:y
	int hasFeature;
	//是否包含属性 0:n 1:y
	int hasAttr;
	//是否包含活体和score 0:n 1:y
	int hasLiveScore;
	//是否包含附加的track2数据
	int hasTrack;
	//数据标签，指示是人脸或人体等
	int hasPalmFeature;
	int label;

	//相机私有数据
    TrackData trackData;
    FaceFeature faceFeature;
    LiveData liveness;
    Attribute attribute;
	std::vector<PMatchResult> matchResultList;

	PalmInfo palmInfo;
	PalmFeature palmFeature;

	BioData()
	{
		hasFeature = 0;
		hasAttr = 0;
		hasLiveScore = 0;
		hasTrack = 0;
		hasPalmFeature = 0;
		label = 0;
	}
	BioData(BioData& bioData)
	{
		hasFeature = bioData.hasFeature;
		hasAttr = bioData.hasAttr;
		hasLiveScore = bioData.hasLiveScore;
		hasTrack = bioData.hasTrack;
		hasPalmFeature = bioData.hasPalmFeature;
		label = bioData.label;

		trackData = bioData.trackData;
		faceFeature = bioData.faceFeature;
		liveness = bioData.liveness;
		attribute = bioData.attribute;

		palmInfo = bioData.palmInfo;
		palmFeature = bioData.palmFeature;

		for(int i = 0; i < bioData.matchResultList.size(); i++)
		{
			PMatchResult pMatchResult = new MatchResult(*bioData.matchResultList[i]);
			matchResultList.push_back(pMatchResult);
		}
	}
}*PBioData;

struct CustomBioData{
	//对应图像帧号
	long long frame_index;
	//对应图像size
	int width;
	int height;

	std::vector<PBioData> bioDatas;
};

typedef struct BioRect
{
	POINT point[4];
} BioRect;

struct FaceInfo
{
	 Attribute attribute;
	 FacePose pose;
	 RECT rect;
	 Landmark landmark;
	 float score;

	 FaceInfo()
	 {
		 score = 0.0;
	 }
};

struct BioFeature
{
	string bioType;
	string data;
	int size;

	BioFeature()
	{
		bioType = "";
		data = "";
		size = 0;
	}
};

struct BioPicture
{
	string bioType;
	string data;
	string format;
	int width;
	int height;

	BioPicture()
	{
		bioType = "";
		data = "";
		format = "";
		width = 0;
		height = 0;
	}
};

struct CacheId
{
	string bioType;
	int id;

	CacheId()
	{
		bioType = "";
		id = 0;
	}
};

typedef struct FaceData
{
	FaceInfo faceInfo;
	BioFeature bioFeature;
	BioPicture bioPicture;
	CacheId cacheId;
}*PFaceData;

typedef struct FaceDataList
{
	int status;
	string detail;
	vector<PFaceData> list;

	FaceDataList()
	{
		status = 0;
		detail = "";
	}
}*PFaceDataList;

typedef struct PalmDetectInfo
{
	PalmInfo palmInfo;
	PalmFeature palmFeature;
	BioPicture bioPicture;
	CacheId cacheId;
}*PPalmDetectInfo;

typedef struct PalmDetectInfoList
{
	int status;
	string detail;
	
	vector<PPalmDetectInfo> list;
}*PPalmDetectInfoList;

typedef struct PalmRegInfo
{
	int status;
	string detail;
	string mergeTemplate;
	int mergeTemplateSize;
	CacheId cacheId;

	PalmRegInfo()
	{
		status = 0;
		detail = "";
		mergeTemplate = "";
		mergeTemplateSize = 0;
	}
}*PPalmRegInfo;

typedef struct SnapShot
{
	int status;
	string detail;
	string type;
	string data;
	int width;
	int height;
	int frameId;
	int timeStamp;

	SnapShot()
	{
		status = 0;
		detail = "";
		type = "";
		data = "";
		width = 0;
		height = 0;
		frameId = 0;
		timeStamp = 0;
	}
}*PSnapShot;

typedef struct Statistics
{
	int status;
	string detail;
	int databaseSize;
	int faceCount;
	int featureCount;
	int featureSize;
	int groupCount;
	int palmCount;
	int palmFeatureCount;
	int palmFeatureSize;
	int personCount;
	int pictureCount;
	int pictureSize;

	Statistics()
	{
		status = 0;
		detail = "";
		databaseSize = 0;
		faceCount = 0;
		featureCount = 0;
		featureSize = 0;
		groupCount = 0;
		palmCount = 0;
		palmFeatureCount = 0;
		palmFeatureSize = 0;
		personCount = 0;
		pictureCount = 0;
		pictureSize = 0;
	}
}*PStatistics;

typedef struct AttRecordCount
{
	int status;
	string detail;
	int totalCount;
	int startId;

	AttRecordCount()
	{
		status = 0;
		detail = "";
		totalCount = 0;
		startId = 0;
	}
}*PAttRecordCount;

void clearCustomDataVector(vector<PBioData> &bioDatas);
vector<PBioData> parse_customData(char *json);
vector<PBioData> parseMatchResult(char *json);
string getDetectFaceJson(unsigned char *jpeg, int len, bool feature, bool faceInfo, bool picture);
string getDetectPalmJson(unsigned char *raw, int width, int height, bool feature, bool palmInfo, bool picture);
string getPalmMergeRegJson(bool feature, int *cacheId, int count);
int parseRegFace(char *json, PFaceDataList pFaceDataList);
int parseDetectPalm(char *json, PPalmDetectInfoList pPalmDetectInfoList);
int parseRegPalm(char *json, PPalmRegInfo pPalmRegInfo);
int parseSnapshot(char *json, PSnapShot pSnapShot);
int parseQueryStatistics(char *json, PStatistics pStatistics);
string getAddUserJson(char *userid, char *name);
string getQueryAllUserJson();
int parseJson(char *json, int *status, string &detail);
string getDeleteUserJson(char *userid);
string getAddFaceJson(char *userid, unsigned char *jpeg, int size);
string getAddFaceRegJson(char *userid, int cacheId);
string getAddPalmRegJson(char *userid, int cacheId);
string getDelCacheJson(string bioType, int cacheId);
string getQueryUserJson(char *userid, bool feature, bool picture);
string getSyncTimeJson(char *stime);
int parseDeviceTime(char *json, int *status, string &detail, string &sysTime);
string getAttRecordCountJson();
int parseAttRecordCount(char *json, PAttRecordCount pAttRecordCount);
string getAttRecordJson(int startId, int count, bool attPhoto);