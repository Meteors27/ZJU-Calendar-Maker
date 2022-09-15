# ZJU-Calendar-Maker
一键生成课程表ics文件, 可直接导入iOS日历
## 功能
该脚本能实现浙江大学课程表自动抓取并一键转换为 ics 日历文件，同时具备区别春夏秋冬学期，自动识别单双周课程，节假日无课，调休自动转换等功能。 
导入Apple日历效果如下：

<img width="1440" alt="截屏2022-08-31 22 07 03" src="https://user-images.githubusercontent.com/59506669/187703480-85a36edc-9cc0-4fa7-95e9-2dffb91e4c6f.png">
<img width="1440" alt="截屏2022-08-31 22 06 14" src="https://user-images.githubusercontent.com/59506669/187704250-801ec2ca-ffe0-413d-b41e-55f61220e3d8.png">
<img width="1440" alt="截屏2022-08-31 22 07 42" src="https://user-images.githubusercontent.com/59506669/187704281-112eca0a-e898-4339-8aaa-681484eec1d0.png">

***

## 使用方法
### Step1
安装以下依赖
```python3
import requests
import icalendar
```

### Step2
下载 timetable.py 文件，填写 `username` 和 `password` 为浙大统一身份认证账户密码（默认生成2022-2023学年秋冬课表），运行程序。

### Step3
运行 timetable.py 文件，在同目录下生成 timetable.ics 文件，将该 ics 文件导入 Apple 日历，大功告成！
<img width="687" alt="截屏2022-08-31 22 04 39" src="https://user-images.githubusercontent.com/59506669/187709391-a342e111-a66b-4544-af0c-4a547c463770.png">

### 生成自定义学期课表的方法
`data`表示学年，这里应替换成您希望生成课表的学年
```python3
data = {'xnm': '2022-2023'}
```

`semester_info`表示单个学期的信息，包含了学期名（春/夏/秋/冬），开始时间和结束时间。注意：开始时间必须是某一周的周一，且与`data`学年所匹配。
```python3
semester_info = [
    {'semester': '秋', 'start': '2022-09-12', 'end': '2022-11-06'},
    {'semester': '冬', 'start': '2022-11-07', 'end': '2023-01-01'},
]
```

`holiday`表示节假日的日期，list中每一组小的list中的两个元素分别表示节日的开始和结束日期。请自行参考浙江大学校历的官方安排。
```python3
holiday = [
    ['2022-10-01', '2022-10-07'],
    ['2022-10-21', '2022-10-23']
]
```

`exchange`表示调休的日期，list中每一组小的list中的两个元素分别表示对换的两个日期。请自行参考浙江大学校历的官方安排。
```python3
exchange = [
    ['2022-10-08', '2022-10-06'],
    ['2022-10-09', '2022-10-07'],
    ['2022-10-15', '2022-10-21']
]
```

***

### 待改进的地方


### 致谢

### Reference
https://icalendar.readthedocs.io/en/latest/usage.html
https://www.jianshu.com/p/237c336f0b7f
https://www.jianshu.com/p/4f67fd92acfc
https://www.cnblogs.com/tkqasn/p/6001134.html


