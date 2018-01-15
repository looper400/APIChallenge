from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
import requests
import json
import pandas as pd
from collections import OrderedDict

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
api = Api(app)
username='looper4000@gmail.com'
password='fremont1'

class AttPublicRepo(Resource):
    def get(self):
        #Creating a dataframe to store repository details
        df_repos = pd.DataFrame(columns=('Repo_Name','Repo_Full_Name'))
        #Creating a dataframe to store Issues information
        df_issues = pd.DataFrame(columns=('Issue_Title','Issue_Body','Comments_Link','Repo_Name','Issue_Number'))
        #Creating a dataframe to store Comments information
        df_comments = pd.DataFrame(columns=('Comments_Details','Issue_Number'))
        # Get to fetch ATT public reposigtory information
        req = requests.get("https://api.github.com/orgs/att/repos?type=public",auth=(username, password))
        jdata = json.loads(req.content)
        
        for jd in jdata:
            df_repos.loc[len(df_repos)] = [jd['name'],jd['full_name']]
        for index, i in df_repos.iterrows():
            r1 = "https://api.github.com/repos/att/"+i[0]+"/issues?state=open" #Hitting the github url for att repo to get issues data 
            req1 = requests.get(r1,auth=(username, password))
            jissuedata = json.loads(req1.content)
            for jid in jissuedata:
                df_issues.loc[len(df_issues)] = [jid['title'],jid['body'],jid['comments_url'],i[0],jid['number']]
        for index, i in df_issues.iterrows():
            req2 = requests.get(i[2],auth=(username, password)) #Hitting comments API to fetch comments information
            jcommentsdata = json.loads(req2.content)
            for jcd in jcommentsdata:
                df_comments.loc[len(df_comments)] = [jcd['body'],i[4]]
        #merge the repo name, issue and comments data
        df_1 = pd.merge(df_repos,df_issues,on='Repo_Name')
        df_2 = pd.merge(df_1,df_comments,on='Issue_Number')
        df_2 = df_2[['Repo_Name','Repo_Full_Name','Issue_Number','Issue_Title','Issue_Body','Comments_Details','Comments_Link']]
        df_3_1 = df_2.drop('Repo_Full_Name',axis=1)
        df_3 = df_3_1.drop('Issue_Number',axis=1)
        print list(df_3)
        result = {'data' : [OrderedDict(zip(tuple (list(df_3)), i)) for index, i in df_3.iterrows()]}
        return jsonify(result,sort_keys=False)

api.add_resource(AttPublicRepo, '/attpublicrepo') 

if __name__ == '__main__':
     app.run(port=5022) 
