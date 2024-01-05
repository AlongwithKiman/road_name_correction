import pandas as pd
from model import get_similarity
from model import search_hash
from model import get_hash

from model import make_hash
print(get_similarity('약령시로', '약년시로'))
# address_total = pd.read_csv("./juso_sorted_test.csv")
print('모든 주소를 로딩중입니다..')
# address_total = pd.read_csv("../juso_sorted.csv")
# address_hash = make_hash(datas=address_total)
address_hash = get_hash()
print('주소 로딩 완료.')
address_example = pd.read_csv("../results.csv")['example'][0:108] #GET TEST RESULT EXAMPLE

# print('해시 생성중..')


for idx in range(0,len(address_example)):
    # print(f'{address_example.iloc[idx]}->',end='')
    print(idx+2,end=' ')
    print(address_example.iloc[idx],'->',end=' ')
    print(search_hash(address_target=address_example.iloc[idx], address_hash=address_hash))
