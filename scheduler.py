import os
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=9)
def scheduled_job():
    os.system("python manage.py runbot")

sched.start()