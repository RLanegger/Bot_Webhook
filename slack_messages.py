def buildFlightStatus(lh_api):
    
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