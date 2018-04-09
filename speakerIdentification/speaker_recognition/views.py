from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from speaker_recognition.models import User
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

import json
import numpy as np
import librosa
import ast
from sklearn.neural_network import MLPClassifier
import pickle
import glob
import os
from operator import itemgetter
import uuid
np.set_printoptions(threshold=np.nan)

def createProfileView(request):
    if request.method == 'OPTIONS':
        return HttpResponse()

    if request.method == 'POST':
        uid = str(uuid.uuid4())
        query = User(identificationProfileId=uid, pathNN="Neural_Networks/"+uid+".sav", status=1, idCostumer_id=1)
        query.save()
        resultset = {}
        resultset['identificationProfileId']=uid
        json_data = json.dumps(resultset)
        return HttpResponse(json_data)

def enroll_view(request):
    if request.method == 'OPTIONS':
        return HttpResponse()

    if request.method == 'POST':
        thumbnail = request.FILES['audio']
        enroll_id = request.POST.get('enroll_id')
        fs = FileSystemStorage()
        filename = fs.save(thumbnail.name, thumbnail)
        uploaded_file_url = fs.url(filename)
        json_client = enroll(uploaded_file_url, enroll_id)
        fs.delete(thumbnail.name)
        return HttpResponse(json_client)

def enroll(uploaded_file_url, enroll_id):
    X, sample_rate = librosa.load(uploaded_file_url)
    file = open("EmpowerData/X_train.txt","r")
    X_train = ast.literal_eval(file.read())
    file.close()
    newenroll = True
    if len(X_train)!=0: #si exiten registros
        for searchlist in X_train:
            if searchlist[0] == enroll_id:
                moreenroll(X, sample_rate, searchlist, X_train)
                newenroll = False
                break;
        if newenroll == True:
            enrollfirsttime(enroll_id, X, sample_rate, X_train)
    else:
        enrollfirsttime(enroll_id,X,sample_rate,X_train)
    json_information=train()
    file.close()
    return json_information

def train():
    file = open("EmpowerData/X_train.txt", "r")
    X_train = ast.literal_eval(file.read())
    xtraindata = []
    lenxtrain = []
    idxtraindata = []
    size_ytrain = 0
    for all_xtrain in X_train:
        idxtraindata = idxtraindata + [all_xtrain[0]]
        xtraindata = xtraindata + all_xtrain[1]  ###crea la matriz X_train para clf
        lenxtrain = lenxtrain + [len(all_xtrain[1])]  ###crea un vector con las longitudes de los enroll de cada usuario
        size_ytrain = size_ytrain + len(all_xtrain[1])  ###obtiene la longitud que tendran los Y_train
    i = 0
    j = 0
    indexid = 0
    for ones in lenxtrain:
        Y_train = [0] * size_ytrain
        for i in range(i, ones):
            Y_train[j] = 1
            j += 1
        i = 0
        clf = MLPClassifier(hidden_layer_sizes=(280, 300, 10), activation='identity', solver='lbfgs', random_state=1, max_iter=200, learning_rate_init=0.01)
        clf.fit(np.asarray(xtraindata), np.asarray(Y_train))
        filenameclf = idxtraindata[indexid] + ".sav"
        pickle.dump(clf, open("Neural_Networks/" + filenameclf, 'wb'))
        indexid+=1
    resultset = {}
    resultset['Status'] = 'Success'
    json_data = json.dumps(resultset)
    return json_data


def moreenroll(X, sample_rate, searchlist, X_train):
    mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T
    mfccs = np.array(mfccs)
    i = 0
    while (i < len(mfccs)):
        vector = mfccs[i:i + 170]
        predict_vector = np.mean(vector, axis=0)
        searchlist[1].append(predict_vector.tolist())
        i += 171
    file = open("EmpowerData/X_train.txt", "w")
    file.write(str(X_train))
    file.close()

def enrollfirsttime(enroll_id, X, sample_rate, X_train):
    list_train = [enroll_id, []]
    mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T
    mfccs = np.array(mfccs)
    i = 0
    while (i < len(mfccs)):
        vector = mfccs[i:i + 170]
        predict_vector = np.mean(vector, axis=0)
        list_train[1].append(predict_vector.tolist())
        i += 171
    # file.write(np.array2string(mfccs, precision=8, separator=',', suppress_small=True))
    X_train.append(list_train)
    file = open("EmpowerData/X_train.txt", "w")
    file.write(str(X_train))
    file.close()

def identify_view(request):
    if request.method == 'OPTIONS':
        return HttpResponse()

    if request.method == 'POST':
        thumbnail = request.FILES['audio']
        fs = FileSystemStorage()
        filename = fs.save(thumbnail.name, thumbnail)
        uploaded_file_url = fs.url(filename)
        json_client = identify(uploaded_file_url)
        fs.delete(thumbnail.name)
        return HttpResponse(json_client)

def identify(uploaded_file_url):
    X, sample_rate = librosa.load(uploaded_file_url)
    mfccs = librosa.feature.mfcc(y=X, sr=sample_rate, n_mfcc=40).T
    data = np.asarray(mfccs)
    totalproba =0
    resultlist = []
    for path in glob.glob("Neural_Networks/*.sav"):
        dirname, filename = os.path.split(path)
        clf = pickle.load(open(path, 'rb'))
        i = 0
        count = 0
        probaNN = 0
        while(i<len(data)):
            vector = data[i:i+170]
            predict_vector = np.mean(vector, axis=0)
            probaNN += clf.predict_proba(predict_vector.reshape(1,-1))[0][1]
            count += 1
            i += 171 ###aproximadamente 3 segundos de audio
        resultlist = resultlist+[[filename,probaNN/count]]
        totalproba += (probaNN/count)
    print(clf.classes_)
    predictid = sorted(resultlist, key=itemgetter(1), reverse=True)[0]
    # print(sorted(resultlist, key=itemgetter(1), reverse=True)[0])
    # print(sorted(resultlist, key=itemgetter(1), reverse=True)[len(resultlist)-1])
    print([str(x) + '\n' for x in sorted(resultlist, key=itemgetter(1), reverse=True)])
    resultset = {}
    resultset['id_identification'] = str(predictid[0]).replace(".sav","")
    resultset['confidence'] = str((predictid[1]*100)/totalproba)
    json_data = json.dumps(resultset)
    return json_data

def unroll_view(request):
    if request.method == 'OPTIONS':
        return HttpResponse()

    if request.method == 'POST':
        enroll_id = request.POST.get('enroll_id')
        fs = FileSystemStorage()
        fs.delete("Neural_Networks/"+enroll_id+".sav")
        json_client = unroll(enroll_id)
        return HttpResponse(json_client)

def unroll(enroll_id):
    file = open("EmpowerData/X_train.txt", "r")
    X_train = ast.literal_eval(file.read())
    file.close()
    i=0
    for i in range(0,len(X_train)):
        if(X_train[i][0] == enroll_id):
            X_train.pop(i)
            break;
    file = open("EmpowerData/X_train.txt", "w")
    file.write(str(X_train))
    file.close()
    train()
    query = User.objects.get(identificationProfileId=enroll_id)
    query.status = 0
    query.save()
    resultset = {}
    resultset['Status'] = "Success"
    json_data = json.dumps(resultset)
    return json_data

# def formtest(request):
#     return render(request, "speaker_recognition/form.html")

# Create your views here.

# latest_question_list = Question.objects.all()
# question = get_object_or_404(Question, id=1)
# return render(request,"speaker_recognition/detail.html", {'question': question})
#return HttpResponse(output)
# data = {}
# data['key'] = 'superkey12346'
# json_data = json.dumps(data)
# return render(request, "speaker_recognition/detail.html", {'question': json_data})
######load model
# loaded_model = pickle.load(open(filename, 'rb'))
# result = loaded_model.score(X_test, Y_test)
# print(result)