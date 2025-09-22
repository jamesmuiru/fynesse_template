# address.py
import pandas as pd
import numpy as np
import math
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import plotly.express as px

class HealthFacilityOptimizer:
    def __init__(self, gdf):
        """
        Initialize with a GeoDataFrame containing the required columns.
        """
        self.counties = gdf.copy()
        self.summary = None
        self.cluster_stats = None

    def preprocess(self):
        """Coerce numeric columns, fill missing values, and compute derived indicators."""
        expected_cols = [
            'Shape_Leng','Shape_Area','County','ADM1_PCODE','ADM1_REF','ADM1ALT1EN','ADM1ALT2EN',
            'ADM0_EN','ADM0_PCODE','date','validOn','validTo','Population_density',
            'Health_Facilities_distance','geometry','Total_number_of_facilities',
            'insurance_covered_population','Facilities_Completed','Facilities_Closed',
            '2025_Projected_Population','Have_ever_had_a_pregnancy_loss',
            'Number_of_women_with_underage_pregnancy','Total_Level2_Facilities',
            'LowStaff_Facilities','Percentage_of_scarcity','Ever_got_underage_pregnancy(%)',
            'Number_of_women_5'
        ]
        missing = [c for c in expected_cols if c not in self.counties.columns]
        if missing:
            raise ValueError(f"Missing expected columns: {missing}")

        # Numeric coercion
        num_cols = [
            'Population_density','Health_Facilities_distance','Total_number_of_facilities',
            'insurance_covered_population','Facilities_Completed','Facilities_Closed',
            '2025_Projected_Population','Have_ever_had_a_pregnancy_loss',
            'Number_of_women_with_underage_pregnancy','Total_Level2_Facilities',
            'LowStaff_Facilities','Percentage_of_scarcity','Ever_got_underage_pregnancy(%)',
            'Number_of_women_5'
        ]
        for col in num_cols:
            self.counties[col] = pd.to_numeric(self.counties[col], errors='coerce')

        # Fill sensible defaults
        fill_zero_cols = [
            'Total_number_of_facilities','Facilities_Completed','Facilities_Closed',
            'Total_Level2_Facilities','LowStaff_Facilities','Number_of_women_5'
        ]
        for c in fill_zero_cols:
            self.counties[c] = self.counties[c].fillna(0)
        self.counties['2025_Projected_Population'] = self.counties['2025_Projected_Population'].fillna(0)
        self.counties['Population_density'] = self.counties['Population_density'].fillna(0)
        if self.counties['Health_Facilities_distance'].isna().any():
            maxd = self.counties['Health_Facilities_distance'].max(skipna=True)
            if pd.isna(maxd):
                maxd = 1.0
            self.counties['Health_Facilities_distance'] = self.counties['Health_Facilities_distance'].fillna(maxd*1.2)

        # Derived indicators
        self.counties['Facility_Ratio'] = self.counties['2025_Projected_Population'] / (self.counties['Total_number_of_facilities'] + 1)
        self.counties['Accessibility'] = 1 / (self.counties['Health_Facilities_distance'] + 1)
        self.counties['Scarcity'] = self.counties['Percentage_of_scarcity'].fillna(0)
        self.counties['Vulnerability_raw'] = (
            self.counties['Have_ever_had_a_pregnancy_loss'].fillna(0)*0.5 +
            (self.counties['Number_of_women_with_underage_pregnancy'].fillna(0) / self.counties['Number_of_women_5'].replace(0,np.nan).fillna(1))*0.3 +
            self.counties['Ever_got_underage_pregnancy(%)'].fillna(0)*0.2
        )
        self.counties['LowStaff_Ratio'] = self.counties['LowStaff_Facilities'] / (self.counties['Total_Level2_Facilities'] + 1)

    def normalize_and_score(self):
        """Normalize key indicators and compute composite Priority_Score."""
        scaler = MinMaxScaler()
        to_normalize = ['Facility_Ratio','Accessibility','Scarcity','Vulnerability_raw','LowStaff_Ratio','Population_density']
        counties_norm = self.counties.copy()
        counties_norm[to_normalize] = scaler.fit_transform(counties_norm[to_normalize].fillna(0))
        counties_norm['Inverted_Accessibility'] = 1 - counties_norm['Accessibility']

        weights = {'Facility_Ratio':0.3,'Accessibility':0.2,'Scarcity':0.2,'Vulnerability_raw':0.15,'LowStaff_Ratio':0.1}
        counties_norm['Priority_Score_raw'] = (
            weights['Facility_Ratio']*counties_norm['Facility_Ratio'] +
            weights['Accessibility']*counties_norm['Inverted_Accessibility'] +
            weights['Scarcity']*counties_norm['Scarcity'] +
            weights['Vulnerability_raw']*counties_norm['Vulnerability_raw'] +
            weights['LowStaff_Ratio']*counties_norm['LowStaff_Ratio']
        )
        counties_norm['Priority_Score'] = MinMaxScaler().fit_transform(counties_norm[['Priority_Score_raw']])
        self.counties['Priority_Score'] = counties_norm['Priority_Score']

    def cluster_counties(self, n_clusters=3):
        """Apply KMeans clustering to priority features."""
        features_for_clustering = ['Facility_Ratio','Accessibility','Scarcity','Vulnerability_raw','LowStaff_Ratio','Population_density']
        cluster_scaler = StandardScaler()
        X = cluster_scaler.fit_transform(self.counties[features_for_clustering].fillna(0))
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.counties['Cluster'] = kmeans.fit_predict(X)

    def suggest_new_facilities(self, people_per_facility=30000):
        """Compute suggested new facilities per county."""
        def compute_additional_facilities(row, desired=people_per_facility):
            projected_pop = row['2025_Projected_Population']
            current_fac = row['Total_number_of_facilities']
            target_facilities = math.ceil(projected_pop / (desired if desired>0 else 1))
            additional_needed = max(0, target_facilities - int(current_fac))
            return additional_needed
        self.counties['Suggested_New_Facilities'] = self.counties.apply(lambda r: compute_additional_facilities(r), axis=1)

    def get_summary(self, top_n=10):
        """Return a sorted summary of top counties by priority score."""
        summary_cols = [
            'County','2025_Projected_Population','Total_number_of_facilities','Facility_Ratio',
            'Priority_Score','Cluster','Suggested_New_Facilities','Scarcity','LowStaff_Ratio'
        ]
        self.summary = self.counties[summary_cols].copy().sort_values('Priority_Score', ascending=False).reset_index(drop=True)
        return self.summary.head(top_n)

    def plot_priority(self):
        """Matplotlib and Plotly visualizations for priority and clusters."""
        fig, ax = plt.subplots(1, 2, figsize=(18,9))
        self.counties.plot(column='Priority_Score', cmap='Reds', legend=True, ax=ax[0])
        ax[0].set_title('Priority Score for Facility Placement (0 low - 1 high)')
        ax[0].axis('off')
        self.counties.plot(column='Cluster', categorical=True, legend=True, ax=ax[1])
        ax[1].set_title('KMeans clusters (3) - planning buckets')
        ax[1].axis('off')
        plt.tight_layout()
        plt.show()

        # Interactive Plotly choropleth
        fig = px.choropleth_mapbox(
            self.counties,
            geojson=self.counties.geometry.__geo_interface__,
            locations=self.counties.index,
            color="Priority_Score",
            hover_name="County",
            hover_data={
                "Priority_Score": ':.2f',
                "2025_Projected_Population": True,
                "Total_number_of_facilities": True,
                "Suggested_New_Facilities": True,
                "Cluster": True
            },
            mapbox_style="carto-positron",
            center={"lat": -0.0236, "lon": 37.9062},
            zoom=5.8,
            opacity=0.65,
            color_continuous_scale=[
                [0.0, "lightyellow"],
                [0.3, "orange"],
                [0.6, "orangered"],
                [1.0, "darkred"]
            ]
        )
        fig.update_layout(title={'text': "🩺 Health Facility Optimization Priority Heatmap (Kenyan Counties)",
                                 'y':0.95,'x':0.5,'xanchor':'center','yanchor':'top','font':{'size':20}},
                          margin={"r":0,"t":30,"l":0,"b":0},
                          mapbox_zoom=5.8,mapbox_center={"lat": -0.0236,"lon":37.9062},
                          legend_title="Priority Score")
        fig.show()

