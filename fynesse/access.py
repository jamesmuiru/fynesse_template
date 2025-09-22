# access.py
import geopandas as gpd
import pandas as pd
import os
import requests
import zipfile

class HealthDataLoader:
    def __init__(self, shapefile_zip_url=None):
        """
        Initialize the data loader with GitHub CSV paths.
        Optionally download and extract a shapefile zip from GitHub.
        """
        # GitHub raw URLs for CSV datasets
        base_url = "https://raw.githubusercontent.com/jamesmuiru/mlfccourse/main/csvs"
        self.health_facilities_data = f"{base_url}/facilities_data.csv"
        self.projected_population_2025 = f"{base_url}/projected_population_2025.csv"
        self.teen_pregnancy_bycounty = f"{base_url}/teen_pregnacy_dataByCounty.csv"
        self.level2_nurse_facilities = f"{base_url}/level2_lessthan3nursesfacilities_nurses.csv"
        self.sexual_violence = f"{base_url}/sexual_violence.csv"

        # Optional shapefile zip URL
        self.shapefile_zip_url = shapefile_zip_url
        self.shapefile_dir = "shapefile"
        self.county_shapefile = os.path.join(self.shapefile_dir, "county_with_raster_means.shp")

        # Placeholders for loaded data
        self.county_boundaries_df = None
        self.facilities_df = None
        self.projected_population_df = None
        self.teen_pregnancy_df = None
        self.less_than3_nursefacilities_df = None
        self.sexual_violence_df = None

    def download_and_extract_shapefile(self):
        """Download shapefile zip from GitHub and extract it."""
        if not self.shapefile_zip_url:
            raise ValueError("No shapefile zip URL provided.")
        
        os.makedirs(self.shapefile_dir, exist_ok=True)
        zip_path = os.path.join(self.shapefile_dir, "shapefile.zip")
        
        # Download
        r = requests.get(self.shapefile_zip_url)
        with open(zip_path, "wb") as f:
            f.write(r.content)
        
        # Extract
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(self.shapefile_dir)

    def load_data(self):
        """Load all datasets into memory."""
        # 1️⃣ Shapefile
        if self.shapefile_zip_url:
            self.download_and_extract_shapefile()
            self.county_boundaries_df = gpd.read_file(self.county_shapefile)

        # 2️⃣ CSV datasets
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
