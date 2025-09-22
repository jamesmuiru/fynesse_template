# Define valid counties
valid_counties = [
 'Baringo','Bomet','Bungoma','Busia','Elgeyo-Marakwet','Embu','Garissa','Homa Bay',
 'Isiolo','Kajiado','Kakamega','Kericho','Kiambu','Kilifi','Kirinyaga','Kisii',
 'Kisumu','Kitui','Kwale','Laikipia','Lamu','Machakos','Makueni','Mandera',
 'Marsabit','Meru','Migori','Mombasa',"Murang'a",'Nairobi','Nandi','Narok',
 'Nyamira','Nyandarua','Nyeri','Samburu','Siaya','Taita Taveta','Tana River',
 'Tharaka-Nithi','Trans Nzoia','Turkana','Uasin Gishu','Vihiga','Wajir',
 'West Pokot','Nakuru'
]

def clean_county_names(df, col="County"):
    """
    Standardize County names and remove invalid rows.

    Parameters:
        df (pd.DataFrame): DataFrame to clean
        col (str): Name of the county column

    Returns:
        pd.DataFrame: Cleaned DataFrame
    """
    replacements = {
        "Muranga": "Murang'a",
        "Murang’a": "Murang'a",
        "Taita/Taveta": "Taita Taveta",
        "Tharaka Nithi": "Tharaka-Nithi",
        "TharakaNithi": "Tharaka-Nithi",
        "Elgeyo Marakwet": "Elgeyo-Marakwet",
        "Elgeyo/Marakwet": "Elgeyo-Marakwet",
        "Nairobi City": "Nairobi",
        "HomaBay": "Homa Bay",
        "Total": None  # drop invalid rows
    }

    # Apply replacements
    df[col] = df[col].replace(replacements)

    # Keep only counties that are in the valid list
    df = df[df[col].isin(valid_counties)].copy()

    return df
# assess.py
import matplotlib.pyplot as plt
import geopandas as gpd

def plot_gdf_column(gdf, column, plot_type="bar", top_n=None, figsize=(12,6), title=None):
    """
    Plot a specific column from a GeoDataFrame.

    Parameters:
        gdf (GeoDataFrame): Input GeoDataFrame containing data.
        column (str): Column name to plot.
        plot_type (str): Type of plot: "bar" (default) or "hist".
        top_n (int): If specified, show only top N rows sorted by column value.
        figsize (tuple): Figure size.
        title (str): Optional plot title.

    Returns:
        None: Displays the plot.
    """
    if column not in gdf.columns:
        raise ValueError(f"Column '{column}' not found in the GeoDataFrame")

    # Select data
    data = gdf[[column, "County"]].copy()
    
    # If top_n is specified, sort by column
    if top_n:
        data = data.sort_values(by=column, ascending=False).head(top_n)

    plt.figure(figsize=figsize)

    if plot_type == "bar":
        plt.bar(data["County"], data[column], color="skyblue")
        plt.xticks(rotation=90)
        plt.ylabel(column)
        plt.xlabel("County")
    elif plot_type == "hist":
        plt.hist(data[column], bins=20, color="skyblue", edgecolor="black")
        plt.xlabel(column)
        plt.ylabel("Frequency")
    else:
        raise ValueError("plot_type must be 'bar' or 'hist'")

    if title:
        plt.title(title)
    else:
        plt.title(f"{column} distribution by County")

    plt.tight_layout()
    plt.show()

def plot_gdf_correlation(gdf, exclude_cols=None):
    """
    Generate a correlation heatmap for numeric columns in a GeoDataFrame.

    Parameters:
        gdf (GeoDataFrame): The GeoDataFrame containing county-level data.
        exclude_cols (list): Columns to exclude from correlation calculation.
    """
    import seaborn as sns
    import matplotlib.pyplot as plt

    if exclude_cols is None:
        exclude_cols = ['Shape_Leng', 'Shape_Area', 'ADM1_PCODE', 'ADM1_REF', 
                        'ADM1ALT1EN', 'ADM1ALT2EN', 'ADM0_EN', 'ADM0_PCODE', 
                        'date', 'validOn', 'validTo']

    # Select numeric columns excluding the ones in exclude_cols
    numeric_cols = gdf.select_dtypes(include='number').columns
    numeric_cols = [col for col in numeric_cols if col not in exclude_cols]

    # Compute correlation matrix
    corr = gdf[numeric_cols].corr()

    # Plot heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap='coolwarm', cbar=True, square=True)
    plt.title("Correlation Heatmap of Numeric County Indicators", fontsize=16)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()




