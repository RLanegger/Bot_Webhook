from urllib2 import Request, urlopen, URLError
import requests, datetime, os
from datetime import datetime, timedelta
import json

from flask import Flask
from flask import request
from flask import make_response

client_id = ('edqrrrnzamxxj24z5haa6r4j')
client_secret = ('bVAJshaVVf')

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
#For testing purpose
    request = ('https://posthere.io/9fd0-437b-8051')
    test_data = req
    
    r.requests.post(request, data = test_data)
#For testing end    
    #print("Request:")
    #print(json.dumps(req, indent=4))

#    res = processRequest(req)

#    res = json.dumps(res, indent=4)
    
#    r = make_response(res)
    r = make_response(req)
    r.headers['Content-Type'] = 'application/json'
    return r

def header_token (file):
    now = datetime.now()
    old = now 
    try:
        f = open(file,'r')
    except IOError as e:
        print "I/O error({0}): {1}".format(e.errno, e.strerror)     
    tmp = f.read()
    f.close()
    if tmp:
        strtime = tmp.split(';')[0]
        time = datetime.strptime(strtime, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=+24)
        access_token = tmp.split(';')[1]
        if time < now or len(access_token) <= 20: #Token is invalid because older than 24h
            print ('get new header')
            access_token =  getNewToken()
            f = open(file,'w')
            stream = str(now) + ';' + str(access_token)
            f.write(stream)
            f.close() 
            header_call = getHeader(access_token)
            return header_call
        else:
            header_call = getHeader(access_token)
            return header_call 
    else:
        print 'get initial Header'
        access_token =  getNewToken()
        #f = open(file,'w')
        #stream = str(now) + ';' + str(access_token)
        #f.write(stream)
        #f.close()
        header_call = getHeader(access_token)
        return header_call 
    return 'Error in Authentication'

def getNewToken():
    request = ('https://api.lufthansa.com/v1/oauth/token')
    header_auth = {
        'client_id' : client_id,
        'client_secret': client_secret, 
        'grant_type' : 'client_credentials'}
#    try:            
    r = requests.post(request, data = header_auth)
    j =  r.json() 
#        access_token = { 'Authorization': 'Bearer ' + j['access_token']}
        
    if r.status_code > 299:
        raise URLError('No access token retrieved! :')
    else:
        token = j['access_token']
        return token
#    except URLError, e:
#        print 'Error: ', e
 #   else:
         
    
#def getHeader(access_token):
 #   header_call = {
  #          'Authorization': 'Bearer ' + str(access_token),
   #     'Accept': 'application/json'}
    #return header_call
    
def getHeader():       
    file = './key.txt'
    headers = header_token(file)
    return headers

def callRequest(myrequest, header):
            '''headers = {
                'Authorization': #str(access_token),
                'Bearer 7u4gey8behd39uprkfjqn3tp',
                'Accept': 'application/json',
            'Content-Type' : 'application/json'}'''
        req_data = ('https://api.lufthansa.com/v1/' + myrequest)
        req_call = requests.get(req_data, headers = header) 
        if req_call.status_code > 499:
            raise URLError('No data to process! :')
        else:
               return req_call.json()

def makeWebhookResult(flight, date, status, origin, destination):

    speech = "Your flight" + flight + "on date " + date + " from " + origin + " to " + destination " is " + status

    print("Response:")
    print(speech)   
    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "LH_API_FlightStatus"
    } 
def userInput(req):
    result = req.get("result")
    parameters = result.get("parameters")
    return {
        "flightNumber" : parameters.get("flightNumber"),
        "date": parameters.get("date")
    }

def processRequest(req):
    try:   
        header = getHeader()
        userInput = getInput(flightNumber,date)
        #flightDate = '2016-04-15'
        #flightNumber = raw_input('Enter Flight: ')
        #print flightNumber
        methods = 'operations/flightstatus/' + userInput.get("flightnumber") + '/' + userInput("flightDate") #LH400/2016-04-10'
    
        lh_api = callRequest(methods, header) 
        #print lh_api
        flightStatus = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('TimeStatus',{}).get('Definition')
        originStatus = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('AirportCode',{}) 
        destinationStatus = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Arrival',{}).get('AirportCode',{}) 
        #print flightStatus ,"Origin", originStatus,"Destination", destinationStatus
    
        methods ='references/airports/'+ originStatus + '?LHoperated=true'
        oCityCall = callRequest(methods, header) 
        origin =  oCityCall.get('AirportResource',{}).get('Airports',{}).get('Airport',{}).get('Names',{}).get('Name',{})[1].get('$',{})
        methods ='references/airports/'+ destinationStatus + '?LHoperated=true'
        dCityCall = callRequest(methods, header) 
        destination = dCityCall.get('AirportResource',{}).get('Airports',{}).get('Airport',{}).get('Names',{}).get('Name',{})[1].get('$',{})
        #print flightStatus ,"Origin", origin,"Destination", destination
        speech =  makeWebhookResult(flight, date, flightStatus, origin, destination)
    except URLError, e:
        return {flighstatus}
    else:
        return speech


    

if __name__ == '__main__':
   app.run()  