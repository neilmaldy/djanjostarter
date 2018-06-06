from django.db import models
from django.template.defaultfilters import slugify
import time

# todo update CHECKS here and in forms.py when adding new asupcheck scripts

CHECKS = (
    ('ac-utf-8-vol-lang.py', 'UTF-8 Security Check'),
    # ('ac-burt657692.py', 'Burt 657692 (Dedup)'),
    # ('ac-ctran.py', 'Burt 926521 (CTRAN)'),
    ('ac-nse-check.py', 'Burt 812801 (NSE)'),
    ('ac-burt822180.py', 'Burt 822180 (SP)'),
    # ('ac-atto-fw.py', 'Burt 878406 (ATTO)'),
    ('ac-failed-drives.py', 'Disk Case Failed Drive Counts (ONTAP)'),
    ('ac-leap2nd-nexus.py', 'Cisco Cluster Interconnect Switch'),
    ('ac-customer-logs.py', 'Customer Log Counts'),
    ('ac-drivemine.py', 'Drive Miner'),
    # ('ac-flashcache.py', 'FlashCache FW'),
    # ('ac-hepsu.py', 'HE-PSU Check'),
    ('ac-failed-disk-registry.py', 'Failed Disk Registry Analysis'),
    # ('ac-hourly-ops.py', 'Hourly Ops'),
    ('ac-flash-ib.py', 'IB Scrub Flash Details'),
    ('ac-licensecheck.py', 'License Check'),
    # ('ac-mailbox-check.py', 'Mailbox Disk Check'),
    # ('ac-ndmp-check.py', 'NDMP Frequency'),
    ('ac-optioncheck.py', 'Option Check'),
    ('ac-pam-fc-list.py', 'PAM/FC List'),
    ('ac-section-changes.py', 'Section Changes'),
    ('ac-section-grep.py', 'Simple ASUP Search'),
    ('ac-section-to-csv.py', 'Section to CSV'),
    ('ac-shelf-psus.py', 'Shelf PSU List'),
    ('ac-aggr-raid.py', 'Shelf Redundancy'),
    ('ac-snapmirror-status.py', 'SnapMirror Relationships'),
    ('ac-unowned-disks.py', 'Unowned Disks Report'),
    ('ac-uptime.py', 'Uptime Report'),
    ('ac-drive-spare-aggr.py', 'Bank of America Drive Check'),
    ('ac-xml-section.py', 'XML Section to CSV'),
    # ('ac-simpleasupcheck.py', 'Simple Asup Check'),
    # ('ac-xlsx.py', 'Excel demo'),
    ('ec-health-check.py', 'E-Series Health Check'),
)


class AsupCheckV1(models.Model):

    report_id = models.CharField(max_length=128, unique=True)
    name = models.CharField(max_length=36, default='')
    check = models.CharField(max_length=36, choices=CHECKS)
    email = models.CharField(max_length=36, default='')
    verbose = models.BooleanField(default=False)
    options = models.CharField(max_length=36, default='')
    filers = models.TextField(default='#')
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
            # self.slug = slugify(self.name) + time.strftime("%Y%m%d%H%M%S")
            self.slug = slugify(self.report_id)
            super(AsupCheckV1, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name
