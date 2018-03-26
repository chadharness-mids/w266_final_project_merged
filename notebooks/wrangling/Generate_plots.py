import pandas as pd
import numpy as np
from datetime import timedelta

import bokeh
from bokeh.plotting import show, output_notebook
from bokeh.plotting import figure, show, output_file, reset_output
from bokeh.palettes import brewer, Category20
from bokeh.models import DatetimeTickFormatter
from bokeh.models import HoverTool

from bokeh.resources import CDN
from bokeh.embed import file_html

from bokeh.plotting import output_file
from bokeh.models.annotations import Label

# NFL Color Schemes
colors = pd.read_json('team_colors.json')
nfl_colors = colors.loc[colors['league'] == 'nfl']
nfl_colors['team_name'] = nfl_colors['name'].apply(lambda x: x.split()[-1])


colors = brewer['Paired']

def bokeh_plot_game(game, timeoffset):
    df = pd.read_pickle('../../data/Clean_Game_Data/{}_comment_sentiment.pickle'.format(game))
    df['tooltip'] = [x.strftime("%Y-%m-%d %H:%M:%S") for x in df['comment_created_utc_datetime']]
    df['winPercentageScaled'] = (df['homeWinPercentage'] - 0.5) * 2
    df_filtered = df.loc[df['comment_created_utc_datetime'] < df['comment_created_utc_datetime'].min() + timedelta(hours=5)]
    df_small = df_filtered[['text',
                            'comment_created_utc_datetime',
                            'winPercentageScaled',
                            'comment_body',
                            'author_flair',
                            'vader_compound',
                            'vader_neg',
                            'vader_neu',
                            'vader_pos',
                            'tooltip']]

    # Create dataframes for each comment type
    home_team_comments = df_filtered.loc[df_filtered['author_flair'] == df_filtered['home_team'].loc[1]].copy()
    away_team_comments = df_filtered.loc[df_filtered['author_flair'] == df_filtered['away_team'].loc[1]].copy()
    other_comments = df_filtered.loc[(df_filtered['author_flair'] != df_filtered['away_team'].loc[1]) &
                            (df_filtered['author_flair'] != df_filtered['home_team'].loc[1])].copy()

    # Create Bokeh Figure
    p = figure(plot_height=500,
               plot_width=1000,
               sizing_mode='scale_width',
               x_axis_type="datetime",
               tools=['xwheel_zoom', 'xpan', 'reset', 'xbox_zoom', 'save'],
               title="Game Analysis {}".format(game),
               y_range = (-1,1))

    # Add Lines
    winpct = p.line(x='comment_created_utc_datetime',
                    y='winPercentageScaled',
                    source=df_small,
                    color='#000000')

    # Add Rolling Sentiment

    window_home = round(len(home_team_comments) / 20)
    window_away = round(len(away_team_comments) / 20)
    window_other = round(len(other_comments) / 20)

    # Configure Colors
    home_team_text = df_filtered['home_team'].loc[1]
    away_team_text = df_filtered['away_team'].loc[1]

    hometeamcolor = nfl_colors.loc[nfl_colors['team_name'] == home_team_text]['colors'].values[0]['hex'][0]
    awayteamcolor = nfl_colors.loc[nfl_colors['team_name'] == away_team_text]['colors'].values[0]['hex'][0]

    home_team_comments['vader_rolling'] = home_team_comments['vader_compound'].rolling(window=window_home).mean(center=True) * 4
    away_team_comments['vader_rolling'] = away_team_comments['vader_compound'].rolling(window=window_away).mean(center=True) * 4
    other_comments['vader_rolling'] = other_comments['vader_compound'].rolling(window=window_other).mean(center=True) * 4

    p.line(x=home_team_comments['comment_created_utc_datetime'],
           y=home_team_comments['vader_rolling'],
           legend='Vader Sentiment {} Fans Rolling'.format(df_filtered['home_team'].loc[1]),
           color='#'+hometeamcolor)
    p.line(x=away_team_comments['comment_created_utc_datetime'],
           y=away_team_comments['vader_rolling'],
           legend='Vader Sentiment {} Fans Rolling'.format(df_filtered['away_team'].loc[1]),
           color='#'+awayteamcolor)
    p.line(x=other_comments['comment_created_utc_datetime'],
           y=other_comments['vader_rolling'],
           legend='Vader Sentiment Others Rolling',
           color='#999999')

    # Create Hovertool
    my_hover = HoverTool()
    my_hover.tooltips = [
        ("Datetime", '@tooltip'),
        ("winPercentageScaled", "@winPercentageScaled"),
        ("Last Play","@text"),
        ("Comment","@comment_body"),
        ("Comment Author Flair", "@author_flair"),
        ("Comment Vader Sentiment", "@vader_compound"),
        ("Vader Negative", "@vader_neg"),
        ("Vader Positive", "@vader_pos"),
        ("Vader Neutral", "@vader_neu"),]
    my_hover.formatters = {"Datetime": "datetime"}
    my_hover.renderers = [winpct]
    my_hover.mode = 'vline'
    p.add_tools(my_hover)

    # Make line hide when clicked in legend
    p.legend.click_policy = "hide"
    p.xgrid.visible = False

    # Add labels
    hometeamtext = Label(x=df['comment_created_utc_datetime'].min(), y=0.90, text='{} Winning'.format(home_team_text))
    awayteamtext = Label(x=df['comment_created_utc_datetime'].min(), y=-0.90, text='{} Winning'.format(away_team_text))

    p.add_layout(hometeamtext)
    p.add_layout(awayteamtext)

    # Show the Plot
    return p


good_data_games = pd.read_csv('../../data/Good_Games_with_DateGameNames.csv')
ggames = good_data_games['matched_game_date'].values

# good_data_games = good_data_gam

for ggame in good_data_games.iterrows():
    gamename = ggame[1]['matched_game_date']
    offset = ggame[1]['Timeoffset']
    print(gamename)
    print(offset)
    try:
        reset_output()
        output_file('html/{}.html'.format(gamename.replace(' ','_'), title=gamename))
        p = bokeh_plot_game(gamename.replace(' ','_').replace('.',''), timeoffset=offset)
        show(p)
    except:
        print("Didnt Work for {}".format(gamename))
