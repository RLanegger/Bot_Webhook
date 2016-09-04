class Token:
    
    def __init__(self ,url ,client_id , client_secret):
        self.authUrl = url
        self.client_id = client_id
        self.grant_type = 'client_credentials'
        self.client_secret = client_secret
        self.access_token = ''
        self.isAuthenticated = False
        self.requests = __import__('requests')
        #import requests, datetime , os
    
    def authenticate(self):
        header_auth = { 'client_id' : self.client_id, 'client_secret': self.client_secret, 'grant_type' : self.grant_type }
        #try:
        r = self.requests.post(self.authUrl , data = header_auth)
        j =  r.json() 
#        access_token = { 'Authorization': 'Bearer ' + j['access_token']}
        if r.status_code > 299:
            raise URLError('No access token retrieved! :')
            print 'Error in  Authorization'
        else:
            self.access_token = j['access_token']
            self.isAuthenticated = True 
            print 'Successful authorized'
	            #return token
        #except URLError, e:
        #   print 'Error: ', e
	 #   else:
     
     #	    request = ('https://api.lufthansa.com/v1/oauth/token')
     #	    url = ('https://api.lufthansa.com/v1/oauth/token')