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

        # Searching Series
        search_query = input("Série: ")
        search_url = f"https://www1.pobre.tv/tvshows?search={search_query}"

        # Obtaining search results
        series_found = scrapSeries(search_url)

        if not series_found:
            input("Nenhum resultado encontrado, prima Enter para continuar...")
            continue

        # Choosing a series, index 3 is series URL no need to show
        series_chosen = chooseMenu(
            series_found, hideIndex=[3],
            headers={
                "Séries encontradas": ""
            }
        )

        series_url = series_chosen[3]  # URL from the chosen series

        # Search Seasons (use series name and metadata just for UX on the top of the search, visual purposes only, use link to do the webscraping)
        seasons_found = scrapSeasons(series_chosen)

        # Choosing season from the chosen series
        season_chosen = chooseMenu(
            seasons_found, indexed=False, horizontal=True,
            headers={
                "Série": series_chosen[0],
                "Temporadas encontradas": ""
            }
        )

        # Search Season's available episodes (ex: https://pobre.tv/tvshows/tt1475582/season/2/))
        episodes_found = scrapEpisodes(f"{series_url}/season/{season_chosen}")

        # Choose Episode to watch
        episode_chosen = chooseMenu(
            episodes_found, hideIndex=[0],
            headers={
                "Série": series_chosen[0],
                "Temporada": season_chosen,
                "Episódios encontrados": ""
            }
        )

        episode_id = episode_chosen[0]

        print("Getting stream url and subtitle url... (permitir até 1 minuto)")
        stream_url, subtitle_url = get_episode_stream_url(
            f"{season_chosen_url}/episode/{episode_id}")  # Link to extract the stream URL

        # TODO:Migrate this to get_episode_stream_url and raise custom exception maybe
        if not stream_url:
            print("Não foi possivel buscar o URL da stream.")
            exit(1)

        # TODO: Download subtitle to tmp file and delete after vlc dies

        print(f"Stream url: {stream_url}")
        # Play VLC stream, os.system stops program execution until VLC closes.
        execute_OS_command(
            "vlc", r'"C:\Program\ Files\VideoLAN\VLC\vlc.exe"', [stream_url])
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
