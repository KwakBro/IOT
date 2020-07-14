#2019 교내 IoT공모전 참가작  
![image](https://user-images.githubusercontent.com/68212288/87460190-69e7d480-c647-11ea-91ac-7bcf450ac948.png)

배경
===
캠핑장 및 글램핑장에서 난방기구에 의한 CO 중독과 취침시의 화재 발생은  
생각보다 많은 사람들의 목숨을 앗아갔음.  
때문에 이와같은 위급 상황에서의 자동 경보/환기/신고 시스템을 통해  
캠핑장에서의 인명 피해를 줄이고자 함.

-------------------------------------------------------------------------

구조
===
n개의 Client < 텐트, 캠프 > + 각 Client의 주인 < 이용객 >  
1개의 Server < 관리자 >

-------------------------------------------------------------------------

사용 HW
===  
+ CO 측정 - [MQ-2 Smoke/LPG/CO Gas Sensor Module](http://sandboxelectronics.com/?p=165 "go to product specification")  

    아날로그 전압값을 받기 위한 MCP3008 칩 [SPI interface 사용]  
    
+ O2 측정 - [LuminOx Optical Oxygen Sensors](https://www.sstsensing.com/product/luminox-optical-oxygen-sensors-2/ "go to product spec")  

    UART serial 이용.
    

+ Raspberry PI 3  
+ LED, FAN, BOOZER  

-------------------------------------------------------------------------

기여도
===
Raspberry Pi 와 Sensor 들의 Serial Communication 구현 및 데이터 정형화  
Client 측의 RX, TX Thread 구성.  
Application의 제어기능 위한 Control 프로토콜 제안 및 기능 구현

-------------------------------------------------------------------------

기능
===
![image](https://user-images.githubusercontent.com/68212288/87463004-bd5c2180-c64b-11ea-9da7-393d864424d7.png)  
+ Client는 각자의 CO, 산소 수치를 실시간으로 전송한다  
+ Client와 연결된 주인은 Mobile Application을 이용해 조명,환풍구 등의 동작을 조절 가능하다  
+ Client에 비정상적인 산소,CO 농도를 포착시에 자동으로 Server에게 알린다.  
+ Server는 위험상태라 여긴 텐트의 위치를 자동으로 문자 전송한다.   

-------------------------------------------------------------------------

Master 동작
---
![image](https://user-images.githubusercontent.com/68212288/87464710-89363000-c64e-11ea-9ec1-8daea26a6c8e.png)  

    관리자 모드 선택
    
![image](https://user-images.githubusercontent.com/68212288/87464901-d914f700-c64e-11ea-9614-cc16bfaf1715.png)  

    실시간 캠프별 산소/일산화탄소 농도 측정  
    
![image](https://user-images.githubusercontent.com/68212288/87465037-09f52c00-c64f-11ea-8060-1b93f2cfd386.png)  

    경고상태 진입  
    
![image](https://user-images.githubusercontent.com/68212288/87465219-3ad56100-c64f-11ea-8d2f-bf29d48283d5.png)  
    
    심각상태 진입  
    119 SMS 발송 및 텐트 환기, 경고 알람 수행  
    
![image](https://user-images.githubusercontent.com/68212288/87465317-65bfb500-c64f-11ea-87ab-c275a8bf9173.png)  

    구조요청 전송
    
-------------------------------------------------------------------------

Client 동작
---
![image](https://user-images.githubusercontent.com/68212288/87465382-81c35680-c64f-11ea-8b68-9492425b78d4.png)  

    텐트 정보 등록

![image](https://user-images.githubusercontent.com/68212288/87465435-9a337100-c64f-11ea-91b7-c33c13043d7e.png)  

    사용자 어플로써 텐트 조작 기능

    
