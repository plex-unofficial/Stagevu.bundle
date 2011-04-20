# Created by bitter 

from PMS import XML
from PMS.Decorators import handler
from PMS.Objects import *
from PMS.Shortcuts import R, L

from urllib import urlencode

# urls
URL                     = "http://stagevu.com"
VIDEOS_URL              = URL + "/videos"
SEARCH_URL              = URL + "/search"

# text
SEARCH_TEXT             = L("Search Stagevu")
POPULAR_TEXT            = L("Popular Videos")
RECENTLY_ADDED_TEXT     = L("Recently Added")
HIGHEST_RATED_TEXT      = L("Highest Rated")

MORE_TEXT               = L("More...")

# Init ########################################################################
def Start():

    Plugin.AddViewGroup("InfoList", viewMode = "InfoList", mediaType="items")

    MediaContainer.art       = R('art-default.png')
    MediaContainer.viewGroup = "InfoList"
    MediaContainer.title1    = "Stagevu"


# Main ########################################################################
@handler('/video/stagevu', 'Stagevu')
def main_menu(sender=None):
    dir = MediaContainer()
    dir.Append(Function(DirectoryItem(browse, POPULAR_TEXT), orderby='dviews'))
    dir.Append(Function(DirectoryItem(browse, RECENTLY_ADDED_TEXT), orderby='submittime'))
    dir.Append(Function(DirectoryItem(browse, HIGHEST_RATED_TEXT), orderby='rating'))
    dir.Append(Function(InputDirectoryItem(query_video_items,
                                           title=SEARCH_TEXT,
                                           prompt=SEARCH_TEXT,
                                           thumb=R('search.png'))))
    return dir

def browse(sender, orderby='dviews', query=None):
    dir = MediaContainer(title2=sender.itemTitle)
    html = XML.ElementFromURL(VIDEOS_URL, isHTML = True)
    for link in html.xpath("//div[@id='topnav']/a"):
        category=link.text
        dir.Append(Function(DirectoryItem(render_video_items, title=category),
                            title=sender.itemTitle + " - " + category, 
                            query={'category':category, 'sortby':orderby}))
    return dir

def query_video_items(sender, query=None, page=1):
    return render_video_items(sender, query, {'for':query, 'in':'videos'})

# Display video items on page
def render_video_items(sender=None, title=None, query={}, page=1):
    dir = MediaContainer(title2=title)
    url = SEARCH_URL + "?" + urlencode(query) + "&" + urlencode({'page':page})
    html = XML.ElementFromURL(url, isHTML = True)
    
    for item in html.xpath("//div[@class='resultcont']"):
        videoLink   = item.xpath("h2/a")
        videoTitle  = get_text(videoLink)
        videoUrl    = get_attribute(videoLink,'href')
        if videoTitle and videoUrl:
            videoDescription = get_text(item.xpath("p"))
            videoThumbnail   = get_attribute(item.xpath("a/img"), 'src')
            dir.Append(VideoItem(resolve_video_url(videoUrl),
                                 title=videoTitle,
                                 summary=videoDescription,
                                 thumb=videoThumbnail))
    if not html.xpath("//a[@class='oldest current' and text()='Last']"):
        dir.Append(Function(DirectoryItem(render_video_items, title=MORE_TEXT),
                            title=title, query=query, page=page+1))
    return dir

def resolve_video_url(videoUrl):
    page = XML.ElementFromURL(videoUrl, isHTML = True)
    return get_attribute(page.xpath("//embed[@type='video/divx']"), 'src')


# Utils #######################################################################

def get_attribute(itemlist, attribute):
    return itemlist[0].get(attribute) if len(itemlist) else None

def get_text(itemlist):
    return itemlist[0].text if len(itemlist) else None
