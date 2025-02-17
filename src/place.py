import re
import requests
from bs4 import BeautifulSoup
import json
import os

def isKakaoPlace(url):
    pattern1 = r'^https?://kko\.to/'
    pattern2 = r'^https?://place\.map\.kakao\.com/'
    pattern3 = r'^https?://map\.kakao\.com/'

    if re.search(pattern1, url) or re.search(pattern2, url) or re.search(pattern3, url):
        return True
    return False

def crawlingKakaoPlace(url):

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"
    }

    # 변경 url 받아서 처리
    response = requests.get(url, allow_redirects=False, headers=header)
    if(300 <= response.status_code < 400):
        url = response.headers['Location']

    place_id = None

    result = {
        "type" : "place",
        "page_url" : url,
        "site_name" : "KakaoMap",
    }

    #장소id 찾기
    match = re.search(r'https?:\/\/place.map.kakao.com\/(\d+)', url)
    if match:
        place_id = match.group(1)
    
    match = re.search(r'itemId=(\d+)', url)
    if match:
        place_id = match.group(1)

    response = requests.get("https://place.map.kakao.com/main/v/" + place_id, headers=header)

    place_obj = json.loads(response.text)

    wpointx = place_obj['basicInfo']['wpointx']
    wpointy = place_obj['basicInfo']['wpointy']

    transfer_point_api_headers = {
        'Authorization': 'KakaoAK ' + os.environ['KAKAO_API_KEY']
    }

    transfer_point_api_result = requests.get("https://dapi.kakao.com/v2/local/geo/transcoord.json?" + "x=" + str(wpointx) + "&y=" + str(wpointy) + "&input_coord=WCONGNAMUL&output_coord=WGS84", headers=transfer_point_api_headers)
    point_obj = json.loads(transfer_point_api_result.text)

    result['lat'] = point_obj['documents'][0]['y']
    result['lng'] = point_obj['documents'][0]['x']
    result['title'] = place_obj['basicInfo']['placenamefull']
    result['address'] = place_obj['basicInfo']['address']['region']['newaddrfullname'] + " " + place_obj['basicInfo']['address']['newaddr']['newaddrfull'] + " " + place_obj['basicInfo']['address']['addrdetail']
    result['phonenum'] = place_obj['basicInfo']['phonenum']
    result['zipcode'] = place_obj['basicInfo']['address']['newaddr']['bsizonno']
    result['homepage'] = place_obj['basicInfo']['homepage']
    result['category'] = place_obj['basicInfo']['category']['catename']

    return result

def isNaverPlace(url):
    pattern1 = r'https?:\/\/map.naver.com\/p\/entry\/place\/(\d+)'
    pattern2 = r'https?:\/\/naver.me\/\w+'
    
    if re.search(pattern1, url) or re.search(pattern2, url):
        return True
    return False

def crawlingNaverPlace(url):

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"
    }

    # 변경 url 받아서 처리
    response = requests.get(url, allow_redirects=False, headers=header)
    if(300 <= response.status_code < 400):
        url = response.headers['Location']

    result = {
        "type" : "place",
        "page_url" : url,
        "site_name" : "NaverMap",
    }    
    
    place_id = None

    #장소id 찾기
    match = re.search(r'https?:\/\/map.naver.com\/p\/entry\/place\/(\d+)', url)
    if match:
        place_id = match.group(1)

    response = requests.get("https://map.naver.com/p/api/place/summary/" + place_id, headers=header)

    place_obj = json.loads(response.text)

    result['title'] = place_obj['name']
    result['address'] = place_obj['roadAddress']
    result['lat'] = place_obj['y']
    result['lng'] = place_obj['x']
    result['phonenum'] = place_obj['buttons']['phone']
    result['category'] = place_obj['category']

    return result
