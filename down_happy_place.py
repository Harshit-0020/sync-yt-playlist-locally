import requests
import os
import json

# This whole thing gets detected under REMOTE API EVENT


# TODO: Convert into a Jdownloader class


def download_urls(dload_urls, JD_LOCALHOST=r"http://127.0.0.1:3128/"):
    local_dloader_address = JD_LOCALHOST

    # HACK: Check if Jdownloader is running
    dloader_status_url = local_dloader_address + "jdcheck.js"
    try:
        response = requests.get(dloader_status_url)
        print("===" * 15)
        print(f"> Downloader running status: {response.status_code}")
        print("===" * 15)

    except Exception as e:
        print("===" * 15)
        print("> Possibly Jdownloader is not running!")
        print("===" * 15)
        print(e)
        return

    # HACK: Add a link and download if downloader is running
    if response.status_code == 200:
        print("===" * 15)
        add_links_url = JD_LOCALHOST + r"linkcollector/addLinksAndStartDownload"
        dload_payload = {
            "links": dload_urls,
            "packageName": "",
            "extractPassword": "",
            "downloadPassword": "",
        }
        response = requests.post(url=add_links_url, data=dload_payload)
        print(f"> Download request status: {response.status_code}")
        print(f"> Download request output: {response.json()}")
        print("===" * 15)


# TODO: Function to regularly detect changes in a youtube playlist
def detect_playlist_changes(API_KEY, playlistId) -> bool:
    request_endpoint_info = r"https://www.googleapis.com/youtube/v3/playlists"
    request_endpoint_items = r"https://www.googleapis.com/youtube/v3/playlistItems"

    payload = {
        "part": "snippet",
        "id": f"{playlistId}",
        "key": f"{API_KEY}",
        "fields":"items(snippet/title)" # Comment to get extra information about playlist
    }
    
    req_header = {"referer": r"http://localhost:4444"}
    print("===" * 15)

    print("> Initiating playlist metadata get...")
    playlist_response = requests.get(request_endpoint_info, params=payload,headers=req_header)
    json_playlist_response = playlist_response.json()
    playlist_title = json_playlist_response['items'][0]['snippet']['title']
    
    print(f"> Requested playlist's title: {playlist_title}")


    payload = {
        "part": "snippet",
        "fields":"items(kind),items(snippet/title),items(snippet(resourceId/kind)),items(snippet(resourceId/videoId))",
        "playlistId": f"{playlistId}",
        "key": f"{API_KEY}",
        "maxResults":"50"
    }

    print("==="*15)
    print("> Initiating playlist items GET...")
    
    response = requests.get(request_endpoint_items, params=payload,headers=req_header)
    json_response = response.json()

    print(f"> Request status: {response.status_code}")
    print("==="*15)

    with open("./response.json", "w") as f:
        f.write(json.dumps(json_response,indent=4))
    
    # TODO: Iterate over all videos and 
    # trigger downloads for those not present in local directory
    # video_list = json_response['items']

    # # Check if video present on system or not:
    # for video in video_list:
    #     if os.path.exists("C:\\Users\\harsh\\Videos\\"):

    #         for root, dirs, files in os.walk("C:\\Users\\harsh\\Videos"):
    #             if 

    return False


# TODO: Regularly perform downloads

if __name__ == "__main__":
    urls = r"https://www.youtube.com/watch?v=SR__amDl1c8"
    API_KEY = r"AIzaSyAbfXRWxZ-EujvNmfHaFxE0TZgIOwmNr3g"
    # download_urls(dload_urls=urls)
    playlistID = r"PLvkrU3vRXLfzaqM8QIK_NXPkhidjDdEMn"
    detect_playlist_changes(API_KEY=API_KEY, playlistId=playlistID)
