#!/bin/python3

from pobreScrapper import *
from ui import *
import os


def main():

    # TODO: submodularize to support movies and anime from site
    # Search Series Loop
    while(True):

        os.system("clear")
        # TODO: Reactivate user input and correct search_url formatting
        # Getting search input
        search_query = input("Série: ")

        search_url = f"https://pobre.tv/tvshows?search={search_query}"
        #search_url = "https://pobre.tv/tvshows?search=sherlock"

        # Obtaining search results
        series_found = scrapSeries(search_url)

        if not series_found:
            input("Nenhum resultado encontrado, prima Enter para continuar...")
            continue

        print("Séries encontradas:")
        # Choosing a series menu
        series_chosen = chooseMenu(series_found)

        # URL from the chosen series
        series_url = series_chosen[3]

        # Search Seasons (use series name and metadata just for UX on the top of the search, visual purposes only, use link to do the webscraping)
        seasons_found = scrapSeasons(series_chosen)

        os.system("clear")
        print(f"Série: {series_chosen[0]}")
        print("Temporadas encontradas:")
        # Choosing season from the chosen series
        season_chosen = chooseMenu(seasons_found, indexed=False)

        # Season URL to scrape episodes (ex: https://pobre.tv/tvshows/tt1475582/season/2/)
        season_chosen_url = f"{series_url}/season/{season_chosen}"

        # Search Season's available episodes
        episodes_found = scrapEpisodes(season_chosen_url)

        os.system("clear")
        print(f"Série: {series_chosen[0]} Temporada {season_chosen}")
        print("Episódios encontrados:")
        # Choose Episode to watch
        episode_chosen = chooseMenu(episodes_found)
        # TODO: when choosing on menu, dont show Episode's ID
        # print(episode_chosen)
        episode_id = episode_chosen[0]

        # Link to extract the stream URL
        stream_extract_url = f"{season_chosen_url}/episode/{episode_id}"

        print("Getting stream url...")
        stream_url = get_episode_stream_url(stream_extract_url)
        # TODO: For now starting vlc with os.system, in the future have proper vlc implementation and detect if closed to open menu
        os.system(f"vlc {stream_url}")

        # VLC stream
        # if VLC dies, show menu (see diagram)

        exit(0)


if __name__ == "__main__":
    main()
