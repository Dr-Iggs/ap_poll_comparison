#%%
import pandas as pd
import numpy as np

df = pd.DataFrame()
for year in range(1980,2025,1):
    print(year)
    yeardf = pd.read_html(f'past_polls/{year}.xls',header=0)[0]
    yeardf['Year'] = year
    df=pd.concat([df,yeardf])

df['SchoolName'] = df['School'].str.replace(r'\s*\(.*?\)', '', regex=True)
df['YearTxt'] = df['Year'].astype(str)
df['ReleaseDate'] = np.where(df['Date']=='Final',df['YearTxt']+'-12-31',
                             np.where(df['Date']=='Preseason',df['YearTxt']+'-08-01',
                             df['Date']))
df.head()
df.drop(columns=['YearTxt','This Week']).to_csv('AP Poll 1980-2024.csv')


# %%
df = pd.read_csv('AP Poll 1980-2024.csv')
better_team = 'BYU'
worse_team = 'Alabama'

grouped = df[df['SchoolName'].isin([better_team,worse_team])].groupby(by=['Year','ReleaseDate'])
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
week_comparison = df[df['SchoolName'].isin([better_team, worse_team])]
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

#%%
# "SCATTERPLOT" OF EVERY POLL AND WHO LED WHEN
result['Winner'] = np.where(result['better_team_rank']>result['worse_team_rank'],worse_team,
                     np.where(result['better_team_rank']<result['worse_team_rank'],better_team,
                     'tie')
)
has_better = df[df['SchoolName']==better_team].assign(rank_better=lambda x: x.Rk).filter(['ReleaseDate','SchoolName','rank_better'])
has_worse = df[df['SchoolName']==worse_team].assign(rank_worse=lambda x: x.Rk).filter(['ReleaseDate','SchoolName','rank_worse'])
polls = df[['ReleaseDate', 'Date']].drop_duplicates()\
    .merge(has_better,how='left', on='ReleaseDate')\
    .merge(has_worse,how='left', on='ReleaseDate',  )\
    .sort_values('ReleaseDate')
polls['Winner'] = np.where(polls['rank_worse'].notna() & polls['rank_better'].notna(),
                           np.where(polls['rank_worse']>polls['rank_better'],better_team,worse_team),
                    np.where(polls['rank_worse'].notna(),worse_team,
                    np.where(polls['rank_better'].notna(),better_team,
                        'Neither')))
polls['Year'] = polls['ReleaseDate'].str[:4].astype(int)
polls['Week'] = polls.groupby('Year').cumcount() + 1
polls.head()

# Assuming polls DataFrame has 'Rank' and 'Year' columns
fig = px.scatter(polls, x='Week', y='Year', title="Rank vs Year Scatter Plot",color="Winner",
                 color_discrete_sequence=polls['Color'].unique())

# Show the plot
fig.show()

#%%
teams = {
  # American
  "Cincinnati" : ("#000000", "#E2001D"),
  "East Carolina" : ("#582884", "#FFD80E"),
  "Houston" : ("#C8102E", "#FFFFFF"),
  "Memphis" : ("#074389", "#9FA1A2"),
  "Navy" : ("#002058", "#D2C38D"),
  "SMU" : ("#E80132", "#002E9F"),
  "South Florida" : ("#00392A", "#C3B163"),
  "Temple" : ("#940031", "#FFFFFF", "#000000"),
  "Tulane" : ("#005834", "#FFFFFF","#01A5D8"),
  "Tulsa" : ("#002F67", "#A59C68"),
  "UCF" : ("#B9A569", "#000000"),
  # ACC
  "Boston College" : ("#8E1C2F", "#DCCEA6"),
  "Clemson" : ("#F56700", "#FFFFFF", "#3B1E72"),
  "Duke" : ("#092F87", "#FFFFFF"),
  "Florida State" : ("#782F40", "#CFB988", "#FFFFFF"),
  "Georgia Tech" : ("#002C56", "#A5805A"),
  "Louisville" : ("#CA0019", "#000000", "#FEBB0C"),
  "Miami" : ("#E95700", "#FFFFFF", "#004E2E"),
  "NC State" : ("#CD0000", "#000000", "#FFFFFF"),
  "North Carolina" : ("#77A9CE", "#FFFFFF", "#112849"),
  "Notre Dame" : ("#011142", "#9D8839", "#01873B"),
  "Pittsburgh" : ("#003295", "#FFBA15"),
  "Syracuse" : ("#F14F23", "#FFFFFF", "#091F40"),
  "Virginia" : ("#232B42", "#FC5A1D"),
  "Virginia Tech" : ("#6E2A3D", "#D74B29", "#FFFFFF"),
  "Wake Forest" : ("#000000", "#D0BA89"),
  # Big 12
  "Baylor" : ("#004834", "#FEBB30"),
  "Iowa State" : ("#960023", "#F9AE0D"),
  "Kansas" : ("#0051BC", "#000000", "#E90004"),
  "Kansas State" : ("#512888", "#FFFFFF", "#D1D1D1"),
  "Oklahoma" : ("#890002", "#FFFFFF"),
  "Oklahoma State" : ("#FF5C00", "#000000"),
  "TCU" : ("#4F2683", "#E6E7E8", "#000000"),
  "Texas" : ("#B44E2D", "#FFFFFF"),
  "Texas Tech" : ("#000000", "#CD0000", "#FFFFFF"),
  "West Virginia" : ("#012753", "#E8AD1C"),
  # B1G
  "Illinois" : ("#E94B37", "#14284B", "#FFFFFF"),
  "Indiana" : ("#990100", "#FFFFFF"),
  "Iowa" : ("#000000", "#F4CA16"),
  "Maryland" : ("#E31130", "#FFD300", "#000000"),
  "Michigan State" : ("#18453B", "#FFFFFF"),
  "Michigan" : ("#00274A", "#FFCF07"),
  "Minnesota" : ("#5F102E", "#FDC325"),
  "Nebraska" : ("#DD1B36", "#FFFFFF"),
  "Northwestern" : ("#59088F", "#FFFFFF", "#000000"),
  "Ohio State" : ("#BA0000", "#666666", "#000000"),
  "Penn State" : ("#002E62", "#FFFFFF"),
  "Purdue" : ("#000000", "#B2946B","#848B8E"),
  "Rutgers" : ("#D00829", "#FFFFFF", "#000000"),
  "Wisconsin" : ("#B40024", "#FFFFFF", "#000000"),
  # Conference USA
  "Charlotte" : ("#006A3E", "#FFFFFF", "#9C8847"),
  "Florida Atlantic" : ("#CD0000", "#FFFFFF", "#002F67"),
  "Florida International" : ("#081E3F", "#B6862D"),
  "Louisiana Tech" : ("#002D88", "#FFFFFF", "#CC3039"),
  "Marshall" : ("#046330", "#000000"),
  "Middle Tennessee" : ("#0067A4", "#FFFFFF", "#D2D5D8"),
  "North Texas" : ("#00853E", "#FFFFFF"),
  "Old Dominion" : ("#003769", "#FFFFFF", "#959CA1"),
  "Rice" : ("#091C5B", "#FFFFFF", "#B3B3B3"),
  "Southern Mississippi" : ("#030003", "#FFC527", "#FFFFFF"),
  "UAB" : ("#007149", "#161111", "#D0C781", "#D91D40"),
  "UTEP" : ("#041E42", "#FF8201", "#FFFFFF", "#B1B3B3"),
  "UTSA" : ("#002344", "#FFFFFF", "#E46B2B"),
  "Western Kentucky" : ("#C4013C", "#FFFFFF", "#000000"),
  # FBS Independents
  "Army" : ("#18191D", "#D8BA8A"),
  "BYU" : ("#001C54", "#FFFFFF", "#003EB1"),
  "Liberty" : ("#092643", "#FFFFFF", "#9A0000"),
  "New Mexico State" : ("#8B090E", "#FFFFFF", "#000000"),
  "UConn" : ("#0B2240", "#FFFFFF", "#A1A8AD","#EB092A"),
  "UMass" : ("#A50C31", "#FFFFFF", "#000000", "#D7D7D7"),
  # Mid-American
  "Akron" : ("#00275F", "#FFFFFF", "#948C76"),
  "Ball State" : ("#BA0C2F", "#FFFFFF", "#000000"),
  "Bowling Green" : ("#F15C26", "#542E1C", "#FFFFFF"),
  "Buffalo" : ("#005BBB", "#FFFFFF", "#000000"),
  "Central Michigan" : ("#4B0124", "#FEAF30", "#FFFFFF"),
  "Eastern Michigan" : ("#0F6838", "#FFFFFF", "#A8ADAD"),
  "Kent State" : ("#1E3C72", "#ECAA23", "#FFFFFF"),
  "Miami (OH)" : ("#D40124", "#FFFFFF", "#9BA3AA"),
  "Northern Illinois" : ("#000000", "#FFFFFF", "#BA0C2F"),
  "Ohio" : ("#006A4D", "#FFFFFF", "#000000", "#E5BD87"),
  "Toledo" : ("#002047", "#FFCE04", "#FFFFFF"),
  "Western Michigan" : ("#6D4022", "#000000", "#FFFFFF", "#B8A46A"),
  # Mountain West
  "Air Force" : ("#005DAB", "#FFFFFF", "#C5C5C5"),
  "Boise State" : ("#002FA2", "#FB440F", "#FFFFFF"),
  "Colorado State" : ("#184C27", "#FFFFFF","#C9C573"),
  "Fresno State" : ("#D12130", "#FFFFFF", "#14284D"),
  "Hawaii" : ("#00632C", "#B8B8B8", "#FFFFFF", "#000000"),
  "Nevada" : ("#021D42", "#FFFFFF", "#A8ADB4"),
  "New Mexico" : ("#BC032C", "#FFFFFF", "#A1A2A4", "#000000"),
  "San Diego State" : ("#C41230", "#FFFFFF", "#000000"),
  "San Jose State" : ("#0035AA", "#FFFFFF", "#FFBA12"),
  "UNLV" : ("#000000", "#E61A38", "#959CA1"),
  "Utah State" : ("#113257", "#FFFFFF", "#ACAAA5"),
  "Wyoming" : ("#533528", "#FEC524", "#FFFFFF"),
  # Pac-12
  "Arizona State" : ("#7A0C2F", "#000000", "#FFC422"),
  "Arizona" : ("#001B5C", "#FFFFFF", "#C2002C"),
  "California" : ("#02264A", "#F5C035", "#FFFFFF"),
  "Colorado" : ("#000000", "#D0B87D", "#FFFFFF"),
  "Oregon" : ("#004F28", "#FFF000", "#B2B7BB"),
  "Oregon State" : ("#000000", "#DD4200", "#FFFFFF"),
  "Stanford" : ("#8D1515", "#FFFFFF", "#007762"),
  "UCLA" : ("#007EC3", "#FDB827", "#FFFFFF"),
  "USC" : ("#951D32", "#FFC828", "#FFFFFF"),
  "Utah" : ("#CD0000", "#FFFFFF", "#000000"),
  "Washington" : ("#2F0067", "#FFFFFF", "#E9D5A3"),
  "Washington State" : ("#991E32", "#FFFFFF", "#5F6A71"),
  # SEC
  "Alabama" : ("#A8042D", "#FFFFFF", "#CACACA"),
  "Arkansas" : ("#A51E37", "#FFFFFF", "#000000"),
  "Auburn" : ("#001F4C", "#FFFFFF", "#FF6402"),
  "Florida" : ("#002D88", "#FFFFFF", "#FB440F"),
  "Georgia" : ("#D80100", "#FFFFFF", "#000000"),
  "Kentucky" : ("#002FA2", "#FFFFFF"),
  "LSU" : ("#4E2784", "#FFC324", "#FFFFFF"),
  "Mississippi State" : ("#5D1020", "#FFFFFF", "#C3C8C9"),
  "Missouri" : ("#000000", "#F1BA29", "#FFFFFF"),
  "Ole Miss" : ("#13213C", "#CC1130", "#FFFFFF"),
  "South Carolina" : ("#21201E", "#76000C", "#FFFFFF"),
  "Tennessee" : ("#F77E02", "#FFFFFF"),
  "Texas A&M" : ("#500000", "#FFFFFF", "#B1B3B6"),
  "Vanderbilt" : ("#000000", "#D0BA89", "#FFFFFF"),
  # Sun Belt
  "Appalachian State" : ("#000000", "#FFD205", "#FFFFFF"),
  "Arkansas State" : ("#000000", "#D02130", "#FFFFFF"),
  "Coastal Carolina" : ("#000000", "#006F72", "#FFFFFF", "#A27752"),
  "Georgia Southern" : ("#00183F", "#FFFFFF", "#9DA3A7", "#89714C"),
  "Georgia State" : ("#0133A0", "#FFFFFF", "#CD112C"),
  "Louisiana" : ("#FFFFFF", "#D2152A", "#000000"),
  "South Alabama" : ("#00205C", "#FFFFFF", "#BF0D3E"),
  "Texas State" : ("#571C1F", "#AD9256"),
  "Troy" : ("#6D0017", "#FFFFFF", "#B4B5B9"),
  "UL Monroe" : ("#810028", "#FFFFFF", "#F6B312"),
  "Neither" : ('#000000','#FFFFFF')
}

polls['Color'] = polls['Winner'].map(lambda winner: teams[winner][0])

#%%
from team_colors import team_colors