# daehancon
## 0. 대회 설명

* 주요 과제 : 다양한 형식의 비정제 영문 주소를 활용하여 한국 주소 체계에 맞는 영문주소 AI번역 시스템 구현

* 주어진 데이터 : 총 5개 대표 조합 케이스 제공 (영문주소 + 배송요구사항("문 앞"), 영문주소 + 한글주소, 영문주소 + 특수기호, 표준 주소 체계 무시, 오입력)

* 정답 데이터 형식 : https://www.juso.go.kr에서 지원하는 한국 도로명 주소 형식이고, 특정 주소가 해당 웹사이트에서 검색이 불가능한 경우에는 ‘답 없음' 형식도 존재.

* 채점 방식 : Input으로 주어진 영문 주소를 번역한 결과가, https://www.juso.go.kr/ 에서의 존재 여부와 형식 일치 여부


## 1. 콘다 환경 설정 및 필요한 라이브러리 설치

```
conda create -n momal python=3.9
conda activate momal
```

CUDA 버전과 개발 환경에 맞게 Pytorch를 설치해주세요.
자세한 내용은 https://pytorch.org/ 를 참고하세요.

```
#For CUDA 10.x
pip3 install torch torchvision torchaudio
#For CUDA 11.x
pip3 install torch==1.9.0+cu111 torchvision==0.10.0+cu111 torchaudio==0.9.0 -f https://download.pytorch.org/whl/torch_stable.html
```

마지막으로 추가 라이브러리를 설치합니다.
```
pip install -r requirements.txt
```

## 2. Flask 서버 설정

본 AI서버는 Flask로 제공됩니다.
다음은 API 명세입니다.
API_URL:5000/api, POST
* request
  ```
  {
    requestList: {seq:String, requestAddress:String]...}[]
  }
  ```
* response (성공시)
  ```
  {
    HEADER:{
        "RESULT_CODE": "S",
        "RESULT_MSG": "Success"
    }
    BODY:{seq:String, requestAddress:String]...}[]
  }
  ```
