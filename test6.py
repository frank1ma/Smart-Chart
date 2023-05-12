import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets,QtCharts

df = pd.DataFrame(columns=["index","x","y"])
# add new dataframe with index=1,x=1,y=2
df2 = pd.DataFrame([[12,12,1],[12,2,3],[1,2,3]], columns=["index","x","y"])
df3 = pd.DataFrame([[12,12],[12,2],[1,2]], columns=["x1","y1"])
#df3 = pd.DataFrame([[1,1,2]], columns=["index","x","y"])
ddf = pd.concat([df2, df3],axis=1)
print(ddf)