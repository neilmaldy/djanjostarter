from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.conf import settings
from django.core.files import File
import os

from . import models


class HomePageView(TemplateView):
    template_name = 'home.html'


class ReportListView(LoginRequiredMixin, ListView):
    model = models.Report
    template_name = 'report_list.html'
    login_url = 'login'


class ReportDetailView(LoginRequiredMixin, DetailView):
    model = models.Report
    template_name = 'report_detail.html'
    login_url = 'login'


class ReportUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Report
    fields = [
        'name',
        'input_files',
        'risks_to_highlight',
        'hostname_risks_to_highlight',
        'repeat_risks_to_highlight',
        'risks_to_ack',
        'hostname_risks_to_ack',
        'risks_to_remove',
        'hostname_risks_to_remove',
        'risks_to_monitor',
        'risk_comments',
        'host_risk_comments',
        'sites_to_remove',
        'hostnames_to_remove',
    ]
    template_name = 'report_edit.html'
    login_url = 'login'

    def form_valid(self, form):
        self.request.FILES['input_files'].open('r')
        with open(os.path.join(settings.MEDIA_ROOT, 'file.txt'), 'w') as f:
            f.write(str(self.request.FILES['input_files'].read().upper()))
        form.instance.output_file.save('file.txt', File(open(os.path.join(settings.MEDIA_ROOT, 'file.txt'))))
        return super().form_valid(form)


class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Report
    template_name = 'report_delete.html'
    success_url = reverse_lazy('report_list')
    login_url = 'login'


class ReportCreateView(LoginRequiredMixin, CreateView):
    model = models.Report
    template_name = 'report_new.html'
    fields = [
        'name',
        'input_files',
        'risks_to_highlight',
        'hostname_risks_to_highlight',
        'repeat_risks_to_highlight',
        'risks_to_ack',
        'hostname_risks_to_ack',
        'risks_to_remove',
        'hostname_risks_to_remove',
        'risks_to_monitor',
        'risk_comments',
        'host_risk_comments',
        'sites_to_remove',
        'hostnames_to_remove',
    ]
    login_url = 'login'

    def form_valid(self, form):
        form.instance.author = self.request.user
        self.request.FILES['input_files'].open('r')
        with open(os.path.join(settings.MEDIA_ROOT, 'file.txt'), 'w') as f:
            f.write(str(self.request.FILES['input_files'].read().upper()))
        form.instance.output_file.save('file.txt', File(open(os.path.join(settings.MEDIA_ROOT, 'file.txt'))))
        return super().form_valid(form)
