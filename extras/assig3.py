# Compute Jaccard index for all pairs of instances

import pandas as pd

# Read data

df = pd.read_excel("data.xlsx")
instruments=df["instrument"].apply(lambda x: set(x))
print(instruments)

def jaccard_index(a, b):
    """Compute Jaccard index for two sets a and b."""
    return len(a & b) / len(a | b)

jaccard = []
for i in range(len(instruments)):
    # print(i)
    for j in range(i+1, len(instruments)):
        # print(j)
        jaccard.append((i, j, jaccard_index(instruments[i], instruments[j])))

# Sort pairs by Jaccard index
jaccard = sorted(jaccard, key=lambda x: x[2])
print(jaccard)
# Print pairs with lowest Jaccard index
# print("Pairs with lowest Jaccard index:")
# for pair in jaccard[:5]:
#     print(f"Pair {pair[0]} and {pair[1]} have Jaccard index {pair[2]:.3f}")

