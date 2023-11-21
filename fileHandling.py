import os
import json

slash = "/"
absolute_path = os.path.dirname(__file__)
class iggyFile:
    def read(interactionUser, guild): # feed me a discord interaction object

        # set file name for user
        userFileName = f"{interactionUser.id}.json"

        # define class for user data values
        class iggyDataClass:
            # set default values for if they're missing from the user file:
            def __init__(self,
                        displayName=interactionUser.global_name,
                        userid=str(interactionUser.id),
                        keymashScore="0",
                        kittyScore="0",
                        boopScore="0",
                        gagType="none",
                        gagOwner=str(interactionUser.id),
                        thirdPerson="off",
                        yinglet="off",
                        twin=str(interactionUser.id)):
                #initialize the values
                self.displayName = displayName
                self.userid = userid
                self.keymashScore = keymashScore
                self.kittyScore = kittyScore
                self.boopScore = boopScore
                self.gagType = gagType
                self.gagOwner = gagOwner
                self.thirdPerson = thirdPerson
                self.yinglet = yinglet
                self.twin = twin

        # check if json file exists
        iggyDataFileExists = os.path.exists(f"{absolute_path}{slash}userData{slash}{guild.id}{slash}{userFileName}")

        # load data from json if the file exists
        if iggyDataFileExists == True:
            iggyFile = open(f"{absolute_path}{slash}userData{slash}{guild.id}{slash}{userFileName}")
            iggyDataRaw = json.load(iggyFile)
        
        # make a dictionary with just user id if the file doesn't exists
        else:
            iggyDataRaw = {"userid": f'{interactionUser.id}'} 

        # make object, use default values only if the keys are missing in the JSON
        iggyData = iggyDataClass(
            iggyDataRaw.get('displayName', iggyDataClass().displayName),
            iggyDataRaw.get('userid', iggyDataClass().userid),
            iggyDataRaw.get('keymashScore', iggyDataClass().keymashScore),
            iggyDataRaw.get('kittyScore', iggyDataClass().kittyScore),
            iggyDataRaw.get('boopScore', iggyDataClass().boopScore),
            iggyDataRaw.get('gagType', iggyDataClass().gagType),
            iggyDataRaw.get('gagOwner', iggyDataClass().gagOwner),
            iggyDataRaw.get('thirdPerson', iggyDataClass().thirdPerson),
            iggyDataRaw.get('yinglet', iggyDataClass().yinglet),
            iggyDataRaw.get('twin', iggyDataClass().twin)
        )

        # return user data object
        return iggyData 
    
    def write(iggyData, interactionUser, guild): # feed me a iggyData object and user id

        # set file name for user
        userFileName = f"{interactionUser.id}.json"

        # Convert the user data object to a dictionary
        iggyDataDict = {
            "displayName": interactionUser.global_name,
            "userid": str(interactionUser.id),
            "keymashScore": iggyData.keymashScore,
            "kittyScore": iggyData.kittyScore,
            "boopScore": iggyData.boopScore,
            "gagType": iggyData.gagType,
            "gagOwner": iggyData.gagOwner,
            "thirdPerson": iggyData.thirdPerson,
            "yinglet": iggyData.yinglet,
            "twin": iggyData.twin
        }

        # check if server directory exists
        serverPathExists = os.path.exists(f'{absolute_path}{slash}userData{slash}{guild.id}') # define checking for if server path exists
        # check if server has a folder, if not make one
        if serverPathExists == False: 
            os.mkdir(f'{absolute_path}{slash}userData{slash}{guild.id}')

        # write the dictionary to a json file
        with open(f"{absolute_path}{slash}userData{slash}{guild.id}{slash}{userFileName}", 'w') as file:
            json.dump(iggyDataDict, file, indent=4)  # indent parameter for human-readable formatting (optional)
