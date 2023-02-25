import numpy as np
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

    return (f,d,e , f/(f+d+e))

print(jaccard_index((0,1,0,0,0,1,0,0,1),( 0,0,1,0,0,0,0,0,1)))


