# 심평원 비급여진료비정보서비스 OpenAPI 요약

출처: 공공데이터포털 OpenAPI 활용가이드 (건강보험심사평가원, 비급여진료비정보서비스, 마지막 개정 2019-09-27)
원본 문서는 오래됐고 예시 응답에 오타가 있다. **필드 이름은 실제 응답을 기준으로 확인한다.**

## 공통

- 기본 URL: `http://apis.data.go.kr/B551182/nonPaymentDamtInfoService/{오퍼레이션}`
- 응답 형식: XML (`<response><header>...</header><body><items><item>...</item></items><numOfRows/><pageNo/><totalCount/></body></response>`)
- 공통 요청 파라미터

| 이름 | 설명 | 필수 |
|---|---|---|
| ServiceKey | 공공데이터포털 인증키 (requests params로 넘길 때는 Decoding 키) | 필수 |
| pageNo | 페이지 번호 | 선택 |
| numOfRows | 한 페이지 결과 수 (항목 크기 2자리) | 선택 |

- 공통 응답: `resultCode`(00 = 정상), `resultMsg`, `numOfRows`, `pageNo`, `totalCount`
- 평균 응답 500ms, 초당 최대 30건
- 오퍼레이션 1, 2번은 2016년 2월 이전 데이터라 사용하지 않는다

## 3. 비급여항목코드조회 (2016.3 이후)

- 오퍼레이션: `getNonPaymentItemCodeList2`
- 요청 파라미터: 공통만
- 쓰임: 항목 목록과 설명. 설명(`cmmtTxt`)은 RAG 검색 대상

| 응답 필드 | 뜻 | 예시 |
|---|---|---|
| npayCd | 비급여코드 | RZ6410000 |
| npayKorNm | 비급여 한글명 | 처치 및 수술료/보조생식술-난자채취 및 처리 |
| npayMdivCd / npayMdivCdNm | 중분류 코드 / 이름 | P / 처치 및 수술료 |
| npaySdivCd / npaySdivCdNm | 소분류 코드 / 이름 | P12 / 보조생식술-난자채취 및 처리 |
| npayDtlDivCd / npayDtlDivCdNm | 상세분류 코드 / 이름 | P12 / 보조생식술-난자채취 및 처리 |
| cmmtTxt | 상세분류 설명 (비어 있을 수 있음) | 양측기준이며, 초음파유도료 포함입니다. |
| adtFrDd | 적용개시일자 (YYYYMMDD) | 20180402 |
| adtEndDd | 적용종료일자 (99991231 = 현재 유효) | 99991231 |

주의: 예시 응답에 같은 npayCd가 두 번 나온다. 저장할 때 중복을 거른다.

## 4. 비급여항목병원목록요약 (2016.3 이후)

- 오퍼레이션: `getNonPaymentItemHospList2`
- 쓰임: 항목 하나를 넣으면 그 항목이 있는 병원 목록과 병원별 최소, 최대 가격. 여기서 병원 코드(ykiho)를 얻는다

| 요청 파라미터 | 뜻 | 필수 |
|---|---|---|
| itemCd | 항목코드 (예: ABZ010001) | 필수 |
| clCd | 종별코드 ("" 전체, 01 상급종합, 11 종합병원, 41 치과병원) | 선택 |
| sidoCd | 시도코드 (예: 110000 서울) | 선택 |
| sgguCd | 시군구코드 (예: 110007) | 선택 |
| yadmNm | 병원명 | 선택 |
| searchWrd | 비급여 항목명 검색어 | 선택 |

| 응답 필드 | 뜻 | 예시 |
|---|---|---|
| ykiho | 암호화된 요양기호 (병원 고유값) | JDQ4MTg4... |
| yadmNm | 병원명 | 경희대학교병원 |
| clCd / clCdNm | 종별 코드 / 이름 | 01 / 상급종합 |
| sidoCd / sidoCdNm | 시도 코드 / 이름 | 110000 / 서울 |
| sgguCd / sgguCdNm | 시군구 코드 / 이름 | 110007 / 동대문구 |
| urlAddr | 병원 비급여 안내 URL | http://... |
| npayCd, npayKorNm | 비급여코드, 한글명 | ABZ010001, 상급병실료차액/1인실 |
| npayMdivCd(Nm), npaySdivCd(Nm), npayDtlDivCd(Nm) | 분류 코드와 이름 | |
| adtFrDd, adtEndDd | 적용개시일자, 적용종료일자 | 20180402, 99991231 |
| minPrc | 이 병원의 최소가격 | 206000 |
| maxPrc | 이 병원의 최대비용 | 360000 |

## 5. 비급여항목병원목록상세 (2016.3 이후)

- 오퍼레이션: `getNonPaymentItemHospDtlList`
- 쓰임: 병원 하나의 모든 비급여 항목 가격
- 주의: **항목코드로 거를 수 없다.** 병원 하나에 항목이 200개 넘게 올 수 있다(예시 totalCount 229). 받은 뒤 필요한 항목만 남긴다

| 요청 파라미터 | 뜻 | 필수 |
|---|---|---|
| ykiho | 암호화된 요양기호 | 필수 |
| clCd | 종별코드 | 선택 |
| sidoCd | 시도코드 | 선택 |
| sgguCd | 시군구코드 | 선택 |
| yadmNm | 병원명 | 선택 |

| 응답 필드 | 뜻 | 예시 |
|---|---|---|
| ykiho, yadmNm | 병원 코드, 병원명 | 중앙대학교병원 |
| clCd / clCdNm | 종별 | 01 / 상급종합 |
| sidoCd / sidoCdNm | 시도 | 110000 / 서울 |
| sgguCd / sgguCdNm | 시군구 | 110008 / 동작구 |
| urlAddr | 병원 URL | http://... |
| sno | 일련번호 | 240 |
| npayCd | 비급여코드 | HE1180000 |
| npayKorNm | 비급여 한글명 | MRI진단료/근골격계 /고관절 |
| yadmNpayCdNm | 병원이 붙인 항목 이름 | Hip MRI |
| adtFrDd, adtEndDd | 적용개시일자, 적용종료일자 | 20180402, 99991231 |
| curAmt | 현재금액 | 739000 |

## 6. 비급여진료비용종별정보

- 오퍼레이션: `getNonPaymentItemClcdList`
- 요청 파라미터: 공통만
- 쓰임: 항목별로 병원 종별 최소, 최대, 평균, 중간 가격 (통계)
- 형태: **한 줄에 종별마다 칸이 따로 있는 옆으로 긴 형태**

| 응답 필드 | 뜻 |
|---|---|
| npayCd, npayKorNm | 비급여코드, 이름 |
| stdDate | 적용시작일 (YYYYMMDD) |
| prcMax{종별} | 최대비용 |
| prcMin{종별} | 최소비용 |
| prcAvg{종별} | 평균비용 |
| middAvg{종별} | 중간비용 |

종별 접미사: `All` 전체, `Usgh` 상급종합, `Gnhp` 종합병원, `Dety` 치과병원, `Cmdc` 한방병원, `Hosp` 병원, `Recu` 요양병원
예: `prcMaxUsgh` = 상급종합 최대비용

## 7. 비급여진료비용지역별정보

- 오퍼레이션: `getNonPaymentItemSidoCdList`
- 요청 파라미터: 공통만
- 쓰임: 항목별로 시도별 최소, 최대, 평균, 중간 가격 (통계)
- 형태: **한 줄에 시도마다 칸이 따로 있는 옆으로 긴 형태** (시도 18개 × 통계 4개)

| 응답 필드 | 뜻 |
|---|---|
| npayCd, npayKorNm | 비급여코드, 이름 |
| stdDate | 적용시작일 (YYYYMMDD) |
| prcMax{시도} | 최대비용 |
| prcMin{시도} | 최소비용 |
| prcAvg{시도} | 평균비용 |
| middAvg{시도} | 중간비용 |

시도 접미사: `All` 전체, `Sl` 서울, `Ps` 부산, `Ich` 인천, `Tg` 대구, `Kw` 광주, `Dj` 대전, `Usn` 울산, `Kyg` 경기, `Kaw` 강원, `Ccbk` 충북, `Ccn` 충남, `Clb` 전북, `Cln` 전남, `Ksb` 경북, `Ksn` 경남, `Chj` 제주, `Sejong` 세종
예: `prcAvgSl` = 서울 평균비용

## ERD와 수집에 반영할 점

1. 6번, 7번의 옆으로 긴 형태는 그대로 테이블로 만들지 않는다. (항목, 시도 또는 종별, 기준일, 최소, 최대, 평균, 중간) 형태로 한 줄씩 풀어서 저장한다. 시도 접미사와 시도 코드(110000 등)를 이어 주는 표가 필요하다
2. 통계에서 **가격 0은 "0원"이 아니라 "데이터 없음"**이다 (예시에서 대구만 값이 있고 나머지 시도는 전부 0). 0은 NULL로 저장한다
3. 날짜는 YYYYMMDD 문자열로 온다. 날짜 형식으로 바꾸고, 99991231은 "현재 유효"로 처리한다
4. 병원별 가격 수집 순서: 3번으로 항목 목록 → 고른 항목으로 4번 호출해 병원 목록(ykiho) → 병원마다 5번 호출 → 필요한 항목만 남겨 저장
5. 5번은 병원 하나에 여러 페이지가 나올 수 있어 병원당 여러 번 호출한다. 개발계정 호출 한도(10,000건)를 넘지 않게 호출 수를 미리 계산한다
6. 항목 코드가 중복으로 올 수 있어 저장 전에 거른다
7. 예시 응답에 `TNPAY_DTL_DIV_CD_NMD`, `dovCd1Nm` 같은 오타 필드가 있다. 실제 응답에서 필드 이름을 확인한다
8. 이 API는 병원급 이상 의료기관만 포함한다
