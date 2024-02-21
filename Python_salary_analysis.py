"""
Assignment Name: Final Project Webscraper
Tayin Desai
CS 021 / Spring 2023

Program Description: This program is a webscraper that takes data from the website SimplyHired and produces
a horizontal bar graph to represent the data. The program first iterates through a list of free proxies scraped from
a free proxy website. Once a working proxy is found, the script gets and parses the html from SimplyHired, and appends
it to a list.  The data from that list is then used to create a bar graph, including the labels and bar values.


Reference Links:
Matplotlib
https://stackoverflow.com/questions/56638239/matplotlib-horizontal-bar-chart-with-time-in-hoursminutesseconds-on-x-axis
https://matplotlib.org/stable/index.html#matplotlib-release-documentation
https://www.youtube.com/watch?v=9VK8quGFcSE&t=446s

Indeed Scraper
https://www.youtube.com/watch?v=-SjrfjKJqqI&t=362s
https://www.youtube.com/watch?v=uBAaQ1Oif9k&t=5s

Regular Expressions
https://docs.python.org/3/library/re.html

Beautiful Soup
https://beautiful-soup-4.readthedocs.io/en/latest/

"""
import matplotlib.pyplot as plt
import numpy as np
import re
import requests
from bs4 import BeautifulSoup as bs


def get_proxies():
    # get request for free proxies site
    page = requests.get('https://free-proxy-list.net/')
    # parse html
    soup = bs(page.content, 'html.parser')
    # init table data as list - this is where we will store all information from the table
    table_data = []
    # access html from outermost element
    table = soup.find('tbody')
    # iterate over each row in grid
    for row in table:
        # iterate over each data in row
        for td in row:
            # append all data to the list
            table_data.append(str(td))
    # get ports
    ports = table_data[1::8]
    stripped_ports = []
    # iterate over ips
    for port in ports:
        # strip html elements
        stripped_ports.append(port.strip('</td>'))
    # put raw ips into list
    html_ips = table_data[::8]
    # initialize stripped ips
    stripped_ips = []
    # iterate over ips
    for ip in html_ips:
        # strip html elements
        stripped_ips.append(ip.strip('</td>'))

    return stripped_ips, stripped_ports


def get_inputs():
    # get user inputs
    skill = input('Enter your skill: ').strip()
    place = input('Enter your place: ').strip()
    return skill, place


def scrape(ips, ports):
    proxies = []  # initialize proxies as empty list
    data = []  # initialize data as empty list
    # for each ip
    for i in range(len(ips)):
        # proxy = ip concat with port separated by :
        proxy = ips[i] + ":" + ports[i]
        # append each proxy port pair to list
        proxies.append(proxy)

    skill, place = get_inputs()
    # set user agent
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/58.0.3029.110 Safari/537.3'
    }
    # concat url with inputs
    url = 'https://www.simplyhired.com/search?q=' + skill + '&l=' + place
    # iterate over each proxy
    for proxy in proxies:
        try:
            # make a request using proxy
            response = requests.get('https://www.google.com/', headers=headers, proxies={"http": proxy, "https": proxy},
                                    timeout=2)
            # if the request was successful
            if response.status_code == 200:
                # print success message
                print(proxy + " is working!")
                # make request to job search url
                page = requests.get(url)
                # parse html
                soup = bs(page.content, 'html.parser')
                # get job titles
                print(soup)
                titles = soup.findAll(attrs={'data-testid': 'searchSerpJobTitle'})
                # get company names
                companies = soup.findAll(attrs={'data-testid': 'companyName'})
                # get salary information
                salaries = soup.findAll(attrs={'data-testid': 'searchSerpJobSalaryEst'})
                # get job locations
                locations = soup.findAll(attrs={'data-testid': 'searchSerpJobLocation'})
                # iterate over each datum
                for title, company, salary, location in zip(titles, companies, salaries, locations):
                    # get rid of hourly wages
                    if 'hour' not in salary.text:
                        # split the high and low estimates into their own element
                        sal = salary.text.split()
                        # set low estimate as float
                        sal_digit_low = float(re.sub(r'[^\d.]+', '', sal[1]))
                        # set high estimate as float
                        sal_digit_high = float(re.sub(r'[^\d.]+', '', sal[3]))
                        # if the salary is represented in the thousands, get rid of the last 3 0s
                        if sal_digit_high >= 1000:
                            sal_digit_high = float(float(sal_digit_high)/1000)
                        if sal_digit_low >= 1000:
                            sal_digit_low = float(float(sal_digit_low)/1000)
                        # append all the data to the data list in order
                        data.append(title.text)
                        data.append(company.text)
                        data.append(sal_digit_low)
                        data.append(sal_digit_high)
                        data.append(location.text)
                    # tell use that the jobs with hourly wages are not included in summary
                    else:
                        print(f'No salary information for {title.text, company.text}. It was removed from the data')
                return data
        # Handle if the proxy does not connect
        except:
            print(proxy + " missed. Trying again...")  # print fail message


def main():
    ip_list, port_list = get_proxies()  # get proxies
    data = scrape(ip_list, port_list)  # scrape data using working proxy
    company_titles = list(data[1::5])  # set graph variables as lists to be using in graph
    highs = list(data[3::5])
    lows = list(data[2::5])

    # create the figure and axis
    fig, ax = plt.subplots()
    # account for text
    plt.subplots_adjust(left=0.4)
    # set y labels
    y_pos = np.arange(len(company_titles))
    ax.set_yticks(y_pos)
    ax.set_yticklabels(company_titles)
    # set x limits and labels
    ax.set_xlim([0, 150])
    ax.set_xlabel('Salary (Thousands of $USD)')
    # create horizontal bars
    ax.barh(y_pos, highs, color='tab:blue', height=0.4, align='center')
    ax.barh(y_pos - 0.4, lows, color='tab:orange', height=0.4, align='center')
    # add legend
    ax.legend(['High Estimated Salary', 'Low Estimated Salary'], loc='upper right')
    # show graph
    plt.title('Salary Comparison')
    plt.show()


# call main
if __name__ == '__main__':
    main()
