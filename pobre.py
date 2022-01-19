#!/bin/python3

from pobreScrapper import *
from ui import *
import os

# Dominio que funciona agora
DOMAIN = "www1.pobre.tv"


def main():

    # TODO: Handle Exceptions correctly by creating custom exceptions
    # TODO: submodularize to support movies and anime from site
    # Search Series Loop
    while(True):

        execute_OS_command("clear", "cls")

        # Searching Series
        search_query = input("Série: ")
        search_url = f"https://{DOMAIN}/tvshows?search={search_query}"

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

        season_chosen_url = f"{series_url}/season/{season_chosen}"
        # Search Season's available episodes (ex: https://pobre.tv/tvshows/tt1475582/season/2/))
        episodes_found = scrapEpisodes(season_chosen_url)

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

        # Obtaining stream and subtitle URLs
        stream_url, subtitle_url = get_episode_stream_url(
            f"{season_chosen_url}/episode/{episode_id}")  # Link to extract the stream URL

        if not stream_url:
            print("Não foi possivel buscar o URL da stream.")
            exit(1)

        print(f"Stream url: {stream_url}")
        if subtitle_url:
            print(f"Subtitle url: {subtitle_url}")
            # TODO: Download subtitle to tmp file and delete after vlc dies
            execute_OS_command(
                "vlc", r'"C:\Program\ Files\VideoLAN\VLC\vlc.exe"', [stream_url])
        else:
            print(
                "Não foi possivel extrair os subtitulos, continuando com a visualização da stream á mesma.")
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
