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


