import requests
import os
import json
from time import sleep
from collections import deque
from pprint import pprint

# This whole thing gets detected under REMOTE API EVENT


# TODO: Convert into a Jdownloader class


def download_urls(dload_urls, DEST_FOLDER, JD_LOCALHOST=r"http://127.0.0.1:3128/"):
    local_dloader_address = JD_LOCALHOST

    # HACK: Check if Jdownloader is running
    dloader_status_url = local_dloader_address + "jdcheck.js"
    try:
        response = requests.get(dloader_status_url)
        # print("===" * 15)
        # print(f"> Downloader running status: {response.status_code}")
        # print("===" * 15)

    except Exception as e:
        print("===" * 15)
        print("> Possibly Jdownloader is not running!")
        print("===" * 15)
        print(e)
        return

    # HACK: Add a link and download if downloader is running
    if response.status_code == 200:
        print("===" * 15)

        # HACK: POSTMAN -> This works perfectly

        # endpoint -> http://127.0.0.1:3128/linkgrabberv2/addLinks

        # body (not parameters) -> Python requests : data => body | params => paremeters
        # {
        #     "params": [
        #         {
        #             "assignJobID": true,
        #             "autoExtract": false,
        #             "autostart": true,
        #             "deepDecrypt": false,
        #             "destinationFolder": "C:\\Users\\harsh\\Videos\\Youtube",
        #             "links": "https://www.youtube.com/watch?v=SR__amDl1c8",
        #             "overwritePackagizerRules": true,
        #             "priority": "DEFAULT",
        #         }
        #     ]
        # }

        # Linkgrabberv2 in python doesn't work
        add_links_url = JD_LOCALHOST + "linkgrabberv2/addLinks"
        dload_payload = {
            "params": [
                {
                    "assignJobID": True,
                    "autoExtract": False,
                    "autostart": True,
                    "deepDecrypt": False,
                    "destinationFolder": DEST_FOLDER,
                    "links": dload_urls,
                    "overwritePackagizerRules": True,
                    "priority": "DEFAULT",
                }
            ]
        }
        req_header = {"Content-Type": "application/json"}
        response = requests.post(
            url=add_links_url, json=dload_payload, headers=req_header
        )
        json_response = response.json()
        if response.status_code != 200:
            print("===" * 15)
            print(f"> Download request status: {response.status_code}")
            print(f"> Download request output: {json_response}")
            print("===" * 15)

        

        # print("===" * 15)
        # print(json_response)
        return (json_response["data"]["id"], response.status_code)



# TODO: Function to regularly detect changes in a youtube playlist
def detect_playlist_changes(
    API_KEY, playlistId, LOCAL_PLAYLIST_DIR, JD_LOCALHOST=r"http://127.0.0.1:3128/"
) -> bool:
    request_endpoint_info = r"https://www.googleapis.com/youtube/v3/playlists"
    request_endpoint_items = r"https://www.googleapis.com/youtube/v3/playlistItems"

    payload = {
        "part": "snippet",
        "id": f"{playlistId}",
        "key": f"{API_KEY}",
        "fields": "items(snippet/title)",  # Comment to get extra information about playlist
    }

    req_header = {"referer": r"http://localhost:4444"}
    print("===" * 15)

    print("> Initiating playlist metadata get...")
    playlist_response = requests.get(
        request_endpoint_info, params=payload, headers=req_header
    )
    json_playlist_response = playlist_response.json()
    playlist_title = json_playlist_response["items"][0]["snippet"]["title"]

    print(f"> Requested playlist's title: {playlist_title}")

    payload = {
        "part": "snippet",
        "fields": "items(kind),items(snippet/title),items(snippet(resourceId/kind)),items(snippet(resourceId/videoId))",
        "playlistId": f"{playlistId}",
        "key": f"{API_KEY}",
        "maxResults": "50",
    }

    print("===" * 15)
    print("> Initiating playlist items GET...")

    response = requests.get(request_endpoint_items, params=payload, headers=req_header)
    json_response = response.json()

    print(f"> Request status: {response.status_code}")
    print("===" * 15)

    try:
        print("> Storing playlist items API response...", end="")
        with open(os.getcwd() + "\\response.json", "w") as f:
            f.write(json.dumps(json_response, indent=4))
        print("Complete.")
    except Exception as e:
        print("> An error occured while storing API resonse!")
    print("===" * 15)

    # TODO: Iterate over all videos and
    # trigger downloads for those not present in local directory

    item_list = json_response["items"]
    item_count = 0
    video_count = 0

    playlist_path = LOCAL_PLAYLIST_DIR + f"\\{playlist_title}"
    if not (os.path.exists(playlist_path)):
        try:
            print("> Creating directory for playlist...", end="")
            os.mkdir(playlist_path)
            print("Complete.")
            print("===" * 15)
        except Exception as e:
            print("> An error occured while )creating dir for playlist!")
            print(e)

    erred_dloads = []
    added_dloads = deque([])

    print("> \tCOMMENCE PLAYLIST SYNC...")
    for item in item_list:
        print("+++" * 15)
        if item["kind"] == "youtube#playlistItem":
            item_snippet = item["snippet"]
            if item_snippet["resourceId"]["kind"] == "youtube#video":
                video_title = item_snippet["title"]
                video_id = item_snippet["resourceId"]["videoId"]
                video_path = playlist_path + f"\\{video_title}"

                # TODO: Trigger the download of above video link in jdownloader
                # at specified location

                if not (os.path.exists(video_path)):
                    video_url = "https://www.youtube.com/watch?v=" + video_id
                    print(f"> Downloading video [{video_title} : {video_url}]")

                    # Trigger download of above url in Jdownloader at video path
                    print("> Adding Link to downloader...", end="")
                    video_dload_jobId, status_code = download_urls(
                        dload_urls=video_url, DEST_FOLDER=video_path
                    )
                    if (status_code) != 200:
                        print(
                            f"> An error occured in downloading: [{video_title}: {video_dload_jobId}]"
                        )
                        erred_dloads.append(
                            {
                                "video_title": video_title,
                                "video_url": video_url,
                                "jobId": video_dload_jobId,
                            }
                        )
                    else:
                        added_dloads.append((video_dload_jobId, 1))
                        print("Done.")
                else:
                    print("> Video present at destination.")

                video_count += 1

            item_count += 1

    
    print("==="*15)
    print("Waiting to begin link status check...", end="")
    sleep(25)
    print("complete. Starting now!")
    print("==="*15)
    # # TODO: Check the links that have started downloading. POP THEM

    dloads_started = deque([])

    while added_dloads:
        print("> Scanning Link Grabber for pending items...")
        query_url = JD_LOCALHOST + "/linkgrabberv2/queryLinks"
        payload = {"queryParams": {"jobUUIDs":[str(added_dloads[0])]}}
        response = requests.get(query_url, params=json.dumps(payload))
        json_response = response.json()


        if response.status_code != 200:
            print("> Error scanning items in linkgrabber.")
        else:
            
            if len(json_response['data']) > 0:
                # Item is still in linkgrabber
                round = added_dloads[0][1]
                round += 1
                if round > 2:
                    print("> Add provision to shift into force download.")
                    # TODO: Items not erroring out, initiate force download and shift to dload_list
                    print("> Add provision to handle error occuring")
                    # TODO: Add provision to handle items which are erroring out
                    # Add them to erred items and pop from added_dloads
                else:
                    link = added_dloads.popleft()
                    added_dloads.append(link)
            else:
                # Job is not present in linkgrabber 
                dloading = added_dloads.popleft()
                dloads_started.append(dloading)
    
    print("> Linkgrabber Empty.")

    # Now check download list for all items:
        # if (): # Download started
        #     added_dloads.popleft()
        # else ():    # Attempt force download

    print("+++" * 15)
    print("> \tPLAYLIST SYNC COMPLETE.")
    print("===" * 15)
    print("> Total playlist items: ", item_count)
    print("> Total videos in playlist: ", video_count)
    print("===" * 15)

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
    # download_urls(dload_urls=urls, DEST_FOLDER="C:\\Users\\harsh\\Videos\\Youtube")
    playlistID = r"PLvkrU3vRXLfzaqM8QIK_NXPkhidjDdEMn"
    LOCAL_PLAYLIST_LOCATION = "C:\\Users\\harsh\\Videos\\Youtube"
    detect_playlist_changes(API_KEY=API_KEY, playlistId=playlistID, LOCAL_PLAYLIST_DIR=LOCAL_PLAYLIST_LOCATION)
