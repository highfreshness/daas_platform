# DaaS 환경 내 SaaS 애플리케이션 운영 관리를 위한 플랫폼 구축(백엔드)

## 프로젝트 설명
DaaS(Desktop as a Service) 환경에서 SaaS(Software as aService) 애플리케이션을 배포하고
이를 운영 및 관리하기 위한 통합 플랫폼 구축

## 목표 및 기능 
1. DaaS 구축을 위한 API 구현
2. SaaS 버전 관리를 위한 API 구현

## 기술 스택
Apache Guacamole==1.5.5<br>
Python==3.10.12<br>
fastapi==0.112.1<br>
uvicorn==0.30.6<br>
httpx==0.27.0<br>
pydantic==2.8.2<br>
PyGithub==2.4.0<br>
PyYAML==5.4.1<br>
Terraform-CLI==1.9.5<br>
AWS-CLI==2.17.37<br>

## 플로우 차트
### Backend
![백엔드-플로우차트](images/backend_logic.drawio.png)

### DaaS Connection Create
![DaaS-Connection](images/connection_post.drawio.png)

### DaaS Connection Delete
![DaaS-Connection](images/connection_delete.drawio.png)

### SaaS Version Control
![SaaS Version Control](images/version_control.drawio.png)

### Backend CI/CD
![Backend CI/CD](images/Jenkins_pipeline.png)

## 문의 
meteo0718@gmail.com