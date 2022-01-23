import tabula
import PyPDF2
import re
from os import listdir
from os.path import isfile, join
from datetime import datetime
import math
import pandas

path_to_report_directory = "/Users/andrew/projects/covid-19-pediatric/pediatric-state-reports-to-process/"
path_to_output_directory = "/Users/andrew/projects/covid-19-pediatric/scraped_data/"


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


if __name__ == '__main__':
    filenames = [f for f in listdir(path_to_report_directory) if isfile(join(path_to_report_directory, f))]

    for filename in filenames:
        print(f'Processing file [{filename}]')
        file = join(path_to_report_directory, filename)
        pdfFileObj = open(file, 'rb')

        # creating a pdf reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        # creating a page object
        pageObj = pdfReader.getPage(0)

        # extracting text from page
        page1_text = pageObj.extractText()

        regex = "Version: ([0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4})"
        date_string = re.search(regex, page1_text).group(1)
        date = datetime.strptime(date_string, '%m/%d/%y')
        print(date)

        tables = tabula.read_pdf(file, pages="all", multiple_tables=True)

        hospitalization_tables = []
        case_tables = []

        for table in tables:
            row_0 = table.loc[[0]].values.tolist()[0]

            print("Checking table...")
            print(table.columns)
            print(row_0)

            if ("Cumulative total cases" in table.columns and len(table.columns) == 8 and (
                    "Location" in table.columns or "Location" in row_0)):
                case_tables.append(table)
                print(f"Found case table:\n{table}")

            if ("Percent children of total" in table.columns and (
                    len(table.columns) == 6 or len(table.columns) == 7) and (
                    "Location" in table.columns or "Location" in row_0)):
                hospitalization_tables.append(table)
                print(f"Found hospitalization table:\n{table}")

        output_filename = f"cases-by-state-{date.strftime('%Y-%m-%d')}.csv"
        output_file_path = join(path_to_output_directory, output_filename)
        column_headers = ["Location", "Age range", "Child population, 2019",
                          "Cumulative child cases",
                          "Percent children of total cases", "Cumulative total cases (all ages)",
                          "Cases per 100,000 children"]
        save_tables_to_csv(case_tables, output_file_path, column_headers)

        output_filename = f"hospitalizations-by-state-{date.strftime('%Y-%m-%d')}.csv"
        output_file_path = join(path_to_output_directory, output_filename)
        column_headers = ["Location", "Age range", "Cumulative child hospitalizations",
                          "Cumulative total hospitalizations (all ages)",
                          "Percent children of total hospitalizations", "Hospitalization rate"]
        save_tables_to_csv(hospitalization_tables, output_file_path, column_headers)
