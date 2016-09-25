"""
This file is to scrap the sector change data from Google Finance.
The final output contains the following info:

1. The sector name
2. The percentage change in sector value
3. The biggest gainer and the percentage change in the biggest gainer 
4. The biggest loser and the percentage change in the biggest loser

Output is in the format of json.
"""

url = r'https://www.google.com/finance'

def get_sectors(original_url):
	'This function returns the list of [sector_name, sector_detail_url, sector_change] for all sectors'
	# get raw data
	import requests
	from bs4 import BeautifulSoup
	response = requests.get(original_url)
	page_soup = BeautifulSoup(response.content,'lxml')
	page_data = page_soup.find('div',{'id':'secperf'})
	list_of_name_url = []
	# get name and url for all sectors
	for tag in page_data.find_all('a'):
		name = tag.text
		url = r'https://www.google.com/' + tag.get('href')
		name_and_url = []
		name_and_url.append(name)
		name_and_url.append(url)
		list_of_name_url.append(name_and_url)
	rates = []
	# get percentage change for all sectors
	for tag in page_data.find_all('span'):
		rates.append(float(tag.text.strip("(%)")))
	# combine name, url and change
	for i in range(len(rates)):
		list_of_name_url[i].append(rates[i])
	return list_of_name_url

def get_little_info(tag):
	"Get the tag name and find the data in the tag. Put them into a certain format"
	name = tag.find('a').text
	rate = float(tag.find_all('span')[1].text.strip("(%)"))
	return_dic = {'change':rate,'equity':name}
	return return_dic

def get_detail_info(list_of_urls):
	"Get the list returned from get_sectors, get the detail info of these sectors and put them into a dictionary."
	import requests
	from bs4 import BeautifulSoup
	all_data = {}
	for page_info in list_of_urls:
		sec_info = {}
		name = page_info[0]
		url = page_info[1]
		rates = page_info[2]
		# get the raw data
		response = requests.get(url)
		page_soup = BeautifulSoup(response.content,'lxml')
		# find the table containing required data
		table_data = page_soup.find('table',{'class':'topmovers'})
		# find all rows
		all_rows = table_data.find_all('tr')
		# find specific stocks and put the data into certain format
		sec_info["biggest_gainer"] = get_little_info(all_rows[1])
		sec_info["biggest_loser"] = get_little_info(all_rows[7])
		sec_info["change"] = rates
		all_data[name] = sec_info
	return all_data

def conclusion(url):
	"Conclude the data into the final format. This is the only function that should be called from the outside world."
	import json
	return_data = {}
	try:
		list_of_name_url = get_sectors(url)
		all_data = get_detail_info(list_of_name_url)
		return_data["status"] = "GOOD"
		return_data["result"] = all_data
	# status is "BAD" if it failed for any reason.
	except:
		return_data["status"] = "BAD"
	return json.dumps(return_data)

print(conclusion(url))

