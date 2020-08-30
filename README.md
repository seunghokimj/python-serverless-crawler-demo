# Python Serverless Crawler Demo

Python과 AWS Lambda 를 사용한 crawler 만들기 입니다.

[변규현님(novemberde) Github](https://github.com/novemberde) 많이 참고하였습니다.

**변규현님께 감사드립니다.**

## Objective

Amazon Web Service 를 활용하여 Serverless architecture로 웹크롤러를 배포합니다.

크롤링된 데이터는 DynamoDB에 저장합니다.

## AWS Resources

AWS에서 사용하는 리소스는 다음과 같습니다.

- Cloud9: 코드 작성, 실행 및 디버깅을 위한 클라우드 기반 IDE.
- Lambda: 서버를 프로비저닝하거나 관리하지 않고도 코드를 실행할 수 있게 해주는 컴퓨팅 서비스. 서버리스 아키텍쳐의 핵심 서비스.
- DynamoDB: 완벽하게 관리되는 NoSQL 데이터베이스 서비스로, 원활한 확장성과 함께 빠르고 예측 가능한 성능을 제공.

## Cloud 9 시작하기

Cloud9 은 하나의 IDE입니다. 그렇지만 이전의 설치형 IDE와는 다릅니다. 설치형 IDE는 로컬 PC에 프로그램을 설치하던가
실행하는 방식이었다면, Cloud9은 브라우저가 실행가능한 모든 OS에서 사용이 가능합니다.

맨 처음 Cloud9은 AWS 내에서가 아닌 별도의 서비스로 제공되었습니다. AWS에 인수된 이후 Cloud9은 AWS의 Managed Service형태로 바뀌었고,
AWS의 서비스와 결합하여 사용이 가능해졌습니다. 코드 편집과 명령줄 지원 등의 평범한 IDE 기능을 지니고 있던 반면에, 현재는 AWS 서비스와
결합되어 직접 Lambda 코드를 배포하던가, 실제로 Cloud9이 실행되고 있는 EC2의 컴퓨팅 성능을 향상시켜서
로컬 PC의 사양에 종속되지 않은 개발을 할 수가 있습니다.

그러면 Cloud9 환경을 시작해봅시다.

[Cloud 9 Console](https://ap-northeast-2.console.aws.amazon.com/cloud9/home?region=ap-northeast-2)에 접속합니다.

아래와 같은 화면에서 [Create Environment](https://ap-northeast-2.console.aws.amazon.com/cloud9/home/create) 버튼을 누릅니다.

![c9-create](/images/c9-create.png)

Name과 Description을 다음과 같이 입력합니다.

- Name: PythonServerless


![c9-create-name](/images/c9-create-name.png)

Configure Setting은 다음과 같이 합니다.

- Environment Type: EC2
- Instance Type: T2.micro
- Cost Save Setting: After 30 minutes
- Network Settings: Default

![c9-conf](/images/c9-conf.png)

모든 설정을 마쳤다면 Cloud9 Environment를 생성하고 Open IDE를 통해 개발 환경에 접속합니다.

접속하면 다음과 같은 화면을 볼 수 있습니다.

1. 현재 Environment name
2. EC2에서 명령어를 입력할 수 있는 Terminal
3. Lambda Functions
    - Local Functions: 배포되지 않은 편집중인 Functions
    - Remote Functions: 현재 설정해놓은 Region에 배포된 Lambda Functions
4. Preferences

![c9-env](/images/c9-env.png)


- Preferences > AWS SETTINGS > Region > Asia Pacific(Seoul)

Preferences(설정 화면)에서 ap-northeast-2(Seoul Region)으로 바꾸어줍니다.
![c9-region](/images/c9-pref-region.png)


- Preferences > AWS SETTINGS > Credentials > off

이번 실습은 관리자 권한의 credentials을 생성하여 진행합니다. Cloud9이 temporary credentials 은 off 합니다.
![c9-region](/images/c9-pref-credentials.png)


- Preferences > PROJECT SETTINGS > Python Support > Python Version > Python3

현재 project python version이 python2 로 되어 있다면, python3으로 변경합니다.
![c9-env-python](/images/c9-pref-python.png)

## S3 Bucket 생성하기
Amazon Simple Storage Service는 인터넷용 스토리지 서비스입니다. 파일들을 업로드 / 다운로드 할 수 있으며 AWS에서 핵심적인 서비스 중 하나입니다. 여러 방면으로 활용할 수 있지만 여기서는 소스코드와 관련 패키지의 저장소 역할을 합니다. 

[S3의 메인](https://console.aws.amazon.com/s3/home?region=ap-northeast-2) 으로 가서 버킷 생성하기 버튼을 클릭합니다.
![s3-create-btn](/images/s3-create-btn.png)

아래와 같이 입력하고 생성버튼을 클릭합니다.

- 버킷 이름(Bucket name): USERNAME-serverless-demo // 여기서 USERNAME을 수정합니다. e.g.) seungho-serverless-demo
- 리전(Region): 아시아 태평양(서울)
![s3-create-btn](/images/s3-create-1.png)

## DynamoDB 테이블 생성하기

DynamoDB를 설계할 시 주의해야할 점은 [FAQ](https://aws.amazon.com/ko/dynamodb/faqs/)를 참고하시길 바랍니다.

이제 DynamoDB에 Todo table을 생성할 것입니다. 파티션 키와 정렬 키는 다음과 같이 설정합니다.

- 테이블 이름: PortalNews 
- 파티션키(Partition Key): portal
- 정렬키(Sort Key): createdAt

그럼 [DynamoDB Console](https://ap-northeast-2.console.aws.amazon.com/dynamodb/home?region=ap-northeast-2#)로 이동합니다.
테이블 만들기를 클릭하여 아래와 같이 테이블을 생성합니다.

![dynamodb-create](/images/dynamodb-create.png)

## AWS Credentials 설정
오늘 실습하는 Cloud9 환경에은 aws의 여러 리소스를 생성하는 권한(s3, IAM Policy, Role 등 생성)이 필요합니다. Cloud9에 환경에 **관리자 사용자** 를 추가하여 실습을 진행합니다.

### AWS IAM
AWS는 을 통해 [IAM(Identity and Access Management)](https://console.aws.amazon.com/iam/home#/home) AWS resource에 권한을 설정합니다.

IAM 에 관련하여 도움되는 내용입니다.
- [IAM 모범 사례](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/best-practices.html)
- [자습서: IAM 역할을 사용한 AWS 계정 간 액세스 권한 위임](https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/tutorial_cross-account-with-roles.html)

#### 관리자 사용자 추가

관리자 사용자와 access key를 생성합니다.

[IAM 사용자](https://console.aws.amazon.com/iam/home#/users) 에 접속하여 사용자 추가 버튼을 선택합니다.

![iam-create-user-0](/images/iam-create-user-0.png)

사용자 이름을 입력하고, 액세스 유형에 프로그래밍 방식 액세스를 선택합니다.

![iam-create-user-1](/images/iam-create-user-1.png)

'권한 설정: 기존 정책 직접 연결' 탭을 선택 하고 **AdministratorAccess** 를 선택합니다.
![iam-create-user-2](/images/iam-create-user-2.png)


사용자 만들기 버튼을 누르면 관라자 사용자가 생성됩니다.
![iam-create-user-3](/images/iam-create-user-3.png)

마지막으로 access key를 csv로 다운로드 받으면 access key와 secret key를 얻을 수 있고 다운받은 파일은 다음과 같습니다.
![iam-create-user-4](/images/iam-create-user-4.png)

**crentials.csv**

```
User name,Password,Access key ID,Secret access key,Console login link
python-serverless,,YOUR_ACCESS_KEY,YOUR_SECRET_ACCESS_KEY,https://############.signin.aws.amazon.com/console
```

#### Cloud9 에 AWS Credentials 적용
생성한 access key를 Cloud9에 적용합니다.

터미널에서 아래처럼 aws cli 를 사용합니다.

``` sh

$ aws configure
AWS Access Key ID [None]: YOUR_ACCESS_KEY
AWS Secret Access Key [None]: YOUR_SECRET_ACCESS_KEY
Default region name [None]: ap-northeast-2
Default output format [None]: json
```

제대로 access key를 입력했는지 확인해 봅니다.
``` sh

$ cat ~/.aws/credentials
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
aws_session_token =

$ aws s3 ls
# print s3 bucket list
```

이제 AWS credentials 설정을 마쳤습니다.


## Python 개발 환경 설정
### .bash profile 설정
터미널에서 python 관련 개발환경 명령어를 미리 설정 하도록, Cloud9의 .bash_profile 을 수정합니다.

만약 Cloud9이 아닌 local 에서 실습을 진행하시는 분은, 이 부분은 설정하지 않으셔도 됩니다.

```sh
$ wget https://raw.githubusercontent.com/seunghokimj/python-serverless-crawler-demo/master/cloud9_bash_profile
$ cp cloud9_bash_profile ~/.bash_profile

```

현재 터미널을 종료하고 새로운 터미널에서 작업을 시작합니다.

![c9-new-terminal](/images/c9-new-terminal.png)


### virtualenv 설정
실습을 위한 독립된 python 개발 환경을 생성합니다.

Python 개발 환경 관리는 [virtualenv](https://virtualenv.pypa.io/) 라는 툴을 사용합니다.

```sh
$ virtualenv -p python3 venv
ec2-user:~/environment $ . venv/bin/activate
(venv) ec2-user:~/environment $ python
Python 3.6.11 (default, Jul 20 2020, 22:15:17) 
[GCC 4.8.5 20150623 (Red Hat 4.8.5-28)] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>  

```

python version 설정을 완료하였습니다.


## [Zappa - Serverless Python Web Services](https://www.zappa.io/)

![Zappa main](/images/zappa-main.png)

Zappa는 AWS Lambda serverless 를 위한 python framework 입니다.

> Zappa makes it super easy to build and deploy server-less, event-driven Python applications (including, but not limited to, WSGI web apps) on AWS Lambda + API Gateway.
> Think of it as "serverless" web hosting for your Python apps.
> That means infinite scaling, zero downtime, zero maintenance - and at a fraction of the cost of your current deployments!

Zappa는 python이 설치되어 있는 환경에서 사용할 수 있습니다.

open source로 기여하고 싶다면 [https://github.com/Miserlou/Zappa](https://github.com/Miserlou/Zappa)에서 issue와 pull request를 등록해주세요.


### Zappa 살펴보기

Zappa를 사용하기 위해서 명령어들을 살펴봅시다.

위에서 설정한 virtualenv 환경에서 작업합니다.

```sh
# Zappa 설치
(venv) $ pip install zappa
Successfully installed ... zappa-0.51.0 zipp-3.1.0

# 명령어들을 확인해봅니다.
(venv) $ zappa --help
usage: zappa [-h] [-v] [--color {auto,never,always}]
             {certify,deploy,init,package,template,invoke,manage,rollback,schedule,status,tail,undeploy,unschedule,update,shell}
             ...

Zappa - Deploy Python applications to AWS Lambda and API Gateway.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Print the zappa version
  --color {auto,never,always}

subcommands:
  {certify,deploy,init,package,template,invoke,manage,rollback,schedule,status,tail,undeploy,unschedule,update,shell}
    certify             Create and install SSL certificate
    deploy              Deploy application.
    init                Initialize Zappa app.
    package             Build the application zip package locally.
    template            Create a CloudFormation template for this API Gateway.
    invoke              Invoke remote function.
    manage              Invoke remote Django manage.py commands.
    rollback            Rollback deployed code to a previous version.
    schedule            Schedule functions to occur at regular intervals.
    status              Show deployment status and event schedules.
    tail                Tail deployment logs.
    undeploy            Undeploy application.
    unschedule          Unschedule functions.
    update              Update deployed application.
    shell               A debug shell with a loaded Zappa object.
```

여기서 자주 사용하게 될 명령어는 다음과 같습니다.

- init: 프로젝트 생성시 사용
- deploy: 첫 배포할 때 사용
- update: deploy 이 후 변경시 사용
- package: 배포될 패키지의 구조를 보고싶을 때 사용
- invoke: 특정 handler를 동작시킬 때 사용
- undeploy: 배포된 리소스를 제거할 때 사용

간단하게 zappa init 명령어를 확인해 봅니다. deploy 명령어는 추후에 사용하겠습니다.

```sh
# first zappa project dir 생성
(venv) ec2-user:~/environment $ mkdir first_zappa && cd first_zappa
# init 으로 기본 설정
(venv) ec2-user:~/environment/first_zappa $ zappa init

███████╗ █████╗ ██████╗ ██████╗  █████╗
╚══███╔╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗
  ███╔╝ ███████║██████╔╝██████╔╝███████║
 ███╔╝  ██╔══██║██╔═══╝ ██╔═══╝ ██╔══██║
███████╗██║  ██║██║     ██║     ██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝     ╚═╝  ╚═╝

Welcome to Zappa!

Zappa is a system for running server-less Python web applications on AWS Lambda and AWS API Gateway.
This `init` command will help you create and configure your new Zappa deployment.
Let's get started!

Your Zappa configuration can support multiple production stages, like 'dev', 'staging', and 'production'.
What do you want to call this environment (default 'dev'): dev

AWS Lambda and API Gateway are only available in certain regions. Let's check to make sure you have a profile set up in one that will work.
Okay, using profile default!

Your Zappa deployments will need to be uploaded to a private S3 bucket.
If you don't have a bucket yet, we'll create one for you too.
What do you want to call your bucket? (default 'zappa-ld67k976y'):

What's the modular path to your app's function?
This will likely be something like 'your_module.app'.
Where is your app's function?: first_zappa

You can optionally deploy to all available regions in order to provide fast global service.
If you are using Zappa for the first time, you probably don't want to do this!
Would you like to deploy this application globally? (default 'n') [y/n/(p)rimary]:

Okay, here's your zappa_settings.json:

{
    "dev": {
        "app_function": "first_zappa",
        "aws_region": "ap-northeast-2",
        "profile_name": "default",
        "project_name": "first-zappa",
        "runtime": "python3.6",
        "s3_bucket": "zappa-ld67k976y"
    }
}

Does this look okay? (default 'y') [y/n]:

Done! Now you can deploy your Zappa application by executing:

        $ zappa deploy dev

After that, you can update your application code with:

        $ zappa update dev

To learn more, check out our project page on GitHub here: https://github.com/Miserlou/Zappa
and stop by our Slack channel here: https://slack.zappa.io

Enjoy!,
 ~ Team Zappa!
```


zappa_settings.json 파일을 확인하면 기본적인 zappa 설정 내용을 확인할 수 있습니다.

자세한 설정 내용은 [zappa github](https://github.com/Miserlou/Zappa) 을 통해 확인하면 알 수 있습니다.


## Python 크롤링 시작하기
파일 트리는 다음과 같습니다.

```txt
environment
└── serverless-crawler  : 작업 디렉터리
    ├── crawler.py  : Lambda에서 trigger하기 위한 handler가 포한됨 파일
    ├── lambda_test.py: lambda function test
    ├── models.py: DynamoDB 모델
    ├── zappa_settings.json : Zappa config file
    └── requirements.txt : 개발을 위해 필요한 library 정보
```

먼저 터미널을 열어 serverless-crawler 디렉터리를 생성하고 각 파일들을 편집합니다.

```sh
(venv) ec2-user:~/environment $ mkdir serverless-crawler && cd serverless-crawler
```

### serverless-crawler/requirements.txt
```txt
beautifulsoup4==4.9.1
pynamodb==4.3.3
python-dateutil==2.6.1
zappa==0.51.0
```

python은 requirements.txt 에 개발에 필요한 라이브러리를 기술합니다.

사용하는 라이브러리는 다음과 같습니다.

- beautifulsoup4: python web scrape 라이브러리
- pynamodb: DynamoDB를 사용하기 쉽도록 Modeling하는 도구
- zappa: python serverless framework

requirements.txt에 있는 라이브러리들을 설치 합니다.

```sh
(venv) ec2-user:~/environment/serverless-crawler $ pip install -r requirements.txt

```


### serverless-crawler/zappa_settings.json
zappa 를 init 하면 zappa_settings.json 파일이 생성됩니다.

```sh
(venv) ec2-user:~/environment/serverless-crawler $ zappa init
...
What do you want to call this environment (default 'dev'): dev
...
What do you want to call your bucket? (default 'zappa-gpz692isv'): 생성한 s3 이름 입력
...
Where is your app's function?: crawler.lambda_handler
...
Would you like to deploy this application globally? (default 'n') [y/n/(p)rimary]: n
...
Does this look okay? (default 'y') [y/n]: y
...
```


**zappa_settings.json** 을 아래처럼 변경하여 저장합니다.

```json
{
    "dev": {
        "aws_region": "ap-northeast-2",
        "profile_name": "default",
        "project_name": "python-serverless-crawler",
        "runtime": "python3.6",
        "s3_bucket": "YOUR_S3_BUCKET",  // 이 부분을 생성한 s3 이름으로 변경

        "apigateway_enabled": false,
        "keep_warm": false,
        "lambda_description": "Python Serverless Crawler",
        "lambda_handler": "crawler.lambda_handler",
        "memory_size": 128
    }
}
```

### serverless-crawler/models.py
```python
from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, ListAttribute

class PortalNews(Model):
    class Meta:
        table_name = "PortalNews"
        region = 'ap-northeast-2'

    portal = UnicodeAttribute(hash_key=True)
    createdAt = UnicodeAttribute(range_key=True)
    section = UnicodeAttribute()
    news = ListAttribute()
```

### serverless-crawler/crawler.py

```python
import requests
import datetime
from bs4 import BeautifulSoup


DEFAULT_TIMEOUT = 10
DEFAULT_HEADER = {
    'User-Agent': 'Mozilla/5.0'
}

MAX_NEWS_LEN = 20


def naver_news_crawler(section):
    title_list = list()
    ...
    return title_list

def daum_news_crawler(section):
    title_list = list()
    ...
    return title_list

def lambda_handler(event, context):
    naver_results = {v: naver_news_crawler(k) for k, v in NAVER_SECTIONS.items()}
    daum_results = {v: daum_news_crawler(k) for k, v in DAUM_SECTIONS.items()}

    # print(naver_results)
    # print(daum_results)

    if all(naver_results.values()) and all(daum_results.values()):
        return 'success'
    else:
        return 'error'

```


### serverless-crawler/lambda_test.py
```python
from crawler import lambda_handler

print(lambda_handler(None, None))
```

터미널에서 테스트 코드를 실행시켜 봅니다.

```sh
(venv) ec2-user:~/environment/serverless-crawler $ python lambda_test.py
success
```

[DynamoDB Console](https://ap-northeast-2.console.aws.amazon.com/dynamodb/home?region=ap-northeast-2#tables:selected=PortalNews)에 들어가서 성공적으로 항목들이 생성되었는지 확인합니다.


## Cloud9에서 배포하기
### Zappa deploy
```sh
(venv) ec2-user:~/environment/serverless-crawler $ zappa deploy dev
Downloading and installing dependencies..
Packaging project as zip.
Uploading python-serverless-crawler-dev-1598697456.zip (9.7MiB)..
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 10.2M/10.2M [00:01<00:00, 8.82MB/s]
Scheduling..
Unscheduled python-serverless-crawler-dev-crawler.lambda_handler.
Scheduled python-serverless-crawler-dev-crawler.lambda_handler with expression rate(10 minutes)!
(venv) ec2-user:~/environment/serverless-crawler $
```

정상적으로 deploy 되었으면, [Lambda Console](https://ap-northeast-2.console.aws.amazon.com/lambda/home?region=ap-northeast-2#/functions) 에서 새로 생성된 `python-serverless-crawler-dev` 함수를 확인 할 수 있습니다.

### Zappa invoke
invoke 를 해봅니다.

```sh
(venv) ec2-user:~/environment/serverless-crawler $ zappa invoke dev
Calling invoke for stage dev..
[START] RequestId: XXXXXXX-.... Version: $LATEST
[END] RequestId: XXXXXXX-....
[REPORT] RequestId: XXXXXXX-....
Duration: 16255.10 ms
Billed Duration: 16300 ms
Memory Size: 128 MB
Max Memory Used: 90 MB
Init Duration: 593.14 ms
```

### Zappa update

주기적으로 크롤링 하도록 함수를 update 를 해봅니다.

`zappa_settings.json` 에서 events 를 추가합니다.

**serverless-crawler/zappa_settings.json**
```json
{
    "dev": {
        ...
        "apigateway_enabled": false,
        "events": [
            {
                "function": "crawler.lambda_handler",
                "expression": "rate(10 minutes)"
            }
        ],
        ...
    }
}
```


```sh
(venv) ec2-user:~/environment/serverless-crawler $ zappa update dev
Calling update for stage dev..
Downloading and installing dependencies..
 - yarl==1.5.1: Using locally cached manylinux wheel
 - multidict==4.7.6: Using locally cached manylinux wheel
 - aiohttp==3.6.2: Using locally cached manylinux wheel
Packaging project as zip.
Uploading python-serverless-crawler-dev-1598725230.zip (11.0MiB)..
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 11.5M/11.5M [00:00<00:00, 21.0MB/s]
Updating Lambda function code..
Updating Lambda function configuration..
Scheduling..
Unscheduled python-serverless-crawler-dev-crawler.lambda_handler.
Scheduled python-serverless-crawler-dev-crawler.lambda_handler with expression cron(0/30 * * * ? *)!
Your updated Zappa deployment is live!

```

성공적으로 update 되었습니다.
지금부터 30분마다 주기적으로 DynamoDB에 랭킹 뉴스 정보가 쌓입니다.

## 리소스 삭제하기
- [ ] lambda 삭제

    서버리스 앱은 내리는 것이 어렵지 않습니다.
    간단한 Command 하나면 모든 스택이 내려갑니다.
    Cloud9에서 새로운 터미널을 열고 다음과 같이 입력합니다.

```sh
(venv) ec2-user:~/environment/serverless-crawler $ zappa undeploy dev
Calling undeploy for stage dev..
Are you sure you want to undeploy? [y/n] y
Unscheduling..
Unscheduled python-serverless-crawler-dev-crawler.lambda_handler.
Deleting Lambda function..
Done!
```
- [ ] IAM 사용자 삭제

    [IAM Console](https://console.aws.amazon.com/iam/home#/users)로 들어가서 오늘 생성한 관리자 사용자(python-serverless)를 삭제합니다.

- [ ] S3 버킷 삭제

    [S3 Console](https://s3.console.aws.amazon.com/s3/home?region=ap-northeast-2)로 들어가서 생성한 s3 버킷(USERNAME-serverless-demo)을 삭제합니다.

- [ ] DynamoDB 테이블 삭제

    [DynamoDB Console](https://ap-northeast-2.console.aws.amazon.com/dynamodb/home?region=ap-northeast-2)로 들어가서 Table을 삭제합니다. 리전은 서울입니다.

- [ ] Cloud9 삭제

    [Cloud9 Console](https://ap-northeast-2.console.aws.amazon.com/cloud9/home?region=ap-northeast-2)로 들어가서 IDE를 삭제합니다. 리전은 서울입니다.


## References

- [https://aws.amazon.com/ko/cloud9/](https://aws.amazon.com/ko/cloud9/)
- [https://www.zappa.io/](https://www.zappa.io/)
- [https://www.crummy.com/software/BeautifulSoup/bs4/doc/](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [https://pynamodb.readthedocs.io](https://pynamodb.readthedocs.io)
