# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import tabula
import PyPDF2
import re
from os import listdir
from os.path import isfile, join

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

    path_to_report_directory = "/Users/andrew/projects/covid-19/pediatric-state-reports/"
    files = [f for f in listdir(path_to_report_directory) if isfile(join(path_to_report_directory, f))]
    # file = "/Users/andrew/projects/covid-19/pediatric-state-reports/AAP and CHA - Children and COVID-19 State Data Report 6.10 FINAL.pdf"

    for filename in files:
        print(f'Processing file [{filename}]')
        file = join(path_to_report_directory, filename)
        pdfFileObj = open(file, 'rb')

        # creating a pdf reader object
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

        # printing number of pages in pdf file
        # print(pdfReader.numPages)

        # creating a page object
        pageObj = pdfReader.getPage(0)

        # extracting text from page
        page1_text = pageObj.extractText()
        # print(page1_text)

        regex = "Version: ([0-9]{1,2}/[0-9]{1,2}/[0-9]{2})"
        date = re.search(regex, page1_text).group(1)
        print(date)

        tables = tabula.read_pdf(file, pages="all", multiple_tables=True)

        for table in tables:
            if ("Percent children of total" in table.columns and len(table.columns) == 7):
                print(table)

                num_rows = len(table)
                table.insert(0, "Date", [date for _ in range(num_rows)], allow_duplicates=True)
                print(table)
