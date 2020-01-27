from django.shortcuts import render
import numpy as np
import pandas as pd
from django.views.generic import ListView, View
from django.views import View


m_df = pd.read_csv('../matches.csv')
d_df = pd.read_csv('../deliveries.csv')


class Index(View):
    template_name = "index.html"

    def get(self, request):
        seasons_list = m_df['season'].unique()
        return render(request, self.template_name, context={'seasons':seasons_list })


class IPLMatchStats(View):
    template_name = "index.html"
    df_by_season = m_df[m_df['season']==2017]

    def loc_won_loss_percent(self):
        max_played_loc = self.df_by_season['city'].value_counts().keys()[0]
        win_loss_df = self.df_by_season[self.df_by_season[
            'city']==max_played_loc][['team1','team2','winner']]
        win_loss_df['loser'] = np.where(
            win_loss_df['team1']==win_loss_df['winner'],
            win_loss_df['team2'],win_loss_df['team1'])
        
        win_loss_df = win_loss_df[['winner','loser']]
        win_in_city = win_loss_df.winner.value_counts().to_dict()
        loss_in_city = win_loss_df.loser.value_counts().to_dict()

        win_loss_per = pd.DataFrame(columns=[
            'teams','win_percent','loss_percent'])
        win_loss_per['teams'] = np.unique(
            win_loss_df[['winner','loser']].values)

        for key, value in win_in_city.items():
            for i in range(len(win_loss_per['teams'])):
                if win_loss_per.loc[i]['teams']==key:
                    win_loss_per.loc[i]['win_percent']=value

        for key, value in loss_in_city.items():
            for i in range(len(win_loss_per['teams'])):
                if win_loss_per.loc[i]['teams']==key:
                    win_loss_per.loc[i]['loss_percent']= value

        win_loss_per['win_percent'].fillna(0, inplace=True)
        win_loss_per['loss_percent'].fillna(0, inplace=True)

        win_loss_per['win_percent'], win_loss_per['loss_percent'] =\
            win_loss_per['win_percent']*100/(
            win_loss_per['win_percent']+win_loss_per['loss_percent']),\
            win_loss_per['loss_percent']*100/(
                win_loss_per['win_percent']+win_loss_per['loss_percent'])            

        data = []
        for i in range(len(win_loss_per['teams'])):
            data.append({
                'team':win_loss_per.loc[i]['teams'],
                'win': win_loss_per.loc[i]['win_percent'],
                'loss':win_loss_per.loc[i]['loss_percent']
                })
        return data

    def get(self, request, season=None):

        seasons_list = m_df['season'].unique()

        if season:
            #filter by season
            self.df_by_season = m_df[m_df['season']==season]

            #1. top four winner teams of season
            top_four_teams = self.df_by_season['winner'].value_counts()[:4]

            #2. which team won the most number of tosses in the season
            top_toss_winners = self.df_by_season['toss_winner'].value_counts()
            
            
            #3. which player won the maximum number of Player of the Match awards in the whole season
            top_player_of_match = self.df_by_season[
                'player_of_match'].value_counts()[:1]
            
            #4. which team won max matches in the whole season
            team_won_max_matches = top_four_teams[:1]
            
            #5. which location has the most number of wins for the top team
            max_played_location = self.df_by_season[self.df_by_season[
                'winner']==team_won_max_matches.keys()[0]][
                'city'].value_counts()
            
            #6. which % of teams decided to bat when they won the toss            
            total_toss_winners = self.df_by_season['toss_winner'].count()            
            toss_winner_bat_first = self.df_by_season['toss_winner'][
                self.df_by_season['toss_decision']=='bat'].count()            
            percentage_of_toss_winner_bat_first=\
                (toss_winner_bat_first*100)/total_toss_winners

            #7. which location hosted most number of matches and win % and loss % for the season
            loc_won_loss_percent = self.loc_won_loss_percent()

            #8. which team won by the highest margin of runs for the season
            run_margin = self.df_by_season[self.df_by_season.win_by_runs==\
                self.df_by_season.win_by_runs.max()][['winner','win_by_runs']]

            #9. Which team won by the highest number of wickets for the season
            team_won_high_num = self.df_by_season[['winner', 'win_by_wickets']
                ].groupby('winner').sum()
            team_won_high_num = team_won_high_num.sort_values(
                by='win_by_wickets', ascending=False)

            #10. How many times has a team won the toss and the match
            team_win_toss_and_match = self.df_by_season[
                self.df_by_season['toss_winner']==self.df_by_season['winner']]\
                    ['toss_winner'].value_counts().to_dict()

        context = {
            'seasons': seasons_list,
            'is_season': season,
            'top_four_teams': top_four_teams.keys(),
            'top_toss_winner': top_toss_winners.keys()[0],
            'top_player_of_match': top_player_of_match.keys()[0],
            'team_won_max_matches': team_won_max_matches.keys()[0],
            'max_played_location': max_played_location[:1].keys()[0],
            'percentage_of_toss_winner_bat_first':
                percentage_of_toss_winner_bat_first,
            'win_loss_per':loc_won_loss_percent,
            'run_margin': run_margin.values,
            'team_won_high_num':team_won_high_num.iloc[0],
            'team_win_toss_and_match':team_win_toss_and_match,
        }
        return render(request, self.template_name, context)

