import pandas as pd
def dtype_edit(dt):
    dt['Search Frequency Rank'] = dt['Search Frequency Rank'].apply(lambda x: str(x).replace(',','')).astype('float64')
    for num in range (1,4):
        for partition in [' Conversion Share',' Click Share', ' bsr1', ' bsr2', ' rating_count',' rating']:
            try:
                column = '#'+str(num)+partition
                dt[column] = dt[column].apply(lambda x: str(x).replace('%','').replace('—','0')).astype('float64')               
            except:
                pass
    return dt

def parser_edit(df_new, df_old):
    df_old = dtype_edit(df_old)
    df_new = dtype_edit(df_new)

    df_left = pd.merge(df_new,df_old[['Search Term', 'Search Frequency Rank']], on = ['Search Term'], how='left')
    df_left.rename({'Search Frequency Rank_x': 'sfr_new', 
           'Search Frequency Rank_y':'sfr_old'}, axis=1, inplace=True)
    df_left['sfr_old'] = df_left['sfr_old'].apply(lambda x: str(x).replace(',','')).astype('float64')
    df_left['search frequency change'] = df_left['sfr_old']- df_left['sfr_new']

    df_left = df_left[[
     'Department',
     'Search Term',
     'sfr_new',
     'sfr_old',
     'search frequency change',
     '#1 Clicked ASIN',
     '#1 Product Title',
     '#1 Click Share',
     '#1 Conversion Share',
     '#1 bsr1',
     '#1 bsr1_name',
     '#1 bsr2',
     '#1 bsr2_name',
     '#1 rating_count',
     '#1 rating',
     '#2 Clicked ASIN',
     '#2 Product Title',
     '#2 Click Share',
     '#2 Conversion Share',
     '#2 bsr1',
     '#2 bsr1_name',
     '#2 bsr2',
     '#2 bsr2_name',
     '#2 rating_count',
     '#2 rating',
     '#3 Clicked ASIN',
     '#3 Product Title',
     '#3 Click Share',
     '#3 Conversion Share',
     '#3 rating_count',
     '#3 rating',
     '#3 bsr1',
     '#3 bsr1_name',
     '#3 bsr2',
     '#3 bsr2_name'

    ]]
    return df_left

def header_edit(dt):
    dt = dt.reset_index()
    new_header = dt.iloc[0] #grab the first row for the header
    dt = dt[1:] #take the data less the header row
    dt.columns = new_header #set the header row as the df header
    return dt