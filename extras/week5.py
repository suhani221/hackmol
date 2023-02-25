import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

# Read data
df = pd.read_excel("preprocessed_data.xlsx")
# question3
instruments = df['instrument']

def jaccard_index(a, b):
    """Compute Jaccard index for two sets a and b."""
    f = 0
    d=0
    e=0
    for i in range(len(a)):
        if (a[i]==b[i] and a[i]==1):
            f +=1
        if (a[i]==0 and b[i]==1):
            d+=1
        if (a[i]==1 and b[i]==0):
            e +=1
    return (1-(f/(f+d+e)))

jaccard = []
for i in range(len(instruments)):
    for j in range(i+1, len(instruments)):
        print(instruments.iloc[i], instruments.iloc[j])
        first = instruments.iloc[i].replace('(', '')
        first = first.replace(')', '')
        second = instruments.iloc[j].replace('(', '')
        second = second.replace(')', '')
        first = tuple(map(int, first.split(',')))
        second = tuple(map(int, second.split(',')))
        print((i, j, jaccard_index(first, second)))
        jaccard.append((i, j, jaccard_index(first, second)))


# Sort pairs by Jaccard index
jaccard = sorted(jaccard, key=lambda x: x[2], reverse=True)

# Print pairs with highest modified Jaccard index
print("Pairs with highest modified Jaccard index:")
for pair in jaccard[:5]:
    print(f"Pair {pair[0]} and {pair[1]} have modified Jaccard index {pair[2]:.3f}")


# # question4
df['Date_Start'] = pd.to_datetime(df['start_time'])
df['Date_Start'] = df['Date_Start'].dt.date
df['Date_Start'] = pd.to_datetime(df['Date_Start'])


df['start time'] = pd.to_datetime((df['start_time'].apply(pd.Timestamp)).astype(str))
df['start time'] = (df['start time'].apply(pd.Timestamp)).dt.time

df['Date_end'] = pd.to_datetime(df['comp_time'])
df['Date_end'] = df['Date_end'].dt.date
df['Date_end'] = pd.to_datetime(df['Date_end'])


df['end time'] = pd.to_datetime((df['comp_time'].apply(pd.Timestamp)).astype(str))
df['end time'] = (df['end time'].apply(pd.Timestamp)).dt.time

df.drop(['Date_end'], axis=1, inplace=True)


df['seconds'] = df['end time'].apply(lambda x: x.hour*3600 + x.minute*60 + x.second) - df['start time'].apply(lambda x: x.hour*3600 + x.minute*60 + x.second)

def find_close(df, height, nose_length):
    df['height_diff'] = abs(df['height'] - height)
    df['nose_length_diff'] = abs(df['nose_length'] - nose_length)
    df['time_diff'] = abs(df['seconds'] - 480)
    df['total_diff'] = df['height_diff'] + df['nose_length_diff'] + df['time_diff']
    return df.sort_values(by='total_diff').head(1)

print(find_close(df, 178, 6.096))

#Question 5
slope, intercept, regress, p, std_err = stats.linregress(df['hand_length_left'],df['hand_length_right'])
plt.scatter(df["hand_length_left"],df["hand_length_right"])
plt.plot(df["hand_length_left"],intercept + slope*df['hand_length_left'],label = 'best_fit_line',color='black')
plt.xlabel("Left Hand Distance")
plt.ylabel("Right Hand Distance")
plt.title("scatterplot")
plt.savefig("q5.png")
plt.show()

expected_slope = 1
percent_deviation = abs(slope - expected_slope) / expected_slope * 100
print(round(percent_deviation, 3), '%')

# box plot
count_row = df.shape[0] 
df["diff"] = 0
for i in range(count_row):
    df["diff"][i] = abs(df["hand_length_left"][i] - df["hand_length_right"][i])
plt.boxplot(df["diff"])
plt.title("BoxPlot")
plt.savefig("q5a.png")
plt.show()

q1 = np.percentile(df["diff"],25)
q3 = np.percentile(df["diff"], 75)  
inter_quartile = q3 - q1
temp1 = q1 - 1.5*inter_quartile
temp2 = q3 + 1.5*inter_quartile
df.drop(df.loc[(df['diff']<temp1) |(df["diff"]>temp2)].index,inplace =True)
slope, intercept, regress, p, std_err = stats.linregress(df['hand_length_left'],df['hand_length_right'])
plt.scatter(df["hand_length_left"],df["hand_length_right"])
plt.plot(df["hand_length_left"],intercept + slope*df['hand_length_left'],label = 'best_fit_line',color='black')
plt.xlabel("Left Hand Distance")
plt.ylabel("Right Hand Distance")
plt.title("scatterplot")
plt.savefig("q5b.png")
plt.show()
expected_slope = 1
percent_deviation = abs(slope - expected_slope) / expected_slope * 100
print(round(percent_deviation, 3), '%')