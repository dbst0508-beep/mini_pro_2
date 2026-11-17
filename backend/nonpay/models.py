from django.db import models #django의 모델 기능 불러오기

class NonpayItem(models.Model): # 비급여 항목 모델 (코드 조회 쪽에서 받아야함)
    #비급여 코드, 문자열 최대 20자,943건 중복 0 확인됨, PK  (비급여 항목을 npay_cd 하나로 구분 가능)
    npay_cd = models.CharField(max_length=20, primary_key=True)
    #항목 이름, TextFild로 글자 제한 X
    kor_nm = models.TextField()
    #중분류 코드 (ex. 1032A)
    mdiv_cd = models.CharField(max_length=20,blank=True)
    #중분류 이름 (ex. MRI-기본검사) 비울 수 있음
    mdiv_nm = models.TextField(blank=True)
    #소분류 코드 (ex. 1032A340)
    sdiv_cd = models.CharField(max_length=20, blank=True)
    #소분류 이름 (ex. 척추-전척추)
    sdiv_nm = models.TextField(blank=True)
    # 상세분류 코드
    dtl_div_cd = models.CharField(max_length=20,blank=True)
    # 상세분류 이름 (ex. 일반)
    dtl_div_nm = models.TextField(blank=True)
    #항목 설명, RAG 검색 대상, 없으면 빈문자열
    cmmt_txt = models.TextField(blank=True)
    #적용 개시 일자 (API의 20201126 > 날짜로 바꿔 저장)
    adt_fr_dd = models.DateField()
    #적용 종료 일자 (9999-12-31 = 현재 유효, 원본 그대로 )
    adt_end_dd = models.DateField()

    class Meta: #이 모델 전체 설정
        verbose_name = "비급여 항목"
        verbose_name_plural = "비급여 항목" #관리자 화면 설정

    def __str__(self): #이 객체를 글자로 보여 주는 함수
        return f"{self.npay_cd} {self.kor_nm}" #ex. "HE1130000MRI/척추 전척추/일반" 

#병원 모델 (요약, 상세 응답에서 받아감)
class Hospital(models.Model): 
    #암호화 요양기호, 병원 고유값 > PK (실제 길이 약 84자)
    ykiho = models.CharField(max_length=200, primary_key=True)
    #병원명 (ex. 중앙대학교 병원)
    yadm_nm = models.TextField()
    #종별코드 (ex. 01), 통계 그룹 코드와 연결 시 사용
    cl_cd = models.CharField(max_length=20)
    # 종별 이름 (ex. 상급 종합)
    cl_cd_nm = models.TextField()
    #시도 코드 (ex. 110000), 통계 그룹과 연결 시 사용
    sido_cd = models.CharField(max_length=20)
    #시도 이름 (ex. 서울)
    sido_cd_nm = models.TextField()
    #시군구 코드 (ex. 110008)
    sggu_cd = models.CharField(max_length=20)
    #시군구 이름 (ex. 동작구)
    sggu_cd_nm = models.TextField()
    # 병원 비급여 안내 주소, 답변의 출처, 없을 시 빈 문자열
    url_addr = models.TextField(blank=True)

    class Meta:
        verbose_name="병원"
        verbose_name_plural ="병원" 
    def __str__(self):
        return self.yadm_nm 

#병원 별 가격 (병원 상세 목록에서 받아감) 
class HospitalPrice(models.Model):
    #어느 병원의 가격인지 (Hospital과 연결), 데이터가 있으면 삭제 방지, 역참조 이름
    hospital = models.ForeignKey(Hospital, on_delete=models.PROTECT,related_name='prices')
    # 어느 항목의 가격인지 (NonpayItem과 연결)
    item = models.ForeignKey(NonpayItem, on_delete=models.PROTECT, related_name='hospital_prices')
    # 일련 번호, 병원 안에서 가격 한 줄 마다 고유
    sno = models.IntegerField()
    # 병원이 붙인 항목 이름 (ex. PFM(구치부))
    yadm_npay_cd_nm = models.TextField(blank=True)
    #현재 금액(원), DB값을 그대로 답변으로 출력
    cur_amt = models.IntegerField()
    #적용 개시 일자, 답변에 붙이는 기준일
    adt_fr_dd = models.DateField()
    #적용종료일자, 9999-12-31 = 현재 유효
    adt_end_dd = models.DateField()

    class Meta: 
        verbose_name = "병원별 가격"
        verbose_name_plural = "병원별 가격"
        #DB에 거는 규칙 , 이 칸들의 조합은 겹치면 안됨.
        constraints = [models.UniqueConstraint(
            #병원, 일련번호, 적용개시일자 
            fields=["hospital","sno","adt_fr_dd"],
            #규칙 이름 (DB안에서 구분용,겹치지 않게)
            name = "uniq_hospital_price",
        ),#규칙하나끝
        ] # 규칙 목록 끝
    
    def __str__(self):
        # ex. JDQ4... UM608F310  600000원
        return f"{self.hospital_id} {self.item_id} {self.cur_amt}원"

#가격 통계 (종별 + 지역을 세로로 풀어서 저장함)
class PriceStat(models.Model):
    KIND_CHOICES = [ #kind 칸에 들어갈 수 있는 값 목록
        ("cl", "종별"), #(DB에 저장되는 값, 화면에 보이는 이름)
        ("sido", "지역") #지역 통계
    ] # 목록 끝

    #어느 항목의 통계인지
    item =models.ForeignKey(NonpayItem,on_delete=models.PROTECT,related_name="stats")
    #구분 종별 또는 지역
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    #그룹 코드 = API 접미사 (Ushg, sl, all)
    group_cd = models.CharField(max_length=10)
    #기준일 (API의 stdDate)
    std_date = models.DateField()
    #최소 비용, 0이거나 태그 없으면 null
    prc_min = models.IntegerField(null=True,blank=True)
    #최대 비용
    prc_max = models.IntegerField(null=True,blank=True)
    #평균 비용
    prc_avg = models.IntegerField(null=True,blank=True)
    #중간 비용
    midd_avg = models.IntegerField(null=True,blank=True)

    class Meta:
        verbose_name = "가격 통계"
        verbose_name_plural = "가격 통계"
        constraints = [ #DB 규칙 목록
            models.UniqueConstraint ( # 여러 칸 조합이 겹치면 안됨
                # 항목 구분, 그룹 코드, 기준일 
                fields= ["item", "kind","group_cd","std_date"],
                #규칙이름
                name="uniq_price_stat",
            ), #규칙 하나 끝
        ] #규칙 목록 끝
    def __str__(self):
        return f"{self.item_id} {self.kind} {self.group_cd} {self.std_date} "
    