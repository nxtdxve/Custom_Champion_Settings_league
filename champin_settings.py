from lcu_driver import Connector
import os
import sys
import shutil
import json
import requests
import subprocess

# pip install lcu-driver

connector = Connector()
currentChampion = "nothing right now"
folderName = "Champion_Settings"
fileName = os.path.basename(sys.executable) # League of Championssettings
fileLocation = sys.executable
fileLocationFolder = os.path.dirname(fileLocation)
startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
backupMark = " [BACKUP]"

@connector.ready
async def connect(connection):
    # Clear the terminal screen
    os.system('cls' if os.name == 'nt' else 'clear')
    print(green('[READY]') + ' You can lock in your champion and I will change your keybinds for that champion')
    # print(connection.address)
    # print(connection.auth_key)
    
@connector.close
async def disconnect():
    print(f'{red("[CLOSED]")} The client has closed')
    
# everytime your League session UPDATEs: 
@connector.ws.register('/lol-gameflow/v1/gameflow-phase', event_types=('UPDATE',))
async def main(connection, event):
    await checkLockIn(connection, event.data)
    await checkPostGame(connection, event.data)
        
async def checkLockIn(connection, event):
    if event == "GameStart":        
        # when the game starts:
        await updateChampion(connection)
        pasteFiles()
        
async def checkPostGame(connection, event):
    if event == 'WaitingForStats':        
        # when the game ends:
        copyFiles()
            
def pasteFiles():
    try:         
        # all the otto settings go into the otto variable
        with open(pathToChampSetting(), 'r') as ottoSettings:
            otto = json.load(ottoSettings)

        # replace the keybind part with the ottoSettings
        with open(pathToRealSettings(), 'r') as leagueSettings:
            settings = json.load(leagueSettings)
            settings['files'][1] = otto
            #the most important bit of code!!

        # write the new data into the PersistedSettings.json
        with open(pathToRealSettings(),'w') as newSettings:
            json.dump(settings, newSettings, indent=4)

        print(f'{lightBlue(f"[UPDATED]")} Replaced keybinds for {currentChampion}!')
    except:
        print(f'{yellow("[FIRST TIME]")} Creating new settings for {currentChampion} (from the original settings)')
        copyFiles(True)
    
def copyFiles(first_time=False):
    # if the champion is played for the first time, it will inherit the settings from the backup file
    # i feel like it is better like this, contact me if you think otherwise: DESPykesfying#3794
    if first_time:
        suffix = backupMark
    else:
        suffix = ''
    
    # save the settings from the PersistedSettings.json
    with open(pathToRealSettings() + suffix, 'r') as leagueSettings:
        settings = json.load(leagueSettings)
        
    # save the leagueSettings into a champion-specific file
    with open(pathToChampSetting(), 'w') as ottoSettings:
        json.dump(settings["files"][1], ottoSettings, indent=4)
              
    print(f"{blue('[SAVED]')} File for {currentChampion} saved!")
    
####################### functions to clean everything up #######################
def whichChampionIs(champion_id):
    # Get the latest version of Data Dragon
    versions_url = "https://ddragon.leagueoflegends.com/api/versions.json"
    response = requests.get(versions_url)
    versions = json.loads(response.content)
    latest_version = versions[0]

    # Get the champion data for the latest version
    url = f"http://ddragon.leagueoflegends.com/cdn/{latest_version}/data/en_US/champion.json"
    response = requests.get(url)
    champions_data = json.loads(response.content)["data"]

    # Loop through the champions data and find the champion with the matching ID
    for champion in champions_data.values():
        if int(champion["key"]) == champion_id:
            return champion["name"]

    # Return an error message if no champion with the matching ID was found
    return f"Error: Champion name not found for ID {champion_id}"

async def updateChampion(connection):    
    champion = await connection.request('get', '/lol-champ-select/v1/current-champion')
    if champion.status != 200:
        return
    
    champion = await champion.json()
    champion = whichChampionIs(champion)
        
    # update currentChampion
    global currentChampion
    currentChampion = champion
    
def setupFolder():
    # create the folder in which this application is going to work with
    try:
        os.mkdir(f"{rootFolder}\{folderName}")
        print(f'Created Folder in: {rootFolder}\{folderName}')
    except:
        print("Seems like it is not the first time I have been installed, but ah well")

def copyItself():
    # copy itself in the Riot Games/League of Legends/Config folder
    
    print(f"Copying myself to {rootFolder}...")
    try:
        shutil.copy(fileLocation, rootFolder)
    except:
        print('Starting programm')
        
    try:
        shutil.copy(fileLocation, startup_folder)
        print('Adding to the startup...')
    except:
        print('Something went wrong.')

def backup():
    if not os.path.isfile(pathToRealSettings() + backupMark):
        with open(pathToRealSettings() + backupMark, 'w') as backupSettings:
            with open(pathToRealSettings(), 'r') as leagueSettings:
                json.dump(json.load(leagueSettings), backupSettings, indent=4)
                # dump the leagueSettings in the backup file
                
        print('Backup succesful.')
    else:
        print('Backup exists already.')

def restart():
    # os.startfile(f'{rootFolder}\\{fileName}')
    subprocess.Popen([f'{rootFolder}\\{fileName}'], creationflags=subprocess.CREATE_NEW_CONSOLE)
    # subprocess.Popen([f'{rootFolder}\\{fileName}', '/c', 'start'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    os._exit(0)
        
def find_folder(name, drive='A'):    
    # this is a recursive function
    if drive == '[':
        print('League of Legends seems to not be installed.')
        return
    
    path = drive + ':\\'
    try:
        print(f'Searching for the Riot Games folder in {path}', end='\r')
        # tries to find the Riot Games folder
        files = os.listdir(path)
        if name in files:
            print("")
            print(f'Found it: {os.path.join(path, name)}')
            return os.path.join(path, name)
            # returns the path to Riot Games
        
        # other wise raise an exception,
        raise Exception
    except:
        # which calls the function again but with the next dive letter
        return find_folder(name, chr(ord(drive) + 1))
        
def pathToChampSetting():
    return f"{rootFolder}/{folderName}/{currentChampion}_settings.otto"

def pathToRealSettings():
    return f'{rootFolder}/PersistedSettings.json'

def blue(text):
    return '\033[34m' + text + '\033[0m'

def green(text):
    return '\033[32m' + text + '\033[0m'

def yellow(text):
    return '\033[33m' + text + '\033[0m'

def lightBlue(text):
    return '\033[94m'+ text + '\033[0m'

def red(text):
    return "\033[31m" + text + "\033[0m"


####################### Main Script #######################
rootFolder = find_folder('Riot Games')  + '\\League of Legends\\Config' # saves the Riot Games folder
backup()
setupFolder()
copyItself()

print(f'Checking wether I am in the correct file location...')
if rootFolder == fileLocationFolder:
    print('YES! Waiting for League of Legends to launch...')
    connector.start()
else:
    print('NO! Restarting programm...')
    restart()


#todo
#check autoupdate
#hide console in system tray (make terminal buy milk in the restart() function)