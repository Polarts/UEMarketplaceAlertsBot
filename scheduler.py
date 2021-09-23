import os
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=10)
def timed_job():
    os.system("python manage.py runbot --debug")

sched.start()