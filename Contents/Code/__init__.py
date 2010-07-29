# PMS plugin framework
import re
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/nickjr"

NAMESPACES = {'media':'http://search.yahoo.com/mrss/', 'mediaad':'http://blip.tv/mediaad'}

NICK_ROOT            = "http://www.nickjr.com"
NICK_SHOWS_LIST      = "http://www.nickjr.com/shows/"
RSS_FEED             = "http://www.nickjr.com/dynamo/video/data/mrssGen.jhtml?type=network&loc=default&hub=kids&mode=playlist&dartSite=nickjr.playtime.nol&mgid=mgid:cms:item:nickjr.com:%s&demo=null&block=true"

NAME = L('Title')
ART  = 'art-default.png'
ICON = 'icon-default.png'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, VideoMainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

####################################################################################################
def VideoMainMenu():
    dir = MediaContainer(mediaType='video')
    content = XML.ElementFromURL(NICK_SHOWS_LIST, isHTML=True, cacheTime=0)
    c = 0
    i = 0
    for test in content.xpath('//div[3]//h2/a'):
    	for item in content.xpath('//div[3]//h2/a'):
    		link = NICK_ROOT + item.get('href')
       		image = item.xpath('//div[3]//div/img')[i].get('src')
       		image = image.split('?', 1)[0]
       		title = item.text
       		if c < 24:   #ONLY NEED 23 SHOWS
       			c += 1
       			if "More Show" in title:
       				continue
       			else:
       				i += 1
    				dir.Append(Function(DirectoryItem(ShowList, title, thumb=image), image = image, pageUrl = link))
    	return dir

####################################################################################################
def ShowList(sender, image, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='List')
    clipdict = {}
    clipdict['false'] = []
    clipdict['true'] = []
    content = XML.ElementFromURL(pageUrl, True)
    for item in content.xpath("//body/div/div/div/div/div/div/div/div/div/div/div/h2/a"):
    	link = NICK_ROOT + item.get('href')
    	title = item.text
    	if "Video" in title:
            showcontent = HTTP.Request(link)
            m = re.compile('KIDS.add."cmsId", ".+?".;').findall(showcontent)
            cmsid = m[0].split('"')[3]
            #Log(cmsid)
            url = RSS_FEED % (cmsid) 
            #Log(url)
            feedcontent = XML.ElementFromURL(url) #.xpath("//item")
            for item in feedcontent.xpath("//item"): #[0].xpath("..//media:category[@label='full']", namespaces=NAMESPACES):
                title = item.xpath(".//media:title", namespaces=NAMESPACES)[0].text
                link = item.xpath('.//media:player', namespaces=NAMESPACES)[0].get('url')
                thumb = item.xpath('.//media:thumbnail', namespaces=NAMESPACES)[0].get('url')
                summary = item.xpath('.//media:description', namespaces=NAMESPACES)[0].text
                if item[0].xpath("..//media:category[@label='full']", namespaces=NAMESPACES):
                    clipdict['false'].append((title, thumb, summary, link))
                elif item[0].xpath("..//media:category[@label='clip']", namespaces=NAMESPACES):
                    clipdict['true'].append((title, thumb, summary, link))
            if clipdict['false']:
                dir.Append(Function(DirectoryItem(VideoList, title="Full Episodes", thumb=image), videolist=clipdict['false']))
            if clipdict['true']:
                dir.Append(Function(DirectoryItem(VideoList, title="Clips", thumb=image), videolist=clipdict['true']))
    return dir
####################################################################################################
def VideoList(sender, videolist):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList')
    for vid in videolist:
        Log(vid[0])
        dir.Append(WebVideoItem(url=vid[3], title=vid[0], thumb=vid[1], summary=vid[2]))
    return dir