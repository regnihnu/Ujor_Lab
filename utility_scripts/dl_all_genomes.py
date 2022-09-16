import os
import sys
import subprocess

os.chdir("genomes")
genome_list = []
with open("genomes_refseq.txt") as refseqs:
    for line in refseqs:
        genome_list.append(line.strip().split(","))

for organism, genome_adr in genome_list[1:]:
    print(">>> Downloading {} genome \n    from {}".format(repr(organism), repr(genome_adr)))
    subprocess.run(["python3", "../utility_scripts/download_genome.py", "-n", organism, "-f", genome_adr, "-o", organism])