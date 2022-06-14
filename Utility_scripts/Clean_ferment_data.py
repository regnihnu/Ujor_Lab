# %%
# Import necessary libraries
import sys
import glob
import os
import io
import csv
import numpy as np
import pandas as pd


# %%
# Description of how to use this ferment data cleaning tool
script_descr = """
Fills in the actual sampling time points and compound concentration results from gas chromatography for all samples recorded in an Excel file.

Accepts exactly one argument, which is the path to an Excel file containing at least three spreadsheets:
    1. "Culture types" - This sheet explains the experimental setup for the sample types.
    2. "Sampling times" - This sheet contains the actual date & time at which samples were taken for measurements.
    3. "Data" - This sheet contains recorded experimental measurements (e.g., optical density, pH). The missing data will be populated into this sheet.

The folder containing the raw data Excel file should have a folder named "gc_output" containing output files from the GC system. The GC output files may also be contained in one level of subfolders within the "gc_output" folder.

Returns 2 files containing cleaned data and 1 file containing the list of compounds measured by gas chromatography into the folder "cleaned_data":
    1. "*cleaned.csv"
    2. "*cleaned.xlsx"
    3. "*compound_list.csv"
"""


# %%
# Read fermentation spreadsheets into dataframes
def read_ferment_data(fermentfile):
    """Read in Excel spreadsheet, clean data, and return data as pandas DataFrames.

    The 3 resulting dataframes are:
        1. ferment_data, containing the experimental measurements
        2. ferment_times, containing the time at which samples were actually taken for measurements
        3. ferment_cultures, containing the experimental setup of the sample types
    """

    ferment_data = pd.read_excel(fermentfile, sheet_name="Data", index_col="Sample ID")

    ferment_times = pd.read_excel(
        fermentfile, sheet_name="Sampling times", index_col="Planned time point"
    )

    ferment_cultures = pd.read_excel(
        fermentfile, sheet_name="Culture types", index_col="Culture type"
    )

    # Drop completely empty columns
    ferment_data.drop(
        columns=ferment_data.columns[ferment_data.isnull().all(axis=0)], inplace=True
    )

    # Fill in culture information
    # for col in ferment_cultures.columns.tolist():
    #     ferment_data.loc[:,col] = ferment_data.loc[:,'Culture type'].map(ferment_cultures[col])

    # Fill in sampling time for all samples in ferment_data, using data from ferment_times
    for col in ferment_times.columns.tolist():
        ferment_data.loc[:, col] = ferment_data.loc[:, "Planned time point"].map(
            ferment_times[col]
        )

    # Calculate actual sampling time points
    ferment_data.loc[:, "Actual time point (h)"] = (
        ferment_data["Actual sampling time"]
        - ferment_times.loc[0, "Actual sampling time"]
    ) / np.timedelta64(1, "h")

    return (ferment_data, ferment_times, ferment_cultures)


# %%
# Read GC results into fermentation dataframe
def read_gc_result(ferment_dataframe, gc_file):
    """Retrieves compound concentration results from a GC output file and record that into the fermetation dataframe.
    
    Uses the unique sample ID to correctly match concentration results to each sample.
    """
    with open(gc_file, "r") as gc_content:
        gc_output = ""
        line_number = 0
        sample_id = -999
        for line in gc_content:
            line_number += 1
            if "[Group Results(Ch1)]" in line:
                break
            if "Sample ID" in line:
                try:
                    sample_id = np.intc(line.split(",")[1])
                except ValueError:
                    pass
            if "[Compound Results(Ch1)]" in line:
                for line2 in gc_content:
                    if "[Group Results(Ch1)]" in line2:
                        break
                    gc_output += line2
                break
    if sample_id >= 0:
        gc_results = pd.read_csv(
            io.StringIO(gc_output),
            header=1,
            usecols=["Name", "Conc."],
            index_col="Name",
        )
        gc_compounds = gc_results.index.rename("Compound")
        ferment_dataframe.loc[sample_id, gc_compounds] = (
            gc_results["Conc."] * 10
        ).tolist()
        return gc_compounds
    else:
        pass


# %%
if __name__ == "__main__":
    if len(sys.argv) != 2:
        # Display script description if incorrectly called
        print(script_descr)
    else:
        # Extract file name and working directory from the provided raw data filepath
        ferment_inpath = sys.argv[1]
        workdir, ferment_infile = os.path.split(ferment_inpath)
        os.chdir(workdir)

        # Read in raw data from Excel file
        ferment_data, ferment_times, ferment_cultures = read_ferment_data(ferment_infile)

        # Read GC output files and record data
        with os.scandir("gc_output") as gc_scan:
            for entry1 in gc_scan:
                if entry1.is_dir():
                    with os.scandir(entry1) as gc_sub_scan:
                        for entry2 in gc_sub_scan:
                            if entry2.is_file and entry2.name.endswith(".txt"):
                                compound_list = read_gc_result(ferment_data, entry2)
                elif entry1.is_file and entry1.name.endswith(".txt"):
                    compound_list = read_gc_result(ferment_data, entry1)

        # Save cleaned and filled dateframes to files
        outdir = "cleaned_data"
        try:
            os.mkdir(outdir)
        except:
            FileExistsError
        
        ferment_outfile = ferment_infile.replace("raw.xlsx", "")

        ferment_data.to_csv(os.path.join(outdir, ferment_outfile + "cleaned.csv"))
        ferment_data.to_excel(os.path.join(outdir, ferment_outfile + "cleaned.xlsx"))
        compound_list.to_series().to_csv(
            os.path.join(outdir, ferment_outfile + "compound_list.csv"),
            index=False,
        )
