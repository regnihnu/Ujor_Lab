# %%
# Import necessary libraries
import glob
from itertools import count
import os
import io
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats


# %%
# Load cleaned and filled dataframes
ferment_data = pd.read_csv(r"csv_files\ferment_data.csv", index_col="Sample ID")
compound_list = pd.read_csv(r"csv_files\compound_list.csv", index_col="Compound").index


# %%
# Separate samples measured using different standards
ferment_data_H = ferment_data.loc[ferment_data["1-propanol standard"] == "Hieu", :]
ferment_data_E = ferment_data.loc[ferment_data["1-propanol standard"] == "Eric", :]

ferm_merge_keys = ferment_data_E.loc[
    :, ["Culture type", "Planned time point", "Replicate"]
]
ferment_compare = pd.merge(
    ferment_data.reset_index(), ferm_merge_keys, how="right"
).set_index("Sample ID")

ferment_compare.loc[:, "Compare sample"] = (
    ferment_compare["Culture type"]
    + " at "
    + ferment_compare["Actual time point (h)"].astype("str")
    + " h"
)

compare_samples = pd.Index(ferment_compare["Compare sample"].unique())
std_source = pd.Index(ferment_compare["1-propanol standard"].unique())


# List culture types
culture_types = pd.Index(ferment_data["Culture type"].unique())

culture_styles = pd.DataFrame(index=culture_types)
culture_styles.loc[:,'Info'] = [
    "L. plantarum pre-culture",
    "C. tyrobutyricum pre-cultyre",
    "L. plantarum alone",
    "C. tyrobutyricum alone",
    "C. tyrobutyricum added to L. plantarum at 0 h",
    "C. tyrobutyricum added to L. plantarum at 3 h",
]
culture_styles.loc[:,'Marker'] = ['v', 'x', '^', 'o', 's', 'D']
# culture_styles.loc[:,'Color'] = []
culture_styles.loc[:,'Fill'] = ['none', 'none', 'none', 'none', 'full', 'full']


# %%
# Plot fermentation product yield (for writings)
ferment_group1 = ferment_data_H.groupby(
    ["Culture type", "Actual time point (h)"], sort=False
)

series_x = ferment_data_H.loc[:, "Actual time point (h)"].unique()

fig1w, ax1s = plt.subplots(
    nrows=int(len(compound_list) / 2),
    ncols=2,
    figsize=(14.5, 20),
    facecolor="white",
    tight_layout=True,
)
fig1w.suptitle("Fermentation Products")

for compound in compound_list:
    ax1 = ax1s.ravel()[compound_list.get_loc(compound)]
    ax1.set_title(compound)
    ax1.set_xlabel("Time (h)")
    ax1.xaxis.set_ticks(np.arange(0, 80, 12))
    ax1.set_ylabel("Concentration (g/L)")
    for culture in culture_types:
        if "pre" not in culture:
            series_y = ferment_group1.mean().loc[culture, compound]
            series_yerr = ferment_group1.std().loc[culture, compound]
            ax1.errorbar(
                series_x,
                series_y,
                label = culture,
                marker = culture_styles.loc[culture, 'Marker'],
                # markerfacecolor = culture_styles.loc[culture, 'Color'],
                fillstyle = culture_styles.loc[culture, 'Fill'],
                ms = 8,
                # alpha = 0.8,
                linestyle = '--',
                linewidth = 1,
                yerr = series_yerr,
                elinewidth = 0.5,
                capsize = 4,
                capthick = 0.5,
            )
            ax1.set_ylim(bottom=0, auto=True)
        else:
            pass
    ax1.legend()


# %%
# Plot culture growth (for writings)
""" ferment_group2 = ferment_data_H.groupby(
    ["Culture type", "Actual time point (h)"], sort=False
)
series_x = ferment_data_H.loc[:, "Actual time point (h)"].unique()

fig2w, ax2 = plt.subplots(figsize=(7, 6.5), facecolor="white", tight_layout=True)
series_x = ferment_data.loc[:, "Actual time point (h)"].unique()[1:]
ax2.set_title("Culture Growth")
ax2.set_xlabel("Time (h)")
ax2.set_ylabel("Optical Density (600nm)")
ax2.xaxis.set_ticks(np.arange(0, 80, 12))

for culture in culture_types:
    if "pre" not in culture:
        series_y = ferment_group2.mean().loc[culture, "OD600 1:1"][1:]
        series_yerr = ferment_group2.std().loc[culture, "OD600 1:1"][1:]
        ax2.errorbar(
            series_x,
            series_y,
            label=culture,
            fmt="o--",
            linewidth=1,
            ms=7,
            yerr=series_yerr,
            elinewidth=0.5,
            capsize=4,
            capthick=0.5,
        )
        ax2.set_ylim(bottom=0, auto=True)
    else:
        pass
ax2.legend()

 """
# %%
# Plot comparision of samples with different standards, by sample (for writings)
ferment_group3a = ferment_compare.groupby(
    ["Compare sample", "1-propanol standard"], sort=False
)

fig3aw, ax3as = plt.subplots(
    nrows=int(len(compare_samples) / 2),
    ncols=2,
    figsize=(12, 12),
    facecolor="white",
    tight_layout=True,
)
fig3aw.suptitle("Comparison between standards")

error_format = {
    "elinewidth": 0.65,
    "capsize": 4,
    "capthick": 0.8,
}

for sample in compare_samples:
    ax3a = ax3as.ravel()[compare_samples.get_loc(sample)]
    ax3a.set_title("Sample: " + sample, pad=12)
    ax3a.set_xlabel("Concentration (g/L)")
    ax3a.xaxis.set_ticks_position("top")
    ax3a.xaxis.set_label_position("top")
    ax3a.tick_params(axis="y", which="major", length=0)
    ax3a.spines["left"].set(linewidth=0.001)
    ax3a.spines["right"].set(visible=False)
    ax3a.spines["bottom"].set(visible=False)

    series_x = compound_list
    ax3a.set_yticklabels(series_x)
    xtick_pos = np.arange(len(series_x))
    bar_offset = np.linspace(-1.2, 1.2, len(std_source))
    ax3a.set_yticks(xtick_pos, series_x)
    barwidth = 0.26

    for std in std_source:
        series_y = ferment_group3a.mean().loc[(sample, std), :][compound_list]
        series_yerr = ferment_group3a.std().loc[(sample, std), :][compound_list]
        ax3a.barh(
            xtick_pos + bar_offset[std_source.get_loc(std)] * barwidth / 2,
            series_y,
            barwidth,
            label=std,
            xerr=series_yerr,
            error_kw=error_format,
        )
        ax3a.set_xlim(left=0, auto=True)
        ax3a.xaxis
        ax3a.legend(title="1-propanol\nstandard")

    for compound in compound_list:
        samples_H = ferment_group3a.get_group((sample, "Hieu"))[compound]
        samples_E = ferment_group3a.get_group((sample, "Eric"))[compound]
        p_value = stats.ttest_rel(samples_H, samples_E)[1]
        if pd.notnull(p_value):
            if p_value < 0.05:
                significance = "*"
            else:
                significance = "ns"
            ann_x = (
                ferment_group3a.mean().loc[(sample, std), :][compound]
                + ferment_group3a.std().loc[(sample, std), :][compound]
            ) * 1.2
            ann_y = xtick_pos[compound_list.get_loc(compound)]
            ax3a.annotate(significance, (ann_x, ann_y))


# %%
# Plot comparision of samples with different standards, by compound (for writings)
ferment_group3b = ferment_compare.groupby(
    ["1-propanol standard", "Compare sample"], sort=False
)

fig3bw, ax3bs = plt.subplots(
    nrows=int(len(compound_list) / 2),
    ncols=2,
    figsize=(12, 14),
    facecolor="white",
    tight_layout=True,
)
fig3bw.suptitle("Comparison between standards")

error_format = {
    "elinewidth": 0.65,
    "capsize": 4,
    "capthick": 0.8,
}

for compound in compound_list:
    ax3b = ax3bs.ravel()[compound_list.get_loc(compound)]
    ax3b.set_title(compound + " (g/L)", pad=12)
    ax3b.xaxis.set_ticks_position("top")
    ax3b.tick_params(axis="y", which="major", length=0)
    ax3b.spines["left"].set(linewidth=0.001)
    ax3b.spines["right"].set(visible=False)
    ax3b.spines["bottom"].set(visible=False)

    series_x = compare_samples
    ax3b.set_yticklabels(series_x)
    xtick_pos = np.arange(len(series_x))
    bar_offset = np.linspace(-1.2, 1.2, len(std_source))
    ax3b.set_yticks(xtick_pos, series_x)

    for std in std_source:
        series_y = ferment_group3b.mean().loc[std, compound]
        series_yerr = ferment_group3b.std().loc[std, compound]
        barwidth = 0.22
        ax3b.barh(
            xtick_pos + bar_offset[std_source.get_loc(std)] * barwidth / 2,
            series_y,
            barwidth,
            label=std,
            xerr=series_yerr,
            error_kw=error_format,
        )
    ax3b.set_xlim(left=0, auto=True)
    ax3b.legend(title="1-propanol\nstandard")

    for sample in compare_samples:
        samples_H = ferment_group3b.get_group(("Hieu", sample))[compound]
        samples_E = ferment_group3b.get_group(("Eric", sample))[compound]
        p_value = stats.ttest_rel(samples_H, samples_E)[1]
        if pd.notnull(p_value):
            if p_value < 0.05:
                significance = "*"
            else:
                significance = "ns"
            ann_x = (
                ferment_group3b.mean().loc[(std, sample), :][compound]
                + ferment_group3b.std().loc[(std, sample), :][compound]
            ) * 1.1
            ann_y = xtick_pos[compare_samples.get_loc(sample)]
            ax3b.annotate(significance, (ann_x, ann_y))


# %%


# %%


# %%
# Plot comparision of samples with different standards, by sample, with zoom (for writings)
ferment_group4a = ferment_compare.groupby(
    ["Compare sample", "1-propanol standard"], sort=False
)

fig4aw, ax4as = plt.subplots(
    nrows=int(len(compare_samples) / 1),
    ncols=2,
    figsize=(13, 24),
    facecolor="white",
    tight_layout=True,
)
fig4aw.suptitle("Comparison between standards")

error_format = {
    "elinewidth": 0.65,
    "capsize": 4,
    "capthick": 0.8,
}

for sample in compare_samples:
    ax4a_index = compare_samples.get_loc(sample) * 2
    # ax4ao, ax4ai = ax4as.ravel()[ax4a_index:ax4a_index+2]
    for ax4a in ax4as.ravel()[ax4a_index : ax4a_index + 2]:
        ax4a.set_title("Sample: " + sample, pad=12)
        ax4a.set_xlabel("Concentration (g/L)")
        ax4a.xaxis.set_ticks_position("top")
        ax4a.tick_params(axis="y", which="major", length=0)
        ax4a.xaxis.set_label_position("top")
        ax4a.spines["left"].set(visible=False, linewidth=0.01)
        ax4a.spines["right"].set(visible=False)
        ax4a.spines["bottom"].set(visible=False)

        series_x = compound_list
        ax4a.set_yticklabels(series_x)
        xtick_pos = np.arange(len(series_x))
        bar_offset = np.linspace(-1.2, 1.2, len(std_source))
        ax4a.set_yticks(xtick_pos, series_x)
        barwidth = 0.26

        for std in std_source:
            series_y = ferment_group4a.mean().loc[(sample, std), :][compound_list]
            series_yerr = ferment_group4a.std().loc[(sample, std), :][compound_list]
            ax4a.barh(
                xtick_pos + bar_offset[std_source.get_loc(std)] * barwidth / 2,
                series_y,
                barwidth,
                label=std,
                xerr=series_yerr,
                error_kw=error_format,
            )
            ax4a.set_xlim(left=0, auto=True)
            ax4a.xaxis
            ax4a.legend(title="1-propanol\nstandard")

        for compound in compound_list:
            samples_H = ferment_group4a.get_group((sample, "Hieu"))[compound]
            samples_E = ferment_group4a.get_group((sample, "Eric"))[compound]
            p_value = stats.ttest_rel(samples_H, samples_E)[1]
            if pd.notnull(p_value):
                if p_value < 0.05:
                    significance = "*"
                else:
                    significance = "ns"
                ann_x = (
                    ferment_group4a.mean().loc[(sample, std), :][compound]
                    + ferment_group4a.std().loc[(sample, std), :][compound]
                ) * 1.2
                ann_y = xtick_pos[compound_list.get_loc(compound)]
                ax4a.annotate(significance, (ann_x, ann_y))


# %%


# %%
# Save figures to files
""" fig1w.savefig(r"Graphs\220322_fermentation_products_vw5.pdf")
fig1w.savefig(r"Graphs\220322_fermentation_products_vw5.svg")

fig2w.savefig(r"Graphs\220322_culture_growth_vw5.pdf")
fig2w.savefig(r"Graphs\220322_culture_growth_vw5.svg")
 """


fig3aw.savefig(r"Graphs\220322_compare_standards_vw3a.pdf")
fig3aw.savefig(r"Graphs\220322_compare_standards_vw3a.svg")

fig3bw.savefig(r"Graphs\220322_compare_standards_vw3b.pdf")
fig3bw.savefig(r"Graphs\220322_compare_standards_vw3b.svg")


# %%
