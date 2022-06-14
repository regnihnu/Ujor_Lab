# %%
import argparse
import os
import sys
import subprocess
import glob
import gzip
import urllib
import requests


# %%
script_descr = """
Download entries from KEGG, such as gene or protein sequences in fasta format.

If multiple accession numbers are provided, they will be combined into one output fasta file. The output file will be *.fna for genes and *.faa for proteins.

"""


# %%
def download_KEGG_gene(accessions, seqtypes, outfile):
    """Download gene or protein sequence(s) in fasta format using KEGG ID numbers."""
    datatypes = {"nucl": ["ntseq", ".fna"], "prot": ["aaseq", ".faa"]}
    
    for seqtype in seqtypes:
        kegg_link = "http://rest.kegg.jp/get/{}/{}".format(
            "+".join(accessions), datatypes[seqtype][0]
        )
        kegg_page = urllib.request.urlopen(kegg_link)
        kegg_lines = kegg_page.readlines()

        with open(outfile+datatypes[seqtype][1], "wb") as fasta_file:
            for kegg_line in kegg_lines:
                fasta_file.write(kegg_line)


# %%
if __name__ == "__main__":
    dlkegg_parser = argparse.ArgumentParser(
        description=script_descr,
        fromfile_prefix_chars="@",
        add_help=False,
    )
    dlkegg_group1 = dlkegg_parser.add_argument_group("Information to be provided")
    dlkegg_group1.add_argument(
        "-a", "--accession",
        help="(Required) Comma-separated list of accession numbers.",
        metavar="<accession>",
        required=True,
    )
    dlkegg_group1.add_argument(
        "-t", "--seq-type",
        help="(Required) Type of sequence to be downloaded. Can be either 'nucl' or 'prot', or both in a comma-separated list. This applies to all accession numbers provided.",
        metavar="<seqtype>",
        required=True,
    )
    dlkegg_group1.add_argument(
        "-o", "--outfile",
        help="(Required) Path to output fasta file that will be created to contain the downloaded sequence(s). Only provide the base name for the file, without the extensions such as .fna or .faa. The appropriate extension will be automatically appended based on the indicated sequence type.",
        metavar="<path/basename>",
        required=True,
    )
    if len(sys.argv) == 1:
        dlkegg_parser.print_help()
    else:
        dlkegg_args = dlkegg_parser.parse_args()
        accessions = dlkegg_args.accession.split(",")
        seqtypes = dlkegg_args.seq_type.split(",")
        download_KEGG_gene(accessions, seqtypes, dlkegg_args.outfile)