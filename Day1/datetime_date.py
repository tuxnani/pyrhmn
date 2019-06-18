#!python3

from datetime import datetime
from datetime import date

datetime.today()
#datetime.datetime(2018, 2, 19, 14, 38, 52, 133483)

today = datetime.today()


type(today)
#<class 'datetime.datetime'>


todaydate = date.today()

todaydate
#datetime.date(2018, 2, 19)

type(todaydate)
#<class 'datetime.date'>

todaydate.month
#2

todaydate.year
#2018

todaydate.day
#19


independence = date(2019, 8, 15)
independence
#datetime.date(2019, 8, 15)

if independence is not todaydate:
    print("Sorry there are still " + str((independence - todaydate).days) + " until Independence Day!")
else:
    print("Yay it's Independence Day!")