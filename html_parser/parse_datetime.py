from datetime import datetime


month_num = [('янв', '01'), ('фев', '02'), ('мар', '03'),
             ('мая', '05'), ('дек', '12'), ('ноя', '11'),
             ('окт', '10'), ('сен', '09'), ('авг', '08'),
             ('июл', '07'), ('апр', '04'), ('июн', '06')]


def str_to_datetime(date_time):
    for old, new in month_num:
        date_time = date_time.replace(old, new)

    len_date = len(date_time.split())
    if len_date == 4:
        return datetime.strptime(date_time, '%d %m %Y, %H:%M')
    if len_date == 3:
        result = datetime.strptime(date_time, '%d %m, %H:%M')
        return result.replace(year=datetime.now().year)
    if len_date == 1:
        result = datetime.strptime(date_time, '%H:%M')
        return result.replace(day=datetime.now().day, month=datetime.now().month, year=datetime.now().year)
    raise TypeError('No available cast from "{}" to datetime object'.format(date_time))
