# this is a class that pulls data from the "Battery System Components Spreadsheet" and constructs cells and other system components as necessary

import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

class systemConstruction:
	def __init__(self,name):
		self.user = name
		# do the authenticating here?
		scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
		creds = ServiceAccountCredentials.from_json_keyfile_name("testSheets-62f6c09b9d0d.json", scope)

		gc = gspread.authorize(creds)
		wks = gc.open("sample sheet").sheet1
		data = wks.get_all_values()
		headers = data.pop(0)
		df = pd.DataFrame(data, columns=headers)

	def importParameter(self, system, component, subcomponent):
		sheet = service.spreadsheets()
		result = sheet.values().get(spreadsheetId=spreadsheetID,range="Sheet1!A1:C6").execute()
		values = result.get('values', [])

	def buildCell(self):
		# this will construct a cell based on the parameters specified in the spreadsheet
		# can then use it to estimate cell costs
		print('hello world')

	def buildBatteryModule(self):
		# this will construct modules based on specified technologies
		print('hello world')


	def buildRack(self):
		# this will construct the rack based on the module details and the specified system techs
		print('hello world')


	def buildSystem(self):
		# this will construct the overall system based on the racks specified, and other balance of system components
		print('hello world')
