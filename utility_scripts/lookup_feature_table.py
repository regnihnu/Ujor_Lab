# %%
# Import dependencies
from msilib import sequence
from multiprocessing.spawn import old_main_modules
from optparse import Values
import subprocess
from numpy import append
import pandas as pd
from Bio import SeqIO
pd.options.display.max_columns = 999


# %%
# Define utility functions


def select_fields(feature_table: pd.DataFrame, fields: int = 1, Benchling: int = 1):
    """Display the genome feature table with selected information fields.

    fields = 1, 2, or 3 (optional).
        1 : (default) use recommended fields (:start:end, strand, name, symbol, locus_tag)
        2 : use the same fields from the genome feature table
        3 : fields of your choice (type exactly as they are listed)

    Benchling = 0 or 1 (optional).
        1 : (default) replace the 'start' and 'end' fields with a ':start:end' field for easier locus search and selection in Benchling.
        0 : No preference
    """
    if fields == 1:
        selected_fields = [":start:end", "strand", "name", "symbol", "locus_tag"]
    elif fields == 2:
        selected_fields = feature_table.columns.tolist()
    elif fields == 3:
        selected_fields = []
        field_count = str(input(print("Number of fields to be included: ")))
        number = 0
        while number < field_count:
            selected_fields.append(input(print(f"Field {number+1}: ")))
            number += 1
    if Benchling == 1:
        if ":start:end" in selected_fields:
            pass
        else:
            try:
                selected_fields.insert(0, ":start:end")
                selected_fields.remove("start")
                selected_fields.remove("end")
            except ValueError:
                pass
    feature_table_selected = feature_table
    if ":start:end" in selected_fields:
        feature_table_selected[":start:end"] = (
            ":"
            + feature_table["start"].astype(str)
            + ":"
            + feature_table["end"].astype(str)
        )
    else:
        pass
    return feature_table_selected[selected_fields]


def lookup_loci(
    feature_table: pd.DataFrame, column: str, col_values: list or str or int
):
    # to be worked on
    """Choose a column in the genome feature table and search for the ORF or locus that has specific values for that column (e.g., contains a given base pair position, or has a specific locus tag).

    column = base or loctag (locus tag)
    """
    if column == "base":

        base = int(input(print("Base pair position to look up: ")))
        located_loci = feature_table[
            (feature_table["start"] < base) & (feature_table["end"] > base)
        ]
    elif column == "locus_tag":
        locus_tags = []
        loci_count = int(input(print("Number of locus tags to look up: ")))
        loci_counter = 0
        while loci_counter < loci_count:
            locus_tags.append(input(print(f"Locus {loci_counter+1}: ")))
        located_loci = feature_table[feature_table["locus_tag"].isin(locus_tags)]
    else:
        print("Searching using this column is not supported yet.")
    return located_loci.reset_index(drop=True)


# %%
# Read in feature table
feature_table = pd.read_table(
    r"H:\Ujor_Lab\Proj_Dairy_succinate\Sequences\Genomes\Ctyro_KCTC_5387_feat-table.txt"
)
feature_table[":start:end"] = (
    ":" + feature_table["start"].astype(str) + ":" + feature_table["end"].astype(str)
)
feature_table


# %%
# Look up with old locus tags
old_loci = ["CTK_C00760"]
new_loci = feature_table.loc[
    feature_table["attributes"].str.lstrip("old_locus_tag=").isin(old_loci), 'locus_tag'
]
table_lookup = feature_table.loc[
    feature_table["locus_tag"].isin(new_loci), :
]
table_lookup


# %%
# Obtain sequence from downloaded genbank
prot_gbs = [
    r"H:\Ujor_Lab\Proj_Plant_butanol\Sequences\DisA\Cbeij_DisA_protein.gp",
    r"H:\Ujor_Lab\Proj_Plant_butanol\Sequences\Pde\Cbeij_Pde_protein.gp"
]
for prot_gb in prot_gbs:
    for record in SeqIO.parse(prot_gb, format='gb'):
        print(record.id)
        print(record.description)
        print(record.seq, end="\n"*2)
        

# %%

