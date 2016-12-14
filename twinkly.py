#!/usr/bin/env python

# USAGE:
# ./twinkly.py -i <ip_addr> -m <mode>
# mode = off, start, stop

import os
import requests
import json
import sys
import getopt
import base64
import string
import random

class Xled:
    def __enter__(self):
        return self;

    def __exit__(self, type, value, traceback):
        print "Logging out!"
        self.logOut()

    def __init__(self,ip):
        self.ip = ip
        self.headers = {
            'Content-Type' : 'application/json;charset=utf-8',
            'Content-Length' : 0
        }
        self.connector = requests.Session()
        self.baseUrl = '/xled/v1/'
        self.headers['X-Auth-Token'] = ''
        print "Connecting to "+self.ip
        self.login()
        print "Logged in! Auth token: "+self.headers['X-Auth-Token']
        self.verifyLogin()

    '''
    Generate Challenge Code
    '''
    def generateChallengeCode(self):
        randomBytes = os.urandom(32)
        return base64.b64encode(randomBytes)

    '''
    Save the Authorization Token in the headers
    for subsequent requests
    '''
    def login(self):
        self.headers['X-Auth-Token'] = self.loginCode()

    '''
    Retrieves the Authentication Token
    '''
    def loginCode(self):
        challenge = self.generateChallengeCode()
        payload = {
          "challenge" : challenge
        }
        print "Challenge code generated: "+challenge
        response = self.post('login',payload)
        if(response.status_code == 200):
            return response.json()['authentication_token']
        else:
            raise Exception('Could not authenticate')

    '''
    Verify that the login was successful.
    (Cannot skip it)
    '''
    def verifyLogin(self):
        response = self.post('verify',{})
        return self.checkResponse(response)

    '''
    Make a GET request
    '''
    def get(self,endpoint):
        if 'Content-Length' in self.headers:
            del self.headers['Content-Length']
        response = self.connector.get('http://'+self.ip+self.baseUrl+endpoint, headers=self.headers);
        return self.checkResponse(response)

    '''
    Make a POST request
    '''
    def post(self,endpoint,payload):
        data = json.dumps(payload)
        self.headers['Content-Length'] = str(len(data))
        # print self.headers
        # print data
        # print data
        response = self.connector.post('http://'+self.ip+self.baseUrl+endpoint, data, headers=self.headers)
        return self.checkResponse(response)

    '''
    Get the current mode of light
    '''
    def getMode(self):
        response = self.get('led/mode')
        return response.json()['mode']

    '''
    Get network information from the lights
    '''
    def getStatus(self):
        response = self.get('network/status')
        print response.content
        return response.json()

    '''
    Change the light mode
    '''
    def changeMode(self,data):
        response = self.post('led/mode', data)
        return self.checkResponse(response)

    '''
    Stop the animation
    '''
    def stopAnimation(self):
        print "Stopping the animation..."
        response = self.changeMode({"mode":"rt"})
        print "Animation stopped!"
        return response

    '''
    Start the animation
    '''
    def startAnimation(self):
        print "Starting the animation..."
        response =  self.changeMode({"mode":"movie"})
        print "Animation started!"
        return response

    '''
    Turn off the lights
    '''
    def turnOff(self):
        print "Turning off the lights..."
        response = self.changeMode({"mode":"off"})
        print "Turned off the lights!"
        return response

    def firmwareVersion(self):
        response = self.get('fw/version')
        return self.checkResponse(response)

    '''
    Check if the response is a 200 status code
    '''
    def checkResponse(self,response):
        if(response.status_code == 200):
            return response
        else:
            raise Exception(response.content)

    '''
    Log out
    '''
    def logOut(self):
        return self.post('logout',{})



'''
Get the CLI args
'''
def main(argv):
    global ip
    global mode
    try:
      opts, args = getopt.getopt(argv,"i:m:")
    except getopt.GetoptError:
      print sys.argv[0]+' -i <ip_address>'
      print "-m mode [rt,off,movie]"
      sys.exit(2)
    for opt, arg in opts:
      if opt in ("-i", "--ip"):
         ip = arg
      elif opt in ("-m", "--mode"):
         mode = arg

'''
START HERE
'''
ip = ''
mode = None

if len(sys.argv) < 2:
    print sys.argv[0]+' -i <ip_address>'
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])

mode_function = {
    'off' : 'turnOff',
    'stop' : 'stopAnimation',
    'start' : 'startAnimation'
}

with Xled(ip) as ledController:
    print "Firmware Version: "+ ledController.firmwareVersion().json()['version']
    if(mode):
        getattr(ledController, mode_function[mode])()


# print ledController.getMode()
# pprint(ledController.getStatus())
# print ledController.turnOff()
# print ledController.startAnimation()
# print ledController.stopAnimation()



