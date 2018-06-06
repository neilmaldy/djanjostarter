from django import forms
from asupcheck.models import AsupCheckV1
import time
import unicodedata
import re

# todo update CHECKS here and in models.py when adding new asupcheck scripts

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


class AsupCheckV1Form(forms.ModelForm):
    report_id = forms.CharField(widget=forms.HiddenInput(), required=False)
    name = forms.CharField(max_length=36, label="*Your Name: ", min_length=1, required=True)
    check = forms.ChoiceField(choices=CHECKS, label="*Check: ", required=True)
    email = forms.CharField(widget=forms.TextInput, max_length=36, label="*User Name: ", min_length=1, required=True)
    verbose = forms.BooleanField(label="Verbose Output: ", required=False)
    options = forms.CharField(widget=forms.TextInput, max_length=36, label="Options: ", required=False)
    # asupcheck now supports cluster uuids
    filers = forms.CharField(widget=forms.Textarea, label="*Serial numbers, cluster UUIDs, options: ", required=True)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    # An inline class to provide additional information on the form.
    class Meta:
        # Provide an association between the ModelForm and a model
        model = AsupCheckV1
        fields = ('name', 'check', 'email', 'verbose', 'options', 'filers', 'report_id')

    def clean(self):
        print("Cleaning...")
        cleaned_data = self.cleaned_data
        if 'name' in cleaned_data:
            name = cleaned_data.get('name')
            # ascii_name = str(unicodedata.normalize('NFKD', name).encode('ascii', 'ignore'))
            ascii_name = name
            cleaned_data['report_id'] = time.strftime("%Y%m%d%H%M%S") + '-' + ascii_name + '-' + cleaned_data['check']
            print("have report_id " + cleaned_data['report_id'])
            cleaned_data['slug'] = cleaned_data['report_id']
        else:
            self._errors['name'] = [u'SAM Name is required']

        if 'email' in cleaned_data:
            temp_email = cleaned_data['email']
            if '@' in temp_email:
                # try to remove @domain from email
                cleaned_data['email'] = temp_email.split('@')[0]
            print("have user name " + cleaned_data['email'])
        else:
            self._errors['email'] = [u'SAM Userid is required']
        return cleaned_data
