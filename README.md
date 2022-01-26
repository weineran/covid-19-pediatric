# covid-19-pediatric

## Source Data
Reports can be downloaded from The Internet. URLs follow a couple different date formats. For example:
* Report for 12/2/21: https://downloads.aap.org/AAP/PDF/AAP%20and%20CHA%20-%20Children%20and%20COVID-19%20State%20Data%20Report%2012.2.21%20FINAL.pdf
* Report for 12/9/21 (notice no year in the URL): https://downloads.aap.org/AAP/PDF/AAP%20and%20CHA%20-%20Children%20and%20COVID-19%20State%20Data%20Report%2012.9%20FINAL.pdf

Try for example:
```
wget https://downloads.aap.org/AAP/PDF/AAP%20and%20CHA%20-%20Children%20and%20COVID-19%20State%20Data%20Report%2012.9%20FINAL.pdf
```

NOTE: The weekly reports containing the source data is also saved in this repo for convenience (and redundancy).
But some users may prefer to obtain the reports directly from the AAP.

## How to use
### Scrape data from reports
`./venv/bin/python main.py <path-to-reports-to-process> <output-dir> <path-to-move-reports-after-processing>`

Example:
`./venv/bin/python main.py pediatric-state-reports-to-process/ scraped_data/ pediatric-state-reports/`

### Combine weekly CSVs into aggregate CSVs
`./venv/bin/python combine-csvs.py <path-to-input-csvs> <output-dir>`

Example:
`./venv/bin/pytho combine-csvs.py scraped_data/ combined_data/`

