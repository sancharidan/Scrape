# import dependencies
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import pandas as pd
import argparse


###-----Parameters - input from user----###
parser = argparse.ArgumentParser()
parser.add_argument('--WAIT_TIME', default = 15, type = int, help = 'Specify time in seconds to wait for loading new pages')
parser.add_argument('--CHROMEDRIVER_PATH',  default = "./chromedriver", help = 'Path to chromedriver executable')
parser.add_argument('--OUTPUT_PATH',  default = "./SIS_Faculty_Data.csv", help = 'Output filepath')

# parse input arguments
inP = parser.parse_args()
WAIT_TIME = inP.WAIT_TIME # specify number of seconds to wait for a page to load completely
CHROMEDRIVER_PATH = inP.CHROMEDRIVER_PATH # path to chromedriver executable
OUTPUT_PATH = inP.OUTPUT_PATH # path to output file for storing scraped data in csv format

###----Start Scraping using Selenium and BeautifulSoup----###

faculty_data = [] # initialize list to store scraped information

# initialise webdriver and communicate with url
try:
    url_prefix = "https://sis.smu.edu.sg"
    url = "https://sis.smu.edu.sg/faculty##region-page-top"
#     driver = webdriver.Chrome('./chromedriver')
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.implicitly_wait(30)
    driver.get(url)
except Exception as e:
    pass

# run while loop till 'Next' page element is not found
while True:
    
    # initialize BeautifulSoup object for parsing html
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # find profile section to parse required information
    div_profile_right = soup.find_all('div', {'class':'profile-right'})

    try:
        for profile in div_profile_right:

            # parsing faculty page url suffix and faculty name
            title = profile.find_all('h3', {'class':'title'})
            h3 = title[0].find('a')
            url_suffix = h3['href']
            name = h3.contents[0]

            # parsing field designation
            desig = profile.find_all('div', {'class':'field designation ng-binding'})[0]
            designation = [d.strip() for d in desig.contents if str(d)!='<br/>']

            # parsing field qualifications
            quali = profile.find_all('div', {'class':'field qualifications ng-binding'})
            qualification = ''
            if quali:
                qualification = [q.strip() for q in quali[0].contents][0]

            # parsing research areas
            div = profile.find_all('div', {'class':'itemTree ng-binding'})[0]
            ul = div.find_all('ul', {'class' : 'term'})[0]
            a = div.find_all('a')
            research_areas = [c.contents[0].strip() for c in a]
            faculty_data.append({'Profile Link':url_prefix+url_suffix, 'Name':name, \
                                 'Designation':designation, 'Qualification':qualification, \
                                 'Research Areas':research_areas})
        
        # Find and click Next button
        button = driver.find_element_by_partial_link_text('Next')
        driver.execute_script("arguments[0].click()", button)
        # wait for 't' seconds for new page to load completely
        time.sleep(WAIT_TIME)
    
    # handle exception occuring at last page when 'Next' button isn't available
    except NoSuchElementException as e:
        print ('End of all pages!')
        break
    # handle all other exceptions
    except Exception as e:
        print ('Exception occured',e)
        continue

# move data to a dataframe and store in csv
faculty_df = pd.DataFrame(faculty_data)
faculty_df.to_csv(OUTPUT_PATH, index = False)

# free memory
del faculty_df, faculty_data
driver.quit()