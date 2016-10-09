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
    
def buildGateSpeech(depgate):
    
        date = str(depgate.get('date'))
        origin = str(depgate.get('origin'))
        gate = str(depgate.get('gate'))
        terminal = str(depgate.get('terminal'))
        flight = str(depgate.get('flight'))
        
        speech = 'Your flight' + flight + ' on date ' + date + ' from ' + origin + ' departs from Terminal ' +  terminal + ' Gate ' + gate

        slack_message = { 
            "text": speech,
            "attachments": [ 
                {
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
                  ]
              }
       
    #    print("Response:")
    #    print(speech)   
        return {
            "speech": speech,
            "displayText": speech,
       
            # "contextOut": [],
            "source": "LHOpenAPITerminalGate",
            "data": { "slack" : slack_message }
        }
 
 
def buildLoungeInfoSpeech(loungedata):    
    
    speech = 'Your City contains the following lounges '
    for lounge in loungedata:
        speech += str(lounge.get('Name')) + ', '
        slack_message = {
            "text": speech,
            "attachments": [
                {
                    "title": lounge.get('Name'),
                    "color": "#36a64f",
                    "fields" : [
                        {
                            "title": "Location",
                            "value": lounge.get('Location'),
                            "short": "false"
                        },
                        {
                            "title": "Date",
                            "value": lounge.get('OpeningHours'),
                            "short": "false"
                        }
                    ]
                }
            ]
        }
       
        #    print("Response:")
        #    print(speech)   
        return { "speech": speech, "displayText": speech, "source": "LHOpenAPILoungeInfo", "data": { "slack" : slack_message } }
           
def errorHandling(e, actions):
    return {
            "speech": e.reason,
            "displayText": e.reason,
       
            # "contextOut": [],
            "source": actions,
            #"data": { "slack" : slack_message }
        }