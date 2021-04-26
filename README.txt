Group 05 formed by:

[Hugo Enrile] @hugo-enrile
[Alejandro Gouloumis] @agouloumis
[Joel Ramirez] @TMPLR11


Files and directory:

All files have to be at the same working directory. In addition to the files there are two folders: outputs, where the .csv files created by the different scripts are, and analysis, which contains the data and notebook necessary to carry out the last part of the project.

To run:

Each individual part is runned separately. Part 1 generates all the assets csv' required. Part 2 create portfolio allocations, Part 3 creates trading methodologies.
Part 4 take all the csv created and generate the metrics of the portfolio.

The only requirement is to have the working directory with all the scripts and csv that are generated during the process at the same place.

Requirements:

The libraries required are in the requirements.txt and can be installed through: pip install -r requirements.txt

Files:

Part1: Webscrapping part
Generates: A CSV per asset

Part2: Creation of the different combinations of the portfolio
Generates: Portfolio_allocations.csv

Part3: Definition of the investment methodologies with and without rebalancing, from portfolio allocations
Generates: Trading_methodologies.csv

Part4: Calculation of the portfolio metrics
Generates: Portfolio_Metrics.csv

Report_DS.pdf: Report of the analysis part


