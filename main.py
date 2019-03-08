# core modules

# other modules
import pandas as pd
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class App:
    def __init__(self, teams_path, output_path, cur_year, team):
        self.teamsPath = teams_path
        self.output_path = output_path
        self.cur_year = cur_year
        self.team = team

    def get_recruit_data(self):
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        driver = webdriver.Firefox(capabilities=cap, executable_path="C:\\Users\\bslabach\\PycharmProjects\\RecruitingData\\geckodriver.exe")
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
                            'Status')]

        for element in offers_list:

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
                recruit_status = element.find('.//div[5]/div/span').text

            recruit_data = (recruit_name.strip(),
                            recruit_url[2:].strip(),
                            recruit_pos.strip(),
                            recruit_hs.strip(),
                            recruit_metrics.strip(),
                            recruit_rating.strip(),
                            recruit_status)

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

    a = App("lib/teams-fbs.json", "lib/output.csv", year, team)
    a.get_recruit_data()


if __name__ == "__main__":
    main()
