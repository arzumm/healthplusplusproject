import requests
import json
import time

def test():
    #base = r'http://localhost:8080/' 
    base = r'https://utopian-caldron-256501.appspot.com/'

    url = base + r'restart'
    requests.get(url)

    url = base + r'template'
    fil = open('/Users/dfan/Downloads/first.JPG', 'rb')
    img = {'pic': ('first.JPG',fil,'multipart/form-data',{'Expires': '0'})}
    requests.post(url, files=img)
    fil.close()
    
    time.sleep(5)

    url = base + r'templateMeta'
    data = {'params': {'date': '482,964,1084,1047', 'age': '451,1134,716,1236', 'how did you hear about this clinic': '1054,1290,2268,1382',
    'symptoms': '1165,1389,2614,1547', 'other practicioners': '396,1622,2644,1769', 'psychiatric hospitalizations': '386,1838,\
    2642,1965', 'ect': '858,1972,1274,2055', 'psychotherapy': '1884,2008,2672,2080', 'drug1': '415,2364,1157,2437', 'dose1': '1214,2377,\
    1883,2447', 'duration1': '1926,2373,2677,2454', 'drug2': '415,2437,1178,2509', 'dose2': '1184,2450,1848,2516', 'duration2': '1902,2453,\
    2666,2526', 'drug3': '439,2508,1157,2586', 'dose3': '1196,2519,1878,2591', 'duration3': '1943,2532,2657,2603'}, 'results': {}}
    headers = {'Content-type': 'application/json'}
    requests.post(url, data=json.dumps(data), headers=headers)

    time.sleep(5)

    url = base + r'newpic'
    fil = open('/Users/dfan/Downloads/second.JPG', 'rb')
    img = {'pic': ('second.JPG',fil,'multipart/form-data',{'Expires': '0'})}
    requests.post(url, files=img)
    fil.close()
    
    time.sleep(5)

    url = base + r'getdata'
    resp = requests.get(url)
    print(resp.content)
    print(resp.json())

if __name__ == '__main__':
    test()