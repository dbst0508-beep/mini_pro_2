#Django 테스트 기본 클래스 (DB를 깨끗하게 되돌려 줌)
from django.test import TestCase
from datetime import date # 날짜 값을 만들기 위함
#DB 규칙 (중복 금지)를 어겼을 때 나는 에러
from django.db import IntegrityError
#테스트할 모델 불러오기
from .models import Hospital, HospitalPrice, NonpayItem # 

#HospitalPrice의 중복 금지 규칙
class HospitalPriceUniqueTest(TestCase):
    def setUp(self):  #각 테스트 직전 매번 실행되는 준비 함수
        self.hospital = Hospital.objects.create( #테스트용 병원 생성
            ykiho = "TEST_YKIHO", #암호화 값 대신 테스트용 값
            yadm_nm = "중앙대학교병원", # 병원명
            cl_cd = "01", cl_cd_nm = "상급종합", #종별
            sido_cd="110000", sido_cd_nm = "서울", #시도
            sggu_cd = "110008", sggu_cd_nm="동작구" #시군구
        ) # 병원 생성 완료
        self.item = NonpayItem.objects.create ( #테스트용 항목 생성
            npay_cd = "UM608F310", #PFM 크라운 코드
            kor_nm = "치과의 보철료/크라운/PFM",#항목 이름
            adt_fr_dd = date(2026, 9, 3), #적용개시일자
            adt_end_dd = date(9999, 12,31) #적용종료일자
        )

    def make_price(self, sno, amt): #가격 한 줄을 만드는 함수
        return HospitalPrice.objects.create( #가격 한줄 저장
            #같은 병원 같은 항목
            hospital = self.hospital, item=self.item, 
            #일련번호와 금액은 인자로
            sno = sno , cur_amt=amt, 
            #같은 적용 기간
            adt_fr_dd=date(2026, 9, 3), adt_end_dd = date(9999, 12, 31),
        )
    #테스트 1: 구치부 전치부처럼 sno만 다르면 둘 다 저장돼야함
    def test_same_item_different_sno_both_saved(self):
        #PFM 구치부 600,000원
        self.make_price(1248,600000)
        #PFM 전치부 650,000
        self.make_price(1247, 650000)
        # 두 줄 모두 저장됐는지 확인
        self.assertEqual(HospitalPrice.objects.count(),2)

    #테스트 2 : 병원 sno 적용 개시일자가 같으면 거부 돼야함
    def test_same_hospital_sno_date_rejected(self):
        #첫번째 저장은 성공
        self.make_price(1248, 600000)
        #이 블록 안에서 IntegrityError가 나야 통과
        with self.assertRaises(IntegrityError):
        #똑같은 조합으로 한번 더 저장 시도 > DB에서 막혀야함 
            self.make_price(1248, 600000)