import copy
import datetime
import re
import time
import requests
from bs4 import BeautifulSoup
from datetime import *
from icalendar import Calendar, Event


def transdate(tmp):
    result = dict()
    if tmp[0] == '一':
        weekday = 0
    elif tmp[0] == '二':
        weekday = 1
    elif tmp[0] == '三':
        weekday = 2
    elif tmp[0] == '四':
        weekday = 3
    elif tmp[0] == '五':
        weekday = 4
    elif tmp[0] == '六':
        weekday = 5
    elif tmp[0] == '日':
        weekday = 6
    tm = re.split(r',', tmp[1])
    # print(time)

    if tm[0] == '1':
        start = time(8, 0, 0)
    elif tm[0] == '2':
        start = time(8, 50, 0)
    elif tm[0] == '3':
        start = time(9, 50, 0)
    elif tm[0] == '4':
        start = time(10, 40, 0)
    elif tm[0] == '5':
        start = time(11, 30, 0)
    elif tm[0] == '6':
        start = time(13, 15, 0)
    elif tm[0] == '7':
        start = time(14, 5, 0)
    elif tm[0] == '8':
        start = time(14, 55, 0)
    elif tm[0] == '9':
        start = time(15, 55, 0)
    elif tm[0] == '10':
        start = time(16, 45, 0)
    elif tm[0] == '11':
        start = time(18, 30, 0)
    elif tm[0] == '12':
        start = time(19, 20, 0)
    elif tm[0] == '13':
        start = time(20, 10, 0)

    if tm[-1] == '1':
        end = time(8, 45, 0)
    elif tm[-1] == '2':
        end = time(9, 35, 0)
    elif tm[-1] == '3':
        end = time(10, 35, 0)
    elif tm[-1] == '4':
        end = time(11, 25, 0)
    elif tm[-1] == '5':
        end = time(12, 15, 0)
    elif tm[-1] == '6':
        end = time(14, 0, 0)
    elif tm[-1] == '7':
        end = time(14, 50, 0)
    elif tm[-1] == '8':
        end = time(15, 40, 0)
    elif tm[-1] == '9':
        end = time(16, 40, 0)
    elif tm[-1] == '10':
        end = time(17, 30, 0)
    elif tm[-1] == '11':
        end = time(19, 15, 0)
    elif tm[-1] == '12':
        end = time(20, 5, 0)
    elif tm[-1] == '13':
        end = time(20, 55, 0)

    return weekday, start, end, tmp[2]


# requests获取网页内容
def html_get(xh, cookie):
    url = f'http://jwbinfosys.zju.edu.cn/xskbcx.aspx?xh={xh}'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    headers = {
        'Cookie': cookie,
        'User-Agent': user_agent
    }

    resp = requests.get(url, headers=headers)
    print(resp)
    text = resp.text
    resp.close()
    return text


# beautifulsoup解析数据
def html_decode(text):
    page = BeautifulSoup(text, 'html.parser')
    table = page.find('table', attrs={'class': 'datagridstyle'})
    trs = table.find_all('tr')[1:]
    timetable = []
    for tr in trs:
        tds = tr.find_all('td')
        lesson = dict()
        lesson['number'] = tds[0].text
        lesson['name'] = tds[1].text
        lesson['teacher'] = tds[2].text
        lesson['semester'] = tds[3].text
        lesson['date'] = tds[4].text
        lesson['location'] = tds[5].text
        timetable.append(copy.deepcopy(lesson))
        lesson.clear()
    return timetable


def timetable_process(timetable):
    result = []

    # 删除短学期课程
    temptable = timetable.copy()
    for lesson in temptable:
        if re.search('短', lesson['semester']):
            timetable.remove(lesson)
            continue
    del temptable

    re_date = re.compile(r'(?P<weekday>.)第(?P<seq>.*?)节(?:周|$|{(?P<opt>..)})')
    re_loc = re.compile(r'(紫金港|玉泉|西溪|华家池|之江)')
    print('\nyour lessons are below:')
    for lesson in timetable:
        cnt = 0
        lesson_split = []
        loc = re_loc.split(lesson['location'])
        for item in re_date.finditer(lesson['date']):
            lesson_split.append(copy.deepcopy(lesson))
            # print(item.groups())
            lesson_split[cnt]['weekday'], lesson_split[cnt]['start'], lesson_split[cnt]['end'], lesson_split[cnt][
                'weekopt'] = transdate(item.groups())
            lesson_split[cnt]['location'] = loc[cnt * 2 + 1] + loc[cnt * 2 + 2]
            cnt += 1
        # 打印阶段性测试
        for item in lesson_split:
            print(item['name'], '\t', item['location'], '\t', item['weekday'], '\t', item['start'], '\t', item['end'],
                  '\t', item['weekopt'])
            result.append(item)
        print("-------------------------------------------------------------------------------------")
        lesson_split.clear()
    return result


def make_ics(table, semesters, holiday, exchange):
    def not_holiday(d):
        for period in holiday:
            if date.fromisoformat(period[0]) <= d <= date.fromisoformat(period[1]):
                return False
        return True

    def exchange_date(d):
        for couple in exchange:
            if d == date.fromisoformat(couple[0]):
                return date.fromisoformat(couple[1])
            elif d == date.fromisoformat(couple[1]):
                return date.fromisoformat(couple[0])
        return d

    def week_num(current_d, start_d):
        if start_d.weekday() != 0:
            print('学期开始日期不是周一，请重新检查！')
        return (current_d - start_d).days // 7
    # 制作ics文件
    cal = Calendar()
    cal.add('X-WR-CALNAME', '课程表')
    cal.add('X-APPLE-CALENDAR-COLOR', '#540EB9')
    cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
    cal.add('VERSION', '2.0')
    for season in semesters:
        start_date = date.fromisoformat(semesters[season][0])
        end_date = date.fromisoformat(semesters[season][1])
        dt = start_date
        while dt != end_date:
            for lesson in table:
                if lesson['semester'].find(season) != -1 and not_holiday(dt):
                    if exchange_date(dt).weekday() == lesson['weekday'] and ((week_num(exchange_date(dt), start_date) % 2 == 0 and lesson['weekopt'] == '双周') or (week_num(exchange_date(dt), start_date) % 2 == 1 and lesson['weekopt'] == '单周') or lesson['weekopt'] is None):
                        event = Event()
                        dtstart = datetime.combine(dt, lesson['start'])
                        dtend = datetime.combine(dt, lesson['end'])
                        if lesson['location'].find('紫金港') != -1:
                            location = '浙江大学紫金港校区' + lesson['location'].split('紫金港')[1]
                        event.add('uid', f'{datetime.now().timestamp()}@meteors')
                        event.add('dtstart', dtstart)
                        event.add('dtend', dtend)
                        event.add('summary', lesson['name'])
                        event.add('location', location)
                        cal.add_component(event)
                        del event
            dt += timedelta(days=1)
    with open('timetable.ics', 'wb') as file:
        file.write(cal.to_ical())
    print('\nics file succesfully generated!')


if __name__ == '__main__':
    # 个人基本信息
    xh = 3200000000
    cookie = 'ASP.NET_SessionId=xxxxxxxxxxxxxxxxxxxxxxxx'
    semester = {
        '秋': ['2022-09-12', '2022-11-07'],
        '冬': ['2022-11-07', '2023-01-02']
    }
    holiday = [
        ['2022-10-01', '2022-10-07'],
        ['2022-10-21', '2022-10-23']
    ]
    exchange = [
        ['2022-10-08', '2022-10-06'],
        ['2022-10-09', '2022-10-07'],
        ['2022-10-15', '2022-10-21']
    ]
    with open('resp.txt', 'r') as f:
        text = f.read()
    # text = html_get(xh, cookie)
    table = html_decode(text)
    table = timetable_process(table)

    # print(table)
    make_ics(table, semester, holiday, exchange)
