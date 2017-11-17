#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
import urllib
from google.appengine.api import urlfetch
import json
import random
import string
#google stuff
#for online development
clientID = "447665954215-b061ske9bctnk7fqjjb5rdm5f9vde718.apps.googleusercontent.com"
clientSecret = "nNTre703s2ayMTu_OyLiPPmD"

googleURL = "https://accounts.google.com/o/oauth2/v2/auth"
gplusURL = "https://www.googleapis.com/plus/v1/people/me"


homeURL = "https://mrfluff-183203.appspot.com"
redirectURI = "https://mrfluff-183203.appspot.com/oauth"


#load up the environments
JINJA_ENVIRONMENT = jinja2.Environment(
    autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/template"))


class MainHandler(webapp2.RequestHandler):
    def get(self):
        #construct url for oauth
        #make random state string
        state = "MagicKittenExpress"

        oAuthURL = googleURL + "?"
        oAuthURL += "scope=email"
        oAuthURL += '&access_type=offline'
        oAuthURL += "&include_granted_scopes=true"
        oAuthURL += "&state="
        oAuthURL += state
        oAuthURL += "&redirect_uri=" + redirectURI
        oAuthURL += "&response_type=code"
        oAuthURL += "&client_id=" + clientID

        templateVariables = {
            "backGround" : "/static/img/stupidCat.jpg",
            "url" : oAuthURL
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(templateVariables))


class NamePageHandler(webapp2.RequestHandler):
    def get(self):
        templateVariables = {"backGround" : "/static/img/stupidCat2.jpg"}
        template = JINJA_ENVIRONMENT.get_template('namePage.html')
        self.response.write(template.render(templateVariables))


class ErrorHandler(webapp2.RequestHandler):
    def get(self):
        templateVariables = {"backGround": "/static/img/stupidSadFuzzy.jpg"}
        template = JINJA_ENVIRONMENT.get_template('nope404.html')
        self.response.write(template.render(templateVariables))


class OAuthHandler(webapp2.RequestHandler):
    def get(self):
        state = self.request.GET['state']
        code = self.request.GET['code']
        #did the state get sent correctly?
        if(state != "MagicKittenExpress"):
            template = JINJA_ENVIRONMENT.get_template('nope404.html')
            self.response.write(template.render())
            return

        #build token request
        header = {'Content-Type':'application/x-www-form-urlencoded'}
        postVariables = {
            'code':code,
            'client_id': clientID,
            'client_secret': clientSecret,
            'redirect_uri': redirectURI,
            'grant_type': 'authorization_code'
        }

        encodedData = urllib.urlencode(postVariables)
        #request token
        result = urlfetch.fetch(url="https://www.googleapis.com/oauth2/v4/token/",
                                headers=header,
                                payload=encodedData,
                                method=urlfetch.POST)

        token = json.loads(result.content)

        header ={'Authorization':'Bearer '+ token['access_token']}
        response = urlfetch.fetch(gplusURL, headers=header, method=urlfetch.GET)

        gplusData = json.loads(response.content)
        name = gplusData["name"]["givenName"] + " " + gplusData["name"]["familyName"]

        #display data in the next page
        template = JINJA_ENVIRONMENT.get_template('namePage.html')
        templateVariables = {
            "backGround": "/static/img/stupidCat2.jpg",
            'userName': name,
            'email':gplusData['emails'][0]['value'],
            'state': state
        }

        self.response.write(template.render(templateVariables))



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/index.html', MainHandler),
    ('/namePage.html', NamePageHandler),
    ('/oauth', OAuthHandler),
    ('/.*', ErrorHandler)
], debug=True)
