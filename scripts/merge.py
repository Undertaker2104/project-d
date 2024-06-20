import pandas as pd

# Lees de Excel-bestanden in pandas DataFrames
actionscopes_df = pd.read_excel('./Data/translated_actionscopes.xlsx')
service_joborders_df = pd.read_excel('./Data/translated_service_joborders.xlsx')

# Voer de merge uit op de kolom 'Actionscope.Code'
merged_df = pd.merge(actionscopes_df, service_joborders_df, left_on='Code', right_on='Actionscope.Code', how='outer')
#columns_to_drop = ['Priority', 'Relation.Relation ID', 'Salesorder']

# Drop the irrelevant columns
#merged_df.drop(columns=columns_to_drop, inplace=True)
# Sla de DataFrame op als Excel-bestand
merged_df.to_excel('./Data/merged_data.xlsx', index=False)
