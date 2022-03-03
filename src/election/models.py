from django.db import models 


class Election(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    public_key = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(choices=(
        ("started", "started"),
        ("ended", "ended"),
        ("prepration", "prepration")
    ),max_length=30, default="prepration")

    def __str__(self):
        return self.title

    def save(self, ):
        self.start_time = self.start_time.replace(minute=0, second=0, microsecond=0)
        self.end_time = self.end_time.replace(minute=0, second=0, microsecond=0)
        super().save()

    