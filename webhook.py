from urllib2 import Request, urlopen, URLError
import requests, datetime , os
import urllib2
from datetime import datetime, timedelta
import json
import sys
from slack_messages import buildSpeech,buildFlightStatusSpeech, buildGateSpeech,errorHandling, buildLoungeInfoSpeech
#from helpers import is_json
from declarations import Token
from fares import buildfaresummary
from lounges import loungeFeatures, buildLoungeInfo
import pickle

from flask import Flask
from flask import request
from flask import make_response

status = 'LHOpenAPIFlightStatus'
gate = 'LHOpenAPITerminalGate'
loungeInfo = 'LHOpenAPILoungeInfo'
fareSummary = 'faresummary'
noDataInQuery = 'Query no data'

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

def getNewToken():
    request = ('https://api.lufthansa.com/v1/oauth/token')
    header_auth = {
        'client_id' : client_id,
        'client_secret': client_secret, 
        'grant_type' : 'client_credentials'}
    try:            
        r = requests.post(request, data = header_auth)
        j =  r.json() 
        if r.status_code > 299:
            raise URLError('No access token retrieved! :')
            print 'AUTHORIZATION --> Error in  Authorization'
        else:
            token = j['access_token']
            print 'AUTHORIZATION --> Successful authorized'
            return token
            
    except URLError, e:
        print 'Error: ', e
 
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
            if req_call.status_code == 404:
                print 'RESPONSE --->', noDataInQuery
                result =  'Query no data'
                return result
            else:
                raise URLError('Error in Input data')
        else:
            return req_call.json()
   
    
def getInputDate(indate):
    print 'INDATE --> ', indate
    #Intended for any date conversion error in API.AI (bug corrected)
    rfcString = indate.get('rfcString')
    print 'RFCSTRING --> ', rfcString
    #if sys.platform == 'darwin':
    #date = rfcString[0:4] + '-' + str(int(rfcString[4:6])) + '-' + rfcString[6:8]
    #else:
#    date = indate
    date = rfcString[0:4] + '-' + str(int(rfcString[4:6])) + '-' + rfcString[6:8]
 #     print date
#      print rfcString
    return date
      
def userInput(actions, parameters,header):
    print 'ACTIONS --> ',actions
    result = []
    if actions == status or actions == gate:
        #print parameters.get('date')
        date = getInputDate(parameters.get('date'))
        #print 'Date for FlightStatus ', date
        result.append({'flightNumber' : parameters.get('FlightNumber'),'date': date})
    elif actions == fareSummary:
        print 'FareSummary'
        result.append(actions)
    elif actions == loungeInfo:
        airports = getAirportCode(parameters.get('city'),header)
        for airport in airports:
           result.append({'airportCode' : airport })
    return result

def constructMethods(actions,uinput):
    methods = []
    if actions == status or actions == gate:
        for inputLine in uinput:
            flightDate = str(inputLine.get("date"))
            flightNumber = str(inputLine.get("flightNumber"))
            flightNumber.replace(" ","") 
        #print flightNumber
            methods.append ('operations/flightstatus/' + flightNumber + '/' + flightDate )#LH400/2016-04-10'
        #print methods
    elif actions == fareSummary:
#        origin = buildairport(uiput.get(segments))
#        destination
#        catalog
#        traveldate 
#        returndate
#        travellers
        faretype = 'BASIC'
        methods.append ('offers/fares/fares?')
    elif actions == loungeInfo:
        for airportCode in uinput:
            methods.append ('offers/lounges/' + str(airportCode.get('airportCode')) )
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
            'date' : parameters[0].get('date'),
            'flight' : parameters[0].get('flightNumber')
            }

        return depgate
        
def processRequest(req):
    try:
        lh_apis =[]
        builddata = []
        speechBody =[]
        header = getHeader()
        result = req.get('result') 
        #print 'RESULT --> ' , result
        actions = result.get('action')  #get what ressource to ask on API
        print 'ACTION --> ', actions
        parameters = result.get('parameters')
        print 'PARAMETER --> ', parameters
        uinput = userInput(actions, parameters,header)
        print 'UINPUT --> ' , uinput
        methods = constructMethods(actions,uinput)

    #print methods   
        for method in methods:
            data = callRequest(method, header)
#            print 'LHAPI -->', str(data)
            if data <> noDataInQuery:
                lh_apis.append(data)
            
    #print lh_api
        print 'LH_API LIST --> ', str(len(lh_apis))
        for lh_api in lh_apis:

            print 'ACTION --> ', str(actions)
            if actions == status:   
                builddata.append(buildFlightStatus(lh_api, uinput,header))
                speechBody.append(buildFlightStatusSpeech(builddata))
            elif actions == gate:
        #GateInformation from Flightstatus

                builddata.append(buildGateInformation(lh_api, uinput,header))
#                print 'BUILDDATA --> ', str(builddata)
                speechBody.append(buildGateSpeech(builddata))
#                print 'Speechbody'
#        elif actions == fareSummary:
#            faresummary = buildfaresummary(lh_api, uiput,header)
#            print 'SPEECH -->'
            elif actions == loungeInfo:
#                    print lh_api
                lounges = buildLoungeInfo(lh_api,uinput,header)
                for lounge in lounges:
                    speechBody.append(buildLoungeInfoSpeech(lounge))
#                    builddata.append(buildLoungeInfoSpeech(lounge))
#                    speechBody.append(builddata)
            
            print 'BUILDDATA LIST --> ', str(len(builddata))

#        print 'LHAPI BUILD --> ', builddata
        speech = buildSpeech(speechBody)       
        return speech
    except URLError, e:
        speech = errorHandling(e,actions)
        print 'ERROR --> ', e
        raise URLError(speech)

#        return e #URLError('Error in Input data')
            
def getAirportCode(cityCode,header):
    airportCodes =  []
    methods = 'references/cities/'+ str(cityCode) + '?limit=20&offset=0'
    CityResource =  callRequest(methods, header)    
    airports = CityResource.get('CityResource').get('Cities').get('City').get('Airports').get('AirportCode')
    if isinstance(airports, list):
        for airport in airports:
            print 'AIRPORTS --> ' + airport
            airportCodes.append (airport)
    else:
           print 'AIRPORT --> ' + airports
           airportCodes.append (airports)
    print airportCodes
    return airportCodes

def is_json(myjson):
    if myjson == noDataInQuery:
        return False
    else:
        return True         

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
  
    print "Starting app on port %d" % port
    if sys.platform == 'darwin':
        app.run(debug=False, port=port, host='127.0.0.1') 
    else:
        app.run(debug=False, port=port, host='0.0.0.0') 

        

    
 