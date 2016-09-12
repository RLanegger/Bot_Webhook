from urllib2 import Request, urlopen, URLError
import requests, datetime , os
import urllib2
from datetime import datetime, timedelta
import json
import sys
from slack_messages import buildFlightStatusSpeech, buildGateSpeech,errorHandling
from declarations import Token
import pickle

from flask import Flask
from flask import request
from flask import make_response

status = 'LHOpenAPIFlightStatus'
gate = 'LHOpenAPITerminalGate'

client_id = ('edqrrrnzamxxj24z5haa6r4j')
client_secret = ('bVAJshaVVf')

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])

def webhook():
    try:
        req = request.get_json(silent=True, force=True)

        res = processRequest(req)
        #print res
        res = json.dumps(res, indent=4)
        r = make_response(res)
        r.headers['Content-Type'] = 'application/json'
        return r
    except URLError, e:
        #print e.reason
        res = json.dumps(e.reason, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

    

def header_token ():
    file = './header.txt'
    now = datetime.now()
    old = now 
    try:
        f = open(file,'r')
        old_line = f.read()
        print ('TOKEN FILE --> ' + str(old_line) )
        f.close()
        strtime = old_line.split(';')[1]
        time = datetime.strptime(strtime, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=+24)
        print 'TIME --> ', time
        old_access_token = old_line.split(';')[0]
        if time < now or len(old_access_token) <= 20: #Token is invalid because older than 24h
            print 'AUTHENTICATION --> get Header'
            mytoken = Token('https://api.lufthansa.com/v1/oauth/token' ,client_id , client_secret)
            mytoken.authenticate()
            if mytoken.isAuthenticated == True:
                header_call = createHeader(mytoken.access_token)
                f = open(file,'w')
                new_line = mytoken.access_token + ';'  + str(datetime.now())
                f.write(new_line)          
        else:
            print 'AUTHENTICATION --> REUSE Header'
            header_call = createHeader(old_access_token)
        return header_call
    except IOError as e:
#        print "I/O error({0}): {1}".format(e.errno, e.strerror)   
        print 'AUTHENTICATION --> GET Header'
        mytoken = Token('https://api.lufthansa.com/v1/oauth/token' ,client_id , client_secret)
        mytoken.authenticate()
        if mytoken.isAuthenticated == True:
            header_call = createHeader(mytoken.access_token)
            f = open(file,'w')
            new_line = mytoken.access_token + ';'  + str(datetime.now())
            f.write(new_line)
        
#    return 'Error in Authentication'

def getNewToken():
    request = ('https://api.lufthansa.com/v1/oauth/token')
    header_auth = {
        'client_id' : client_id,
        'client_secret': client_secret, 
        'grant_type' : 'client_credentials'}
    try:            
        r = requests.post(request, data = header_auth)
        j =  r.json() 
#        access_token = { 'Authorization': 'Bearer ' + j['access_token']}

        if r.status_code > 299:
            raise URLError('No access token retrieved! :')
            print 'AUTHORIZATION --> Error in  Authorization'
        else:
            token = j['access_token']
            print 'AUTHORIZATION --> Successful authorized'
            return token
            
    except URLError, e:
        print 'Error: ', e
 #   else:
 
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except TypeError, e:
        return False
    return True         
    
def createHeader(access_token):
    header_call = {
            'Authorization': 'Bearer ' + str(access_token),
        'Accept': 'application/json'}
    return header_call
    
def getHeader():       
    file = './key.txt'
    headers = header_token()

    return headers

def callRequest(myrequest, header):
#            headers = {
#                'Authorization': #str(access_token),
#                'Bearer 7u4gey8behd39uprkfjqn3tp',
#                'Accept': 'application/json',
#            'Content-Type' : 'application/json'}
        req_data = 'https://api.lufthansa.com/v1/' + myrequest
#        try:
#        req_data = data
        print 'REQUEST --> ', req_data
        req_call = requests.get(req_data, headers = header) 
        print 'RESPONSE STATUS ---> ',str(req_call.status_code)
        if req_call.status_code <> 200:
            raise URLError('Error in Input data')
        else:
            return req_call.json()
   
    
def getInputDate(indate):
    print 'INDATE --> ', indate
    #Intended for any date conversion error in API.AI (bug corrected)
    #rfcString = indate.get('date')
    #print 'RFCSTRING --> ', rfcstrin
    #if sys.platform == 'darwin':
    #date = rfcString[0:4] + '-' + str(int(rfcString[4:6])) + '-' + rfcString[6:8]
    #else:
    #    date = rfcString[0:4] + '-' + str(int(rfcString[4:6]) - 1  ) + '-' + rfcString[6:8]
 #     print date
#      print rfcString
    return indate
      
def userInput(actions, parameters):
    print 'ACTIONS --> ',actions
    if actions == status or actions == gate:
        #print parameters.get('date')
        date = getInputDate(parameters.get('date'))
        #print 'Date for FlightStatus ', date
        result = {
            'flightNumber' : parameters.get('FlightNumber'),
            "date": date
                }
 
    return result

def constructMethods(actions,uinput):
    if actions == status or actions == gate:
        flightDate = str(uinput.get("date"))
        flightNumber = str(uinput.get("flightNumber")) 
        #print flightNumber
        methods = 'operations/flightstatus/' + flightNumber + '/' + flightDate #LH400/2016-04-10'
        #print methods
    return methods
    
def buildFlightStatus(lh_api, parameters,header):
    
    status = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('TimeStatus',{}).get('Definition')
    originStatus = str(lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('AirportCode',{}) )
    destinationStatus = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Arrival',{}).get('AirportCode',{}) 
    #print flightStatus ,"Origin", originStatus,"Destination", destinationStatus
    
    methods ='references/airports/'+ originStatus + '?LHoperated=true'
    oCityCall = callRequest(methods, header) 
    origin =  oCityCall.get('AirportResource',{}).get('Airports',{}).get('Airport',{}).get('Names',{}).get('Name',{})[1].get('$',{})
    methods ='references/airports/'+ destinationStatus + '?LHoperated=true'
    dCityCall = callRequest(methods, header) 
    destination = dCityCall.get('AirportResource',{}).get('Airports',{}).get('Airport',{}).get('Names',{}).get('Name',{})[1].get('$',{})
    #print flightStatus ,"Origin", origin,"Destination", destination
    
    flightstatus = {
        'status' : status,
        'origin' : origin,
        'destination' : destination,
        'date' : parameters.get('date'),
        'flight' : parameters.get('flightNumber')
        }

    return flightstatus

def buildGateInformation(lh_api, parameters,header):
    
        originStatus = str(lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('AirportCode',{}) )
        terminal = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('Terminal',{}).get('Name')
        gate = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('Terminal',{}).get('Gate')
    
        methods ='references/airports/'+ originStatus + '?LHoperated=true'
        oCityCall = callRequest(methods, header) 
        origin =  oCityCall.get('AirportResource',{}).get('Airports',{}).get('Airport',{}).get('Names',{}).get('Name',{})[1].get('$',{})
    
        depgate = {
            'origin' : originStatus,
            'terminal' : terminal,
            'gate' : gate,
            'date' : parameters.get('date'),
            'flight' : parameters.get('flightNumber')
            }

        return depgate
 
def processRequest(req):
    try:
        header = getHeader()
        result = req.get('result') 
        #print 'RESULT --> ' , result
        actions = result.get('action')  #get what ressource to ask on API
        print 'ACTION --> ', actions
        parameters = result.get('parameters')
        print 'PARAMETER --> ', parameters
        uinput = userInput(actions, parameters)
        print 'UINPUT --> ' , uinput
        methods = constructMethods(actions,uinput)
    #print methods   
        lh_api = callRequest(methods, header)
    #print lh_api
        if actions == 'LHOpenAPIFlightStatus':
            flightstatus =  buildFlightStatus(lh_api, uinput,header)
            speech = buildFlightStatusSpeech(flightstatus)
            print 'SPEECH -->', flightstatus
        elif actions == 'LHOpenAPITerminalGate':
        #GateInformation from Flightstatus
            depgate = buildGateInformation(lh_api, uinput,header)
            speech = buildGateSpeech(depgate)
            print 'SPEECH -->', depgate
        return speech
    except URLError, e:
        speech = errorHandling(e,actions)
        print 'ERROR --> ', e
        raise URLError(speech)

#        return e #URLError('Error in Input data')
            

            
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
  
    print "Starting app on port %d" % port
    if sys.platform == 'darwin':
        app.run(debug=False, port=port, host='127.0.0.1') 
    else:
        app.run(debug=False, port=port, host='0.0.0.0') 

        

    
 