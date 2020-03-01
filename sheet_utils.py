from googleapiclient.discovery import build
from google.oauth2 import service_account

SERVICE_ACCOUNT_FILE = 'drive-scraping-f784fb17e899.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1ktaU3bGXfJYGeDxreaNMPbEykoI2KIiFJKZpaISs6ws'

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,
                                                              scopes=SCOPES)

service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()

def add_sheet(sheet_name):
    req_body = {
        'requests': [ {
            'addSheet': {
                'properties': {
                    'title': sheet_name
                }
            }
        }]
    }
    
    req = sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=req_body)
    req.execute()


def fill_sheet(sheet_name, values):
    data = [{'range': sheet_name,
             'values': values},
        # Additional ranges to update ...
    ]
    
    req_body = {
        'valueInputOption': 'USER_ENTERED',
        'data': data
    }
    
    res = service.spreadsheets().values().batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body=req_body).execute()
    
    return res.get('totalUpdatedCells')


def delete_sheet(sheet_id):
    req_body = {
        'requests': [ {
            'deleteSheet': {
                'sheetId': sheet_id
            }
        }]
    } 
    
    req = sheet.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=req_body)
    req.execute()


def get_sheet_ids():
    request = sheet.get(spreadsheetId=SPREADSHEET_ID, includeGridData=False)
    response = request.execute()
    
    ids = [s['properties']['sheetId'] for s in response['sheets'] ]
    # Return all sheets ids except for the first sheet
    return ids[1:]


