def buildSpeech(slack):
        
   # Anzahl der ISntanzene ist falsch
    print 'SLACK 1 --> ', str(slack)          
    allbodies = []
    if len(slack) > 1:
        for speechbody in slack:
            speech = speechbody.get('speech') 
            source = speechbody.get('source')
            attachment = speechbody.get('attachment')
            allbodies.append({ "text": speech,"attachments": attachment })
    else:
       speech = slack[0].get('speech')
       source = slack[0].get('source')
       attachment = slack[0].get('attachment')
       allbodies.append({ "text": speech,"attachments": attachment })   
        
    slack_message = {
            "speech": speech,
            "displayText": speech,
            "source": source,
            "data": { "slack" : allbodies }
        }
    print 'SLACK 2 --> ', str(slack_message)          
    return slack_message 


def buildFlightStatusSpeech(flightstatus):
    
    status = str(flightstatus.get('status'))
    origin = str(flightstatus.get('origin'))
    destination = str(flightstatus.get('destination'))
    date = str(flightstatus.get('date'))
    flight = str(flightstatus.get('flight'))
        
    speech = 'Your flight ' + flight + 'on date ' + date + ' from ' + origin + ' to ' + destination + ' is ' + status
    
    if status == 'Flight Delayed':
        color = '#FF0000'
    else:
        color = "#36a64f"
        
    slack_message = {
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
       
#    print("Response:")
#    print(speech)
    slack = { 'attachment' : slack_message, 'speech': speech, 'source': 'LHOpenAPIFlightStatus' }
    return slack
    
def buildGateSpeech(depgates):
    depgate = depgates[0]
    date = str(depgate.get('date'))
    origin = str(depgate.get('origin'))
    gate = str(depgate.get('gate'))
    terminal = str(depgate.get('terminal'))
    flight = str(depgate.get('flight'))
        
    speech = 'Your flight' + flight + ' on date ' + date + ' from ' + origin + ' departs from Terminal ' +  terminal + ' Gate ' + gate
    slack_message = {
        "title": 'Terminal Gate Information for ' + flight,
        "color": "#36a64f",
        "fields" : [
            {
                "title": "Date",
                "value": date,
                "short": "false"
            },
            {
                "title": "Origin",
                "value": origin,
                "short": "false"
            },
            {
                "title": "Terminal",
                "value": terminal,
                "short": "false"
            },
            {
                "title": "Gate",
                "value": gate,
                "short": "false"
            }
        ]
    }
    slack = { 'attachment' : slack_message, 'speech': speech, 'source': 'LHOpenAPITerminalGate' }
    print 'SLACK Speech --> ', str(slack)
    return slack
 
 
def buildLoungeInfoSpeech(loungedata):    
#    print 'LOUNGE_SPEECH --> ', loungedata
    speech = 'Your City contains the following lounges '
    slack_message = {
        "title": loungedata.get('Name'),
        "color": "#36a64f",
        "fields" : [
            {
                "title": "Location",
                "value": loungedata.get('Location'),
                "short": "false"
            },
            {
                "title": "Date",
                "value": loungedata.get('OpeningHours'),
                "short": "false"
            }
        ]
    }  
    #return { "speech": speech, "displayText": speech, "source": "LHOpenAPILoungeInfo", "data": { "slack" : slack_message } }
    slack = { 'attachment' : slack_message, 'speech': speech, 'source': 'LHOpenAPILoungeInfo' }
    return slack   
def errorHandling(e, actions):
    return {
            "speech": e.reason,
            "displayText": e.reason,
       
            # "contextOut": [],
            "source": actions,
            #"data": { "slack" : slack_message }
        }