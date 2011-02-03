# PMS plugin framework
import re

####################################################################################################

VIDEO_PREFIX = "/video/nickjr"

NAMESPACES = {'media':'http://search.yahoo.com/mrss/', 'mediaad':'http://blip.tv/mediaad'}

NICK_ROOT            = "http://www.nickjr.com"
NICK_SHOWS_LIST      = "http://www.nickjr.com/common/data/kids/get-kids-config-data.jhtml?fsd=/dynaboss&urlAlias=kids-video-landing&af=false"
RSS_FEED             = "http://www.nickjr.com/dynamo/video/data/mrssGen.jhtml?type=network&loc=default&hub=kids&mode=playlist&dartSite=nickjr.playtime.nol&mgid=mgid:cms:item:nickjr.com:%s&demo=null&block=true"

NAME = L('Title')
ART  = 'art-default.png'
ICON = 'icon-default.png'

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, L('VideoTitle'), ICON, ART)
    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")
    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)

####################################################################################################
def MainMenu():
    dir = MediaContainer(mediaType='video', viewGroup='List')
    content = JSON.ObjectFromURL(NICK_SHOWS_LIST)
    for item in content['config']['promos'][0]['items']:
        title = item['title'].replace('&amp;', '&')
        image = NICK_ROOT + item['thumbnail']
        link = NICK_ROOT + item['link']
        dir.Append(Function(DirectoryItem(ShowList, title, thumb=image), image = image, pageUrl = link))
    return dir

####################################################################################################
def ShowList(sender, image, pageUrl):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup='List')
    clipdict = {}
    clipdict['false'] = []
    clipdict['true'] = []
    showcontent = HTTP.Request(pageUrl).content
    m = re.compile('KIDS.add."cmsId", ".+?".;').findall(showcontent)
    cmsid = m[0].split('"')[3]
    url = RSS_FEED % (cmsid)
    feedcontent = XML.ElementFromURL(url) #.xpath("//item")
    for item in feedcontent.xpath("//item"): #[0].xpath("..//media:category[@label='full']", namespaces=NAMESPACES):
        title = item.xpath(".//media:title", namespaces=NAMESPACES)[0].text
        link = item.xpath('.//media:player', namespaces=NAMESPACES)[0].get('url')
        thumb = item.xpath('.//media:thumbnail', namespaces=NAMESPACES)[0].get('url')
        duration = int(item.xpath('.//media:content', namespaces=NAMESPACES)[0].get('duration').replace(':', '')) * 1000   ##ADDED replace(':', '') FOR PROTECTION AGAINST A FEW VIDEOS THAT HAVE "MIN:SEC" RATHER THAN JUST "SEC" 
        summary = item.xpath('.//media:description', namespaces=NAMESPACES)[0].text
        if item[0].xpath("..//media:category[@label='full']", namespaces=NAMESPACES):
            clipdict['false'].append((title, thumb, summary, link, duration))
        elif item[0].xpath("..//media:category[@label='Playtime Clip']", namespaces=NAMESPACES):
            clipdict['true'].append((title, thumb, summary, link, duration))
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
        dir.Append(WebVideoItem(url=vid[3], title=vid[0], thumb=vid[1], summary=vid[2], duration=vid[4]))
    return dir