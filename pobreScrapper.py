from seleniumwire import webdriver
from bs4 import BeautifulSoup

from time import sleep
import requests

from sys import platform
from pathlib import Path

import re

"""
[start] Menu selection scrapping (no selenium)

This is scraping used to select Series, then season, then episode.
"""


def safeGETrequest(query: str):
    """
        A GET request that returns True if successfull (200+) or False if not
    """
    request = requests.get(query)

    if(request.status_code >= 200 and request.status_code <= 299):
        return request.content
    else:
        print(
            f"Pobre.tv está down provavelmente. Status code = {request.status_code}")
        raise Exception


def scrapSeries(query: str):
    """
        Scraps pobre.tv to search series

        @returns List of series (ex: [
            ["Sherlock", "2010", "Comedy, Drama", "https://pobre.tv/tvshows/tt1475582"],
            ["Sherlock2", "2010", "Comedy, Drama", "https://pobre.tv/tvshows/tt1475582"],
            ["Sherlock3", "2010", "Comedy, Drama", "https://pobre.tv/tvshows/tt1475582"]
        ])
    """
    html_doc = safeGETrequest(query)

    soup = BeautifulSoup(html_doc, "html.parser")

    # Obtaining from html markup the search result's titles and years
    html_results = soup.find('div', attrs={'class': 'listing'}).find_all('a')

    results = []
    for result in html_results:
        # Organized search results
        title = result.find("span").text
        year = result.find("div", attrs={"class": "y"}).text
        category = result.find("div", attrs={"class": "c"}).text
        href = result["href"]

        results.append([title, year, category, href])

    return results


def scrapSeasons(series_url: str):
    """
        Scraps available series from chosen series

        @returns available season's numbers and corresponding links (ex: [["1","https://season_link"], ["2","https://season_link"], ["3","https://season_link"], ["4","https://season_link"]])
    """

    # Obtaining from html the available seasons
    html_doc = safeGETrequest(series_url)

    soup = BeautifulSoup(html_doc, "html.parser")

    seasons_available = soup.find(id="seasonsList").text.split(" ")

    # removing spaces from list
    seasons_available = [season for season in seasons_available if season]

    return seasons_available


def scrapEpisodes(season_chosen_url: str):
    """
        Scraps available episodes from chosen season

        @returns List containing episode's ids and corresponding titles (ex: [["0", "Unaired Pilot"], ["1","Um Estudo em Rosa"], ["2","O banqueiro Cego"]])
                 Using episodes Ids because its more correct that using list index, because episode id is more correct when communicating with API
                 For example in the above example, the first episode has id 0, but that is because it is a special episode, an unaired one, and its registered in the API as ID 0
                 In other shows, the first episode has usually id 1
                 So to be more correct, we extract episode id from the page, instead from list index

                 Title is used for visual purposes
    """

    # Obtaining from html the available seasons
    html_doc = safeGETrequest(season_chosen_url)

    soup = BeautifulSoup(html_doc, "html.parser")

    episodes_links = soup.find(
        "div", attrs={"id": "episodesList"}).find_all("a")

    episodes_data = []
    for episode_link in episodes_links:

        episode_id = episode_link.find(
            "div", {"data-episode-number": True})["data-episode-number"]

        episode_title = episode_link.find("div", {"class": "title"}).text

        episodes_data.append([episode_id, episode_title])

    return episodes_data


"""
[end] Menu selection scrapping (no selenium)

[start] Stream video link scrapping (selenium)

This scraping is used to get the video stream link
It uses selenium because it uses dinamic javascript on the website
and to get the video stream you have to jump through some loops.
"""


def waitFindElement(driver, xpath: str):
    """
        @brief Wait until element is found/loaded using xpath and return it

        @return Element wanted
    """
    while True:
        sleep(0.4)
        try:
            # TODO: Timeout if it doesnt find element in X amount of time
            # print(xpath)
            element = driver.find_element_by_xpath(xpath)
            #print(f"Element {element.get_attribute('tagName')} found")
            return element
        except Exception as e:
            # print(e)
            continue


def close_popups(driver):
    """
    @brief closes tabs that were opened while clicking the pre play button
    """
    #print("Closing pop ups")

    main_window = driver.window_handles[0]

    for tab in driver.window_handles:
        if tab != main_window:
            driver.switch_to.window(tab)
            driver.close()

    driver.switch_to.window(main_window)


def clickPrePlayButton(driver, btn_xpath):
    """
        @brief Clicks pre play button until new tabs stop opening

        @params
            @driver <- browser
            @btn_xpath <- string to find the button, since the site can update, this way it is more practical to update

        pre play button is a fake video player button that is used for pop up ads,
        after ads pass and the button is clicked
        the video stream will start playing (could be ad or actual vid stream)

        After clicking popping up all the ads, it will close all pop ups
    """
    #print("Clicking pre play button until ads stop popping up")

    prePlaybutton = waitFindElement(driver, btn_xpath)

    # Initial tab quantity
    prev_tab_count = len(driver.window_handles)

    while True:
        # button click
        driver.execute_script("arguments[0].click();", prePlaybutton)

        # clicking until tab quantity stops going up
        tab_qtd = len(driver.window_handles)
        if(tab_qtd > prev_tab_count):
            prev_tab_count = tab_qtd
        else:
            break

    close_popups(driver)


def skipVideoAd(driver, video_element):
    print("Starting ad skip...")

    print("Waiting for ad to load...")
    video_duration = video_element.get_attribute("duration")
    while video_duration == "NaN":
        video_duration = video_element.get_attribute("duration")
        sleep(0.8)

    print("Actually skipping ad")
    #print("Current video time (should be 0) = " + video_element.get_attribute("currentTime"))
    driver.execute_script("""
    video = document.getElementsByTagName('video')[0];
    video.currentTime = video.duration;
    """)
    #print("Current video time (should be 15+-) = " + video_element.get_attribute("currentTime"))

    if(video_element.get_attribute("currentTime") == video_duration):
        print("Ad skipped successfully")
    else:
        print("Unable to skip ad, raising exception for now, maybe later retry the whole algorithm idk")
        raise Exception
        # return False


def getLoadedVideoStreamUrl(driver, video_xpath):
    # TODO: Very slow but works, find a way to click on page because it loads the ad instantly, this works for now tho
    print("Waiting to get video")
    video_element = waitFindElement(driver, video_xpath)

    video_src = video_element.get_attribute("src")
    while not video_src:
        video_src = video_element.get_attribute("src")

    # Problably ad
    if("pobre.tv" in video_src or "BT.mp4" in video_src):
        print("Ad found")
        skipVideoAd(driver, video_element)

        # If video duration becomes NaN, it means that the actual series video as loaded but hasnt been started (no need to start it, just need to
        #                                                                                                       detect when its loaded to extract
        #                                                                                                       src.
        while(video_element.get_attribute("duration") != "NaN"):
            sleep(0.3)

        #print("Video src:")
        video_src = video_element.get_attribute("src")

    else:
        print("No ad found")

    return video_src


def getSubtitles(driver):
    print("Extracting subtitles...")
    try:
        for i in range(5):
            sleep(0.4)

            srt_file = re.search("[\"\'].*\.srt[\"\']",
                                 driver.page_source)

            if srt_file:
                print("Subtitles found: ")
                return srt_file.group(0)  # group(0) extracts matched string

        # TODO: find subtitles through tracker tag if the above doesnt work
        return None

    except Exception as e:
        print("No subtitles found...")
        print("Exception message: " + str(e))
        return None

def obtainBrowserDriver():
    """
    @brief  Tenta usar o chrome ou o firefox como browser driver e devolve o que tiver sucesso
    @returns driver
    TODO: maybe store a cache of the browser that has previously worked instead of always looping through the array and failing possibly
    """
    implemented_browsers = ["firefox","chrome"]
    for implemented_browser in implemented_browsers:
        print("attempting to use " + implemented_browser)
        if(implemented_browser == "chrome"):
            # TODO:Retirar o headless e ver se o css/GET da pagina esta mesmo otimizado e se ha coisas que se podem desativar que estao a ocupar muita velocidade de processamento/net
            chrome_options = webdriver.ChromeOptions()

            # This should optimize speed
            prefs = {'profile.default_content_setting_values': {'images': 2, 
                                'plugins': 2, 'geolocation': 2,
                                'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
                                'mouselock': 2, 
                                'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2,
                                'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2,
                                'push_messaging': 2,  'metro_switch_to_desktop': 2,
                                'app_banner': 2, 'site_engagement': 2,
                                }}
            chrome_options.add_experimental_option('prefs', prefs)
            chrome_options.add_argument("disable-infobars")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("window-size=100,100")


            # Dont visually open browser window
            #chrome_options.add_argument("--headless")

            # Creating and returning the browser driver
            if platform == "win32":
                # If on windows TODO: em todos os sistemas operativos, detetar se o user fez download do driver, se nao, automaticamente buscar o driver da net e por na pasta. assim fica com o atualizado no momento que faz o push, em vez de ter um driver antigo ja commited no projeto
                return webdriver.Chrome(chrome_options=chrome_options, executable_path=str(Path(Path(__file__).parent.resolve()))+r'\BrowserDrivers\chromedriver.exe')
                
            else:
                # If on linux and should work on mac
                return webdriver.Chrome(chrome_options=chrome_options)
        elif(implemented_browser == "firefox"):

            #TODO: in all browsers, if captcha is detected, open the browser for user completion or have solution to the captcha problem
            firefox_options = webdriver.FirefoxOptions()
            # Dont visually open browser window
            firefox_options.add_argument("--headless")

            firefox_profile = webdriver.FirefoxProfile()

            # Disable image loading
            firefox_profile.set_preference("permissions.default.image", 2)

            # Options that should help
            firefox_profile.set_preference(
                "browser.helperApps.deleteTempFileOnExit", True)
            firefox_profile.set_preference("reader.parse-on-load.enabled", False)
            firefox_profile.set_preference(
                "browser.display.show_image_placeholders", False)
            firefox_profile.set_preference(
                "browser.display.use_document_colors", False)
            firefox_profile.set_preference("browser.display.use_document_fonts", 0)

            # TODO: Disable CSS

            # Driver is basically browser controller
            if platform == "win32":
                # If on windows
                return webdriver.Firefox( options=firefox_options, firefox_profile=firefox_profile, executable_path=str(Path(Path(__file__).parent.resolve()))+r"\BrowserDrivers\geckodriver.exe")
            else:
                # If on linux
                return webdriver.Firefox( options=firefox_options, firefox_profile=firefox_profile, log_path='/dev/null')

def get_episode_stream_url(episode_url):
    """
        Gets stream url and subtitle url if available
    """

    # Automaticamente tenta usar o chrome, se falhar tenta com firefox
    driver = obtainBrowserDriver()

    try:
        print("Getting stream url and subtitle url... (permitir até 1 minuto)")
        driver.get(episode_url)
        driver.minimize_window()

        # Only continue if request was successfull
        for request in driver.requests:
            if request.response:
                status_code = request.response.status_code
                if request.url == episode_url:
                    if status_code < 200 or status_code >= 300:
                        print(
                            "O site provavelmente não está ativo. Tente novamente mais tarde ou contacte desenvolvedor. Status code = "+status_code)
                        return False
                    else:
                        break

        clickPrePlayButton(
            driver, "//div[contains(@class,'prePlaybutton')]")

        # Iframe contains that contains the video
        #print("Attempting to find iframe element")
        iframe = waitFindElement(
            driver, "//iframe[@allowfullscreen='true' and @frameborder='0' and @scrolling='no']")

        # Change Iframe to be the "main html document", this enables searching and interacting with items inside it, including the video we want
        driver.switch_to.frame(iframe)

        subtitle_url = getSubtitles(driver)
        print(subtitle_url)

        print("Extracting stream url...")
        stream_url = getLoadedVideoStreamUrl(driver, "//video")

        # If driver is still opened, close all tabs correctly, this prevents redundant disk space allocation not being cleared
        driver.quit()

        return [stream_url, subtitle_url]

    except Exception as e:
        print("Something bad happened")
        print(str(e))

        # If driver is still opened, close all tabs correctly, this prevents redundant disk space allocation not being cleared
        driver.quit()
        return False
