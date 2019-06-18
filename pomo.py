#!/usr/bin/env python3

import gtts
import os
import time

workTime = 25
breakTime = 5

workTimeSec = workTime * 60
breakTimeSec = breakTime * 60

workTimerStartAlertText = 'Work time started. Work timer has been set for ' + str(workTime) + 'minutes. Work Hard.'
breakTimerStartAlertText = 'Work time over. Break timer has been set for ' + str(breakTime) + ' minutes. Have Fun.'

workTimerStartAlert = gtts.gTTS(text = workTimerStartAlertText, lang = 'en')
workTimerStartAlert.save('/var/tmp/workTimerStartAlert.mp3')
os.system('mpg123 /var/tmp/workTimerStartAlert.mp3')

startTime = time.time()
while time.time() != startTime + workTimeSec:
    pass

breakTimerStartAlert = gtts.gTTS(text = breakTimerStartAlertText, lang = 'en')
breakTimerStartAlert.save('/var/tmp/breakTimerStartAlert.mp3')
os.system('mpg123 /var/tmp/breakTimerStartAlert.mp3')

# run the break clock
startTime = time.time()    # store the starting time
while time.time() != startTime + breakTimeSec:
    pass
