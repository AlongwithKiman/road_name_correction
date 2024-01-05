import difflib
import json
from collections import deque
def get_hash():
    with open("./address_hash.json", "r",encoding='utf-8') as f:
        address_hash=json.load(f)
    return address_hash

def make_hash(datas):
    address_hash = {}
    for i in range(0,len(datas)):
        juso = datas.iloc[i]

        #GET/PREPROCESS COLUMNS
        sido = juso['sido']
        sigungu = juso['sigungu']
        upmyundong = juso['upmyundong']
        doro = juso['doro']
        info = ("지하" if juso['jiha'] == 1 else "") + str(juso['num1'])+'-'+("None" if juso['num2'] == 0 else str(juso['num2']))

        #MAKE HASH
        if info not in address_hash:
            address_hash[info]=[]
        address_hash[info].append(f'{sido} {sigungu} {upmyundong} {doro}')
        print(f'{i}번쨰 완료.')
    with open("./address_hash.json", "w",encoding='utf-8') as f:
        json.dump(address_hash, f,indent=4,ensure_ascii=False)
    return address_hash

def search_hash(address_target, address_hash): #BFS
    address_list = address_target.split(' ')
    last_idx = len(address_list)-1
    target = address_list[last_idx]
    etc = address_list[0:last_idx]
    result='NONE'
    max = 0
    try:
        for address in address_hash[target]:
            similarity = get_similarity(address,' '.join(etc))
            if(similarity>max):
                result=address
                max = similarity
    except:
        return result
    return f'{result} {target}'



def get_similarity(target,match):
    similarity = difflib.SequenceMatcher(None, target, match).ratio()
    return similarity 