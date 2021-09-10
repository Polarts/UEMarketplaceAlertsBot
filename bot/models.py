from django.db import models

class AssetSource(models.Model):

    class SourceTypes(models.TextChoices):
        JSON = 'JSON',
        SCRAPE = 'SCRP'

    title = models.CharField(max_length=200)
    type = models.CharField(
        max_length=4, 
        choices=SourceTypes.choices, 
        default=SourceTypes.JSON
    )
    post_title = models.CharField(max_length=200)
    url = models.CharField(max_length=1000)


class Asset(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    time_stamp = models.DateTimeField()
    sent = models.BooleanField()
    source = models.ForeignKey(AssetSource, on_delete=models.CASCADE)

class AppState(models.Model):
    
    class PlayStates(models.TextChoices):
        PLAY = 'PLAY',
        STOP = 'STOP'

    class HealthStates(models.TextChoices):
        GOOD = 'GOOD',
        BAD = 'BAD',
        PENDING = 'PEND'

    play_state = models.CharField(
        max_length=4,
        choices=PlayStates.choices,
        default=PlayStates.STOP
    )
    health_state = models.CharField(
        max_length=4,
        choices=HealthStates.choices,
        default=HealthStates.PENDING
    )

class LogEntry(models.Model):

    class LogEntryTypes(models.IntegerChoices):
        LOG = 0,
        WARN = 1,
        ERR = 2

    time_stamp = models.DateTimeField()
    source = models.CharField(max_length=200)
    type = models.IntegerField(choices=LogEntryTypes.choices)
    text = models.CharField(max_length=1000)