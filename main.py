import requests
import pandas as pd
import streamlit as st
from datetime import datetime


class SleeperAPI:
    def __init__(self, username):
        self.username = username
        self.base_url = "https://api.sleeper.app/v1"

    def get_user_id(self):
        response = requests.get(f'{self.base_url}/user/{self.username}')
        data = response.json()
        return data['user_id']

    def get_rosters(self, user_id, league_id, draft_id=None):
        if draft_id:
            response = requests.get(f'{self.base_url}/league/{league_id}/rosters/{draft_id}')
        else:
            response = requests.get(f'{self.base_url}/league/{league_id}/rosters')
        rosters = response.json()
        return pd.DataFrame(rosters)


class ValuesScraper:
    def __init__(self, values_url, players_url):
        self.values_url = values_url
        self.players_url = players_url

    def scrape_values(self):
        values_df = pd.read_csv(self.values_url)
        players_df = pd.read_csv(self.players_url)
        return values_df, players_df


def main():
    username = st.text_input('Enter your sleeper username here', 'brochillington')

    api = SleeperAPI(username)
    user_id = api.get_user_id()

    # Fetch startup draft picks
    startup_picks_df = api.get_picks(user_id, league_id, draft_id=startup_draft_id)

    # Fetch rookie draft picks
    rookie_picks_df = api.get_picks(user_id, league_id, draft_id=rookie_draft_id)

    rosters_df = api.get_rosters(user_id, league_id)

    values_scraper = ValuesScraper('https://raw.githubusercontent.com/stranger9977/Sleeper-API-Tools/master/values/values.csv',
                                   'https://raw.githubusercontent.com/stranger9977/Sleeper-API-Tools/master/values/player_urls.csv')
    values_df, players_df = values_scraper.scrape_values()

    # Merge values and players with rosters_df
    rosters_values_df = rosters_df.merge(players_df, left_on='players', right_on='player_id', how='left')
    rosters_values_df = rosters_values_df[['display_name', 'full_name', 'merge_name', 'position', 'team_logo_espn', 'headshot_url']]
    rosters_values_df.dropna(subset=['full_name'], inplace=True)

    # Display rosters_values_df
    st.dataframe(rosters_values_df)


if __name__ == '__main__':
    main()

