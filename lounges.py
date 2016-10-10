def loungeFeatures(lhapi, uipunt, header):
###### Retrieve Lounge info

    loungeFeatures = req_json.get('LoungeResource',{}).get('Lounges',{}).get('Lounge',{})[0].get('Features',{})
    
    return loungeFeatures
    
def buildLoungeInfo (lh_api,uinput,header):
    lounges = lh_api.get('LoungeResource').get('Lounges').get('Lounge')

    loungeInfo = []
    if len(lounges) > 1:
        print 'LOUNGES --> List ' + str(len(lounges))
        for lounge in lounges:
            loungeInfo.append( {
                'Name' : lounge.get('Names').get('Name').get('$'),
                'Location' : lounge.get('Locations').get('Location')[1].get('$'),
                'OpeningHours' : lounge.get('OpeningHours')#.get('OpeningHours')[0].get('$')
            })
    else:
        print 'LOUNGES --> Single ' + str(len(lounges))
        loungeInfo.append( {
            'Name' : lounges.get('Names').get('Name').get('$'),
            'Location' : lounges.get('Locations').get('Location')[1].get('$'),
            'OpeningHours' : lounges.get('OpeningHours')#.get('OpeningHours')[0].get('$')
        })
#    print 'LOUNGEINFO --> ', str(loungeInfo)
    return loungeInfo
    