from .celery import app as celery_app #Django가 켜질 때 같은 폴더의 celery를 불러와 celery 앱도 같이 준비함

__all__=("celery_app",) # 이 패키지에서 밖으로 내보낼 이름 목록

