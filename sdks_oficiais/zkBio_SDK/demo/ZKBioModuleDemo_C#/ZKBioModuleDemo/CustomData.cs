using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using System;
using System.Collections.Generic;
using System.Text;

namespace ZKBioModuleDemo
{
    public class CustomDataParse
    {
        public static List<BioData> parse_customData(String json)
        {
            List<BioData> bioDataList = new List<BioData>();
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return null;
            }
            if (!jObject.ContainsKey("label"))
            {
                return null;
            }
            int nLabel = int.Parse(jObject["label"].ToString());
            if (1 == nLabel)
            {
                if (jObject.ContainsKey("face"))
                {
                    JArray faceArray = (JArray)jObject["face"];
                    bool isFirstFace = true;
                    for(int i=0;i<faceArray.Count;i++)
                    {
                        if (null == faceArray[i] || ! faceArray[i].HasValues)
                        {
                            continue;
                        }
                        JObject tracker = (JObject)faceArray[i]["tracker"];
                        BioData tmpBioData = new BioData();
                        tmpBioData.hasTrack = 1;
                        tmpBioData.label = nLabel;
                        tmpBioData.trackData = new TrackData();
                        tmpBioData.trackData.trackId = int.Parse(tracker["trackId"].ToString());
                        tmpBioData.trackData.blur = float.Parse(tracker["blur"].ToString());
                        tmpBioData.trackData.snap_type = tracker["snapType"].ToString();
                        tmpBioData.trackData.pose = new FacePose();
                        tmpBioData.trackData.pose.yaw = float.Parse(tracker["pose"]["yaw"].ToString());
                        tmpBioData.trackData.pose.pitch = float.Parse(tracker["pose"]["pitch"].ToString());
                        tmpBioData.trackData.pose.roll = float.Parse(tracker["pose"]["roll"].ToString());
                        tmpBioData.trackData.rect = new RECT();
                        tmpBioData.trackData.rect.left = int.Parse(tracker["rect"]["left"].ToString());
                        tmpBioData.trackData.rect.top = int.Parse(tracker["rect"]["top"].ToString());
                        tmpBioData.trackData.rect.right = int.Parse(tracker["rect"]["right"].ToString());
                        tmpBioData.trackData.rect.bottom = int.Parse(tracker["rect"]["bottom"].ToString());
                        tmpBioData.trackData.landmark = new Landmark();
                        tmpBioData.trackData.landmark.count = int.Parse(tracker["landmark"]["count"].ToString());
                        tmpBioData.trackData.landmark.data = tracker["landmark"]["data"].ToString();
                        if (isFirstFace)
                        {
                            JObject firstFace = (JObject)faceArray[i];
                            if (firstFace.ContainsKey("attribute"))
                            {
                                tmpBioData.hasAttr = 1;
                                tmpBioData.attribute = new Attribute();
                                tmpBioData.attribute.age = int.Parse(firstFace["attribute"]["age"].ToString());
                                tmpBioData.attribute.beauty = int.Parse(firstFace["attribute"]["beauty"].ToString());
                                tmpBioData.attribute.cap = int.Parse(firstFace["attribute"]["cap"].ToString());
                                tmpBioData.attribute.expression = int.Parse(firstFace["attribute"]["expression"].ToString());
                                tmpBioData.attribute.eye = int.Parse(firstFace["attribute"]["eye"].ToString());
                                tmpBioData.attribute.gender = int.Parse(firstFace["attribute"]["gender"].ToString());
                                tmpBioData.attribute.glasses = int.Parse(firstFace["attribute"]["glasses"].ToString());
                                tmpBioData.attribute.mouth = int.Parse(firstFace["attribute"]["mouth"].ToString());
                                tmpBioData.attribute.mustache = int.Parse(firstFace["attribute"]["mustache"].ToString());
                                tmpBioData.attribute.respirator = int.Parse(firstFace["attribute"]["respirator"].ToString());
                                tmpBioData.attribute.skinColor = int.Parse(firstFace["attribute"]["skinColor"].ToString());
                                tmpBioData.attribute.smile = int.Parse(firstFace["attribute"]["smile"].ToString());
                            }
                            if (firstFace.ContainsKey("feature"))
                            {
                                tmpBioData.faceFeature = new FaceFeature();
                                tmpBioData.faceFeature.size = int.Parse(firstFace["feature"]["size"].ToString());
                                tmpBioData.faceFeature.verTemplate = firstFace["feature"]["data"].ToString();
                            }
                            if (firstFace.ContainsKey("liveness"))
                            {
                                tmpBioData.hasLiveScore = 1;
                                tmpBioData.liveness.livenessScore = float.Parse(firstFace["liveness"]["livenessScore"].ToString());
                                tmpBioData.liveness.liveness = int.Parse(firstFace["liveness"]["liveness"].ToString());
                                tmpBioData.liveness.irFrameId = Int64.Parse(firstFace["liveness"]["irFrameId"].ToString());
                                tmpBioData.liveness.quality = float.Parse(firstFace["liveness"]["quality"].ToString());
                                tmpBioData.liveness.livenessMode = int.Parse(firstFace["liveness"]["livenessMode"].ToString());
                            }
                            if (firstFace.ContainsKey("identify"))
                            {
                                JArray identifyArray = (JArray)firstFace["identify"];
                                int nIdentifyCount = identifyArray.Count;
                                if (nIdentifyCount > 0)
                                {
                                    tmpBioData.matchResultList = new List<MatchResult>();
                                }
                                for (int j = 0; j < nIdentifyCount; j++)
                                {
                                    MatchResult matchResult = new MatchResult();
                                    matchResult.groupId = identifyArray[j]["groupId"].ToString();
                                    matchResult.name = identifyArray[j]["name"].ToString();
                                    matchResult.personId = identifyArray[j]["personId"].ToString();
                                    matchResult.userId = identifyArray[j]["userId"].ToString();
                                    matchResult.similarity = float.Parse(identifyArray[j]["similarity"].ToString());
                                    tmpBioData.matchResultList.Add(matchResult);
                                }
                            }
                            isFirstFace = false;
                        }
                        bioDataList.Add(tmpBioData);
                    }
                    if (bioDataList.Count == 0)
                    {
                        return null;
                    }
                }
               
            }
            else if (5 == nLabel)
            {
                if (jObject.ContainsKey("palm"))
                {
                    JArray palmArray = (JArray)jObject["palm"];
                    for(int i=0;i<palmArray.Count;i++)
                    {
                        if (null == palmArray[i] || !palmArray[i].HasValues)
                        {
                            continue;
                        }
                        BioData tempBioData = new BioData();
                        tempBioData.label = nLabel;
                        if (((JObject)palmArray[i]).ContainsKey("trackInfo"))
                        {
                            tempBioData.hasTrack = 1;
                            tempBioData.palmInfo.imageQuality = int.Parse(palmArray[i]["trackInfo"]["imageQuality"].ToString());
                            tempBioData.palmInfo.points[0].x = int.Parse(palmArray[i]["trackInfo"]["rect"]["x0"].ToString());
                            tempBioData.palmInfo.points[0].y = int.Parse(palmArray[i]["trackInfo"]["rect"]["y0"].ToString());
                            tempBioData.palmInfo.points[1].x = int.Parse(palmArray[i]["trackInfo"]["rect"]["x1"].ToString());
                            tempBioData.palmInfo.points[1].y = int.Parse(palmArray[i]["trackInfo"]["rect"]["y1"].ToString());
                            tempBioData.palmInfo.points[2].x = int.Parse(palmArray[i]["trackInfo"]["rect"]["x2"].ToString());
                            tempBioData.palmInfo.points[2].y = int.Parse(palmArray[i]["trackInfo"]["rect"]["y2"].ToString());
                            tempBioData.palmInfo.points[3].x = int.Parse(palmArray[i]["trackInfo"]["rect"]["x3"].ToString());
                            tempBioData.palmInfo.points[3].y = int.Parse(palmArray[i]["trackInfo"]["rect"]["y3"].ToString());
                        }
                        if (((JObject)palmArray[i]).ContainsKey("feature"))
                        {
                            tempBioData. hasPalmFeature = 1;
                            tempBioData.palmFeature.verTemplateSize = int.Parse(palmArray[i]["feature"]["verTemplateSize"].ToString());
                            tempBioData.palmFeature.verTemplate = palmArray[i]["feature"]["verTemplate"].ToString();
                        }
                        tempBioData.matchResultList = new List<MatchResult>();
                        if (((JObject)palmArray[i]).ContainsKey("identify"))
                        {
                            JArray identifyArray = (JArray)palmArray[i]["identify"];
                            int nIdentifyCount = identifyArray.Count;
                            for (int j = 0; j < nIdentifyCount; j++)
                            {
                                MatchResult matchResult = new MatchResult();
                                matchResult.groupId = identifyArray[j]["groupId"].ToString();
                                matchResult.name = identifyArray[j]["name"].ToString();
                                matchResult.personId = identifyArray[j]["personId"].ToString();
                                matchResult.userId = identifyArray[j]["userId"].ToString();
                                matchResult.similarity = float.Parse(identifyArray[j]["similarity"].ToString());
                                tempBioData.matchResultList.Add(matchResult);
                            }
                        }
                        if (tempBioData.matchResultList.Count == 0)
                        {
                            tempBioData.matchResultList = null;
                        }
                        bioDataList.Add(tempBioData);
                    }
                }
            }
            if (bioDataList.Count == 0)
            {
                return null;
            }
            return bioDataList;
        }

        public static List<BioData> parseMatchResult(String json)
        {
            List<BioData> bioDataList = new List<BioData>();
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return null;
            }
            if (!jObject.ContainsKey("events"))
            {
                return null;
            }
            JArray eventArrays = (JArray)jObject["events"];
            if (eventArrays.Count == 0)
            {
                return null;
            }
            for (int i=0;i<eventArrays.Count;i++)
            {
                int nLabel = int.Parse(eventArrays[i]["label"].ToString());
                if (1 == nLabel)
                {
                    if (((JObject)eventArrays[i]).ContainsKey("face"))
                    {
                        JArray faceArray = (JArray)eventArrays[i]["face"];
                        if (faceArray.HasValues && faceArray.Count > 0)
                        {
                            BioData bioData = new BioData();
                            bioData.label = nLabel;
                            JObject firstFace = (JObject)faceArray[0];
                            if (firstFace.ContainsKey("identify"))
                            {
                                JArray identifyArray = (JArray)firstFace["identify"];
                                int nIdentifyCount = identifyArray.Count;
                                if (nIdentifyCount > 0)
                                {
                                    bioData.matchResultList = new List<MatchResult>();
                                }
                                for (int j = 0; j < nIdentifyCount; j++)
                                {
                                    MatchResult matchResult = new MatchResult();
                                    matchResult.groupId = identifyArray[j]["groupId"].ToString();
                                    matchResult.name = identifyArray[j]["name"].ToString();
                                    matchResult.personId = identifyArray[j]["personId"].ToString();
                                    matchResult.userId = identifyArray[j]["userId"].ToString();
                                    matchResult.similarity = float.Parse(identifyArray[j]["similarity"].ToString());
                                    bioData.matchResultList.Add(matchResult);
                                }
                                bioDataList.Add(bioData);
                            }
                        }
                    }
                }
                else if (5 == nLabel)
                {
                    if (((JObject)eventArrays[i]).ContainsKey("palm"))
                    {
                        JArray palmArray = (JArray)jObject["palm"];
                        for (int j = 0; j < palmArray.Count; j++)
                        {
                            if (null == palmArray[j] || !palmArray[j].HasValues)
                            {
                                continue;
                            }
                            BioData tempBioData = new BioData();
                            tempBioData.label = nLabel;
                            tempBioData.matchResultList = new List<MatchResult>();
                            if (((JObject)palmArray[j]).ContainsKey("identify"))
                            {
                                JArray identifyArray = (JArray)palmArray[j]["identify"];
                                int nIdentifyCount = identifyArray.Count;
                                for (int k = 0; k < nIdentifyCount; k++)
                                {
                                    MatchResult matchResult = new MatchResult();
                                    matchResult.groupId = identifyArray[k]["groupId"].ToString();
                                    matchResult.name = identifyArray[k]["name"].ToString();
                                    matchResult.personId = identifyArray[k]["personId"].ToString();
                                    matchResult.userId = identifyArray[k]["userId"].ToString();
                                    matchResult.similarity = float.Parse(identifyArray[k]["similarity"].ToString());
                                    tempBioData.matchResultList.Add(matchResult);
                                }
                            }
                            if (tempBioData.matchResultList.Count == 0)
                            {
                                tempBioData.matchResultList = null;
                            }
                            bioDataList.Add(tempBioData);
                        }
                    }
                }
            }
            return bioDataList;
        }

        public static string getDetectFaceJson(byte[] jpeg, int len, bool feature, bool faceInfo, bool picture)
        {
            JObject root = new JObject();
            if (null != jpeg)
            {
                JObject image = new JObject();
                image["bioType"] = "face";
                image["data"] = Convert.ToBase64String(jpeg, 0, len, Base64FormattingOptions.None);
                image["format"] = "jpeg";
                root["image"] = image;
            }
            root["feature"] = feature;
            root["faceInfo"] = faceInfo;
            root["picture"] = picture;
            return root.ToString();
        }
        public static string getDetectPalmJson(byte[] raw, int width, int height, bool feature, bool palmInfo, bool picture)
        {
            JObject root = new JObject();

            if (null != raw)
            {
                JObject image = new JObject();
                image["bioType"] = "palm";
                image["data"] = Convert.ToBase64String(raw, 0, width*height, Base64FormattingOptions.None);
                image["format"] = "gray";
                image["width"] = width;
                image["height"] = height;
                root["image"] = image;
            }
            root["feature"] = feature;
            root["palmInfo"] = palmInfo;
            root["picture"] = picture;
            return root.ToString();
        }
        public static string getPalmMergeRegJson(bool feature, int[] cacheId, int count)
        {
            JObject root = new JObject();
            root["feature"] = feature;
            JArray ids = new JArray();
            for (int i = 0; i < count; i++)
            {
                JObject item = new JObject();
                item["bioType"] = "palm";
                item["data"] = cacheId[i];
                ids.Add(item);
            }
            root["cacheIds"] = ids;
            return root.ToString();
        }

        public static bool parseRegFace(String json, ref FaceDataList faceDataList)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            faceDataList.status = int.Parse(jObject["status"].ToString());
            faceDataList.detail = jObject["detail"].ToString();
            if (!jObject.ContainsKey("data") || !((JObject)jObject["data"]).ContainsKey("faces"))
            {
                return true;
            }
            faceDataList.list = new List<FaceData>();
            JArray faceArray = (JArray)jObject["data"]["faces"];
            for (int i=0; i< faceArray.Count; i++)
            {
                JObject faceItem = (JObject)faceArray[i];
                FaceData faceData = new FaceData();
                if (faceItem.ContainsKey("faceInfo"))
                {
                    JObject faceInfo = (JObject)faceItem["faceInfo"];
                    faceData.faceInfo = new FaceInfo();
                    faceData.faceInfo.attribute = new Attribute();
                    faceData.faceInfo.attribute.age = int.Parse(faceInfo["attribute"]["age"].ToString());
                    faceData.faceInfo.attribute.beauty = int.Parse(faceInfo["attribute"]["beauty"].ToString());
                    faceData.faceInfo.attribute.cap = int.Parse(faceInfo["attribute"]["cap"].ToString());
                    faceData.faceInfo.attribute.expression = int.Parse(faceInfo["attribute"]["expression"].ToString());
                    faceData.faceInfo.attribute.eye = int.Parse(faceInfo["attribute"]["eye"].ToString());
                    faceData.faceInfo.attribute.gender = int.Parse(faceInfo["attribute"]["gender"].ToString());
                    faceData.faceInfo.attribute.glasses = int.Parse(faceInfo["attribute"]["glasses"].ToString());
                    faceData.faceInfo.attribute.mouth = int.Parse(faceInfo["attribute"]["mouth"].ToString());
                    faceData.faceInfo.attribute.mustache = int.Parse(faceInfo["attribute"]["mustache"].ToString());
                    faceData.faceInfo.attribute.respirator = int.Parse(faceInfo["attribute"]["respirator"].ToString());
                    faceData.faceInfo.attribute.skinColor = int.Parse(faceInfo["attribute"]["skinColor"].ToString());
                    faceData.faceInfo.attribute.smile = int.Parse(faceInfo["attribute"]["smile"].ToString());
                    faceData.faceInfo.pose = new FacePose();
                    faceData.faceInfo.pose.pitch = float.Parse(faceInfo["pose"]["pitch"].ToString());
                    faceData.faceInfo.pose.roll = float.Parse(faceInfo["pose"]["roll"].ToString());
                    faceData.faceInfo.pose.yaw = float.Parse(faceInfo["pose"]["yaw"].ToString());
                    faceData.faceInfo.rect = new RECT();
                    faceData.faceInfo.rect.left = int.Parse(faceInfo["rect"]["left"].ToString());
                    faceData.faceInfo.rect.top = int.Parse(faceInfo["rect"]["top"].ToString());
                    faceData.faceInfo.rect.right = int.Parse(faceInfo["rect"]["right"].ToString());
                    faceData.faceInfo.rect.bottom = int.Parse(faceInfo["rect"]["bottom"].ToString());
                    faceData.faceInfo.landmark = new Landmark();
                    faceData.faceInfo.landmark.count = int.Parse(faceInfo["landmark"]["count"].ToString());
                    faceData.faceInfo.landmark.data = faceInfo["landmark"]["data"].ToString();
                    faceData.faceInfo.score = float.Parse(faceInfo["score"].ToString());
                }
                if (faceItem.ContainsKey("feature"))
                {
                    JObject feature = (JObject)faceItem["feature"];
                    faceData.bioFeature = new BioFeature();
                    faceData.bioFeature.bioType = feature["bioType"].ToString();
                    faceData.bioFeature.data = feature["data"].ToString();
                    faceData.bioFeature.size = int.Parse(feature["size"].ToString());
                }

                if (faceItem.ContainsKey("picture"))
                {
                    JObject picture = (JObject)faceItem["picture"];
                    faceData.bioPicture = new BioPicture();
                    faceData.bioPicture.bioType = picture["bioType"].ToString();
                    faceData.bioPicture.data = picture["data"].ToString();
                    faceData.bioPicture.format = picture["format"].ToString();
                    faceData.bioPicture.width = int.Parse(picture["width"].ToString());
                    faceData.bioPicture.height = int.Parse(picture["height"].ToString());
                }

                if (faceItem.ContainsKey("cacheId"))
                {
                    JObject cacheId = (JObject)faceItem["cacheId"];
                    faceData.cacheId = new CacheId();
                    faceData.cacheId.id = int.Parse(cacheId["data"].ToString());
                    faceData.cacheId.bioType = cacheId["bioType"].ToString();
                }
                faceDataList.list.Add(faceData);
                return true;
            }
            return false;
        }

        public static bool parseDetectPalm(String json, ref PalmDetectInfoList palmDetectInfoList)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            palmDetectInfoList.status = int.Parse(jObject["status"].ToString());
            palmDetectInfoList.detail = jObject["detail"].ToString();
            if (!jObject.ContainsKey("data") || !((JObject)jObject["data"]).ContainsKey("faces"))
            {
                return true;
            }
            JArray palmArray = (JArray)jObject["data"]["palms"];
            for (int i = 0; i < palmArray.Count; i++)
            {
                JObject palmtem = (JObject)palmArray[i];
                PalmDetectInfo palmDetectInfo = new PalmDetectInfo();
                if (palmtem.ContainsKey("palmInfo"))
                {
                    JObject palmInfo = (JObject)palmtem["palmInfo"];
                    palmDetectInfo.palmInfo = new PalmInfo();
                    palmDetectInfo.palmInfo.imageQuality = int.Parse(palmInfo["imageQuality"].ToString());
                    palmDetectInfo.palmInfo.templateQuality = int.Parse(palmInfo["templateQuality"].ToString());
                    palmDetectInfo.palmInfo.points = new POINT[4];
                    palmDetectInfo.palmInfo.points[0].x = int.Parse(palmInfo["rect"]["x0"].ToString());
                    palmDetectInfo.palmInfo.points[0].y = int.Parse(palmInfo["rect"]["y0"].ToString());
                    palmDetectInfo.palmInfo.points[1].x = int.Parse(palmInfo["rect"]["x1"].ToString());
                    palmDetectInfo.palmInfo.points[1].y = int.Parse(palmInfo["rect"]["y1"].ToString());
                    palmDetectInfo.palmInfo.points[2].x = int.Parse(palmInfo["rect"]["x2"].ToString());
                    palmDetectInfo.palmInfo.points[2].y = int.Parse(palmInfo["rect"]["y2"].ToString());
                    palmDetectInfo.palmInfo.points[3].x = int.Parse(palmInfo["rect"]["x3"].ToString());
                    palmDetectInfo.palmInfo.points[3].y = int.Parse(palmInfo["rect"]["y3"].ToString());
                }

                if (palmtem.ContainsKey("feature"))
                {
                    JObject feature = (JObject)palmtem["feature"];
                    palmDetectInfo.palmFeature = new PalmFeature();
                    palmDetectInfo.palmFeature.verTemplate = feature["verTemplate"].ToString();
                    palmDetectInfo.palmFeature.verTemplateSize = int.Parse(feature["verTemplateSize"].ToString());
                    palmDetectInfo.palmFeature.verTemplate = feature["preTemplate"].ToString();
                    palmDetectInfo.palmFeature.verTemplateSize = int.Parse(feature["preTemplateSize"].ToString());
                }
                if (palmtem.ContainsKey("picture"))
                {
                    JObject picture = (JObject)palmtem["picture"];
                    palmDetectInfo.bioPicture = new BioPicture();
                    palmDetectInfo.bioPicture.bioType = picture["bioType"].ToString();
                    palmDetectInfo.bioPicture.data = picture["data"].ToString();
                    palmDetectInfo.bioPicture.format = picture["format"].ToString();
                    palmDetectInfo.bioPicture.width = int.Parse(picture["width"].ToString());
                    palmDetectInfo.bioPicture.height = int.Parse(picture["height"].ToString());
                }

                if (palmtem.ContainsKey("cacheId"))
                {
                    JObject cacheId = (JObject)palmtem["cacheId"];
                    palmDetectInfo.cacheId = new CacheId();
                    palmDetectInfo.cacheId.id = int.Parse(cacheId["data"].ToString());
                    palmDetectInfo.cacheId.bioType = cacheId["bioType"].ToString();
                }
                palmDetectInfoList.list.Add(palmDetectInfo);
                return true;
            }
            return false;
        }

        public static bool parseRegPalm(String json, ref PalmRegInfo palmRegInfo)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            palmRegInfo.status = int.Parse(jObject["status"].ToString());
            palmRegInfo.detail = jObject["detail"].ToString();
            if (0 == palmRegInfo.status)
            {
                JObject palmObject = (JObject)jObject["data"]["palm"];
                palmRegInfo.mergeTemplate = palmObject["feature"]["mergeTemplate"].ToString();
                palmRegInfo.mergeTemplateSize = int.Parse(palmObject["feature"]["mergeTemplateSize"].ToString());
                if (palmObject.ContainsKey("cacheId"))
                {
                    palmRegInfo.cacheId = new CacheId();
                    palmRegInfo.cacheId.id = int.Parse(palmObject["cacheId"]["data"].ToString());
                    palmRegInfo.cacheId.bioType = palmObject["cacheId"]["bioType"].ToString();
                }
            }
            return true;
        }

        public static bool parseSnapshot(string json, ref SnapShot snapShot)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            snapShot.status = int.Parse(jObject["status"].ToString());
            snapShot.detail = jObject["detail"].ToString();
            if (0 == snapShot.status)
            {
                snapShot.type = jObject["data"]["snapshot"]["type"].ToString();
                snapShot.data = jObject["data"]["snapshot"]["data"].ToString();
                snapShot.width = int.Parse(jObject["data"]["snapshot"]["width"].ToString());
                snapShot.height = int.Parse(jObject["data"]["snapshot"]["height"].ToString());
                snapShot.frameId = int.Parse(jObject["data"]["snapshot"]["frameId"].ToString());
                snapShot.timeStamp = int.Parse(jObject["data"]["snapshot"]["timeStamp"].ToString());
            }
            return true;
        }

        public static bool parseQueryStatistics(String json, ref Statistics statistics)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            statistics.status = int.Parse(jObject["status"].ToString());
            statistics.detail = jObject["detail"].ToString();
            statistics.databaseSize = int.Parse(jObject["data"]["databaseSize"].ToString());
            statistics.faceCount = int.Parse(jObject["data"]["faceCount"].ToString());
            statistics.featureCount = int.Parse(jObject["data"]["featureCount"].ToString());
            statistics.featureSize = int.Parse(jObject["data"]["featureSize"].ToString());
            statistics.groupCount = int.Parse(jObject["data"]["groupCount"].ToString());
            statistics.palmCount = int.Parse(jObject["data"]["palmCount"].ToString());
            statistics.palmFeatureCount = int.Parse(jObject["data"]["palmFeatureCount"].ToString());
            statistics.palmFeatureSize = int.Parse(jObject["data"]["palmFeatureSize"].ToString());
            statistics.personCount = int.Parse(jObject["data"]["personCount"].ToString());
            statistics.pictureCount = int.Parse(jObject["data"]["pictureCount"].ToString());
            statistics.pictureSize = int.Parse(jObject["data"]["pictureSize"].ToString());
            return true;
        }

        public static string getAddUserJson(String userid, String name)
        {
            JObject root = new JObject();
            root["personId"] = userid;
            root["name"] = name;
            return root.ToString();
        }

        public static string getQueryAllUserJson()
        {
            JObject root = new JObject();
            root["pageIndex"] = 0;
            root["pageSize"] = 0;
            return root.ToString();
        }

        public static bool parseJson(String json, ref int status, ref string detail)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            status = int.Parse(jObject["status"].ToString());
            detail = jObject["detail"].ToString();
            return true;
        }

        public static string getDeleteUserJson(string userid)
        {
            JObject root = new JObject();
            root["personId"] = userid;
            return root.ToString();
        }

        public static string getAddFaceJson(String userid, byte[] jpeg, int size)
        {
            JObject root = new JObject();
            root["personId"] = userid;
            JArray array = new JArray();
            JObject item = new JObject();
            item["bioType"] = "face";
            item["data"] = Convert.ToBase64String(jpeg, 0, size, Base64FormattingOptions.None);
            item["format"] = "jpeg";
            array.Add(item);
            root["images"] = array;
            return root.ToString();
        }

        public static string getAddFaceRegJson(String userid, int cacheId)
        {
            JObject root = new JObject();
            root["personId"] = userid;
            JArray array = new JArray();
            JObject item = new JObject();
            item["bioType"] = "face";
            item["data"] = cacheId;
            array.Add(item);
            root["cacheIds"] = array;
            return root.ToString();
        }

        public static string getAddPalmRegJson(String userid, int cacheId)
        {
            JObject root = new JObject();
            root["personId"] = userid;
            JArray array = new JArray();
            JObject item = new JObject();
            item["bioType"] = "palm";
            item["data"] = cacheId;
            array.Add(item);
            root["cacheIds"] = array;
            return root.ToString();
        }

        public static string getDelCacheJson(string bioType, int cacheId)
        {
            JObject root = new JObject();
            JObject data = new JObject();
            data["bioType"] = bioType;
            data["data"] = cacheId;
            root["cacheId"] = data;
            return root.ToString();
        }

        public static string getQueryUserJson(String userid, bool feature, bool picture)
        {
            JObject root = new JObject();
            root["personId"] = userid;
            JArray array = new JArray();
            JObject itemFace = new JObject();
            itemFace["bioType"] = "face";
            itemFace["feature"] = feature;
            itemFace["picture"] = picture;
            array.Add(itemFace);
            JObject itemPalm= new JObject();
            itemPalm["bioType"] = "palm";
            itemPalm["feature"] = feature;
            array.Add(itemPalm);
            root["data"] = array;
            return root.ToString();
        }

        public static string getSyncTimeJson(string stime)
        {
            JObject root = new JObject();
            root["syncTime"] = stime;
            return root.ToString();
        }

        public static bool parseDeviceTime(String json, ref int status, ref string detail, ref string sysTime)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            status = int.Parse(jObject["status"].ToString());
            detail = jObject["detail"].ToString();
            if (0 == status)
            {
                if (!jObject.ContainsKey("data") || !((JObject)(jObject["data"])).ContainsKey("sysTime"))
                {
                    return false;
                }
                sysTime = jObject["data"]["sysTime"].ToString();
            }
            return true;
        }

        public static string getAttRecordCountJson()
        {
            JObject root = new JObject();
            root["startId"] = -1;
            return root.ToString();
        }
        public static bool parseAttRecordCount(String json, ref AttRecordCount attRecordCount)
        {
            JObject jObject = (JObject)JsonConvert.DeserializeObject(json);
            if (null == jObject)
            {
                return false;
            }
            if (!jObject.ContainsKey("status") || !jObject.ContainsKey("detail"))
            {
                return false;
            }
            attRecordCount.status = int.Parse(jObject["status"].ToString());
            attRecordCount.detail = jObject["detail"].ToString();
            attRecordCount.totalCount = int.Parse(jObject["totalCount"].ToString());
            if (jObject.ContainsKey("startId"))
            {
                attRecordCount.startId = int.Parse(jObject["startId"].ToString());
            }
            return true;
        }

        public static string getAttRecordJson(int startId, int count, bool attPhoto)
        {
            JObject root = new JObject();
            root["startId"] = startId;
            root["reqCount"] = count;
            root["needImg"] = attPhoto;
            return root.ToString();
        }
    }
}
