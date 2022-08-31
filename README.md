# ZJU-Calendar-Maker
一键生成课程表ics文件, 可直接导入iOS日历
## 功能
该脚本能实现浙江大学课程表自动抓取并一键转换为 ics 日历文件，同时具备区别春夏秋冬学期，自动识别单双周课程，节假日无课，调休自动转换等功能。 
导入Apple日历效果如下：

<img width="1440" alt="截屏2022-08-31 22 07 03" src="https://user-images.githubusercontent.com/59506669/187703480-85a36edc-9cc0-4fa7-95e9-2dffb91e4c6f.png">
<img width="1440" alt="截屏2022-08-31 22 06 14" src="https://user-images.githubusercontent.com/59506669/187704250-801ec2ca-ffe0-413d-b41e-55f61220e3d8.png">
<img width="1440" alt="截屏2022-08-31 22 07 42" src="https://user-images.githubusercontent.com/59506669/187704281-112eca0a-e898-4339-8aaa-681484eec1d0.png">

## 使用方法
### Step1
安装以下依赖
```python3
import copy
import datetime
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import *
from icalendar import Calendar, Event
```

### Step2
下载 timetable.py 文件，修改 xh 为自己的学号，并用 chrome 等浏览器登录 jwbinfosys.zju.edu.cn 进入个人课表界面，右键点击检查，点击 network ，查看 xskbcx.aspx 的 cookie ，找到 ASP.NET_SessionId ，并填写进去
```python3
if __name__ == '__main__':
    # 个人基本信息
    xh = 3200000000
    cookie = 'ASP.NET_SessionId=xxxxxxxxxxxxxxxxxxxxxxxx'
```
<img width="839" alt="截屏2022-08-31 22 48 44" src="https://user-images.githubusercontent.com/59506669/187709106-cfa93cf1-04a9-42ca-b34c-15987f5f440c.png">

### Step3
运行 timetable.py 文件，在同目录下生成 timetable.ics 文件，将该 ics 文件导入 Apple 日历，大功告成！
<img width="687" alt="截屏2022-08-31 22 04 39" src="https://user-images.githubusercontent.com/59506669/187709391-a342e111-a66b-4544-af0c-4a547c463770.png">
