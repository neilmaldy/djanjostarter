from django.shortcuts import render
from asupcheck.models import AsupCheckV1
from asupcheck.forms import AsupCheckV1Form
import time
import unicodedata
import re
import csv
import sys
import os
import os.path
from myLogging import printToLog


def thanks2(request):

    # Render the response and send it back!
    return render(request, 'thanks2.html')


def asupcheckv1view(request):
    # A HTTP POST?
    if request.method == 'POST':
        form = AsupCheckV1Form(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            printToLog("form.is_valid() returned True")
            # Save the new category to the database.
            model_instance = form.save(commit=True)
            # print "Writing filers.txt from view"

            debug_it = False
            # print type(model_instance.customer_name)
            # print type(model_instance.name)
            # print type(model_instance.filers)
            # print model_instance.email

            ascii_report_id = re.sub(r'\W+', '_', model_instance.report_id)
            job_file_name = ascii_report_id + ".txt"
            printToLog(job_file_name)
            # output_file_name = ascii_report_id + ".csv"
            output_file_name = ascii_report_id
            printToLog(output_file_name)
            # ascii_filers = str(unicodedata.normalize('NFKD', model_instance.filers).encode('ascii', 'ignore'))
            ascii_filers = model_instance.filers
            for line in ascii_filers.splitlines():
                if line:
                    if "#option:report_name:" in line:
                        temp_words = line.strip().split("#option:report_name:")
                        if len(temp_words) == 2:
                            if temp_words[1]:
                                output_file_name = temp_words[1].strip().replace(' ', '_')
                        break
            i = 0
            # output_file = open("Z:\\AsupMining\on_demand\\new\\" + job_file_name, 'wb')
            # todo fix output_file
            # output_file = open("/home/xubuntu/AsupMining/on_demand/new/" + job_file_name, 'wb')
            output_file = open("new_jobs/" + job_file_name, 'w')

            if "ec-" in model_instance.check:
                job_command = "#job_command:e-asupcheck.py"
            else:
                job_command = "#job_command:asupcheck.py"

            if model_instance.verbose:
                output_file.write(job_command + " -v -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name + '\n')
                print(job_command + " -v -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name)
                # output_file.write("#job_command:asupcheck.py -v -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name + '\n')
                # print "#job_command:asupcheck.py -v -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name
            else:
                # output_file.write("#job_command:burt822180check.py:" + job_file_name + ':' + output_file_name + '\n')
                output_file.write(job_command + " -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name + '\n')
                print(job_command + " -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name)
                # output_file.write("#job_command:asupcheck.py -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name + '\n')
                # print "#job_command:asupcheck.py -c " + model_instance.check + ":" + job_file_name + ':' + output_file_name
            i += 1

            for line in ascii_filers.splitlines():
                if line:
                    i += 1
                    output_file.write(line + '\n')
                    if debug_it:
                        printToLog(line)

            output_file.write('#option:email:' + model_instance.email + '@netapp.com\n')

            printToLog("Sending report to " + model_instance.email + '@netapp.com')
            output_file.close()
            os.chmod("new_jobs/" + job_file_name, 0o666)
            printToLog("wrote " + str(i) + " lines to " + job_file_name)

            # Now call the index() view.
            # The user will be shown the homepage.
            return thanks2(request)

        else:
            # The supplied form contained errors - just print them to the terminal.
            print(form.errors)
    else:
        # If the request was not a POST, display the form to enter details.
        form = AsupCheckV1Form()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).
    return render(request, 'asupcheck.html', {'form': form})


def dashboard(request):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        # category_list = asupcheckv1.objects.order_by('-report_id')
        category_list = AsupCheckV1.objects.filter(report_id__contains=time.strftime("%Y%m%d")).order_by('-report_id')
        context_dict = {'categories': category_list}
    except AsupCheckV1.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'dashboard.html', context_dict)


def dashboard2(request):

    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # So the .get() method returns one model instance or raises an exception.
        category_list = AsupCheckV1.objects.order_by('-report_id')
        # category_list = asupcheckv1.objects.filter(report_id__contains=time.strftime("%Y%m%d")).order_by('-report_id')
        context_dict = {'categories': category_list}
    except AsupCheckV1.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything - the template displays the "no category" message for us.
        pass

    # Go render the response and return it to the client.
    return render(request, 'dashboard2.html', context_dict)
