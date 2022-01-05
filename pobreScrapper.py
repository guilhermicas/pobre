from seleniumwire import webdriver
from bs4 import BeautifulSoup

from time import sleep
import requests


"""
[start] Menu selection scrapping (no selenium)

This is scraping used to select Series, then season, then episode.
"""


def scrapSeries(query: str):
    """
        Scraps pobre.tv to search series

        @returns List of series (ex: [
            ["Sherlock", "2010", "Comedy, Drama", "https://pobre.tv/tvshows/tt1475582"],
            ["Sherlock2", "2010", "Comedy, Drama", "https://pobre.tv/tvshows/tt1475582"],
            ["Sherlock3", "2010", "Comedy, Drama", "https://pobre.tv/tvshows/tt1475582"]
        ])
    """
    html_doc = requests.get(query).content
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


def scrapSeasons(series_chosen: str):
    """
        Scraps available series from chosen series

        @returns available season's numbers and corresponding links (ex: [["1","https://season_link"], ["2","https://season_link"], ["3","https://season_link"], ["4","https://season_link"]])
    """

    # print(series_chosen)
    series_url = series_chosen[3]

    # Obtaining from html the available seasons
    html_doc = requests.get(series_url).content
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
    html_doc = requests.get(season_chosen_url).content
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
        while(video.get_attribute("duration") != "NaN"):
            sleep(0.3)

        #print("Video src:")
        video_src = video.get_attribute("src")

    else:
        print("No ad found")

    return video_src


def get_episode_stream_url(episode_url):
    firefox_options = webdriver.FirefoxOptions()
    # Dont visually open browser window
    firefox_options.add_argument("--headless")

    firefox_profile = webdriver.FirefoxProfile()
    # Disable image loading
    firefox_profile.set_preference("permissions.default.image", 2)
    # Disable CSS loading
    firefox_profile.set_preference('permissions.default.stylesheet', 2)

    # Driver is basically browser controller
    driver = webdriver.Firefox(
        options=firefox_options, firefox_profile=firefox_profile)

    try:
        driver.get(episode_url)

        clickPrePlayButton(
            driver, "//div[contains(@class,'prePlaybutton')]")

        # Iframe contains that contains the video
        #print("Attempting to find iframe element")
        iframe = waitFindElement(
            driver, "//iframe[@allowfullscreen='true' and @frameborder='0' and @scrolling='no']")

        # Change Iframe to be the "main html document", this enables searching and interacting with items inside it, including the video we want
        driver.switch_to.frame(iframe)

        print("Extracting stream url...")
        stream_url = getLoadedVideoStreamUrl(driver, "//video")

        driver.quit()

        return stream_url

        # If driver is still opened, close all tabs correctly, this prevents redundant disk space allocation not being cleared
    except Exception as e:
        print("Something bad happened")
        print(str(e))

        # If driver is still opened, close all tabs correctly, this prevents redundant disk space allocation not being cleared
        driver.quit()
