using System;
using System.Collections.Generic;
using System.Text;

namespace ZKBioModuleDemo
{    public struct Landmark
    {
        public int count;               //landmark数量
        public string data;             //landmark坐标
    };

    public struct FacePose
    {
        public float yaw;
        public float pitch;
        public float roll;
    };

    public struct RECT
    {
        public long left;
        public long top;
        public long right;
        public long bottom;
    };

    public struct POINT
    {
        public long x;
        public long y;
    };

    public struct TrackData
    {
        public int trackId;           //人脸跟踪id
        public float blur;            //模糊度
        public Landmark landmark;     //关键点
        public FacePose pose;         //人脸角度
        public RECT rect;             //人脸框
        public string snap_type;      //抓拍类型，"enter", "leave", "single", "timing"
    };

    public struct LiveData
    {
        public float livenessScore;             //活体分数
        public int liveness;                    //活体状态值
        public int livenessMode;                //活体模式,"ir","rgb"
        public long irFrameId;                  //红外帧索引
        public float quality;                   //质量
    };

    public struct Attribute
    {
        public int age;             //年龄
        public int beauty;          //颜值
        public int cap;             //帽子
        public int expression;      //表情
        public int eye;             //闭眼
        public int gender;          //性别,[1,男][2，女]
        public int glasses;         //眼镜
        public int mouth;           //张嘴
        public int mustache;        //是否有胡子
        public int respirator;      //口罩
        public int skinColor;       //肤色
        public int smile;           //微笑
    };

    public struct FaceFeature
    {
        public string verTemplate;
        public int size;
    };

    public struct PalmInfo
    {
        public POINT[] points;
        public int imageQuality;
        public int templateQuality;
    };

    public struct PalmFeature
    {
        public string verTemplate;
        public string preRegTemplate;
        public int verTemplateSize;
        public int preRegTemplateSize;
    };

    public struct MatchResult
    {
        public string groupId;
        public string name;
        public string personId;
        public string userId;
        public float similarity;
    };

    public struct BioData
    {
        //是否包含特征向量 0:n 1:y
        public int hasFeature;
        //是否包含属性 0:n 1:y
        public int hasAttr;
        //是否包含活体和score 0:n 1:y
        public int hasLiveScore;
        //是否包含附加的track2数据
        public int hasTrack;
        //数据标签，指示是人脸或人体等
        public int hasPalmFeature;
        public int label;

        //相机私有数据
        public TrackData trackData;
        public FaceFeature faceFeature;
        public LiveData liveness;
        public Attribute attribute;
        public List<MatchResult> matchResultList;
        public PalmInfo palmInfo;
        public PalmFeature palmFeature;
    };

    public struct CustomBioData
    {
        //对应图像帧号
        public UInt64 frame_index;
        //对应图像size
        public int width;
        public int height;
        public List<BioData> bioDatas;
    };

    public struct BioRect
    {
        public POINT[] point;
    };

    public struct FaceInfo
    {
        public Attribute attribute;
        public FacePose pose;
        public RECT rect;
        public Landmark landmark;
        public float score;
    };

    public struct BioFeature
    {
        public string bioType;
        public string data;
        public int size;
    };

    public struct BioPicture
    {
        public string bioType;
        public string data;
        public string format;
        public int width;
        public int height;
    };

    public struct CacheId
    {
        public string bioType;
        public int id;
    };

    public struct FaceData
    {
        public FaceInfo faceInfo;
        public BioFeature bioFeature;
        public BioPicture bioPicture;
        public CacheId cacheId;
    };

    public struct FaceDataList
    {
        public int status;
        public string detail;
        public List<FaceData> list;
    };

    public struct PalmDetectInfo
    {
        public PalmInfo palmInfo;
        public PalmFeature palmFeature;
        public BioPicture bioPicture;
        public CacheId cacheId;
    };

    public struct PalmDetectInfoList
    {
        public int status;
        public string detail;
        public List<PalmDetectInfo> list;
    };

    public struct PalmRegInfo
    {
        public int status;
        public string detail;
        public string mergeTemplate;
        public int mergeTemplateSize;
        public CacheId cacheId;
    };

    public struct SnapShot
    {
        public int status;
        public string detail;
        public string type;
        public string data;
        public int width;
        public int height;
        public int frameId;
        public int timeStamp;
    };

    public struct Statistics
    {
        public int status;
        public string detail;
        public int databaseSize;
        public int faceCount;
        public int featureCount;
        public int featureSize;
        public int groupCount;
        public int palmCount;
        public int palmFeatureCount;
        public int palmFeatureSize;
        public int personCount;
        public int pictureCount;
        public int pictureSize;
    };

    public struct AttRecordCount
    {
        public int status;
        public string detail;
        public int totalCount;
        public int startId;
    };
}
