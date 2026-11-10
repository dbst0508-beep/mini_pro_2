import os #환경변수를 다루는 기본 모듈

from celery import Celery  # celery 앱을 만드는 클래스

#celery가 읽을 장고 설정 파일의 위치
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


app = Celery("config") #celery 앱 생성, 이름은 프로젝트 폴더 이름과 맞춤
#settings.py 에서 CELERY로 시작하는 값만 celery 설정으로 읽음
app.config_from_object("django.conf:settings", namespace="CELERY")
#INSTALLED_APPS 에 있는 tasks.py를 자동으로 찾아 등록함
app.autodiscover_tasks() 

@app.task #아래 함수를 celery가 뒤에서 실행할 수 있는 태스크로 등록
def ping(): #연결 확인용 태스크 
    return "pong" # 성공하면 redis를 거쳐 pong 반환
