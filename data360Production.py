#from __future__ import with_statement
import requests
import json
import sys
import certifi
from pprint import pprint
from os.path import expanduser
from datetime import datetime, timedelta

# Get user's home folder
home = expanduser("~")

# OAuth 2 credentials
credentials = {
    'client_id': None,
    'client_secret': None
}

# OAuth 2 token
token = {
    'access_token': None,
    'expires_at': None
}


def get_credentials():
    """ Retrieves the credentials from a json file """

    try:
        credentials_path = './credentials.json'
        with open(credentials_path) as credentials_file:
            global credentials
            json_resp = json.load(credentials_file)
            credentials["client_id"] = json_resp["client_id"]
            credentials["client_secret"] = json_resp["client_secret"]
            print("Got credentials from file")
    except EnvironmentError:
        pprint('Error opening file ' + credentials_path)
        sys.exit(1)


def get_new_token():
    """ Get a new OAuth token"""

    global credentials, token

    url = "https://developer.api.autodesk.com/authentication/v1/authenticate"

    payload = "client_id=" + credentials["client_id"] + "&client_secret=" + credentials["client_secret"] + \
              "&grant_type=client_credentials"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache"
    }

    response = requests.request("POST", url, data=payload, headers=headers, verify=certifi.where())
    if response.status_code == 200:
        json_resp = json.loads(response.text)
        token["access_token"] = json_resp["access_token"]
        expires_in = datetime.now() + timedelta(seconds=json_resp["expires_in"])
        token["expires_at"] = expires_in
        print('Got OAuth token: ' + token["access_token"])
        return True
    else:
        print('Failed to get access token')
        return False


def check_token():
    """ Checks if token is still valid, if it's expiring or expired get a new token """
    if token["access_token"]:
        if token["expires_at"]:
            expires = token["expires_at"]
            total_seconds = (expires - datetime.now()).total_seconds()
            if total_seconds > 120:
                return
            else:
                print('Token expired getting new token')
                get_new_token()
        else:
            print('Token invalid getting new token')
            get_new_token()
    else:
        print('Token invalid getting new token')
        get_new_token()


# Call this method to initialize module
def init(client_id=None, client_secret=None):
    """ Initializes the Data 360 module"""

    global credentials

    if (client_id is not None) & (client_secret is not None):
        credentials["client_id"] = client_id
        credentials["client_secret"] = client_secret
    else:
        get_credentials()

    get_new_token()

def get_readings(orgId, groupId, projectId, sensorList=None, startTS=None, endTS=None, latestReading=False, rollupFrequency=None):
    """ Retrieves a reading from Data 360"""

    global token
    check_token()
    if token["access_token"]:
        url = "https://data360.api.autodesk.com/api/v1/projects/" + projectId + "/readings"
        #url = "https://projectdasher-staging.api.autodesk.com/api/v1/projects/" + projectId + "/readings"

        headers = {
            'authorization': "Bearer " + token["access_token"],
            'accept': "application/json",
            'cache-control': "no-cache"
        }

        querystring = {}

        if sensorList is not None:
            querystring.update({'sensorList': sensorList})
        if startTS is not None:
            querystring.update({'startTS': startTS})
        if endTS is not None:
            querystring.update({'endTS': endTS})
        if rollupFrequency is not None:
            querystring.update({'rollupFrequency': rollupFrequency})
        if latestReading is True:
            querystring.update({'latestReading': 'True'})

        querystring.update({'organizationId': orgId})
        querystring.update({'groupId': groupId})

        response = requests.request("GET", url, data=None, headers=headers,
                                    params=querystring, verify=certifi.where())
        if response.status_code == 200:
            # print json.dumps(json.loads(response.text), indent=4, sort_keys=True)
            return json.loads(response.text)
        else:
            print('Failed to get readings: ' + response.text)
            return None
    else:
        print('Token not available')
        return False


def create_reading(orgId, groupId, projectId, sensorId, ts, val):
    """Stores data in Data360.

       Keyword arguments:
       orgId -- The company identifier (required)
       groupId -- The site identifier (required)
       projectId -- The project identifier (required)
       sensorId -- The sensor identifier (required)
       ts -- The reading date and time in UTC (required)
       val -- The value from the sensor(required)
       :rtype: Boolean
    """

    global token
    check_token()
    if token["access_token"]:

        url = "https://data360.api.autodesk.com/api/v1/projects/" + projectId + "/readings"
        #url = "https://projectdasher-staging.api.autodesk.com/api/v1/projects/" + projectId + "/readings"

        payload = "{ 'readingList': [{'sensorId': '" + sensorId + "','ts':'" + ts + "','val':'" + val.__str__() + "'}], 'groupId': '" + groupId + "','organizationId': '" + orgId + "'}"

        headers = {
            'authorization': "Bearer " + token["access_token"],
            'content-type': "application/json",
            'accept': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=payload, headers=headers, verify=certifi.where())

        if response.status_code == 201:
            #print json.dumps(json.loads(response.text), indent=4, sort_keys=True)
            return True
        else:
            print('Failed to create reading: ' + response.text)
            return False
    else:
        print('Token not available')
        return False
    
def create_readings(orgId, groupId, projectId, sensorId, ts, val):
    """Stores data in Data360.

       Keyword arguments:
       orgId -- The company identifier (required)
       groupId -- The site identifier (required)
       projectId -- The project identifier (required)
       sensorId -- The list of sensor identifiers (required)
       ts -- The readings date and time in UTC for each sensor in order(required)
       val -- The value from each sensor(required)
       :rtype: Boolean
    """
    # sensorIds, ts and val need all be the same size...assert!

    global token
    check_token()
    if token["access_token"]:

        url = "https://data360.api.autodesk.com/api/v1/projects/" + projectId + "/readings"
        #url = "https://projectdasher-staging.api.autodesk.com/api/v1/projects/" + projectId + "/readings"

        # payload header
        payload = "{ 'readingList': ["
        
        for i in range( 0, len(sensorId) ):
            payload += "{'sensorId': '" + sensorId[i] + "','ts':'" + ts[i] + "','val':'" + val[i].__str__() + "'}"
            if i < (len(sensorId) - 1) :
                payload += ","

        # payload footer
        payload += "], 'groupId': '" + groupId + "','organizationId': '" + orgId + "'}"


        headers = {
            'authorization': "Bearer " + token["access_token"],
            'content-type': "application/json",
            'accept': "application/json",
            'cache-control': "no-cache"
        }

        response = requests.request("POST", url, data=payload, headers=headers, verify=certifi.where())

        if response.status_code == 201:
            # print json.dumps(json.loads(response.text), indent=4, sort_keys=True)
            return True
        else:
            print('Failed to create reading: ' + response.text)
            return False
    else:
        print('Token not available')
        return False


def splash(orgId=None, groupId=None, projectId=None, sensorId=None):
    """ Returns a URL that can be used to see a Splash chart with the sensor data"""

    if (orgId is None) & (groupId is None) & (projectId is None) & (sensorId is None):
        return "Missing Splash parameters"

    #These are the default parameters for the Hackathon. Please update them accordingly
    COMPANYID = orgId
    SITEID = groupId
    SPLASH_SERVER = "http://ec2-50-16-225-76.compute-1.amazonaws.com/data360/viewer.php?"

    splash_url = SPLASH_SERVER + "building=" + projectId + "&companyId=" \
                 + COMPANYID + "&siteId=" + SITEID + "&point=" + sensorId;

    return splash_url

