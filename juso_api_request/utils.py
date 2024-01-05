import asyncio
import aiohttp
import json
import re
import pandas as pd
import difflib
from collections import deque

with open("config.json", "r") as config_file:
    config_data = json.load(config_file)
JUSO_API_KEY = config_data["JUSO_API_KEY"]
GOOGLE_API_KEY = config_data["GOOGLE_API_KEY"]
SEARCH_ENGINE_ID = config_data["SEARCH_ENGINE_ID"]


def check_if_all_token_included(query_string, target_string):

    target_split = target_string.split(" ")
    _split = query_string.split(" ")

    for token in _split:
        if token != "" and token not in target_split:
            return False

    return True


# return count, index
def same_number_addr_idx(building_numbers, target_building_number, count_jiha=False):
    if not target_building_number:
        return []

    if count_jiha:
        remove_jiha = target_building_number.replace("지하", "")
        ret = []
        for idx, building_number in enumerate(building_numbers):
            if remove_jiha in building_number:
                ret.append(idx)

        return ret

    else:
        ret = []
        for idx, building_number in enumerate(building_numbers):
            if target_building_number == building_number:
                ret.append(idx)

        return ret


def remove_parenthesis(input_str):
    if "(" not in input_str:
        return input_str
    idx = input_str.index("(")
    return input_str[:idx].strip()


def check_numeric_dash_jiha_string(input_str):
    numeric_pattern = r'^\d+$'
    numeric_dash_numeric_pattern = r'^\d+-\d+$'
    underground_numeric_pattern = r'^지하\d+$'
    underground_numeric_dash_numeric_pattern = r'^지하\d+-\d+$'

    if re.match(numeric_pattern, input_str) or re.match(numeric_dash_numeric_pattern, input_str) or re.match(underground_numeric_pattern, input_str) or re.match(underground_numeric_dash_numeric_pattern, input_str):
        return True

    return False


def get_building_number(addr):
    _split = addr.split(" ")
    for token in _split:
        if check_numeric_dash_jiha_string(token):
            return token

    return None


async def juso_api(session, query):
    API_KEY = JUSO_API_KEY
    print(query)
    url = f"https://business.juso.go.kr/addrlink/addrLinkApi.do?currentPage=1&countPerPage=10&keyword={query}&confmKey={API_KEY}&hstryYn=Y&resultType=json"
    async with session.get(url) as response:
        return await response.json()


async def api_main(request_list, api_function):

    # 여기에 주소 20000개 list 저장
    # addr_list = ["지하 1, 왕산로, 동대문구, 서울"] * 100

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        tasks = []
        for addr in request_list:
            task = asyncio.create_task(api_function(session, addr))
            tasks.append(task)

        results = await asyncio.gather(*tasks)

    return results


def process_juso_result(response_list):
    addr_list = []
    for response in response_list:
        try:
            if len(response['results']['juso']) >= 1:
                addr_list.append(response['results']['juso'][0]['roadAddr'])
            else:
                addr_list.append(None)
        except:
            addr_list.append(None)
    return addr_list


def process_juso_result_strict(response_list):
    addr_list = []
    for response in response_list:
        try:
            if response['results']['juso'] and len(response['results']['juso']) == 1:
                addr_list.append(response['results']['juso'][0]['roadAddr'])
            else:
                addr_list.append(None)
        except:
            addr_list.append(None)

    return addr_list


# request_list: 요청 보내는 주소 list
def process_juso_result_strict2(request_list, response_list):
    addr_list = []
    for idx, response in enumerate(response_list):
        try:
            _response = response["results"]["juso"]
            if not _response or len(_response) == 0:
                addr_list.append(None)
            else:
                # juso.go.kr api 결과 목록 (여려개일 수 있음)
                addr_candidates = list(set([x['roadAddr'] for x in _response]))
                target_building_addr = request_list[idx]  # 검색한 주소
                target_building_number = get_building_number(
                    target_building_addr)  # 검색한 주소의 건물본번
                building_numbers = [get_building_number(
                    x) for x in addr_candidates]  # api 결과 목록의 건물본번 목록

                if len(same_number_addr_idx(building_numbers=building_numbers, target_building_number=target_building_number)) >= 1:
                    # 건물본번이 같거나 지하여부만 다른 게 여러 개 존재시
                    # 우선 포함되지 않는 토큰 존재하는 것 걸러냄
                    # 한 개만 존재 시 정답, 그렇지 않으면 답없음
                    same_number_candidate_idx = same_number_addr_idx(
                        building_numbers=building_numbers, target_building_number=target_building_number)
                    addr_same_number_candidate = [
                        addr_candidates[x] for x in same_number_candidate_idx]
                    final_candidate = []
                    for candidate in addr_same_number_candidate:
                        if check_if_all_token_included(query_string=target_building_addr, target_string=candidate):
                            final_candidate.append(candidate)

                    if len(final_candidate) == 1:
                        addr_list.append(final_candidate[0])
                    else:
                        addr_list.append(None)
                    # most_similar = find_most_similar_string(target_string=target_building_addr, string_list=final_candidate,cutoff = 0.1)
                    # addr_list.append(most_similar)
                else:  # 없을 시 답없음
                    addr_list.append(None)
        except:
            addr_list.append(None)

    return addr_list


def remove_none(addr_list):
    _ret = [addr.replace("None", "").replace("  ", " ")
            if addr else "none" for addr in addr_list]
    for i in range(len(_ret)):

        if (_ret[i][-1] == "-"):
            _ret[i] = _ret[i][:-1]

    return _ret


def get_hash():
    with open("/content/drive/MyDrive/Colab Notebooks/leekiman/address_hash.json", "r", encoding='utf-8') as f:
        address_hash = json.load(f)
    return address_hash


def make_hash(datas):
    address_hash = {}
    for i in range(0, len(datas)):
        juso = datas.iloc[i]

        # GET/PREPROCESS COLUMNS
        sido = juso['sido']
        sigungu = juso['sigungu']
        upmyundong = juso['upmyundong']
        doro = juso['doro']
        info = ("지하" if juso['jiha'] == 1 else "") + str(juso['num1']) + \
            '-'+("None" if juso['num2'] == 0 else str(juso['num2']))

        # MAKE HASH
        if info not in address_hash:
            address_hash[info] = []
        address_hash[info].append(f'{sido} {sigungu} {upmyundong} {doro}')

        if (i % 100000 == 0):
            print(f'{i}번쨰 완료.')
    with open("/content/drive/MyDrive/Colab Notebooks/leekiman/address_hash.json", "w", encoding='utf-8') as f:
        json.dump(address_hash, f, indent=4, ensure_ascii=False)
    return address_hash


def search_hash(address_target, address_hash):  # BFS
    address_list = address_target.split(' ')
    last_idx = len(address_list)-1
    target = address_list[last_idx]
    etc = address_list[0:last_idx]
    result = 'NONE'
    max = 0

    try:
        result = find_most_similar_string(' '.join(etc), address_hash[target])
        return f'{result} {target}'
    except:
        return None

    try:
        for address in address_hash[target]:
            similarity = get_similarity(address, ' '.join(etc))
            if (similarity > max):
                result = address
                max = similarity
    except:
        return result
    return f'{result} {target}'


def find_most_similar_string(target_string, string_list, cutoff=0.1):
    closest_matches = difflib.get_close_matches(
        target_string, string_list, n=1, cutoff=cutoff)
    return closest_matches[0] if closest_matches else None


def get_similarity(target, match):
    similarity = difflib.SequenceMatcher(None, target, match).ratio()
    return similarity


# 최종 정답이 들어갈 리스트, 인풋 데이터 주소 리스트, 답 못맞춘 idx 리스트
def search_heuristic(answer_address_list, address_list, wrong_idx, suffix,process_method=process_juso_result_strict):
    ret_answer_address_list = answer_address_list.copy()
    address_list_to_search = []
    for i in wrong_idx:
        _split = address_list[i].split(" ")
        for token in _split:
            if token.endswith(suffix):
                _split.remove(token)
                break

        address_list_to_search.append(" ".join(_split))

    _loop = asyncio.get_event_loop()

    results = _loop.run_until_complete(
        api_main(request_list=address_list_to_search, api_function=juso_api))
    if process_method == "strict":
        _juso_result = process_juso_result_strict(results)
    elif process_method == "strict2":
        _juso_result = process_juso_result_strict2(address_list_to_search,results)

    ret_wrong_idx = []
    for i, res in enumerate(_juso_result):
        if res:
            ret_answer_address_list[wrong_idx[i]] = res
        else:
            ret_wrong_idx.append(wrong_idx[i])

    # 최종 정답이 들어갈 리스트(여기서 얻은 정답 채워서), 아직까지도 답 못맞춘 idx 리스트
    return ret_answer_address_list, ret_wrong_idx


# 최종 정답이 들어갈 리스트, 인풋 데이터 주소 리스트, 답 못맞춘 idx 리스트
def search_heuristic_remove_invalid(answer_address_list, address_list, wrong_idx,process_method="strict"):
    ret_answer_address_list = answer_address_list.copy()
    address_list_to_search = []
    valid_suffix_list = ["시", "도", "군", "구", "읍", "면", "동", "로", "길"]
    for i in wrong_idx:
        _split = address_list[i].split(" ")
        for token in _split:
            for suffix in valid_suffix_list:
                if not (token.endswith(suffix) or "-" in token or token.isdigit()):
                    _split.remove(token)
                    break

        address_list_to_search.append(" ".join(_split))

    _loop = asyncio.get_event_loop()

    results = _loop.run_until_complete(
        api_main(request_list=address_list_to_search, api_function=juso_api))
    #_juso_result = process_juso_result_strict2(address_list_to_search,results)
    if process_method == "strict":
        _juso_result = process_juso_result_strict(results)
    elif process_method == "strict2":
        _juso_result = process_juso_result_strict2(address_list_to_search,results)
    ret_wrong_idx = []
    for i, res in enumerate(_juso_result):
        if res:
            ret_answer_address_list[wrong_idx[i]] = res
        else:
            ret_wrong_idx.append(wrong_idx[i])

    # 최종 정답이 들어갈 리스트(여기서 얻은 정답 채워서), 아직까지도 답 못맞춘 idx 리스트
    return ret_answer_address_list, ret_wrong_idx


def hash_heuristic(answer_address_list, address_list, wrong_idx):
    ret_answer_address_list = answer_address_list.copy()
    address_list_to_search = [address_list[i] for i in wrong_idx]
    address_list_for_juso = []

    for addr in address_list_to_search:
        _searched = search_hash(address_target=addr, address_hash=address_hash)
        address_list_for_juso.append(_searched)

    _loop = asyncio.get_event_loop()
    # print(address_list_for_juso)
    results = _loop.run_until_complete(api_main(
        request_list=remove_none(address_list_for_juso), api_function=juso_api))

    _juso_result = process_juso_result(results)
    ret_wrong_idx = []
    for i, res in enumerate(_juso_result):
        if res:
            ret_answer_address_list[wrong_idx[i]] = res
        else:
            ret_wrong_idx.append(wrong_idx[i])

    return ret_answer_address_list, ret_wrong_idx
