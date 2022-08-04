# %%
# Import necessary libraries
import os
import sys
import subprocess
import glob
import gzip
import argparse


# %%
# Description of the script's function
script_descr = """
Download and format all of the files associated with a genome from the NCBI's ftp site.

All associated files will be downloaded, including genomic DNA, proteins, RNAs, feature table.
These files will also be formatted into BLAST-able databases.
"""


# %%
def download_genome(ftp_address, outdir, organism=None):
    if organism == None:
        organism = os.path.split(outdir)[1]
    message = "\nStarting genome download for {}\nfrom {}\ninto {}\n".format(
        organism, ftp_address, outdir
    )
    print(message)

    start_dir = os.getcwd()
    try:
        os.mkdir(outdir)
    except:
        FileExistsError
    os.chdir(outdir)

    wget_cmd = [
        "wget",
        ftp_address,
        "--recursive",
        "--no-parent",
        "--no-directories",
        "--continue",
    ]
    subprocess.run(wget_cmd)

    split_ftp = ftp_address.split("/")
    old_name = split_ftp[-1]
    mmv_cmd = ["mmv", f"{old_name}*", f"{organism}#1"]
    subprocess.run(mmv_cmd)

    for gzfile in glob.glob("*.gz"):
        gzip_cmd = ["gzip", "-drv", gzfile]
        subprocess.run(gzip_cmd)

    blastdb = {
        "nucl": glob.glob(f"{organism}*.fna"),
        "prot": glob.glob(f"{organism}*.faa"),
    }
    for dbtype, dbfiles in blastdb.items():
        for dbfile in dbfiles:
            makeblastdb_cmd = ["makeblastdb", "-dbtype", dbtype, "-in", dbfile]
            subprocess.run(makeblastdb_cmd)

    print(
        "\n{} genome downloaded and formatted successfully.\nThe associated files are available in {}\n".format(
            organism, outdir
        )
    )
    with os.scandir() as filelisting:
        for entry in filelisting:
            print(entry.name)
    print()
    os.chdir(start_dir)
    return outdir


# %%
# Perform genome download if this script is called as the main script from the terminal
if __name__ == "__main__":
    dlgenome_parser = argparse.ArgumentParser(
        description=script_descr,
        fromfile_prefix_chars="@",
        add_help=False,
    )
    dlgenome_group1 = dlgenome_parser.add_argument_group("Information to provide")
    dlgenome_group1.add_argument(
        "-n", "--organism-name",
        help="(Optional) Organism name. This will be used to create the output folder and rename the files associated with the downloaded genome. Words in the name should be separated by underscores, not spaces. The default value is the name of the last folder in output directory.",
        metavar="<name>",
    )
    dlgenome_group1.add_argument(
        "-f", "--ftp",
        help="(Required) Ftp address of the folder containing this genome on the NCBI's server",
        metavar="<link>",
        required=True,
    )
    dlgenome_group1.add_argument(
        "-o", "--outdir",
        help="(Required) Path to the output folder (which will be created if not present). If organism name is not provided, the end folder in the directory will be used as the organism name.",
        metavar="<path>",
        required=True,
    )
    if len(sys.argv) == 1:
        dlgenome_parser.print_help()
    else:
        dlgenome_args = dlgenome_parser.parse_args()
        download_genome(dlgenome_args.ftp, dlgenome_args.outdir, dlgenome_args.organism)