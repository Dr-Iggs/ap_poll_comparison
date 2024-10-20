import streamlit as st
import pandas as pd
import numpy as np
df = pd.read_csv('AP Poll 1980-2024.csv')
df['Year'] = df['Year'].astype(int)

st.title('AP Poll Team Comparison')
better_team = st.selectbox(label='Select the better team:', 
                           options=df.SchoolName.sort_values().unique(),
                            index=8)
worse_team = st.selectbox(label='Select the worse team:', 
                          options=df.SchoolName.sort_values().unique(),
                          index=96)

if better_team and worse_team:
    # Filter rows where SchoolName is either better_team or worse_team
    week_comparison = df[df['SchoolName'].isin([better_team, worse_team])]

    # Group by Year and ReleaseDate
    filtered_groups = week_comparison.groupby(['Year', 'ReleaseDate']).filter(
        lambda x: set([better_team, worse_team]).issubset(x['SchoolName'].unique())
    )
    if filtered_groups.shape[0] == 0:
        st.write('Those 2 have never appeared in a poll together. Try a different team matchup.')
    # Summarise to calculate the Rank difference and include better_team and worse_team ranks
    else:
        result = filtered_groups.groupby(['Year', 'ReleaseDate','Date']).apply(
            lambda x: pd.Series({
                'better_team_rank': x.loc[x['SchoolName'] == better_team, 'Rk'].values[0],
                'worse_team_rank': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0],
                'rank_difference': x.loc[x['SchoolName'] == worse_team, 'Rk'].values[0] -
                                x.loc[x['SchoolName'] == better_team, 'Rk'].values[0]
            })
        ).reset_index()


        # Display the result
        most_recent = result.query('rank_difference > 0')\
            .sort_values('ReleaseDate',ascending=False)
        
        # BREAK if the better team has never actually out-ranked them in AP
        if most_recent.shape[0]==0:
            st.write(f'Unfortunately, {better_team} has never ranked higher than {worse_team} in the AP Poll.')
            st.write(f'But here are all the times they have polled together:')
            st.dataframe(result\
                    .sort_values('ReleaseDate')\
                    .rename(columns={'better_team_rank':better_team,
                                    'worse_team_rank':worse_team,
                                    'rank_difference':'Rank Difference'})\
                    .drop(columns='ReleaseDate'),
                    hide_index=True)
            
        
        else:
            most_recent = most_recent.iloc[0].to_dict()
            recent_date = np.where(most_recent['Date'] =='Preseason', most_recent['ReleaseDate'][:4]+' Preseason',
                            np.where(most_recent['Date'] =='Final', 'Final ' + most_recent['ReleaseDate'][:4],
                                    most_recent['ReleaseDate']))
            
            st.write(f'Most recently, {better_team} was higher than {worse_team} in the {recent_date} poll.')
            st.write(f'{better_team} was ranked {most_recent["better_team_rank"]}, while {worse_team} was ranked {most_recent["worse_team_rank"]}.')

            st.write(f'Between {min(df.Year)} and {max(df.Year)}, {better_team} and {worse_team} have appeared in the same poll {result.shape[0]} times.')
            st.write(f'{better_team} has led {result.query("rank_difference > 0").shape[0]} time(s), while {worse_team} has led {result.query("rank_difference < 0").shape[0]} time(s), with {result.query("rank_difference == 0").shape[0]} tie(s).')
            st.write()
            st.write('Here is the whole Top 25 from that poll:')
            st.dataframe(df[df['ReleaseDate']==most_recent['ReleaseDate']]\
                            .drop(columns=['Wk','Unnamed: 0','Chng','1st','ReleaseDate','SchoolName']),
                        hide_index=True,
                        width=600,
                        height=950)
            st.write()
            st.write(f'And here are all the times {better_team} has ranked above {worse_team}:')
            st.dataframe(result.query('rank_difference > 0')\
                    .sort_values('ReleaseDate')\
                    .rename(columns={'better_team_rank':better_team,
                                    'worse_team_rank':worse_team,
                                    'rank_difference':'Rank Difference'})\
                    .drop(columns='ReleaseDate'),
                    hide_index=True)