import pandas as pd
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from googleapiclient import discovery
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pickle

def get_values(tab: str, spreadsheet_id: str, cells: str):
    '''Returns a specific range of values from a given spreadsheet

    Parameters
    ----------
    tab: The sheet tab that the function gets values from
    spreadsheet_id: The spreadsheet id in the sheet URL
    cells: The cell range to be returned
    '''
    scope = ['https://www.googleapis.com/auth/spreadsheets']
    SERVICE_ACCOUNT_FILE = 'FILE' #service account file here
    global values_input, service
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope)
    service = discovery.build('sheets', 'v4', credentials=creds)

    range_ = tab+"!"+cells

    sheet = service.spreadsheets()
    result_input = sheet.values().get(spreadsheetId=spreadsheet_id,
                                      range=range_).execute()
    values_input = result_input.get('values', [])

    if not values_input:
        print('No data found.')

    return values_input

class StatError(Exception):
    pass

def write_to_sheet(stage: str, mod: str, mapper: str, artist: str, sr: str, bpm: str, length: str, cs: str, ar: str, od: str, dl: str, status: str):
    '''For submitting/claiming beatmaps, it writes all the given strings for map stats into the spreadsheet and color codes the cells based on the stage, status, and mod values 

    Parameters
    ----------
    stage: The round that the map is going to be used
    mod: The mod the map is being mapped for
    mapper: The mapper submitting the map
    artist: The artist of the song that is being mapped
    sr: The star rating of the submitted map
    bpm: The BPM of the song
    length: How long the song lasts for
    cs: The circle size of the map
    ar: The approach rate of the map
    od: The overall difficulty of the map
    dl: The download link for the map
    status: The current status/progress of the map
    '''
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'FILE' #service account file here
    global values_input, service
    gs = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope)
    service = discovery.build('sheets', 'v4', credentials=creds)
    sheet = gs.open("SHEETNAME")
    worksheet = sheet.worksheet("WORKSHEET")
    sheet_id = 'SHEETID' #Sheet id here
    gid = 'GID' #Sheet gid here



    index = 4
    cell = worksheet.acell('C'+str(index)).value
    stattRed = 0
    stattGreen = 0
    stattBlue = 0
    statbRed = 0
    statbGreen = 0
    statbBlue = 0
    bgRed = 0
    bgGreen = 0
    bgBlue = 0
    txtRed = 0
    txtGreen = 0
    txtBlue = 0
    modRed = 0
    modGreen = 0
    modBlue = 0

    while cell != None: #Determine row to write on based on the first row without any values
        index = index+1
        cell = worksheet.acell('C' + str(index)).value
    if status == 'wip': #Cell/text colors based on the status, mod, and stage
        stattRed = 180
        stattGreen = 180
        stattBlue = 0
        statbRed = 210
        statbGreen = 210
        statbBlue = 0
    if status == 'planning':
        stattRed = 159/255
        stattGreen = 38/255
        stattBlue = 50/255
        statbRed = 209/255
        statbGreen = 118/255
        statbBlue = 130/255
    if mod[:2] == 'NM':
        modRed = 65/255
        modGreen = 132/255
        modBlue = 245/255
    if mod[:2] == 'HD':
        modRed = 210/255
        modGreen = 210/255
        modBlue = 0/255
    if mod[:2] == 'HR':
        modRed = 189/255
        modGreen = 78/255
        modBlue = 90/255
    if mod[:2] == 'DT':
        modRed = 105/255
        modGreen = 0/255
        modBlue = 226/255
    if mod[:2] == 'FM':
        modRed = 98/255
        modGreen = 0/255
        modBlue = 98/255
    if mod[:2] == 'TB':
        modRed = 0/255
        modGreen = 88/255
        modBlue = 120/255
    if stage == 'TBD':
        bgRed = 90/255
        bgGreen = 90/255
        bgBlue = 90/255
        txtRed = 0/255
        txtGreen = 0/255
        txtBlue =  0/255
    if stage == 'QL':
        bgRed = 20/255
        bgGreen = 100/255
        bgBlue = 200/255
        txtRed = 10/255
        txtGreen = 40/255
        txtBlue = 220/255
    if stage == 'RO32':
        bgRed = 249/255
        bgGreen = 187/255
        bgBlue = 253/255
        txtRed = 249/255
        txtGreen = 107/255
        txtBlue =  223/255
    if stage == 'RO16':
        bgRed = 126/255
        bgGreen = 235/255
        bgBlue = 126/255
        txtRed = 10/255
        txtGreen = 100/255
        txtBlue =  10/255
    if stage == 'QF':
        bgRed = 105/255
        bgGreen = 89/255
        bgBlue = 226/255
        txtRed = 70/255
        txtGreen = 0/255
        txtBlue =  176/255
    if stage == 'SF':
        bgRed = 140/255
        bgGreen = 0/255
        bgBlue = 140/255
        txtRed = 45/255
        txtGreen = 0/255
        txtBlue =  45/255
    if stage == 'F':
        bgRed = 0/255
        bgGreen = 138/255
        bgBlue = 150/255
        txtRed = 0/255
        txtGreen = 88/255
        txtBlue =  120/255
    if stage == 'GF':
        txtRed = 159 / 255
        txtGreen = 38 / 255
        txtBlue = 50 / 255
        bgRed = 209 / 255
        bgGreen = 118 / 255
        bgBlue = 130 / 255
    if bgRed == 0 and bgGreen == 0 and bgBlue == 0:
        raise StatError("Invalid round. (Acceptable rounds: TBD, QL, RO32, RO16, QF, SF, F, GF)")
    if modRed == 0 and modGreen == 0 and modBlue == 0:
        raise StatError("Invalid mod. (Acceptable mods: NM, HD, HR, DT, FM, TB)")
    if mod == None:
        raise StatError("You did not put a mod")
    if stage == None:
        raise StatError("You did not put a stage")
    request_body = {
        'requests': [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': gid,

                        'startRowIndex': index-1,
                        'endRowIndex': index,

                        'startColumnIndex': 2,
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': bgRed,
                                'green': bgGreen,
                                'blue': bgBlue
                            },
                            'textFormat': {
                                'foregroundColor': {
                                    'red': txtRed,
                                    'green': txtGreen,
                                    'blue': txtBlue
                                },
                                'fontSize': 10,
                                'fontFamily': "Lexend Deca",
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': gid,

                        'startRowIndex': index-1,
                        'endRowIndex': index,

                        'startColumnIndex': 3,
                        'endColumnIndex': 4
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'foregroundColor': {
                                    'red': modRed,
                                    'green': modGreen,
                                    'blue': modBlue
                                },
                                'fontSize': 10,
                                'fontFamily': "Lexend Deca",
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat)'
                }
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': gid,

                        'startRowIndex': index-1,
                        'endRowIndex': index,

                        'startColumnIndex': 4,
                        'endColumnIndex': 13
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'textFormat': {
                                'foregroundColor': {
                                    'red': modRed,
                                    'green': modGreen,
                                    'blue': modBlue
                                },
                                'fontSize': 10,
                                'fontFamily': "Lexend Deca",
                                'bold': False
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(textFormat)'
                }
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': gid,

                        'startRowIndex': index-1,
                        'endRowIndex': index,

                        'startColumnIndex': 13,
                        'endColumnIndex': 14
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': statbRed,
                                'green': statbGreen,
                                'blue': statbBlue
                            },
                            'textFormat': {
                                'foregroundColor': {
                                    'red': stattRed,
                                    'green': stattGreen,
                                    'blue': stattBlue
                                },
                                'fontSize': 10,
                                'fontFamily': "Lexend Deca",
                                'bold': False
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor, textFormat)'
                }
            }
        ]
    }

    worksheet.update('C'+str(index)+":N"+str(index), [[stage, mod, mapper, artist, sr, bpm, length, cs, ar, od, dl, status]])
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=request_body
    ).execute()
    return

def remove_row(stage: str, mod: str, mapper: str):
    '''For dropping a map, moves a specific row based on the given mapper, mod, and stage

    Parameters
    ----------
    stage: The round that the map is going to be used
    mod: The mod the map is being mapped for
    mapper: The mapper submitting the map
    '''
    scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'FILE'
    global values_input, service
    gs = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=scope)
    service = discovery.build('sheets', 'v4', credentials=creds)
    sheet = gs.open("SHEET")
    worksheet = sheet.worksheet("WORKSHEET")
    index = 4
    found = False
    sheet_id = 'SHEETID'
    gid = 'GID'
    if mod == None:
        raise StatError("You did not put a mod")
    if stage == None:
        raise StatError("You did not put a stage")
    while found == False:
        if(worksheet.acell('C'+str(index)).value) == stage and worksheet.acell('D'+str(index)).value == mod and worksheet.acell('E'+str(index)).value == mapper:
            found = True
        else:
            index = index+1
            if(worksheet.acell('C'+str(index)).value) == None:
                raise StatError("You did not claim **"+stage+": "+mod+"** previously.")

    color = 153/255
    request_body = {
        'requests': [
            {
                'repeatCell': {
                    'range': {
                        'sheetId': gid,

                        'startRowIndex': index - 1,
                        'endRowIndex': index,

                        'startColumnIndex': 2,
                        'endColumnIndex': 3
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': color,
                                'green': color,
                                'blue': color
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor)'
                }
            },
            {
                'repeatCell': {
                    'range': {
                        'sheetId': gid,

                        'startRowIndex': index - 1,
                        'endRowIndex': index,

                        'startColumnIndex': 13,
                        'endColumnIndex': 14
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {
                                'red': color,
                                'green': color,
                                'blue': color
                            },
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor)'
                }
            }
        ]
    }
    worksheet.update('C' + str(index) + ":N" + str(index),[['', '', '', '', '', '', '', '', '', '', '', '']])
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=sheet_id,
        body=request_body
    ).execute()
    return