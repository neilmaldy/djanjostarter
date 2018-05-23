import pandas as pd
import numpy as np
import datetime
import os
import sys
import time
import logging
import platform
import zipfile

debug_it = 0


def print_to_log(log_string):
    """ Print to log file (stderr)
    Prints the logString to stderr, prepends date and time
    """
    print(time.strftime("%H:%M:%S") + ": " + log_string, file=sys.stderr)
    logging.info(time.strftime("%H:%M:%S") + ": " + log_string)
    if debug_it:
        with open("temp.log", mode='a', encoding='utf-8') as templog:
            print(time.strftime("%H:%M:%S") + ": " + log_string, file=templog)


def read_risk_files(input_file=None):
    converters = {'SERIAL NUMBER': str,
                  'MORE INFORMATION 1': str, 'MORE INFORMATION 2': str, 'MORE INFORMATION 3': str, 'MORE INFORMATION 4': str, 'MORE INFORMATION 5': str,
                  'INTERNAL INFORMATION 1': str, 'INTERNAL INFORMATION 2': str, 'INTERNAL INFORMATION 3': str, 'INTERNAL INFORMATION 4': str, 'INTERNAL INFORMATION 5': str}

    expected_columns = {'SERIAL NUMBER',
                        'HOSTNAME',
                        'SITE',
                        'MODEL',
                        'SYSTEM VERSION',
                        'NAME',
                        'CATEGORY',
                        'SEVERITY',
                        'DETAILS',
                        'MORE INFORMATION 1',
                        'MORE INFORMATION 2',
                        'MORE INFORMATION 3',
                        'MORE INFORMATION 4',
                        'MORE INFORMATION 5',
                        'PUBLIC',
                        'INTERNAL INFORMATION 1',
                        'INTERNAL INFORMATION 2',
                        'INTERNAL INFORMATION 3',
                        'INTERNAL INFORMATION 4',
                        'INTERNAL INFORMATION 5'}

    risk_df_list = []

    if input_file:
        if (zipfile.is_zipfile(input_file) or ((type(input_file) is str and '.zip' in input_file))) and not ((type(input_file) is str and '.xlsx' in input_file)):
            my_zip_file = zipfile.ZipFile(input_file)
            for file_name in my_zip_file.namelist():
                print_to_log('Reading ' + file_name)
                risk_df_list.append(pd.read_excel(my_zip_file.open(file_name), skiprows=[0, 1], usecols='A,E:L,O:Y', converters=converters))
        else:
            print_to_log('Reading ' + input_file)
            risk_df_list.append(pd.read_excel(input_file, skiprows=[0, 1], usecols='A,E:L,O:Y', converters=converters))
    else:
        file_count = 1
        file_name = "risk" + str(file_count) + '.xlsx'
        try:
            while os.path.isfile(file_name):
                print_to_log('Reading ' + file_name)
                risk_df_list.append(pd.read_excel(file_name, skiprows=[0, 1], usecols='A,E:L,O:Y', converters=converters))
                file_count += 1
                file_name = "risk" + str(file_count) + '.xlsx'
        except FileNotFoundError:
            print_to_log('Done reading risk file(s)')

    for temp_df in risk_df_list:
        if not (set(temp_df.columns.values) <= expected_columns):
            print_to_log('Missing columns in source report: ' + ','.join(expected_columns - set(temp_df.columns.values)))

    risk_df = pd.concat(risk_df_list)
    risk_df.dropna(subset=['HOSTNAME', "NAME"], how='any', inplace=True)
    risk_df.replace(np.nan, '', inplace=True)
    risk_df['HOSTNAME_RISK'] = risk_df.apply(lambda row: row.HOSTNAME + ',' + row.NAME, axis=1)
    risk_df.set_index('HOSTNAME_RISK', inplace=True)
    return risk_df


def build_set(filename, file_comment='#one entry per line', form_data=None):
    temp_set = set()
    if form_data:
        # lookup filename and return appropriate form data
        if debug_it:
            print_to_log('Using django form data...')
        field_name = filename.replace('.txt', '')
        if field_name in form_data:
            lines = form_data[field_name].splitlines()
            for line in lines:
                if line and line[0] != '#':
                    temp_set.add(line)
                    if debug_it:
                        print_to_log(filename + ' ' + line.strip())
    else:
        try:
            with open(filename, encoding='utf-8') as fp:
                lines = fp.read().splitlines()

            for line in lines:
                if line and line[0] != '#':
                    temp_set.add(line)
                    if debug_it:
                        print_to_log(filename + ' ' + line.strip())
        except FileNotFoundError:
            with open(filename, 'w', encoding='utf-8') as fp:
                print(file_comment, file=fp)
                print_to_log('Created ' + filename)
    return temp_set


def generate_ars_scrub(input_file_name=None, django_form_data=None, working_directory=None, output_file=None):

    if working_directory:
        os.chdir(working_directory)

    if output_file is None:
        output_file = 'risks_' + datetime.date.today().strftime("%Y%W%w")

    df = read_risk_files(input_file_name)

    print_to_log('Adding comments...')

    risk_comments = build_set('risk_comments.txt', '#Use a tab to separate risk from comment', django_form_data)

    comment_by_risk = {}

    for risk_comment in risk_comments:
        try:
            risk, comment = risk_comment.split('\t', 1)
            comment_by_risk[risk] = comment
        except ValueError:
            print_to_log('Could not parse comment ' + risk_comment)

    df['Comments'] = df['NAME'].map(comment_by_risk)

    host_risk_comments = build_set('host_risk_comments.txt', '#Use tabs to separate host, risk, and comment', django_form_data)

    comment_by_host_risk = {}

    for host_risk_comment in host_risk_comments:
        try:
            host_risk, comment = host_risk_comment.split('\t', 1)
            if ',' in host_risk:
                comment_by_host_risk[host_risk] = comment
        except ValueError:
            print_to_log('Could not parse comment ' + host_risk_comment)

    df['Comments'].update(pd.Series(comment_by_host_risk))

    writer = pd.ExcelWriter(output_file + '.xlsx')

    if 'PUBLIC' in list(df.columns.values):
        print_to_log('Removing risks with PUBLIC=N...')
        df[df.PUBLIC == 'N'].to_excel(writer, sheet_name='NotPublic', index=True)
        df.drop(df[df.PUBLIC == 'N'].index, inplace=True)
        df.drop(columns=['PUBLIC'], inplace=True)

    print_to_log('Removing risks per config files...')
    sites_to_remove = build_set('sites_to_remove.txt', form_data=django_form_data)

    risks_to_remove = build_set('risks_to_remove.txt', form_data=django_form_data)

    hostname_risks_to_remove = build_set('hostname_risks_to_remove.txt', form_data=django_form_data)

    hostnames_to_remove = build_set('hostnames_to_remove.txt', form_data=django_form_data)

    df_to_remove = df[(df.SITE.isin(sites_to_remove)) | (df.NAME.isin(risks_to_remove)) | (df.HOSTNAME.isin(hostnames_to_remove)) | (df.index.isin(hostname_risks_to_remove))]

    df_to_remove.to_excel(writer, sheet_name='Remove', index=True)
    # df.drop(list(hostname_risks_to_remove), inplace=True)
    df.drop(df_to_remove.index, inplace=True)
    df.to_excel(writer, sheet_name='RiskDetails', index=True)

    print_to_log('Saving risks dataframe to ' + 'df-' + output_file)
    df.to_pickle('df-' + output_file)

    risks_to_highlight = build_set('risks_to_highlight.txt', form_data=django_form_data)

    hostname_risks_to_highlight = build_set('hostname_risks_to_highlight.txt', form_data=django_form_data)

    risks_to_monitor = build_set('risks_to_monitor.txt', form_data=django_form_data)

    risks_to_ack = build_set('risks_to_ack.txt', form_data=django_form_data)

    hostname_risks_to_ack = build_set('hostname_risks_to_ack.txt', form_data=django_form_data)

    repeat_risks_to_highlight = build_set('repeat_risks_to_highlight.txt', form_data=django_form_data)

    for risk in risks_to_highlight & risks_to_monitor:
        print_to_log('Risk duplicated in risks_to_highlight & risks_to_monitor: ' + risk)

    for risk in risks_to_highlight & risks_to_ack:
        print_to_log('Risk duplicated in risks_to_highlight & risks_to_ack: ' + risk)

    for risk in risks_to_monitor & risks_to_ack:
        print_to_log('Risk duplicated in risks_to_monitor & risks_to_ack: ' + risk)

    for risk in hostname_risks_to_highlight & repeat_risks_to_highlight:
        print_to_log('Risk duplicated in hostname_risks_to_highlight & repeat_risks_to_highlight: ' + risk)

    days = 1
    df_file_prefix = 'df-' + output_file.split('_')[0]
    while days < 90:
        day = (datetime.date.today() - datetime.timedelta(days=days)).strftime("%Y%W%w")
        if not os.path.isfile(df_file_prefix + '_' + day):
            days += 1
            continue
        else:
            print_to_log("Comparing to history from " + day)
            df_previous = pd.read_pickle(df_file_prefix + '_' + day)
            previous_risks = set(df_previous.index)
            new_risks = set(set(df.index))
            if debug_it:
                for new_risk in new_risks - previous_risks:
                    print_to_log('New ' + new_risk)
                for dropped_risk in previous_risks - new_risks:
                    print_to_log('Dropped ' + dropped_risk)
            new_risks_df = df[df.index.isin(new_risks - previous_risks)]
            new_risks_df[~(new_risks_df.NAME.isin(risks_to_ack))].to_excel(writer, sheet_name='NewRisks', index=True)
            # df[(df.index.isin(new_risks - previous_risks)) & ~(df.NAME.isin(risks_to_ack))].to_excel(writer, sheet_name='NewRisks', index=True)
            df_previous[df_previous.index.isin(previous_risks - new_risks)].to_excel(writer, sheet_name='DroppedRisks', index=True)
            repeat_risks_df = df[df.index.isin(new_risks & previous_risks)]
            # todo should we remove acknowledged risks?
            repeat_risks_df[repeat_risks_df.NAME.isin(repeat_risks_to_highlight)].to_excel(writer, sheet_name='RepeatRisks', index=True)
            break

    df[((df.NAME.isin(risks_to_highlight)) | (df.index.isin(hostname_risks_to_highlight))) & ~(df.index.isin(hostname_risks_to_ack))].to_excel(writer, sheet_name='Highlight', index=True)
    df[(df.NAME.isin(risks_to_ack)) | (df.index.isin(hostname_risks_to_ack))].to_excel(writer, sheet_name='Acknowledge', index=True)
    # df[df.index.isin(hostname_risks_to_highlight)].to_excel(writer, sheet_name='HostHighlight', index=True)
    # df[df.index.isin(hostname_risks_to_ack)].to_excel(writer, sheet_name='HostAcknowledge', index=True)
    df[~(df.NAME.isin(risks_to_ack)) & ~(df.NAME.isin(risks_to_highlight)) & ~(df.NAME.isin(risks_to_monitor))].to_excel(writer, sheet_name='NotClassified', index=True)
    df.pivot_table(index='NAME', values=['HOSTNAME'], aggfunc='count').sort_values(by=['HOSTNAME'], ascending=False).to_excel(writer, sheet_name='Summary')
    writer.save()
    print_to_log('Done writing report to ' + output_file + '.xlsx.')
    time.sleep(3)
    if not django_form_data:
        print_to_log('Opening ' + output_file + '.xlsx...')
        if platform.system() == "Darwin":
            # mac
            os.system("open " + output_file + '.xlsx.')
        else:
            # pc
            os.system("start " + output_file + '.xlsx.')


if __name__ == "__main__":
    generate_ars_scrub()
