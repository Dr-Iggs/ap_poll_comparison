#%%
import pandas as pd
year = 2000
df = pd.DataFrame()
for year in range(2000,2024,1):
    yeardf = pd.read_html(f'{year}.xls',header=0)[0]
    yeardf['Year'] = year
    df=pd.concat([df,yeardf])

#%%
import numpy as np
df['SchoolName'] = df['School'].str.replace(r'\s*\(.*?\)', '', regex=True)
df['YearTxt'] = df['Year'].astype(str)
df['ReleaseDate'] = np.where(df['Date']=='Final',df['YearTxt']+'-12-31',
                             np.where(df['Date']=='Preseason',df['YearTxt']+'-08-01',
                             df['Date']))
df.head()
#%%
df.drop(columns=['SchoolRecord','YearTxt']).to_csv('AP Poll 2000-23.csv')


# %%
better_team = 'BYU'
worse_team = 'Alabama'

grouped = df[df['SchoolName'] == better_team | df['SchoolName'] == worse_team].groupby(by=['Year','ReleaseDate'])
filtered_groups = grouped.filter(lambda x: set([better_team, worse_team]).issubset(x['SchoolName'].unique()))
filtered_groups

# %%
week_comparison = df[df['SchoolName'].isin([better_team, worse_team])]

# Group by Year and ReleaseDate
filtered_groups = week_comparison.groupby(['Year', 'ReleaseDate']).filter(
    lambda x: set([better_team, worse_team]).issubset(x['SchoolName'].unique())
)

# Summarise to calculate the Rank difference
result = filtered_groups.groupby(['Year', 'ReleaseDate','Date']).apply(
    lambda x: pd.Series({
        'better_team_rank': x.loc[x['SchoolName'] == better_team, 'Rk'].values[0],
        'worse_team_rank': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0],
        'rank_difference': x.loc[x['SchoolName'] == better_team, 'Rk'].values[0] -
                           x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0]
    })
).reset_index()

# Display the result
result
#%%
most_recent = result.query('rank_difference < 0')\
        .sort_values('ReleaseDate')\
        .iloc[0].to_dict()

recent_date = np.where(most_recent['Date'] =='Preseason', most_recent['ReleaseDate'][:4]+' Preseason',
                np.where(most_recent['Date'] =='Final', 'Final ' + most_recent['ReleaseDate'][:4],
                         most_recent['ReleaseDate']))



#%%
print(f'{better_team} was higher than {worse_team} in the {recent_date} poll.')
print(f'{better_team} was ranked {most_recent["better_team_rank"]}, while {worse_team} was ranked {most_recent["worse_team_rank"]}')

print(f'Between {min(df.Year)} and {max(df.Year)}, {better_team} and {worse_team} have appeared in the same poll {result.shape[0]} times.')
print(f'{better_team} has led {result.query("rank_difference < 0").shape[0]} time(s), while {worse_team} has led {result.query("rank_difference > 0").shape[0]} time(s), with {result.query("rank_difference == 0").shape[0]} tie(s).')
# %%
#The full Top 25 from the most recent better poll
df[df['Date']==most_recent['Date']]

#%%
#The full list of polls where they're better
result.query('rank_difference < 0')\
    .sort_values('ReleaseDate')\
    .rename(columns={'better_team_rank':better_team,
                     'worse_team_rank':worse_team,
                     'rank_difference':'Rank Difference'})\
    .drop(columns='ReleaseDate')

#%%
better_team='Arizona'
worse_team='Houston'
# The most recent week that BYU was in the polls, but not Alabama
filtered_groups = week_comparison.groupby(['Year', 'ReleaseDate']).filter(
    lambda x: (better_team in x['SchoolName'].unique()) and (worse_team not in x['SchoolName'].unique())
)

result = filtered_groups.groupby(['Year', 'ReleaseDate','Date']).apply(
            lambda x: pd.Series({
                'better_team_rank': x.loc[x['SchoolName'] == better_team, 'Rk'].values[0],
                'worse_team_rank': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0],
                'rank_difference': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0] -
                                x.loc[x['SchoolName'] == better_team, 'Rk'].values[0]
            })
        ).reset_index()
result

#%%
#Error detection: they never show up in a poll together
better_team='Arizona'
worse_team='Houston'
week_comparison = df[df['SchoolName'].isin([better_team, worse_team])]
filtered_groups = week_comparison.groupby(['Year', 'ReleaseDate']).filter(
        lambda x: set([better_team, worse_team]).issubset(x['SchoolName'].unique())
    )


result = filtered_groups.groupby(['Year', 'ReleaseDate','Date']).apply(
            lambda x: pd.Series({
                'better_team_rank': x.loc[x['SchoolName'] == better_team, 'Rk'].values[0],
                'worse_team_rank': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0],
                'rank_difference': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0] -
                                x.loc[x['SchoolName'] == better_team, 'Rk'].values[0]
            })
        ).reset_index()
result