# %%
import os
import sys
import subprocess
import glob
import gzip
import urllib
import requests


# %%
script_descr = """
Download sequence entries from KEGG (genes, proteins, etc.) in fasta format

Accepted command line arguments:
    1. Comma-separated list of accession numbers
    2. Type of sequence to be downloaded (nucl or prot). This applies to all accession numbers provided.
    3. Output fasta file containing the downloaded sequences

"""


# %%
def download_KEGG_gene(accessions, seqtype, outfile):
    """Download gene or protein sequence(s) in fasta format using KEGG ID numbers."""
    datatypes = {"nucl": ["ntseq", ".fna"], "prot": ["aaseq", ".faa"]}
    kegg_link = "http://rest.kegg.jp/get/{}/{}".format(
        "+".join(accessions), datatypes[seqtype][0]
    )
    kegg_page = urllib.request.urlopen(kegg_link)
    kegg_lines = kegg_page.readlines()

    with open(outfile, "wb") as faa_file:
        for kegg_line in kegg_lines:
            faa_file.write(kegg_line)


# %%
if __name__ == "__main__":
    accessions = sys.argv[1].split(",")
    seqtype, outfile = sys.argv[2:4]
    download_KEGG_gene(accessions, seqtype, outfile)
