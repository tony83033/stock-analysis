import pandas as pd
import numpy as np
import pymongo
import plotly.express as px
from bson.decimal128 import Decimal128, create_decimal128_context
import decimal
import plotly.graph_objects as go
import sys

from main import mean_and_median
# Increase number of recursion  
sys.setrecursionlimit(100000)
fig = go.Figure()
fig2 = go.Figure()
# Connect to mondoDB
client = pymongo.MongoClient('localhost', 27017)
# Connect to forx_database
db = client['forx_database']
# Connect to collection rowdata
collection = db['rowdata']
# Fetch all data from rowdata
cursor = collection.find({}).limit(10000)
df = pd.DataFrame(cursor)

class analyze:   
    def showdata(self):
        print(df.head())

    def findindex(self,time,mytag):
        global df
        # Fetch Start time 
        start_time = df['Local time'].head(1)
        # Change start time dtype to pandaDatetime 
        start_time = pd.to_datetime(start_time)
        # calculating End time
        end_time   = start_time + pd.to_timedelta(time,'s')
        # Print End Time
        print(end_time)
        # Finding Index for End time
        time_list = df['Local time']
        # Making a list with length of time_tist
        find_index = [None] * (len(time_list))
        # Making a numpy array with a dtype bool
        compare1 = np.array([True], dtype=bool)
        hint = False
        for i in range(len(find_index)):
            find_index[i] = [time_list[i] > end_time]
            if(find_index[i]==compare1[0]):
                print(i)
                # Making a Second Dataframe to index i
                df2 = df.iloc[:i]
                hint = True
                # Drope Dataframe to index i
                df = df.drop(range(0,i))
                # Reset Index of Dataframe
                df = df.reset_index(drop=True)
                break
        if(hint):
            self.mean_median(df2,mytag,time,end_time)
            
        else:
            fig.show()
            self.mean_median_graph(mytag)
    
    def mean_median(self,df2,mytag,time,end_time):
        
        mymean = df2['Ask'].mean() 
        mymedian = df2['Ask'].median()
        print(mymean)
        post = {
        "Time": str(end_time),
        "mean": mymean,
        "median": mymedian
        }

        collection = db[str(mytag)]
        post_id = collection.insert_one(post).inserted_id
        print(post_id)


        print("Done")
        self.make_graph(df2,end_time,time,mytag)
    
    def make_graph(self,df2,end_time,time,mytag):
        ##collection = db[str(mytag)]
        #data = collection.find({}).sort({"_id":pymongo.ASCENDING}).limit(1)
        #print("Previes mead == ",data.get('mean'))
        fig.add_trace(go.Violin(y=df2['Ask'],
                    # x0=my_time[s1],
                    legendgroup='chart',
                    name='my chart',
                    line_color='green',
                    y0="Time",
                    
                    ))
        fig.update_traces(box_visible=True, meanline_visible=True)
        fig.update_layout(violinmode='group')
        
        self.findindex(time,mytag)

    def mean_median_graph(self,mytag):
        
        collection = db[mytag]
        alldata = collection.find({})
        alldata = pd.DataFrame(alldata)
        #print(alldata.head())
        #alldata = px.data.gapminder().query("continent=='Oceania'")
        #fig2.add_trace(line(alldata, x="Time", y="mean"))   
        #fig2 = px.line(alldata, x="Time", y="mean")
        fig2 = px.line(alldata,y="mean")
        fig2.show()
        self.smp(mytag)
    def smp(self,mytag):
        collection = db[mytag]
        data = collection.find({})
        data = pd.DataFrame(data)
        df3 = data['mean']

        windows = df3.expanding()

        moving_averages = windows.mean()
        moving_averages_list = moving_averages.tolist()
        print("Movingavariage is = ",moving_averages_list)

        fig3 = px.line(moving_averages_list)
        fig3.show()
        




if __name__ == "__main__":
    
    myanalyze = analyze()
    while (True):
        mymessage =  ''' ====Welcome====
                    Please chose an options
                    1) Enter time for analysis
                    2) show data frame
                    3) Exit 
                    '''
        print(mymessage)
        try:
            b = int(input("Enter any choise: "))
        except NameError:
            print("Invalid Input")
            continue
        if(b==1):
            time = int(input("Enter time in minutes : "))
            time = time *60
            mytag = input("Enter a Tag: ")
            myanalyze.findindex(time,mytag)
        elif(b==2):
            myanalyze.showdata()
        elif(b==3):
            exit()
        else:
            print("Invalid Input")



        






