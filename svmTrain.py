'''
Created on Mar 2, 2016

@author: incognito
'''
import random
def load_data(folder,label,X,Y,test_x,test_y):
    for k in range(100):
        name=folder+"/"+str(k)
        file=open(name,'r')
        mylist=[]
        for line in file:
            line=line[:-1]
            temp=line.split(',')
            for i in range(len(temp)):
                mylist.append(float(temp[i]))
        mylist=mylist+[0]*(5*50-len(mylist))
        if k%5!=0:
            X.append(mylist)
            Y.append(label)
        else:
            test_x.append(mylist)
            test_y.append(label)
#     print len(test_x),len(test_y),len(X),len(Y)
    
def trainModel():
    from sklearn import svm
    X=[]
    Y=[]
    test_x=[]
    test_y=[]
    load_data("play", 0, X, Y,test_x,test_y)
    load_data("stop", 1, X, Y,test_x,test_y)
    load_data("next", 2, X, Y,test_x,test_y)
    load_data("prev", 3, X, Y,test_x,test_y)
    load_data("ff", 4, X, Y,test_x,test_y)
    load_data("ff2", 5, X, Y,test_x,test_y)
    load_data("rewind", 6, X, Y,test_x,test_y)
    load_data("rewind2", 7, X, Y,test_x,test_y)
    load_data("like", 8 , X, Y,test_x,test_y)
    load_data("unlike", 9, X, Y,test_x,test_y)
    combined = zip(X, Y)
    random.shuffle(combined)
    X[:], Y[:] = zip(*combined)
#     print Y
    print "start learning..."
    for kk, dd, gg, cc in [('linear', 0, 0, 0)]:
        # Fit the model
        clf = svm.SVC(kernel=kk, degree=dd, coef0=cc, gamma=gg)
        clf.fit(X, Y)
        
        y_predict=clf.predict(test_x)
        correct=0
        for i in range(len(y_predict)):
            if y_predict[i]==test_y[i]:
                correct+=1
        accuracy=(correct+0.0)/len(y_predict)
        accuracy=accuracy*100
        print kk, accuracy
        return clf
             
trainModel()