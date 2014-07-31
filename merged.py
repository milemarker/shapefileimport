__author__ = 'djvdorp'
import pandas
import csv

hectopunten_df = pandas.read_csv('output/Hectopunten.csv')
wegvakken_df = pandas.read_csv('output/Wegvakken.csv')

merged_df = pandas.merge(hectopunten_df, wegvakken_df, on='WVK_ID')
merged_df['ID'] = merged_df.index

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

result_df.to_csv('output/merged.csv', mode='wb', index=False, header=True, quoting=csv.QUOTE_NONNUMERIC)