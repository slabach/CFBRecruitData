# import modules
import pandas as pd
from lxml import html
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fuzzywuzzy import fuzz


class App:
    def __init__(self, output_path, cur_year, team):
        self.output_path = output_path
        self.cur_year = cur_year
        self.team = team

    def get_recruit_data(self):

        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Firefox(capabilities=cap,
                                   executable_path="C:\\Users\\bslabach\\PycharmProjects\\RecruitingData\\geckodriver.exe",
                                   options=options)

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
                            'Position',
                            'High School',
                            'Metrics',
                            'Composite Rating',
                            '247 Rating',
                            'Rivals Rating',
                            'Status',
                            'Crystal Ball: Pick / %',
                            '247 Link')]

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
                tfs_cb_list_type = tfs_tree.xpath(
                    '//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/@class')

                # print(tfs_cb_list_type[0])

                if tfs_cb_list_type[0] == 'prediction-list long':
                    tfs_cb_pick = tfs_tree.xpath(
                        '//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/li[1]/span[1]/text()')
                    tfs_cb_perc = tfs_tree.xpath(
                        '//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/li[1]/span[2]/text()')
                else:
                    tfs_cb_pick = tfs_tree.xpath(
                        '//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/li[2]/span[1]/text()')
                    tfs_cb_perc = tfs_tree.xpath(
                        '//*[@id="page-content"]/div[1]/section/header/section[2]/section[2]/ul[1]/li[2]/span[2]/text()')

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

            rivals_search_url = 'https://n.rivals.com/search'
            driver3 = webdriver.Firefox(capabilities=cap,
                                        executable_path="C:\\Users\\bslabach\\PycharmProjects\\RecruitingData\\geckodriver.exe",
                                        options=options)
            driver3.get(rivals_search_url)

            editor = WebDriverWait(driver3, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="search_query"]')))
            editor.send_keys(recruit_name.strip())
            editor.submit()

            WebDriverWait(driver3, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="content_"]')))

            rvls_fname = driver3.find_element_by_css_selector('div.first-name.ng-binding').text
            rvls_lname = driver3.find_element_by_css_selector('div.last-name.ng-binding').text
            rvls_name = rvls_fname + " " + rvls_lname
            rvls_year = driver3.find_element_by_css_selector('td.year > span.pos.ng-binding.ng-scope').text

            diff_ratio = fuzz.token_sort_ratio(rvls_name, recruit_name.strip())

            # print(f"{rvls_fname} {rvls_lname}, {rvls_year}, {rvls_rating}")
            print(f"{diff_ratio}, {rvls_year}")

            if (diff_ratio >= 85) and (rvls_year.strip() == str(self.cur_year)):
                rvls_rating = driver3.find_element_by_css_selector('td.rating > span.pos.ng-binding.ng-scope').text

                if not rvls_rating:
                    rvls_rating = "N/A"
            else:
                rvls_rating = "Look up manually"

            driver3.quit()

            recruit_data = (recruit_name.strip(),
                            recruit_pos.strip(),
                            recruit_hs.strip(),
                            recruit_metrics.strip(),
                            recruit_rating.strip(),
                            tfs_rating,
                            rvls_rating,
                            recruit_status,
                            cb_info,
                            recruit_url_trimmed)

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

    a = App(output_file, year, team)

    a.get_recruit_data()


if __name__ == "__main__":
    main()
