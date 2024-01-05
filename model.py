import difflib
import json
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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
            address_hash[info]={}
        if sido not in address_hash[info]:
            address_hash[info][sido]=[]
        address_hash[info][sido].append(f'{sigungu} {doro} ({upmyundong})')
        if(i%10000==0):
            print(f'{i}번쨰 완료.')
    with open("./address_hash.json", "w",encoding='utf-8') as f:
        json.dump(address_hash, f,indent=4,ensure_ascii=False)
    return address_hash

def search_hash(address_target, address_hash): #BFS
    address_list = address_target.split(' ')
    last_idx = len(address_list)-1
    target = address_list[last_idx]
    sido = address_list[0]
    etc = address_list[1:last_idx]
    result='NONE'
    max = 0
    target_hash = address_hash[target] if target in address_hash.keys() else {}
    first = []
    if(sido=='None'):
        for key in target_hash.keys():
            first+=target_hash[key]
    else:
        
        if(sido in target_hash.keys()):
            first = target_hash[sido]
    second = []
    if('지하'+target in address_hash.keys() and '지하' not in target):
        target_hash = address_hash['지하'+target]
        if(sido=='None'):
            for key in target_hash.keys():
                second+=target_hash[key]
        else:
            if(sido in target_hash.keys()):
                second = target_hash[sido]
    elif(target.replace('지하','') in address_hash.keys() and '지하' in target):
        target_hash = address_hash[target.replace('지하','')]
        if(sido=='None'):
            for key in target_hash.keys():
                second+=target_hash[key]
        else:
            if(sido in target_hash.keys()):
                second = target_hash[sido]
    #여기가 지하여부 수정하는부분
    #만약 테스트하는 애가 지하가 안들어가있으면 지하를 붙인 애들도 같이 불러와서 유사도 검사를함
    answer_sido = ''
    try:
        for address in first+second:
            similarity = get_similarity(' '.join(address.split(' ')[0:len(address)-1]),' '.join(etc))
            if(similarity>max):
                result=address
                max = similarity
    except:
        return f'NONE {max}'
    
    result = result.split(' ')
    target= target.replace('-None','')
    front = ' '.join(result[0:len(result)-1])
    back = result[len(result)-1]
    if(max<0.1):
        return f'NONE {max}'

    return f'{answer_sido} {front} {target} {back} {max}'



def get_similarity(sentence1, sentence2):
    intersection_cardinality = len(set.intersection(*[set(sentence1), set(sentence2)]))
    union_cardinality = len(set.union(*[set(sentence1), set(sentence2)]))
    similar = intersection_cardinality / float(union_cardinality)
    return similar


