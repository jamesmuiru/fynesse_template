# access.py
import geopandas as gpd
import pandas as pd

class HealthDataLoader:
    def __init__(self, base_path="/content/drive/MyDrive/Miniproject"):
        """
        Initialize the data loader with default paths.
        """
        self.base_path = base_path

        # Define file paths
        self.county_shapefile = f"{base_path}/county_with_raster_means.shp"
        self.gpkg_file = f"{base_path}/county_boundaries.gpkg"
        self.health_facilities_data = f"{base_path}/csvs/facilities_data.csv"
        self.projected_population_2025 = f"{base_path}/csvs/projected_population_2025.csv"
        self.teen_pregnancy_bycounty = f"{base_path}/csvs/teen_pregnacy_dataByCounty.csv"
        self.level2_nurse_facilities = f"{base_path}/csvs/level2_lessthan3nursesfacilities_nurses.csv"
        self.sexual_violence = f"{base_path}/csvs/sexual_violence.csv"

        # Placeholders for loaded data
        self.county_boundaries_df = None
        self.facilities_df = None
        self.projected_population_df = None
        self.teen_pregnancy_df = None
        self.less_than3_nursefacilities_df = None
        self.sexual_violence_df = None

    def load_data(self):
        """Load all datasets into memory."""
        # Load county shapefile
        self.county_boundaries_df = gpd.read_file(self.county_shapefile)

        # Convert to GPKG to avoid column truncation and reload
        self.county_boundaries_df.to_file(self.gpkg_file, driver="GPKG")
        self.county_boundaries_df = gpd.read_file(self.gpkg_file)

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
