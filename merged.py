__author__ = 'djvdorp'
import pandas
import csv

hectopunten_df = pandas.read_csv('output/Hectopunten.csv')
#print(len(hectopunten_df))
#print(hectopunten_df[:2])

wegvakken_df = pandas.read_csv('output/Wegvakken.csv')
#print(len(wegvakken_df))
#print(wegvakken_df[:2])

merged_df = pandas.merge(hectopunten_df, wegvakken_df, on='WVK_ID')
merged_df['ID'] = merged_df.index
#print(len(merged_df))
#print(merged_df[:2])

result_df = merged_df[
    ['ID',
     'HECTOMTRNG',
     'LONGITUDE',
     'LATITUDE',
     'STT_NAAM',
     'GME_NAAM',
     'WEGBEHSRT',
     'RPE_CODE',
     'POS_TV_WOL',
     'WEGDEELLTR',
     'HECTO_LTTR',
     'BAANSUBSRT']
]

#print(result_df[:2])
result_df.to_csv('output/merged.csv', index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)