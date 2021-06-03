add = 0
def power(a,b):
    answer = 1 
    for x in range (1,b+1):
        answer = answer*a 
    return(answer)        


for i in range(1,1001): 
    add = add+power(i,i) % pow(10,10)
    print(add % pow(10,10))

