#!/bin/python3

from pobreScrapper import *
from ui import *
import os


def main():

    # TODO: Handle Exceptions correctly by creating custom exceptions
    # TODO: submodularize to support movies and anime from site
    # Search Series Loop
    while(True):

        execute_OS_command("clear", "cls")
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

        execute_OS_command("clear", "cls")
        print(f"Série: {series_chosen[0]}")
        print("Temporadas encontradas:")
        # Choosing season from the chosen series
        season_chosen = chooseMenu(seasons_found, indexed=False)

        # Season URL to scrape episodes (ex: https://pobre.tv/tvshows/tt1475582/season/2/)
        season_chosen_url = f"{series_url}/season/{season_chosen}"

        # Search Season's available episodes
        episodes_found = scrapEpisodes(season_chosen_url)

        execute_OS_command("clear", "cls")
        print(f"Série: {series_chosen[0]} Temporada {season_chosen}")
        print("Episódios encontrados:")
        # Choose Episode to watch
        episode_chosen = chooseMenu(episodes_found)
        # TODO: when choosing on menu, dont show Episode's ID
        # print(episode_chosen)
        episode_id = episode_chosen[0]

        # Link to extract the stream URL
        stream_extract_url = f"{season_chosen_url}/episode/{episode_id}"

        print("Getting stream url... (permitir até 1 minuto)")
        stream_url = get_episode_stream_url(stream_extract_url)

        # TODO:Migrate this to get_episode_stream_url and raise custom exception maybe
        if not stream_url:
            print("Não foi possivel buscar o URL da stream.")
            exit(1)

        print(f"Stream url: {stream_url}")
        # Play VLC stream, os.system stops program execution until VLC closes.
        execute_OS_command(
            "vlc", r"C:\Program Files\VideoLAN\VLC\vlc.exe", [stream_url])
        #os.system(f"vlc {stream_url}")
        #print("Pseudo menu")
        #print("[p] proximo episodio")
        #print("[a] episodio anterior")
        #print("[s] sair")

        # VLC stream
        # if VLC dies, show menu (see diagram)

        exit(0)


if __name__ == "__main__":
    main()
