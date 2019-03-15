# import modules
import pandas as pd
from lxml import html
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import requests


class App:
    def __init__(self, teams_path, output_path, cur_year, team):
        self.teamsPath = teams_path
        self.output_path = output_path
        self.cur_year = cur_year
        self.team = team

    def get_recruit_data(self):
        # gecko = os.path.normpath(os.path.join(os.path.dirname(__file__), 'geckodriver'))
        # binary = FirefoxBinary(r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        driver = webdriver.Firefox(capabilities=cap, executable_path="C:\\Users\\bslabach\\PycharmProjects\\RecruitingData\\geckodriver.exe")
        options = Options()
        options.add_argument('--headless')

        driver.get("https://247sports.com/college/"+self.team+"/Season/"+str(self.cur_year)+"-Football/Offers/")
        show_more_xpath = \
            '//*[@id="page-content"]/div[1]/section[2]/section/div/ul/li[@class="ri-page__list-item showmore_blk"]/a'

        for i in driver.find_elements_by_xpath(show_more_xpath):
            i.click()

        recruit_xpath = \
            '//*[@id="page-content"]/div[1]/section[2]/section/div/ul/li[@class="ri-page__list-item"]/div[1]'

        offers_page = driver.page_source
        html_tree = html.fromstring(offers_page)

        offers_list = html_tree.xpath(recruit_xpath)

        list_of_results = [('Recruit Name',
                            '247 Link',
                            'Position',
                            'High School',
                            'Metrics',
                            'Composite Rating',
                            '247 Rating',
                            'Status',
                            'Crystal Ball / %')]

        for element in offers_list:

            # try:
            recruit = element.find('.//a[@href][1]')
            recruit_url = recruit.attrib['href']
            recruit_name = recruit.text
            recruit_rating = element.find('.//span[6]').text
            recruit_hs = element.find('.//div/span[1]').text
            recruit_metrics = element.find('.//div[3]').text
            recruit_pos = element.find('.//div[6]').text
            recruit_status_div = element.find('.//div[5]')[0].tag
            if recruit_status_div == 'a':
                try:
                    recruit_status = element.find('.//div[5]/a[1]/img').get('title')
                except AttributeError:
                    recruit_status = "N/A"
            else:
                try:
                    recruit_status = element.find('.//div[5]/div/span').text
                except AttributeError:
                    recruit_status = element.find('.//div[5]/img').get('title')

            recruit_url_trimmed = "https://"+recruit_url[2:].strip()

            driver2 = webdriver.Firefox(capabilities=cap,
                                        executable_path="C:\\Users\\bslabach\\PycharmProjects\\RecruitingData\\geckodriver.exe",
                                        options=options)
            driver2.get(recruit_url_trimmed)
            tfs_page = driver2.page_source
            tfs_tree = html.fromstring(tfs_page)

            try:
                tfs_rating = tfs_tree.xpath('//*[@id="page-content"]/div[1]/section/header/section[2]/section[1]/ul[@class="tfs-ranking-list"]/li[1]/span[2]/text()')

                if not tfs_rating:
                    tfs_rating = "N/A"
                else:
                    tfs_rating = tfs_rating[0]
            except AttributeError:
                tfs_rating = "N/A"

            try:
                tfs_cb_pick = tfs_tree.xpath('//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/li[2]/span[1]/text()')
                tfs_cb_perc = tfs_tree.xpath('//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/li[2]/span[2]/text()')
                # print(tfs_cb_perc)

                if not tfs_rating:
                    cb_info = "none"
                else:
                    tfs_cb_pick = tfs_cb_pick[0].strip()
                    tfs_cb_perc = tfs_cb_perc[0].strip()

                    cb_info = tfs_cb_pick + " / " + tfs_cb_perc
            except AttributeError:
                cb_info = "none"
            except IndexError:
                cb_info = "none"

            driver2.quit()

            recruit_data = (recruit_name.strip(),
                            recruit_url_trimmed,
                            recruit_pos.strip(),
                            recruit_hs.strip(),
                            recruit_metrics.strip(),
                            recruit_rating.strip(),
                            tfs_rating,
                            recruit_status,
                            cb_info)
            # except:
            #     recruit_data = ("This",
            #                     "is",
            #                     "an",
            #                     "imaginary",
            #                     "recruit.",
            #                     "Go",
            #                     # "",
            #                     "Hazell!")

            print(recruit_data)

            list_of_results.append(recruit_data)

            df = pd.DataFrame(list_of_results)
            df.to_csv(self.output_path, index=False, header=False)

        print(list_of_results)
        driver.quit()


def main():
    # now = datetime.datetime.now()
    # year = now.year
    year = 2020
    team = "purdue"
    output_file = "lib/output-"+team+"-"+str(year)+".csv"

    a = App("lib/teams-fbs.json", output_file, year, team)

    a.get_recruit_data()


if __name__ == "__main__":
    main()
