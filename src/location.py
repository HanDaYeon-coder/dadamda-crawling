import re
import requests
from bs4 import BeautifulSoup
import json

def isKakaoLocation(url):
    pattern1 = r'^https?://kko\.to/'
    pattern2 = r'^https?://place\.map\.kakao\.com/'
    pattern3 = r'^https?://map\.kakao\.com/'

    if re.search(pattern1, url) or re.search(pattern2, url) or re.search(pattern3, url):
        return True
    return False

def isNaverLocation(url):
    pattern1 = r'https?:\/\/map.naver.com\/p\/entry\/place\/(\d+)'
    pattern2 = r'https?:\/\/naver.me\/\w+'
    
    if re.search(pattern1, url) or re.search(pattern2, url):
        return True
    return False

def crawlingKakaoLocation(url):

    result = {}

    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3"
    }

    # 변경 url 받아서 처리
    response = requests.get(url, allow_redirects=False, headers=header)
    if(300 <= response.status_code < 400):
        url = response.headers['Location']

    place_id = None

    #장소id 찾기
    match = re.search(r'https?:\/\/place.map.kakao.com\/(\d+)', url)
    if match:
        place_id = match.group(1)
    
    match = re.search(r'itemId=(\d+)', url)
    if match:
        place_id = match.group(1)

    response = requests.get("https://place.map.kakao.com/main/v/" + place_id, headers=header)

    location_obj = json.loads(response.text)

    result['title'] = location_obj['basicInfo']['address']['region']['newaddrfullname'] + " " + location_obj['basicInfo']['address']['newaddr']['newaddrfull'] + " " + location_obj['basicInfo']['address']['addrdetail']
    result['wpointx'] = location_obj['basicInfo']['wpointx']
    result['wpointy'] = location_obj['basicInfo']['wpointy']
    result['phonenum'] = location_obj['basicInfo']['phonenum']
    result['bunzino'] = location_obj['basicInfo']['address']['newaddr']['bsizonno']
    result['homepage'] = location_obj['basicInfo']['homepage']
    result['category'] = location_obj['basicInfo']['category']['catename']

    return result