import requests
import re
from icalendar import Calendar, Event
from datetime import *

class TimeTable(object):
    def __init__(self, username, password, semester_info, data, holiday=[], exchange=[]):
        self.username = username
        self.password = password
        self.semester_info = semester_info
        self.data = data
        self.holiday = holiday
        self.exchange = exchange
        self.lessons = {}
        self.info = {}
        self.login_url = "https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fzdbk.zju.edu.cn%2Fjwglxt%2Fxtgl%2Flogin_ssologin.html"
        self.base_url = "http://zdbk.zju.edu.cn/jwglxt/kbcx/xskbcx_cxXsKb.html?gnmkdm=N253508&su=" + username
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            'Connection': 'close'
        }
        self.sess = requests.Session()

        print('username:   ', username)
        print('passwaord:  ', password)

    def login(self):
        res = self.sess.get(self.login_url, headers=self.headers)
        execution = re.search('name="execution" value="(.*?)"', res.text).group(1)
        res = self.sess.get(url='https://zjuam.zju.edu.cn/cas/v2/getPubKey', headers=self.headers).json()
        n, e = res['modulus'], res['exponent']
        encrypt_password = self._rsa_encrypt(self.password, e, n)

        data = {
            'username': self.username,
            'password': encrypt_password,
            'execution': execution,
            '_eventId': 'submit'
        }
        res = self.sess.post(url=self.login_url, data=data, headers=self.headers)

        # check if login successfully
        try:
            dec = res.content.decode()
            if '统一身份认证' in dec:
                raise Exception('登录失败，请核实账号密码重新登录')
        except Exception:
            raise

        return self.sess

    def get_info(self):
        try:
            res = self.sess.post(self.base_url, headers=self.headers, data=data)
            if res.status_code != 200:
                raise Exception("[Error] 课表请求失败")
        except Exception:
            raise
        self.info = res.json()
        return self.info

    def process_info(self):
        lesson_info = self.info['kbList']
        lessons = []
        obj = re.compile(r'(?P<name>.*?)<br>.*?\|(?P<timeinfo>.*?)}<br>(?P<teacher>.*?)<br>(?P<location>.*?)(#|\(|zwf)')
        for info in lesson_info:
            lesson = {
                'name': obj.match(info['kcb']).group('name'),
                'teacher': obj.match(info['kcb']).group('teacher'),
                'location': obj.match(info['kcb']).group('location'),
                'weekday': int(info['xqj']),
                'semester': info['xxq'],
                'timeinfo': obj.match(info['kcb']).group('timeinfo'),
                'start': int(info['djj']),
            }
            lessons.append(lesson)
        self.lessons = lessons
        self._process_odd_and_even()
        return self.lessons

    def _process_odd_and_even(self):
        for lesson in self.lessons:
            num = re.findall('\d+', lesson['timeinfo'])
            lesson['odd'] = lesson['even'] = 0
            if lesson['timeinfo'].find('单') == -1 and lesson['timeinfo'].find('双') == -1:
                lesson['even'] = lesson['odd'] = int(num[0])
            else:
                if lesson['timeinfo'].find('单') != -1:
                    lesson['odd'] = int(num[0])
                if lesson['timeinfo'].find('双') != -1:
                    lesson['even'] = int(num[-1])
        return

    def make_ics_file(self):
        cal = Calendar()
        cal.add('X-WR-CALNAME', '课程表')
        cal.add('X-APPLE-CALENDAR-COLOR', '#540EB9')
        cal.add('X-WR-TIMEZONE', 'Asia/Shanghai')
        cal.add('VERSION', '2.0')
        cnt = 0
        for semester in self.semester_info:
            sem = semester['semester']  # 学期
            start = date.fromisoformat(semester['start'])  # 开始日期
            end = date.fromisoformat(semester['end'])  # 结束日期
            '''start开始日期必须是周一'''
            if start.isoweekday() != 1:
                raise Exception("学期开始日期不是周一, 请更正后输入")
            _date = start  # 当前日期
            while _date <= end:  # 遍历semester中所有日期
                for lesson in self.lessons:  # 在每个日期中遍历所有课程
                    # 还差一个调休
                    len = self._verify(lesson, semester, _date)  # 课程长度
                    if len > 0:
                        '''制作event, 写入calendar'''
                        event = Event()
                        cnt += 1
                        event.add('uid', f'zju@{self.username}@{datetime.now().timestamp()}@{cnt%100}')
                        start_time, end_time = self._convert(lesson, len)
                        dtstart = datetime.combine(_date, start_time)
                        dtend = datetime.combine(_date, end_time)
                        event.add('dtstart', dtstart)
                        event.add('dtend', dtend)
                        event.add('summary', lesson['name'])
                        event.add('location', lesson['location'])
                        cal.add_component(event)
                        del event
                _date += timedelta(days=1)

        '''写入ics文件'''
        try:
            with open('timetable.ics', 'wb') as file:
                file.write(cal.to_ical())
                print('[success] ics日历制作完成!')
        except Exception:
            raise Exception("写入文件失败, 请重试!")

    def _verify(self, lesson, semester, _date):
        """校验lesson课程在指定学期semester和指定日期_date下是否合法

        :param lesson:
        :param semester:
        :param _date:
        :return:lesson课程在date日期下的课程长度, 如果当天没有课程则返回0
        """
        real_date = self._exchange(_date)
        if self._not_holiday(_date) and lesson['semester'].find(semester['semester']) != -1 and real_date.isoweekday() == lesson['weekday']:
            week_num = (real_date - date.fromisoformat(semester['start'])).days // 7 + 1
            if week_num % 2 == 1:
                return lesson['odd']
            else:
                return lesson['even']
        return 0

    def _not_holiday(self, d):
        for period in self.holiday:
            if date.fromisoformat(period[0]) <= d <= date.fromisoformat(period[1]):
                return False
        return True

    def _exchange(self, d):
        for couple in self.exchange:
            if d == date.fromisoformat(couple[0]):
                return date.fromisoformat(couple[1])
            elif d == date.fromisoformat(couple[1]):
                return date.fromisoformat(couple[0])
        return d

    def _convert(self, lesson, len):
        """

        :param lesson: lesson
        :param len: the lenth of the lesson
        :return: start_time, end_time
        """
        if len <= 0:
            pass
            # note
        start_time = [time(8, 0, 0), time(8, 50, 0), time(10, 0, 0), time(10, 50, 0), time(11, 40, 0),
                      time(13, 25, 0), time(14, 15, 0), time(15, 5, 0), time(16, 15, 0), time(17, 5, 0),
                      time(18, 50, 0), time(19, 40, 0), time(20, 30, 0)]
        end_time = [time(8, 45, 0), time(9, 35, 0), time(10, 45, 0), time(11, 35, 0), time(12, 25, 0),
                    time(14, 10, 0), time(15, 0, 0), time(15, 50, 0), time(17, 0, 0), time(17, 50, 0),
                    time(19, 35, 0), time(20, 25, 0), time(21, 15, 0)]
        return start_time[lesson['start'] - 1], end_time[lesson['start'] + len - 1 - 1]

    def _rsa_encrypt(self, password_str, e_str, m_str):
        password_bytes = bytes(password_str, 'ascii')
        password_int = int.from_bytes(password_bytes, 'big')
        e_int = int(e_str, 16)
        m_int = int(m_str, 16)
        result_int = pow(password_int, e_int, m_int)
        return hex(result_int)[2:].rjust(128, '0')


def main(username, password, semester_info, data, holiday=[], exchange=[]):
    print("[status] 初始化...")
    timetable = TimeTable(username, password, semester_info, data, holiday=holiday, exchange=exchange)
    print("[status] 登录...")
    try:
        timetable.login()
    except Exception:
        raise

    print("[status] 获取课表信息...")
    try:
        timetable.get_info()
    except Exception:
        raise

    print("[status] 处理课表信息...")
    try:
        timetable.process_info()
    except Exception:
        raise

    '''
    for lesson in timetable.lessons:
        print(lesson)
    '''

    print("[status] 制作ics日历文件...")
    try:
        timetable.make_ics_file()
    except Exception:
        raise


if __name__ == "__main__":
    '''请填写浙大统一身份认证的账户'''
    username = ''

    '''请填写浙大统一身份认证的密码'''
    password = ''

    '''请填写想要查询的学年，格式为20xx-20xx，注意每次只能查询一个学年'''
    data = {'xnm': '2022-2023'}

    '''请填写想要查询的该学年中的学期，请按照示例格式填写。月和日如果为个位数，需要在前补0，变成两位数字'''
    semester_info = [
        {'semester': '春', 'start': '2023-02-27', 'end': '2023-04-23'},
        {'semester': '夏', 'start': '2023-04-24', 'end': '2023-07-02'},
    ]

    holiday = [
        ['2023-04-05', '2023-04-05'],
        ['2023-04-29', '2023-05-03'],
        ['2023-06-22', '2023-06-24'],
    ]

    exchange = [
        ['2023-05-02', '2023-06-19'],
        ['2023-05-03', '2023-05-14'],
    ]

    try:
        main(username, password, semester_info, data, holiday=holiday, exchange=exchange)
    except Exception as err:
        exit('[error] ' + str(err))
        raise

    '''还需要改地址,kaoshi,uid，上下连接'''
