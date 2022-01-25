import tabula
import PyPDF2
import re
from os import listdir
from os.path import isfile, join, isdir
from datetime import datetime
import math
import pandas
import sys
import time
import shutil

path_to_report_directory = sys.argv[1]
path_to_output_directory = sys.argv[2]
path_to_processed_report_directory = sys.argv[3]

list_of_reports_with_no_case_data = []

list_of_reports_with_no_hospitalization_data = [
    "AAP and CHA - Children and COVID-19 State Data Report 11.26.20 FINAL.pdf",
    "AAP and CHA - Children and COVID-19 State Data Report 12.24.20 FINAL.pdf"
]


def save_tables_to_csv(tables, output_file_path, column_headers):
    for table in tables:
        print(table)
        print(table.columns)

        row_0 = table.loc[[0]].values.tolist()[0]

        should_drop_row = True
        for elem in row_0:
            should_drop_row = should_drop_row and (type(elem) != int or type(elem) != float or math.isnan(elem))
            print(f"[{elem}] [{should_drop_row}]")

        if (should_drop_row):
            print(f"Dropping row [0]")
            table.drop(index=[0], inplace=True)

        col_1 = table[table.columns[1]].values.tolist()
        print(f"col_1 [{col_1}]")
        should_drop_column = True
        for elem in col_1:
            if type(elem) == str:
                should_drop_column = False
            should_drop_column = should_drop_column and math.isnan(elem)
            print(f"[{elem}] [{should_drop_column}]")

        print(f"column_headers before [{column_headers}]")
        if (should_drop_column):
            print(f"Dropping column [{table.columns[1]}]")
            table.drop(columns=[table.columns[1]], inplace=True)

        print(f"column_headers after [{column_headers}]")
        table.columns = column_headers

        num_rows = len(table)
        table.insert(0, "Date", [date for _ in range(num_rows)], allow_duplicates=True)
        print(table)

        print(f"output_file_path [{output_file_path}]")
        print(f"table.columns [{table.columns}]")

    combined_table = pandas.concat(tables)

    with open(output_file_path, 'w', newline='') as csvfile:
        print(combined_table.to_csv(path_or_buf=csvfile, index=False))


def make_some_beeps():
    print('\a')
    time.sleep(0.2)
    print('\a')
    time.sleep(0.2)
    print('\a')
    time.sleep(0.1)
    print('\a')
    time.sleep(0.2)
    print('\a')
    time.sleep(0.4)
    print('\a')
    time.sleep(0.2)
    print('\a')


def do_post_processing(filename):
    print(f'Done processing file [{filename}]')
    source = join(path_to_report_directory, filename)
    dest = join(path_to_processed_report_directory, filename)
    print(f'Moving file to [{dest}]')
    shutil.move(source, dest)


if __name__ == '__main__':
    if not isdir(path_to_report_directory):
        print(f'ERROR: [{path_to_report_directory}] is not a valid directory')
        exit(1)

    if not isdir(path_to_output_directory):
        print(f'ERROR: [{path_to_output_directory}] is not a valid directory')
        exit(1)

    if not isdir(path_to_processed_report_directory):
        print(f'ERROR: [{path_to_processed_report_directory}] is not a valid directory')
        exit(1)

    print(f'Processing files from report directory [{path_to_report_directory}]')
    print(f'Using output directory [{path_to_output_directory}]')
    filenames = [f for f in listdir(path_to_report_directory) if isfile(join(path_to_report_directory, f))]

    for filename in filenames:
        if not filename.lower().endswith('.pdf'):
            print(f'Skipping file [{filename}] because not a pdf.')
            continue

        print(f'Processing file [{filename}]')
        file = join(path_to_report_directory, filename)
        pdfFileObj = open(file, 'rb')

        # creating a pdf reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        # creating a page object
        pageObj = pdfReader.getPage(0)

        # extracting text from page
        page1_text = pageObj.extractText()

        # Get date of report from front page
        regex = "Version\n{0,1}: ([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})"
        regex_match = re.search(regex, page1_text)

        if regex_match is None:
            print(f'Unable to find regex [{regex}] in text [{page1_text}]')
            exit(1)

        date_string = regex_match.group(1)
        date = datetime.strptime(date_string, '%m/%d/%y')
        print(date)

        # Extract all tables from report
        tables = tabula.read_pdf(file, pages="all", multiple_tables=True)

        hospitalization_tables = []
        case_tables = []

        # Loop through tables to find Case data and Hospitalization data
        for table in tables:
            row_0 = table.loc[[0]].values.tolist()[0]

            print("Checking table...")
            print(table.columns)
            print(row_0)

            if (("Cumulative total cases" in table.columns or "Number of child cases" in row_0)
                    and len(table.columns) == 8
                    and ("Location" in table.columns or "Location" in row_0)):
                case_tables.append(table)
                print(f"Found case table:\n{table}")
            else:
                print(f'Not the case table...')
                print(f'* "Cumulative total cases" in table.columns: {"Cumulative total cases" in table.columns}')
                print(f'* len(table.columns) == 8: {len(table.columns) == 8}')
                print(f'* "Location" in table.columns: {"Location" in table.columns}')
                print(f'* "Location" in row_0: {"Location" in row_0}')

            if ("Percent children of total" in table.columns and (
                    len(table.columns) == 6 or len(table.columns) == 7) and (
                    "Location" in table.columns or "Location" in row_0)):
                hospitalization_tables.append(table)
                print(f"Found hospitalization table:\n{table}")
            else:
                print(f'Not the hospitalization table...')
                print(f'* "Percent children of total" in table.columns: {"Percent children of total" in table.columns}')
                print(f'* len(table.columns) == 6: {len(table.columns) == 6}')
                print(f'* len(table.columns) == 7: {len(table.columns) == 7}')
                print(f'* "Location" in table.columns: {"Location" in table.columns}')
                print(f'* "Location" in row_0: {"Location" in row_0}')

        # Save case tables to CSV
        output_filename = f"cases-by-state-{date.strftime('%Y-%m-%d')}.csv"
        output_file_path = join(path_to_output_directory, output_filename)
        column_headers = ["Location", "Age range", "Child population, 2019",
                          "Cumulative child cases",
                          "Percent children of total cases", "Cumulative total cases (all ages)",
                          "Cases per 100,000 children"]

        if len(case_tables) == 0:
            if filename in list_of_reports_with_no_case_data:
                print(f'Skipping creation of case CSV for [{filename}] because this report does not contain case data.')
            else:
                print(f'ERROR: No case tables found in report [{filename}]')
                make_some_beeps()
                exit(1)
        else:
            print(f'Saving [{len(case_tables)}] case tables to CSVs.')
            save_tables_to_csv(case_tables, output_file_path, column_headers)

        # Save hospitalization tables to CSV
        output_filename = f"hospitalizations-by-state-{date.strftime('%Y-%m-%d')}.csv"
        output_file_path = join(path_to_output_directory, output_filename)
        column_headers = ["Location", "Age range", "Cumulative child hospitalizations",
                          "Cumulative total hospitalizations (all ages)",
                          "Percent children of total hospitalizations", "Hospitalization rate"]

        if len(hospitalization_tables) == 0:
            if filename in list_of_reports_with_no_hospitalization_data:
                print(f'Skipping creation of hospitalization CSV for [{filename}] '
                      f'because this report does not contain hospitalization data.')
            else:
                print(f'ERROR: No hospitalization tables found in report [{filename}]')
                make_some_beeps()
                exit(1)
        else:
            print(f'Saving [{len(hospitalization_tables)}] hospitalization tables to CSVs.')
            save_tables_to_csv(hospitalization_tables, output_file_path, column_headers)

        do_post_processing(filename)

    print(f'Done processing files from report directory [{path_to_report_directory}]')
