import pandas
from os import listdir
from os.path import isfile, join

path_to_input_directory = "/Users/andrew/projects/covid-19-pediatric/scraped_data/"
path_to_output_directory = "/Users/andrew/projects/covid-19-pediatric/combined_data/"


def combine_csvs(input_csvs, output_filename):
    dataframes = []

    for input_csv in input_csvs:
        path_to_csv = join(path_to_input_directory, input_csv)
        df = pandas.read_csv(path_to_csv)
        dataframes.append(df)

    combined_df = pandas.concat(dataframes)

    output_file_path = join(path_to_output_directory, output_filename)
    with open(output_file_path, 'w', newline='') as csvfile:
        combined_df.to_csv(path_or_buf=csvfile, sep="|", index=False)


if __name__ == '__main__':
    cases_filenames = [f for f in listdir(path_to_input_directory) if
                       isfile(join(path_to_input_directory, f)) and "cases" in f]
    hospitalizations_filenames = [f for f in listdir(path_to_input_directory) if
                                  isfile(join(path_to_input_directory, f)) and "hospitalizations" in f]

    print(f"cases [{cases_filenames}]")
    print(len(cases_filenames))
    print(f"hospitalizations [{hospitalizations_filenames}]")
    print(len(hospitalizations_filenames))

    combine_csvs(cases_filenames, "cases-by-state.csv")
    combine_csvs(hospitalizations_filenames, "hospitalizations-by-state.csv")
