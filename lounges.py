def loungeFeatures(lhapi, uipunt, header):
###### Retrieve Lounge info

    # retrieve input parameters and assign to variables for convenience.
    lounge = request.params["lounge"]
    #age = request.params["age"]
    header  = {
            'Authorization': 'Bearer hxtrh2zb3ukmfsc5sbk7kw66',
        'Accept': 'application/json'}

    req_data = 'https://api.lufthansa.com/v1/offers/lounges/' + lounge
    req_call = requests.get(req_data, headers = header)
    req_json = req_call.json()
    loungeFeatures = req_json.get('LoungeResource',{}).get('Lounges',{}).get('Lounge',{})[0].get('Features',{})
    # add the message to the function's output.
    response.addOutput('Lounges',lounge_info)

    # return the output.
    response.end()

# pass your function into blockspring.define. tells blockspring what function to run.
    blockspring.define(block)
    
    return loungeFeatures
    
def buildLoungeInfo (lh_api,uinput,header):
    lounges = lh_api.get('LoungeResource').get('Lounges').get('Lounge')
    i = 0
    loungeInfo = []
    for lounge in lounges:
       loungeInfo.append( {
           'Name' : lounge.get('Names').get('Name').get('$'),
           'Location' : lounge.get('Locations').get('Location')[1].get('$'),
           'OpeningHours' : lounge.get('OpeningHours')#.get('OpeningHours')[0].get('$')
       })
       i += 1
    return loungeInfo