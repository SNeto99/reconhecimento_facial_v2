#include <stdio.h>
#include "common.h"
#include "base64.h"
#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

using namespace std;
using namespace rapidjson;

void clearCustomDataVector(vector<PBioData> &bioDatas)
{
	for(int i = 0; i < bioDatas.size(); i++)
	{
		for(int j = 0; j < bioDatas[i]->matchResultList.size(); j++)
		{
			delete bioDatas[i]->matchResultList[j];
		}
		bioDatas[i]->matchResultList.clear();
		delete bioDatas[i];
	}
	bioDatas.clear();
}

vector<PBioData> parse_customData(char *json)
{
	vector<PBioData> bioDataList;
	wchar_t log[128] = {0};
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		printf("HasParseError %d\n", document.GetParseError());
		return bioDataList;
	}

	if(!document.HasMember("label"))
	{
		printf("Can not find label in json\n");
		return bioDataList;
	}

	int label = 0;
	label = document["label"].GetInt();
	if(1 == label)
	{
		if(document.HasMember("face"))
		{
			const Value& faceArray = document["face"];
			if(faceArray.IsArray())
			{
				for(int i = 0; i < faceArray.Size(); i++)
				{
					const Value& tracker = faceArray[i]["tracker"];

					PBioData pbio = new BioData;
					pbio->hasTrack = 1;
					pbio->label = label;

					pbio->trackData.trackId = tracker["trackId"].GetInt();
					pbio->trackData.blur = tracker["blur"].GetFloat();
					pbio->trackData.snap_type = tracker["snapType"].GetString();

					pbio->trackData.pose.yaw = tracker["pose"]["yaw"].GetFloat();
					pbio->trackData.pose.pitch = tracker["pose"]["pitch"].GetFloat();
					pbio->trackData.pose.roll = tracker["pose"]["roll"].GetFloat();

					pbio->trackData.rect.left = tracker["rect"]["left"].GetInt();
					pbio->trackData.rect.top = tracker["rect"]["top"].GetInt();
					pbio->trackData.rect.right = tracker["rect"]["right"].GetInt();
					pbio->trackData.rect.bottom = tracker["rect"]["bottom"].GetInt();

					pbio->trackData.landmark.count = tracker["landmark"]["count"].GetInt();
					pbio->trackData.landmark.data = tracker["landmark"]["data"].GetString();;

					bioDataList.push_back(pbio);
				}
			}

			if(bioDataList.empty())
			{
				return bioDataList;
			}
			PBioData bioData = bioDataList[0];
			const Value& firstFace = faceArray[0];
			if(firstFace.HasMember("attribute"))
			{
				bioData->hasAttr = 1;
				bioData->attribute.age = firstFace["attribute"]["age"].GetInt();
				bioData->attribute.beauty = firstFace["attribute"]["beauty"].GetInt();
				bioData->attribute.cap = firstFace["attribute"]["cap"].GetInt();
				bioData->attribute.expression = firstFace["attribute"]["expression"].GetInt();
				bioData->attribute.eye = firstFace["attribute"]["eye"].GetInt();
				bioData->attribute.gender = firstFace["attribute"]["gender"].GetInt();
				bioData->attribute.glasses = firstFace["attribute"]["glasses"].GetInt();
				bioData->attribute.mouth = firstFace["attribute"]["mouth"].GetInt();
				bioData->attribute.mustache = firstFace["attribute"]["mustache"].GetInt();
				bioData->attribute.respirator = firstFace["attribute"]["respirator"].GetInt();
				bioData->attribute.skinColor = firstFace["attribute"]["skinColor"].GetInt();
				bioData->attribute.smile = firstFace["attribute"]["smile"].GetInt();
			}
			if(firstFace.HasMember("feature"))
			{
				bioData->hasFeature = 1;
				bioData->faceFeature.size = firstFace["feature"]["size"].GetInt();
				bioData->faceFeature.verTemplate = firstFace["feature"]["data"].GetString();
			}
			if(firstFace.HasMember("liveness"))
			{
				bioData->hasLiveScore = 1;
				bioData->liveness.livenessScore = firstFace["liveness"]["livenessScore"].GetFloat();
				bioData->liveness.liveness = firstFace["liveness"]["liveness"].GetInt();
				bioData->liveness.irFrameId = firstFace["liveness"]["irFrameId"].GetFloat();
				bioData->liveness.quality = firstFace["liveness"]["quality"].GetFloat();
				bioData->liveness.livenessMode = firstFace["liveness"]["livenessMode"].GetInt();
			}
			if(firstFace.HasMember("identify"))
			{
				if(firstFace["identify"].IsArray())
				{
					for(int i = 0; i < firstFace["identify"].Size(); i++)
					{
						PMatchResult pMatchResult = new MatchResult();
						pMatchResult->groupId = firstFace["identify"][i]["groupId"].GetString();
						pMatchResult->name = firstFace["identify"][i]["name"].GetString();
						pMatchResult->personId = firstFace["identify"][i]["personId"].GetString();
						pMatchResult->userId = firstFace["identify"][i]["userId"].GetString();		
						pMatchResult->similarity = firstFace["identify"][i]["similarity"].GetFloat();
						bioData->matchResultList.push_back(pMatchResult);
					}
				}
			}
		}
	}
	else if(5 == label)
	{
		if(document.HasMember("palm"))
		{
			const Value& palmArray = document["palm"];
			if(palmArray.IsArray())
			{				
				for(int i = 0; i < palmArray.Size(); i++)
				{
					if(palmArray[i].IsNull())
					{
						continue;
					}
					PBioData pbio = new BioData;;
					pbio->label = label;
					if(palmArray[i].HasMember("trackInfo"))
					{
						pbio->hasTrack = 1;
						pbio->palmInfo.imageQuality = palmArray[i]["trackInfo"]["imageQuality"].GetInt();
						pbio->palmInfo.points[0].x = palmArray[i]["trackInfo"]["rect"]["x0"].GetInt();
						pbio->palmInfo.points[0].y = palmArray[i]["trackInfo"]["rect"]["y0"].GetInt();
						pbio->palmInfo.points[1].x = palmArray[i]["trackInfo"]["rect"]["x1"].GetInt();
						pbio->palmInfo.points[1].y = palmArray[i]["trackInfo"]["rect"]["y1"].GetInt();
						pbio->palmInfo.points[2].x = palmArray[i]["trackInfo"]["rect"]["x2"].GetInt();
						pbio->palmInfo.points[2].y = palmArray[i]["trackInfo"]["rect"]["y2"].GetInt();
						pbio->palmInfo.points[3].x = palmArray[i]["trackInfo"]["rect"]["x3"].GetInt();
						pbio->palmInfo.points[3].y = palmArray[i]["trackInfo"]["rect"]["y3"].GetInt();
					}

					if(palmArray[i].HasMember("feature"))
					{
						pbio->hasPalmFeature = 1;
						pbio->palmFeature.verTemplateSize = palmArray[i]["feature"]["verTemplateSize"].GetInt();
						pbio->palmFeature.verTemplate =palmArray[i]["feature"]["verTemplate"].GetString();
					}

					if(palmArray[i].HasMember("identify"))
					{
						if(palmArray[i]["identify"].IsArray())
						{
							for(int j = 0; j < palmArray[i]["identify"].Size(); j++)
							{
								PMatchResult pMatchResult = new MatchResult();
								pMatchResult->groupId = palmArray[i]["identify"][j]["groupId"].GetString();
								pMatchResult->name = palmArray[i]["identify"][j]["name"].GetString();
								pMatchResult->personId = palmArray[i]["identify"][j]["personId"].GetString();
								pMatchResult->userId = palmArray[i]["identify"][j]["userId"].GetString();
								pMatchResult->similarity = palmArray[i]["identify"][j]["similarity"].GetFloat();

								pbio->matchResultList.push_back(pMatchResult);
							}
						}
					}

					bioDataList.push_back(pbio);
				}
			}
		}
	}

	return bioDataList;
}

vector<PBioData> parseMatchResult(char *json)
{
	vector<PBioData> bioDataList;
	wchar_t log[128] = {0};
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		//printf("HasParseError %d\n", document.GetParseError());
		return bioDataList;
	}

	if(!document.HasMember("events"))
	{
		//printf("Can not find events in json\n");
		return bioDataList;
	}

	const Value& events = document["events"];
	if(events.IsNull())
	{
		return bioDataList;
	}

	for(int k = 0; k < events.Size(); k++)
	{
		int label = 0;
		label = events[k]["label"].GetInt();
		if(1 == label)
		{
			if(events[k].HasMember("face"))
			{
				const Value& faceArray = events[k]["face"];
				if(faceArray.IsArray() && faceArray.Size() > 0)
				{
					if(faceArray[0].HasMember("identify"))
					{
						PBioData pBioData = new BioData;
						pBioData->label = label;
						if(faceArray[0]["identify"].IsArray())
						{
							for(int i = 0; i < faceArray[0]["identify"].Size(); i++)
							{
								PMatchResult pMatchResult = new MatchResult();
								pMatchResult->groupId = faceArray[0]["identify"][i]["groupId"].GetString();
								pMatchResult->name = faceArray[0]["identify"][i]["name"].GetString();
								pMatchResult->personId = faceArray[0]["identify"][i]["personId"].GetString();
								pMatchResult->userId = faceArray[0]["identify"][i]["userId"].GetString();		
								pMatchResult->similarity = faceArray[0]["identify"][i]["similarity"].GetFloat();
								pBioData->matchResultList.push_back(pMatchResult);
							}
						}

						bioDataList.push_back(pBioData);
					}
				}
			}
		}
		else if(5 == label)
		{
			if(events[k].HasMember("palm"))
			{
				const Value& palmArray = events[k]["palm"];
				if(palmArray.IsArray() && palmArray.Size() > 0)
				{				
					if(palmArray[0].HasMember("identify"))
					{
						PBioData pBioData = new BioData;;
						pBioData->label = label;

						if(palmArray[0]["identify"].IsArray())
						{
							for(int j = 0; j < palmArray[0]["identify"].Size(); j++)
							{
								PMatchResult pMatchResult = new MatchResult();
								pMatchResult->groupId = palmArray[0]["identify"][j]["groupId"].GetString();
								pMatchResult->name = palmArray[0]["identify"][j]["name"].GetString();
								pMatchResult->personId = palmArray[0]["identify"][j]["personId"].GetString();
								pMatchResult->userId = palmArray[0]["identify"][j]["userId"].GetString();
								pMatchResult->similarity = palmArray[0]["identify"][j]["similarity"].GetFloat();

								pBioData->matchResultList.push_back(pMatchResult);
							}
						}

						bioDataList.push_back(pBioData);
					}
				}
			}
		}
	}

	return bioDataList;
}

string getDetectFaceJson(unsigned char *jpeg, int len, bool feature, bool faceInfo, bool picture)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	if(NULL != jpeg)
	{
		writer.Key("image");
		writer.StartObject();
		writer.Key("bioType");
		writer.String("face");
		writer.Key("data");
		string str = base64_encode(jpeg, len);
		writer.String(str.c_str());
		writer.Key("format");
		writer.String("jpeg");
		writer.EndObject();
	}
	writer.Key("feature");
	writer.Bool(feature);
	writer.Key("faceInfo");
	writer.Bool(faceInfo);
	writer.Key("picture");
	writer.Bool(picture);
	writer.EndObject();

	return s.GetString();
}

string getDetectPalmJson(unsigned char *raw, int width, int height, bool feature, bool palmInfo, bool picture)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	if(NULL != raw)
	{
		writer.Key("image");
		writer.StartObject();
		writer.Key("bioType");
		writer.String("palm");
		writer.Key("data");
		string str = base64_encode(raw, width*height);
		writer.String(str.c_str());
		writer.Key("format");
		writer.String("gray");
		writer.Key("width");
		writer.Uint(width);
		writer.Key("height");
		writer.Uint(height);
		writer.EndObject();
	}
	writer.Key("feature");
	writer.Bool(feature);
	writer.Key("faceInfo");
	writer.Bool(palmInfo);
	writer.Key("picture");
	writer.Bool(picture);
	writer.EndObject();

	return s.GetString();
}

string getPalmMergeRegJson(bool feature, int *cacheId, int count)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("feature");
	writer.Bool(feature);
	writer.Key("cacheIds");
	writer.StartArray();
	for(int i = 0; i < count; i++)
	{
		writer.StartObject();
		writer.Key("bioType");
		writer.String("palm");
		writer.Key("data");
		writer.Int(cacheId[i]);
		writer.EndObject();
	}
	writer.EndArray();
	writer.EndObject();

	return s.GetString();
}

int parseRegFace(char *json, PFaceDataList pFaceDataList)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}

	pFaceDataList->status = document["status"].GetInt();
	pFaceDataList->detail = document["detail"].GetString();

	if(!document.HasMember("data"))
	{
		return 0;
	}

	if(!document["data"].HasMember("faces"))
	{
		return 0;
	}

	const Value& faces = document["data"]["faces"];
	if(faces.IsArray())
	{
		for(int i = 0; i < faces.Size(); i++)
		{
			const Value& face= faces[i];
			PFaceData pFaceData = new FaceData();

			if(face.HasMember("faceInfo"))
			{
				const Value& faceInfo = face["faceInfo"];
				pFaceData->faceInfo.attribute.age = faceInfo["attribute"]["age"].GetInt();
				pFaceData->faceInfo.attribute.beauty = faceInfo["attribute"]["beauty"].GetInt();
				pFaceData->faceInfo.attribute.cap = faceInfo["attribute"]["cap"].GetInt();
				pFaceData->faceInfo.attribute.expression = faceInfo["attribute"]["expression"].GetInt();
				pFaceData->faceInfo.attribute.eye = faceInfo["attribute"]["eye"].GetInt();
				pFaceData->faceInfo.attribute.gender = faceInfo["attribute"]["gender"].GetInt();
				pFaceData->faceInfo.attribute.glasses = faceInfo["attribute"]["glasses"].GetInt();
				pFaceData->faceInfo.attribute.mouth = faceInfo["attribute"]["mouth"].GetInt();
				pFaceData->faceInfo.attribute.mustache = faceInfo["attribute"]["mustache"].GetInt();
				pFaceData->faceInfo.attribute.respirator = faceInfo["attribute"]["respirator"].GetInt();
				pFaceData->faceInfo.attribute.skinColor = faceInfo["attribute"]["skinColor"].GetInt();
				pFaceData->faceInfo.attribute.smile = faceInfo["attribute"]["smile"].GetInt();

				pFaceData->faceInfo.pose.pitch = faceInfo["pose"]["pitch"].GetFloat();
				pFaceData->faceInfo.pose.roll = faceInfo["pose"]["roll"].GetFloat();
				pFaceData->faceInfo.pose.yaw = faceInfo["pose"]["yaw"].GetFloat();

				pFaceData->faceInfo.rect.left = faceInfo["rect"]["left"].GetInt();
				pFaceData->faceInfo.rect.top = faceInfo["rect"]["top"].GetInt();
				pFaceData->faceInfo.rect.right = faceInfo["rect"]["right"].GetInt();
				pFaceData->faceInfo.rect.bottom = faceInfo["rect"]["bottom"].GetInt();

				pFaceData->faceInfo.landmark.count = faceInfo["landmark"]["count"].GetInt();
				pFaceData->faceInfo.landmark.data = faceInfo["landmark"]["data"].GetString();

				pFaceData->faceInfo.score = faceInfo["score"].GetFloat();
			}

			if(face.HasMember("feature"))
			{
				const Value& feature = face["feature"];
				pFaceData->bioFeature.bioType = feature["bioType"].GetString();
				pFaceData->bioFeature.data = feature["data"].GetString();
				pFaceData->bioFeature.size = feature["size"].GetInt();
			}

			if(face.HasMember("picture"))
			{
				const Value& picture = face["picture"];
				pFaceData->bioPicture.bioType = picture["bioType"].GetString();
				pFaceData->bioPicture.data = picture["data"].GetString();
				pFaceData->bioPicture.format = picture["format"].GetString();
				pFaceData->bioPicture.width = picture["width"].GetInt();
				pFaceData->bioPicture.height = picture["height"].GetInt();
			}

			if(face.HasMember("cacheId"))
			{
				const Value& cacheId = face["cacheId"];
				pFaceData->cacheId.id = cacheId["data"].GetInt();
				pFaceData->cacheId.bioType = cacheId["bioType"].GetString();
			}

			pFaceDataList->list.push_back(pFaceData);
		}		
	}

	return 0;
}

int parseDetectPalm(char *json, PPalmDetectInfoList pPalmDetectInfoList)
{
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}

	pPalmDetectInfoList->status = document["status"].GetInt();
	pPalmDetectInfoList->detail = document["detail"].GetString();

	if(!document.HasMember("data"))
	{
		return 0;
	}

	if(!document["data"].HasMember("palms"))
	{
		return 0;
	}

	const Value& palms = document["data"]["palms"];
	if(palms.IsArray())
	{
		for(int i = 0; i < palms.Size(); i++)
		{
			PPalmDetectInfo pPalmDetectInfo = new PalmDetectInfo;

			if(palms[i].HasMember("palmInfo"))
			{
				const Value& palmInfo = palms[i]["palmInfo"];
				pPalmDetectInfo->palmInfo.imageQuality = palmInfo["imageQuality"].GetInt();
				pPalmDetectInfo->palmInfo.templateQuality = palmInfo["templateQuality"].GetInt();
				pPalmDetectInfo->palmInfo.points[0].x = palmInfo["rect"]["x0"].GetInt();
				pPalmDetectInfo->palmInfo.points[0].y = palmInfo["rect"]["y0"].GetInt();
				pPalmDetectInfo->palmInfo.points[1].x = palmInfo["rect"]["x1"].GetInt();
				pPalmDetectInfo->palmInfo.points[1].y = palmInfo["rect"]["y1"].GetInt();
				pPalmDetectInfo->palmInfo.points[2].x = palmInfo["rect"]["x2"].GetInt();
				pPalmDetectInfo->palmInfo.points[2].y = palmInfo["rect"]["y2"].GetInt();
				pPalmDetectInfo->palmInfo.points[3].x = palmInfo["rect"]["x3"].GetInt();
				pPalmDetectInfo->palmInfo.points[3].y = palmInfo["rect"]["y3"].GetInt();
			}

			if(palms[i].HasMember("feature"))
			{
				const Value& palmFeature = palms[i]["feature"];
				pPalmDetectInfo->palmFeature.verTemplate = palmFeature["verTemplate"].GetString();
				pPalmDetectInfo->palmFeature.verTemplateSize = palmFeature["verTemplateSize"].GetInt();
				pPalmDetectInfo->palmFeature.preRegTemplate = palmFeature["preTemplate"].GetString();
				pPalmDetectInfo->palmFeature.preRegTemplateSize = palmFeature["preTemplateSize"].GetInt();
			}

			if(palms[i].HasMember("picture"))
			{
				const Value& picture = palms[i]["picture"];
				pPalmDetectInfo->bioPicture.bioType = picture["bioType"].GetString();
				pPalmDetectInfo->bioPicture.data = picture["data"].GetString();
				pPalmDetectInfo->bioPicture.format = picture["format"].GetString();
				pPalmDetectInfo->bioPicture.width = picture["width"].GetInt();
				pPalmDetectInfo->bioPicture.height = picture["height"].GetInt();
			}

			if(palms[i].HasMember("cacheId"))
			{
				const Value& cacheId = palms[i]["cacheId"];
				pPalmDetectInfo->cacheId.id = cacheId["data"].GetInt();
				pPalmDetectInfo->cacheId.bioType = cacheId["bioType"].GetString();
			}

			pPalmDetectInfoList->list.push_back(pPalmDetectInfo);
		}
	}

	return 0;
}

int parseRegPalm(char *json, PPalmRegInfo pPalmRegInfo)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}

	pPalmRegInfo->status = document["status"].GetInt();
	pPalmRegInfo->detail = document["detail"].GetString();

	if(0 == pPalmRegInfo->status)
	{
		const Value& palm = document["data"]["palm"];

		pPalmRegInfo->mergeTemplate = palm["feature"]["mergeTemplate"].GetString();
		pPalmRegInfo->mergeTemplateSize = palm["feature"]["mergeTemplateSize"].GetInt();
	
		if(palm.HasMember("cacheId"))
		{
			pPalmRegInfo->cacheId.id = palm["cacheId"]["data"].GetInt();
			pPalmRegInfo->cacheId.bioType = palm["cacheId"]["bioType"].GetString();
		}
	}

	return 0;
}

int parseSnapshot(char *json, PSnapShot pSnapShot)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}
	
	pSnapShot->status = document["status"].GetInt();
	pSnapShot->detail = document["detail"].GetString();

	if(0 == pSnapShot->status)
	{
		pSnapShot->type = document["data"]["snapshot"]["type"].GetString();
		pSnapShot->data = document["data"]["snapshot"]["data"].GetString();
		pSnapShot->width = document["data"]["snapshot"]["width"].GetInt();
		pSnapShot->height = document["data"]["snapshot"]["height"].GetInt();
		pSnapShot->frameId = document["data"]["snapshot"]["frameId"].GetInt();
		pSnapShot->timeStamp = document["data"]["snapshot"]["timeStamp"].GetInt();
	}

	return 0;
}

int parseQueryStatistics(char *json, PStatistics pStatistics)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}
	
	pStatistics->status = document["status"].GetInt();
	pStatistics->detail = document["detail"].GetString();

	pStatistics->databaseSize = document["data"]["databaseSize"].GetInt();
	pStatistics->faceCount = document["data"]["faceCount"].GetInt();
	pStatistics->featureCount = document["data"]["featureCount"].GetInt();
	pStatistics->featureSize = document["data"]["featureSize"].GetInt();
	pStatistics->groupCount = document["data"]["groupCount"].GetInt();
	pStatistics->palmCount = document["data"]["palmCount"].GetInt();
	pStatistics->palmFeatureCount = document["data"]["palmFeatureCount"].GetInt();
	pStatistics->palmFeatureSize = document["data"]["palmFeatureSize"].GetInt();
	pStatistics->personCount = document["data"]["personCount"].GetInt();
	pStatistics->pictureCount = document["data"]["pictureCount"].GetInt();
	pStatistics->pictureSize = document["data"]["pictureSize"].GetInt();

	return 0;
}

string getAddUserJson(char *userid, char *name)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("personId");
	writer.String(userid);
	writer.Key("name");
	writer.String(name);
	writer.EndObject();

	return s.GetString();
}

string getQueryAllUserJson()
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("pageIndex");
	writer.Uint(0);
	writer.Key("pageSize");
	writer.Uint(0);
	writer.EndObject();

	return s.GetString();
}

int parseJson(char *json, int *status, string &detail)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}

	*status = document["status"].GetInt();
	detail = document["detail"].GetString();
	ret = 0;

	return ret;
}

string getDeleteUserJson(char *userid)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("personId");
	writer.String(userid);
	writer.EndObject();

	return s.GetString();
}

string getAddFaceJson(char *userid, unsigned char *jpeg, int size)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("personId");
	writer.String(userid);
	writer.Key("images");
	writer.StartArray();
	writer.StartObject();
    writer.Key("bioType");
    writer.String("face");
	writer.Key("data");
	string str = base64_encode(jpeg, size);
	writer.String(str.c_str());
	writer.Key("format");
    writer.String("jpeg");
    writer.EndObject();
	writer.EndArray();
	writer.EndObject();

	return s.GetString();
}

string getAddFaceRegJson(char *userid, int cacheId)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("personId");
	writer.String(userid);
	writer.Key("cacheIds");
	writer.StartArray();
	writer.StartObject();
    writer.Key("bioType");
    writer.String("face");
	writer.Key("data");
	writer.Int(cacheId);
    writer.EndObject();
	writer.EndArray();
	writer.EndObject();

	return s.GetString();
}

string getAddPalmRegJson(char *userid, int cacheId)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("personId");
	writer.String(userid);
	writer.Key("cacheIds");
	writer.StartArray();

	writer.StartObject();
	writer.Key("bioType");
	writer.String("palm");
	writer.Key("data");
	writer.Int(cacheId);
	writer.EndObject();

	writer.EndArray();
	writer.EndObject();

	return s.GetString();
}

string getDelCacheJson(string bioType, int cacheId)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("cacheId");
	writer.StartObject();
	writer.Key("bioType");
	writer.String(bioType.c_str());
	writer.Key("data");
	writer.Int(cacheId);
	writer.EndObject();
	writer.EndObject();

	return s.GetString();
}

string getQueryUserJson(char *userid, bool feature, bool picture)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("personId");
	writer.String(userid);
	writer.Key("data");
	writer.StartArray();
	writer.StartObject();
    writer.Key("bioType");
    writer.String("face");
	writer.Key("feature");
	writer.Bool(feature);
	writer.Key("picture");
    writer.Bool(picture);
    writer.EndObject();
	writer.StartObject();
    writer.Key("bioType");
    writer.String("palm");
	writer.Key("feature");
	writer.Bool(feature);
    writer.EndObject();
	writer.EndArray();
	writer.EndObject();

	return s.GetString();
}

string getSyncTimeJson(char *stime)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("syncTime");
	writer.String(stime);
	writer.EndObject();

	return s.GetString();
}

int parseDeviceTime(char *json, int *status, string &detail, string &sysTime)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}

	*status = document["status"].GetInt();
	detail = document["detail"].GetString();
	ret = 0;

	if(0 == *status)
	{
		if(!document.HasMember("data") || !document["data"].HasMember("sysTime"))
		{
			return -2;
		}

		sysTime = document["data"]["sysTime"].GetString();
	}

	return ret;
}

string getAttRecordCountJson()
{
	/*
	{
		"startTime" : "2019-10-01 10:00:00",
		"endTime" : "2019-10-01 12:00:00",
	}
	or
	{
		"startId" : -1
	}
	*/
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("startId");
	writer.Int(-1);
	writer.EndObject();

	return s.GetString();
}

int parseAttRecordCount(char *json, PAttRecordCount pAttRecordCount)
{
	int ret = -1;
	Document document;
	document.Parse(json);
	if (document.HasParseError())
	{
		return -1;
	}

	if(!document.HasMember("status") || !document.HasMember("detail"))
	{
		return -2;
	}
	
	pAttRecordCount->status = document["status"].GetInt();
	pAttRecordCount->detail = document["detail"].GetString();

	pAttRecordCount->totalCount = document["totalCount"].GetInt();
	if(document.HasMember("startId"))
	{
		pAttRecordCount->startId = document["startId"].GetInt();
	}

	return 0;
}

string getAttRecordJson(int startId, int count, bool attPhoto)
{
	StringBuffer s;
    Writer<StringBuffer> writer(s);

	writer.StartObject();
	writer.Key("startId");
	writer.Int(startId);
	writer.Key("reqCount");
	writer.Int(count);
	writer.Key("needImg");
	writer.Bool(attPhoto);
	writer.EndObject();

	return s.GetString();
}