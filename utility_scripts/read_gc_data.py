from genericpath import isfile
import sys
import glob
import os
import io
import csv
from unittest import result
import numpy as np
import pandas as pd
import argparse


script_descr = """
Read output text files from gas chromatography and finds the concentration of relevant compounds measured for each experimental sample.

Returns 3 files:
	"*gc.csv" and "*gc.xlsx" containing concentrations of measured compound for each experimental sample.
	"*compound_list.csv" containing the names of the compounds that were measured.
"""


# Define function to read GC results text files
def read_gc_data(gc_file):
    """Retrieves compound concentration results from a single GC output file in .txt format and record the concentrations of all compounds measured as a list..

    Uses the sample ID unique to each experiment to identify experimental samples.
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
        concs = (gc_results["Conc."] * 10).tolist()
        return sample_id, gc_compounds, concs
    else:
        return -999, -999, -999


if __name__ == "__main__":
    read_gc_parser = argparse.ArgumentParser(
        description=script_descr,
        fromfile_prefix_chars="@",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    read_gc_parser_group1 = read_gc_parser.add_argument_group("Information to provide")
    read_gc_parser_group1.add_argument(
        "-f",
        "--file",
        help="GC raw data file. Can be used multiple times.",
        action="append",
        metavar="<file>",
    )
    read_gc_parser_group1.add_argument(
        "-i",
        "--indir",
        help="Directory containing GC raw data files in .txt format. These files can be contained in this directory but can also be contained in subdirectories within this one. Can be used multiple times. \n Note: using a directory with subdirectories requires the '--recursive' option.",
        metavar="<indir>",
        action="append",
    )
    read_gc_parser_group1.add_argument(
        "-o",
        "--outdir",
        help="Directory where the result records will be placed.",
        metavar="<outdir>",
        required=True,
    )
    read_gc_parser_group1.add_argument(
        "-e",
        "--experiment",
        help="Name of the experiment, which will be used as the base name for all result files.",
        metavar="<experiment>",
        required=True,
    )

    read_gc_parser_group2 = read_gc_parser.add_argument_group(
        "Options to modify the script's behavior"
    )
    read_gc_parser_group2.add_argument(
        "-r",
        "--recursive",
        help="Search the provided director(y/ies) and its subdirector(y/ies) recursively for GC raw data files.",
        action="store_true",
    )
    read_gc_parser_group2.add_argument(
        "-v",
        "--verbose",
        help="Displays the script's progress and results in different verbosity levels:\n 1. Display the resulting concentration values for each sample.\n 2. Display the file being read and the resulting concentration values.",
        action="count",
        default=0,
    )

    if len(sys.argv) == 1:
        read_gc_parser.print_help()
    else:
        read_gc_args = read_gc_parser.parse_args()
        read_gc_result = []
        for indir in read_gc_args.indir:
            if read_gc_args.recursive == True:
                for walk_entry in os.walk(indir):
                    for gc_filename in walk_entry[2]:
                        if gc_filename.endswith(".txt"):
                            gc_filepath = os.path.join(walk_entry[0], gc_filename)
                            sample_id, compound_list, concs = read_gc_data(gc_filepath)
                            if sample_id >= 0:
                                read_gc_result.append(
                                    [sample_id, *concs, os.path.basename(gc_filepath)]
                                )
            else:
                for scan_entry in os.scandir(indir):
                    if scan_entry.isfile() and scan_entry.endswith(".txt"):
                        gc_filepath = os.path.join(scan_entry, gc_filename)
                        sample_id, compound_list, concs = read_gc_data(gc_filepath)
                        if sample_id >= 0:
                            read_gc_result.append(
                                [sample_id, *concs, os.path.basename(gc_filepath)]
                            )

        read_gc_result.sort(key=(lambda x: x[0]))

        if read_gc_args.verbose == 1:
            print(
                "\n",
                ("{:^13}" * (1 + len(compound_list))).format(
                    "Sample ID", *compound_list
                ),
            )
            for sample in read_gc_result:
                print(
                    "{:^13}".format(sample[0]),
                    ("{:^13.3}" * (len(compound_list))).format(*sample[1:]),
                    sep="",
                )

        elif read_gc_args.verbose == 2:
            print(
                "\n",
                ("{:^13}" * (2 + len(compound_list))).format(
                    "Sample ID", *compound_list, "File name"
                ),
            )
            for sample in read_gc_result:
                print(
                    "{:^13}".format(sample[0]),
                    ("{:^13.3}" * (len(compound_list))).format(*sample[1:-1]),
                    "{}".format(sample[-1]),
                    sep="",
                )

        # Save to file
        pd.Series(compound_list).to_csv(
            os.path.join(
                read_gc_args.outdir, read_gc_args.experiment + "_compounds.csv"
            ),
            index=False,
        )
        pd.DataFrame(read_gc_result, columns=["Sample ID", *compound_list, "File name"]).to_csv(
            os.path.join(read_gc_args.outdir, read_gc_args.experiment + "_data.csv"),
            index=False,
        )
        pd.DataFrame(read_gc_result, columns=["Sample ID", *compound_list, "File name"]).to_excel(
            os.path.join(read_gc_args.outdir, read_gc_args.experiment + "_data.xlsx"),
            index=False,
        )
