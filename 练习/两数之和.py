n = [1,2,34,5,6,7,8,9,0,89,67,33]
t = 34


for i in range(len(n)):
    for j in range(i + 1,len(n)):
        if n[i] +n[j] == t:
            print(i,j)


