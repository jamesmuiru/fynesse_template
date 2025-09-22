# access.py
import geopandas as gpd
import pandas as pd

class HealthDataLoader:
    def __init__(self):
        """
        Load GeoPackage and CSV datasets directly from GitHub raw URLs.
        """
        # GitHub raw URL for GeoPackage
        self.gpkg_url = "https://raw.githubusercontent.com/jamesmuiru/mlfccourse/main/csvs/county_with_raster_means.gpkg"

        # GitHub raw URLs for CSV datasets
        base_csv_url = "https://raw.githubusercontent.com/jamesmuiru/mlfccourse/main/csvs"
        self.health_facilities_data = f"{base_csv_url}/facilities_data.csv"
        self.projected_population_2025 = f"{base_csv_url}/projected_population_2025.csv"
        self.teen_pregnancy_bycounty = f"{base_csv_url}/teen_pregnacy_dataByCounty.csv"
        self.level2_nurse_facilities = f"{base_csv_url}/level2_lessthan3nursesfacilities_nurses.csv"
        self.sexual_violence = f"{base_csv_url}/sexual_violence.csv"

        # Placeholders for loaded data
        self.county_boundaries_df = None
        self.facilities_df = None
        self.projected_population_df = None
        self.teen_pregnancy_df = None
        self.less_than3_nursefacilities_df = None
        self.sexual_violence_df = None

    def load_data(self):
        """Load all datasets into memory."""
        # Load GeoPackage directly
        self.county_boundaries_df = gpd.read_file(self.gpkg_url)

        # Load CSV datasets
        self.facilities_df = pd.read_csv(self.health_facilities_data)
        self.projected_population_df = pd.read_csv(self.projected_population_2025)
        self.teen_pregnancy_df = pd.read_csv(self.teen_pregnancy_bycounty)
        self.less_than3_nursefacilities_df = pd.read_csv(self.level2_nurse_facilities)
        self.sexual_violence_df = pd.read_csv(self.sexual_violence)

    # ---- Accessor Methods ----
    def get_county_boundaries(self):
        return self.county_boundaries_df

    def get_facilities(self):
        return self.facilities_df

    def get_projected_population(self):
        return self.projected_population_df

    def get_teen_pregnancy(self):
        return self.teen_pregnancy_df

    def get_low_staff_facilities(self):
        return self.less_than3_nursefacilities_df

    def get_sexual_violence(self):
        return self.sexual_violence_df


def merge_dfs_to_gdf(gdf, dfs, key="County"):
    """Merge multiple pandas DataFrames into a GeoDataFrame on a common key."""
    merged = gdf.copy()
    for i, df in enumerate(dfs, 1):
        merged = merged.merge(df, on=key, how="left", suffixes=("", f"_{i}"))
    return merged
