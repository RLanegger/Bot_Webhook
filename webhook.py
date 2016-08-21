from urllib2 import Request, urlopen, URLError
import requests, datetime , os
import urllib2
from datetime import datetime, timedelta
import json
import sys#, slack_messages


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
   
    #print("Request:")
    #print(json.dumps(req, indent=4))
#    print req

    res = processRequest(req)
    
    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

    

def header_token (file):
#    now = datetime.now()
#    old = now 
#    try:
#        f = open(file,'r')
#    except IOError as e:
#        print "I/O error({0}): {1}".format(e.errno, e.strerror)     
#    tmp = f.read()
#    print ('Test - ' + str(tmp) )
#    f.close()
#    if tmp:
#        strtime = tmp.split(';')[0]
#        time = datetime.strptime(strtime, '%Y-%m-%d %H:%M:%S.%f') + timedelta(hours=+24)
#        access_token = tmp.split(';')[1]
#        if time < now or len(access_token) <= 20: #Token is invalid because older than 24h
#            print ('get new header')
#            access_token =  getNewToken()
#            f = open(file,'w')
#            #stream = str(now) + ';' + str(access_token)
#            #f.write(stream)
#            #f.close() 
#            header_call = createHeader(access_token)
#            return header_call
#        else:
#            header_call = createHeader(access_token)
#            return header_call 
#    else:
        print 'get initial Header'
        access_token =  getNewToken()
        #f = open(file,'w')
        #stream = str(now) + ';' + str(access_token)
        #f.write(stream)
        #f.close()
        header_call = createHeader(access_token)
        return header_call        
        
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
        else:
            token = j['access_token']
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
    headers = header_token(file)
    return headers

def callRequest(myrequest, header):
#            headers = {
#                'Authorization': #str(access_token),
#                'Bearer 7u4gey8behd39uprkfjqn3tp',
#                'Accept': 'application/json',
#            'Content-Type' : 'application/json'}
        req_data = 'https://api.lufthansa.com/v1/' + myrequest

#        req_data = data
        #print req_data
        req_call = requests.get(req_data, headers = header) 
        print str(req_call.status_code)
        if req_call.status_code > 499:
            raise URLError('No data to process! :')
        else:
            return req_call.json()


def makeWebhookResult(flight, date, status, origin, destination):
    speech = 'Your flight' + flight + 'on date ' + date + ' from ' + origin + ' to ' + destination + ' is ' + status
    if status == 'Flight Delayed':
        color = '#FF0000'
    else:
        color = "#36a64f"
        
    slack_message = { 
        "text": speech,
        "attachments": [ 
            {
                "title": status,
                "color": color,
                "fields" : [
                          {
                              "title": "Origin",
                              "value": origin,
                              "short": "false"
                          },
                          {
                              "title": "Destination",
                              "value": destination,
                              "short": "false"
                          },
                          {
                              "title": "Date",
                              "value": date,
                              "short": "false"
                          }
                      ]
                  }
              ]
          }
       
#    print("Response:")
#    print(speech)   
    return {
        "speech": speech,
        "displayText": speech,
       
        # "contextOut": [],
        "source": "LHOpenAPIFlightStatus",
        "data": { "slack" : slack_message }
    }
     
    
def getInputDate(indate):
      rfcString = indate.get('rfcString')
      date = rfcString[0:4] + '-' + rfcString[4:6] + '-' + rfcString[6:8]
      return date
      
def userInput(req):

        result = req.get('result')
        contexts = result.get('contexts')
        print contexts
        parameters = result.get("parameters")
        date = getInputDate(parameters.get('date'))
        return { 
            'flightNumber' : parameters.get('flightNumber'),
            "date": date
        }

def processRequest(req):

        header = getHeader()
        uinput = userInput(req)
        flightDate = str(uinput.get("date"))
        flightNumber = str(uinput.get("flightNumber")) 
        #print flightNumber
        methods = 'operations/flightstatus/' + flightNumber + '/' + flightDate #LH400/2016-04-10'
        #print methods
    
        lh_api = callRequest(methods, header) 
        flightStatus = lh_api.get('FlightStatusResource', {}).get('Flights',{}).get('Flight',{}).get('Departure',{}).get('TimeStatus',{}).get('Definition')
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
        speech =  makeWebhookResult(flightNumber, flightDate, flightStatus, origin, destination)
        return speech

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port
    if sys.platform == 'darwin':
        app.run(debug=False, port=port, host='127.0.0.1') 
    else:
        app.run(debug=False, port=port, host='0.0.0.0') 
        

    
 