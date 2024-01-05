# -*- coding: utf-8 -*-
import pandas as pd
import json
import asyncio
from utils import remove_parenthesis, api_main, juso_api,\
    process_juso_result, process_juso_result_strict, process_juso_result_strict2, \
    search_heuristic, remove_none, search_heuristic_remove_invalid
import time

def process_juso_api(juso_list):
    
    # (필요 시)괄호 없애기
    model_result = juso_list
    model_result = [remove_parenthesis(x) for x in model_result]
    loop = asyncio.get_event_loop()


    # Request Juso Api, method: strict2
    results = loop.run_until_complete(
        api_main(request_list=model_result, api_function=juso_api))
    juso_result = process_juso_result_strict2(model_result, results)
    wrong_idx = []
    for idx, res in enumerate(juso_result):
        if not res:
            wrong_idx.append(idx)


    # 결과가 안 나온 주소들에 대해 모델 결과에서 'XX면'을 없앤 뒤 juso api 검색 
    juso_result, wrong_idx = search_heuristic(answer_address_list=juso_result, address_list=remove_none(
        model_result), wrong_idx=wrong_idx, suffix="면",process_method="strict")
 
    # 결과가 안 나온 주소들에 대해 모델 결과에서 'XX동'을 없앤 뒤 juso api 검색   
    juso_result, wrong_utiidx = search_heuristic(answer_address_list=juso_result, address_list=remove_none(
        model_result), wrong_idx=wrong_idx, suffix="동",process_method="strict")

    # 결과가 안 나온 주소들에 대해 모델 결과에서 'XX구'을 없앤 뒤 juso api 검색
    juso_result, wrong_idx = search_heuristic(answer_address_list=juso_result, address_list=remove_none(
        model_result), wrong_idx=wrong_idx, suffix="구",process_method="strict")

    # 결과가 안 나온 주소들에 대해 모델 결과에서 'XX길'을 없앤 뒤 juso api 검색
    juso_result, wrong_idx = search_heuristic(answer_address_list=juso_result, address_list=remove_none(
        model_result), wrong_idx=wrong_idx, suffix="길",process_method="strict")

    # 결과가 안 나온 주소들에 대해 모델 결과에서 invalid한 token들이 있으면 없앤 뒤 juso api 검색
    juso_result, wrong_idx = search_heuristic_remove_invalid(
        answer_address_list=juso_result, address_list=model_result, wrong_idx=wrong_idx,process_method="strict")

    # None --> 답 없음
    juso_result = ["답 없음" if item is None else item for item in juso_result]

    return juso_result
