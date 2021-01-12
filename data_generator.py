import pandas as pd 
import random 
from datetime import datetime 
data = pd.DataFrame(columns=['time','type','ID','fill','lat','long','track']) 
a=0
b=11
for t in range (1,5):
    a=a+100
    b=b+100
    for k in range (a,b): 
        time_ts = 1577836800 
        fill = random.uniform(0, 4.0) 
        lat = random.uniform(50.04, 50.08) 
        long = random.uniform(19.91, 19.95) 
        for p in range(1, 1488):
            time_f = datetime.fromtimestamp(time_ts) 
            data.loc[len(data.index)] = [time_f,'CITY',str(k),fill,lat,long,str(t)] 
            fill = fill + random.uniform(0, 5.0) 
            mess = random.randint(0,300) 
            time_ts = time_ts + 1800 + mess 
            if fill > 83:
                fill = random.uniform(0, 4.0)
data.to_csv(path_or_buf=r'/home/ubuntu/final_heatmap_data.csv', index = False)
