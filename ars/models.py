from django.conf import settings
from django.db import models
from django.urls import reverse


class Report(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    risks_to_highlight = models.TextField(blank=True)
    hostname_risks_to_highlight = models.TextField(blank=True)
    repeat_risks_to_highlight = models.TextField(blank=True)
    risks_to_ack = models.TextField(blank=True)
    hostname_risks_to_ack = models.TextField(blank=True)
    risks_to_remove = models.TextField(blank=True)
    hostname_risks_to_remove = models.TextField(blank=True)
    risks_to_monitor = models.TextField(blank=True)
    risk_comments = models.TextField(blank=True)
    host_risk_comments = models.TextField(blank=True)
    sites_to_remove = models.TextField(blank=True)
    hostnames_to_remove = models.TextField(blank=True)
    input_files = models.FileField(null=True, blank=True)
    output_file = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('report_detail', args=[str(self.id)])