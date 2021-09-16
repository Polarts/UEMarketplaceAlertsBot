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

    def __str__(self):
        return f"{self.title} | {self.type}"


class Asset(models.Model):
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=1000)
    link = models.CharField(max_length=1000)
    time_stamp = models.DateTimeField()
    sent = models.BooleanField()
    source = models.ForeignKey(AssetSource, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} | {('sent' if self.sent else 'unsent')}"

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

    def to_dict(self):
        return {
            'play_state': self.play_state,
            'health_state': self.health_state
        }

class LogEntry(models.Model):

    class LogEntryTypes(models.IntegerChoices):
        LOG = 0,
        WARN = 1,
        ERR = 2

    time_stamp = models.DateTimeField()
    source = models.CharField(max_length=200)
    type = models.IntegerField(choices=LogEntryTypes.choices)
    text = models.CharField(max_length=1000)

    def get_type_string(self):
        return {
            0: 'LOG',
            1: 'WARN',
            2: 'ERR'
        }[self.type]

    def get_formatter_time_stamp(self):
        return self.time_stamp.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"[{self.get_formatter_time_stamp()}] {self.source} | {self.get_type_string()} | {self.text}"

    def to_dict(self):
        return {
            'time_stamp': self.get_formatter_time_stamp(),
            'source': self.source,
            'type': self.get_type_string(),
            'text': self.text
        }
