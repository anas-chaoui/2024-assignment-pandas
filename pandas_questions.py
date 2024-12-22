"""Plotting referendum results in pandas.

In short, we want to make beautiful map to report results of a referendum. In
some way, we would like to depict results with something similar to the maps
that you can find here:
https://github.com/x-datascience-datacamp/datacamp-assignment-pandas/blob/main/example_map.png

To do that, you will load the data as pandas.DataFrame, merge the info and
aggregate them by regions and finally plot them on a map using `geopandas`.
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def load_data():
    """Load data from the CSV files referendum/regions/departments."""
    referendum = pd.read_csv("data/referendum.csv", sep=';')
    regions = pd.read_csv("data/regions.csv")
    departments = pd.read_csv("data/departments.csv")

    return referendum, regions, departments


def merge_regions_and_departments(regions, departments):
    """Merge regions and departments in one DataFrame.

    The columns in the final DataFrame should be:
    ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    """
    regions = regions.rename(columns={'code': 'code_reg', 'name': 'name_reg'})
    departments = departments.rename(columns={
        'code': 'code_dep', 'region_code': 'code_reg', 'name': 'name_dep'
    })

    output = pd.merge(departments, regions, on='code_reg')[
        ['code_reg', 'name_reg', 'code_dep', 'name_dep']
    ]

    return output


def merge_referendum_and_areas(referendum, regions_and_departments):
    """Merge referendum and regions_and_departments in one DataFrame.

    You can drop the lines relative to DOM-TOM-COM departments, and the
    french living abroad.
    """
    referendum['Department code'] = referendum['Department code'].str.zfill(2)
    merged = pd.merge(
        referendum, regions_and_departments,
        left_on='Department code', right_on='code_dep'
    )

    return merged


def compute_referendum_result_by_regions(referendum_and_areas):
    """Return a table with the absolute count for each region.

    The return DataFrame should be indexed by `code_reg` and have columns:
    ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']
    """
    merged = referendum_and_areas.groupby("name_reg").sum(numeric_only=True).reset_index()
    merged = merged.loc[:, ['name_reg', 'Registered', 'Abstentions', 'Null', 'Choice A', 'Choice B']]

    return merged


def plot_referendum_map(referendum_result_by_regions):
    """Plot a map with the results from the referendum.

    * Load the geographic data with geopandas from `regions.geojson`.
    * Merge these info into `referendum_result_by_regions`.
    * Use the method `GeoDataFrame.plot` to display the result map. The results
      should display the rate of 'Choice A' over all expressed ballots.
    * Return a gpd.GeoDataFrame with a column 'ratio' containing the results.
    """
    regions_JSON = gpd.read_file("data/regions.geojson")
    regions_JSON = regions_JSON.rename(columns={'nom': 'name_reg'})

    regions_JSON_merged = pd.merge(referendum_result_by_regions, regions_JSON, on="name_reg")
    regions_JSON_merged = gpd.GeoDataFrame(regions_JSON_merged, geometry='geometry')

    regions_JSON_merged["ratio"] = regions_JSON_merged["Choice A"] / (
        regions_JSON_merged["Choice A"] + regions_JSON_merged["Choice B"]
    )

    regions_JSON_merged.plot(
        column="ratio",
        legend=True,
        legend_kwds={"label": "Ratio of Choice A votes", "orientation": "horizontal"},
    )

    return regions_JSON_merged


if __name__ == "__main__":
    referendum, df_reg, df_dep = load_data()
    regions_and_departments = merge_regions_and_departments(df_reg, df_dep)
    referendum_and_areas = merge_referendum_and_areas(referendum, regions_and_departments)
    referendum_results = compute_referendum_result_by_regions(referendum_and_areas)
    print(referendum_results)

    plot_referendum_map(referendum_results)
    plt.show()

