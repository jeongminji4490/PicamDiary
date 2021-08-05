import cv2
import numpy as np
import tkinter
import sqlite3
import json
import tkinter.filedialog
import PIL.Image
import tkinter.ttk
import os
from os import listdir
from os.path import isfile, join
from tkinter import messagebox
from PIL import Image
from PIL import ImageTk
from keras.preprocessing.image import img_to_array
from keras.models import load_model

"""사진이 저장될 폴더(faces)와 일기장이 저장될 폴더(diary)를 모두 동일한 디렉토리(Journal-master)에 넣었습니당"""
data_path = 'faces/' # 사진이 저장될 폴더 경로
diary_path = 'diary/' # 일기장이 저장될 폴더 경로
"""위에 폴더가 생성된 채로 zip파일로 보냅니다. 혹시 위의 폴더를 찾을 수 없다는 오류가 생기면 해당 폴더들을 삭제하고, 다시 동일한 이름으로 생성해서 실행해주세요!"""
#
data = {}  # json_dictionary

loadFileList = [f for f in listdir(diary_path) if isfile(join(diary_path, f))]
print(loadFileList)  # 해당 폴더에 있는 파일 목록 출력
search = 'Journal-master'

onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# haarcascade_frontalface_default.xml : 정면 얼굴인식용 xml
# CascadeClassifier : 객체 이미지와 객체가 아닌 이미지를 cascade함수로 트레이닝 시켜 객체 검출

# 데이터베이스 생성
con = sqlite3.connect("test.db")  # db생성 후 연결
cur = con.cursor()
sql = "CREATE TABLE IF NOT EXISTS newUser (name TEXT, dp TEXT, stdNum TEXT)"  # 쿼리문 생성, user라는 테이블이 db내에 존재하지 않을 경우 user 테이블 생성
cur.execute(sql)  # 쿼리문 실행(테이블 생성)
con.commit()  # db에 반영

emotion_classifier = load_model('files/emotion_model.hdf5', compile=False)  # 표정인식
EMOTIONS = ["Angry", "Disgusting", "Fearful", "Happy", "Sad", "Surpring", "Neutral"]

root = tkinter.Tk()  # 초기화면

"""
일기보기 오류
1. 일기 제목을 클릭해서 내용/사진을 확인하는건 오류 x
2. 일기 제목을 클릭하지 않고, 바로 검색을 했을 경우 사진과 내용은 뜨지만 날짜/요일/기분이 뜨지 않음 -> searchDiary 부분 수정 ===> 해결!!
3. 검색된 일기 제목을 누르고, 내용 보기 버튼을 누르면 가장 첫번째 일기장의 내용과 그림이 뜸 -> 검색했을 때 검색한 제목에 해당하는 일기장과 그림은 잘 뜨므로, 내용보기 버튼을 또 누를 필요는 없는 것 같아서 버튼 비활성화 ===> 해결!!
"""

def loadPhotoFile(text): #내 PC에서 사진 불러오기
    pfilename = tkinter.filedialog.askopenfilename(initialdir="/", title="사진 불러오기",  filetypes=(("JPG files", "*.jpg"),("all files", "*.*")))
    text.config(text = pfilename)
    text.place(x=40, y=280)  # 라벨을 이미지경로로 업데이트, 사진 줄이기
    data['image'] = pfilename  # 해당 json 파일에 image key를 추가하고, value로 이미지경로 + 이미지명 저장

def readToJson(index, text, text2, text3, text4, tk): #일기(제목,내용,날짜,기분),이미지 위젯에 로드
    with open(diary_path + loadFileList[index], 'r', encoding='utf-8') as json_file:  # 해당 파일명으로
        global image1
        json_data = json.load(json_file)  # json 파일 불러오기
        json_string = json_data["Content"]  # 일기장 내용(Content)을 추출하여 string 변수에 저장
        json_image = json_data["image"]  # 이미지 경로(image)를 추출하여 string 변수에 저장
        json_date = json_data['Date']  # 날짜를 추출하여 string 변수에 저장
        json_week = json_data['dayOfWeek']  # 요일을 추출하여 string변수에 저장
        json_feelings = json_data['feeling']  # 기분을 추출하여 string 변수에 저장
        text.config(text=json_string)  # 라벨을 추출한 일기장 내용으로 업데이트
        text.place(x=375, y=80)
        text2.config(text=json_date)  # 라벨을 추출한 날짜로 업데이트
        text2.place(x=377, y=30)
        text3.config(text=json_week)  # 라벨을 추출한 요일로 업데이트
        text3.place(x=442, y=30)
        text4.config(text=json_feelings)  # 라벨을 추출한 기분으로 업데이트
        text4.place(x=585, y=30)

        imageFrame1 = PIL.Image.open(json_image)  # 이미지를 추출하여 라벨에 저장
        imageFrame2 = imageFrame1.resize((250, 159), PIL.Image.ANTIALIAS)  # 이미지 크기 조절
        image1 = ImageTk.PhotoImage(imageFrame2, master=tk)  # master 설정 안해주면 오류
        imageLabel = tkinter.Label(tk, image=image1).place(x=30, y=270)  # 라벨을 추출한 이미지로 업데이트

def searchDiary(searchText,listbox,content,tk,imageLabel,date,week,feeling): # 일기장 검색 함수
    if searchText in loadFileList:  # 만약 리스트 내 원소에 searchText와 동일한 제목의 일기장이 존재하면
        listbox.insert(0, searchText)  # 리스트박스의 0번째 데이터로 추가
        with open(diary_path + searchText, 'r', encoding='utf-8') as json_file:  # 해당 파일명으로 열기
            global image1
            json_data = json.load(json_file)  # json 파일 불러오기
            json_string = json_data["Content"]  # 일기장 내용(Content)을 추출하여 string 변수에 저장
            json_image = json_data["image"]  # 이미지 경로(image)를 추출하여 string 변수에 저장
            json_date = json_data['Date']  # 날짜를 추출하여 string 변수에 저장
            json_week = json_data['dayOfWeek']  # 요일을 추출하여 string변수에 저장
            json_feelings = json_data['feeling']  # 기분을 추출하여 string 변수에 저장
            content.config(text=json_string)
            content.place(x=375, y=80)
            imageFrame1 = PIL.Image.open(json_image)
            imageFrame2 = imageFrame1.resize((250, 159), PIL.Image.ANTIALIAS)  # 이미지 크기 조절
            image1 = ImageTk.PhotoImage(imageFrame2, master=tk)  # master 설정 안해주면 오류
            imageLabel = tkinter.Label(tk, image=image1).place(x=30, y=270)
            date.config(text=json_date)
            date.place(x=377, y=30)
            week.config(text=json_week)
            week.place(x=442, y=30)
            feeling.config(text=json_feelings)
            feeling.place(x=585, y=30)
            disabledBtn = tkinter.Button(tk, text="내용 보기", state=tkinter.DISABLED).place(x=215, y=215)  # 내용보기 비활성화 버튼
    listbox.delete(1, listbox.size())  # 검색된 일기장 제목만 보이게 하기
    listbox.place(x=30, y=80)

def deleteItem(index,listbox,text,tk,imageLabel): #일기장 삭제 함수
    global delImage3
    with open(diary_path + loadFileList[index], 'r', encoding='utf-8') as json_file:
        json_data = json.load(json_file)
        json_title = json_data["Title"]
        json_file.close()  # 오픈한 파일 닫고
        os.remove(diary_path+json_title)  # 해당 파일 삭제
    listbox.delete(index)  # 인덱스에 해당하는 리스트박스 데이터도 삭제
    text.config(text="삭제")  # 삭제된 일기장의 내용을 "삭제"로 바꿈
    text.place(x=370, y=80)
    delImage1 = PIL.Image.open('그림판_삭제.jpg')  # 삭제 기본 이미지
    delImage2 = delImage1.resize((250, 159), PIL.Image.ANTIALIAS)  # 이미지 크기 조절
    delImage3 = ImageTk.PhotoImage(delImage2, master=tk)  # master 설정 안해주면 오류
    imageLabel = tkinter.Label(tk, image=delImage3).place(x=30, y=270)

def viewDiaryList(): #일기 보기 함수
    diaryList = tkinter.Tk()
    diaryList.geometry('660x480')

    diaryList.title('PicamDiary')

    showtitle = tkinter.Label(diaryList, text="List")
    showtitle.place(x=30, y=60)

    showdiary = tkinter.Label(diaryList, text="content")
    showdiary.place(x=370, y=80)

    showimage = tkinter.Label(diaryList, text="image file")
    showimage.place(x=30, y=340)

    frame = tkinter.Frame(diaryList, width=38, height=8, relief='solid')
    frame.place(x=10, y=111)

    inputListBox = tkinter.Listbox(diaryList, relief='solid', selectmode='extended', fg='black', width=35,
                                   height=8)  # 저장된 파일들을 보여줄 리스트박스 객체, 왼쪽 꽉 채우기

    # 스크롤바 생성
    scrollBar = tkinter.Scrollbar(diaryList, orient='vertical', command=inputListBox.yview)
    scrollBar.pack(side="right", fill="y")
    #inputListBox.pack(side="left", fill="both", expand=True)
    inputListBox.config(yscrollcommand=scrollBar.set)

    searchEntry = tkinter.Entry(diaryList, width=25, relief='solid') #검색창
    searchEntry.place(x=30, y=23)

    # 사진 기본 이미지
    imagelabel = tkinter.Label(diaryList, wraplength=0,
                               text="image", relief='sunken', fg="white", bg='black', bd=1,
                               width=35, height=10)
    imagelabel.place(x=30, y=270)

    # 날짜/요일/기분 텍스트들의 배경이 될 라벨, 회색으로 지정
    MemoLabel = tkinter.Label(diaryList, wraplength=0,
                              relief='solid', bg="gray95", bd=1, width=36, height=2)
    MemoLabel.place(x=375, y=23)

    showfeeling = tkinter.Label(diaryList, text="기분:", justify='left', anchor='nw', fg="black", bg="gray95",
                                width=8, height=1)
    showfeeling.place(x=555, y=30)

    feelingImage = Image.open('happyS.png')  # 기분이미지1
    feelingImage2 = feelingImage.resize((18, 18), Image.ANTIALIAS)
    feelingImage3 = ImageTk.PhotoImage(feelingImage2, master=diaryList)
    feelingLabel = tkinter.Label(diaryList, image=feelingImage3).place(x=515, y=29)

    feelingImages = Image.open('sadS.png')  # 기분이미지2
    feelingImages2 = feelingImages.resize((18, 18), Image.ANTIALIAS)
    feelingImages3 = ImageTk.PhotoImage(feelingImages2, master=diaryList)
    feelingLabels = tkinter.Label(diaryList, image=feelingImages3).place(x=535, y=29)

    searchBtn = tkinter.Button(diaryList, text='검색', width=7, command=lambda:searchDiary(searchEntry.get(),inputListBox,outputLabel,diaryList,imagelabel,outputLabel2,
                                                        outputLabel3,
                                                        outputLabel4)).place(x=215, y=15)  # 검색버튼

    loadBtn = tkinter.Button(diaryList, text='내용 보기',
                             command=lambda: readToJson(inputListBox.index(inputListBox.curselection()),
                                                        outputLabel,
                                                        outputLabel2,
                                                        outputLabel3,
                                                        outputLabel4,
                                                        diaryList), bg='black',fg='white',relief='ridge').place(x=215, y=215)
    outputLabel = tkinter.Label(diaryList, anchor='nw', justify='left', wraplength=270,
                                text="내용", relief='solid', fg="black", bg='white', bd=1,
                                width=36, height=23)  # 각 파일의 내용만 출력해서 보여줄 라벨
    outputLabel.place(x=375, y=80)

    outputLabel2 = tkinter.Label(diaryList,
                                 text="날짜:", justify='left', anchor='nw', fg="black", bg="gray95",
                                 width=10, height=1)
    outputLabel2.place(x=377, y=30)

    outputLabel3 = tkinter.Label(diaryList,
                                 text="요일:", justify='left', anchor='nw', fg="black", bg="gray95",
                                 width=6, height=1)
    outputLabel3.place(x=442, y=30)

    outputLabel4 = tkinter.Label(diaryList,
                                 width=5, height=1, fg="black", bg="gray95")
    outputLabel4.place(x=585, y=30)
    deleteBtn = tkinter.Button(diaryList, fg='white', bg='IndianRed1', text="삭제", width=10,
                               command=lambda: deleteItem(inputListBox.index(inputListBox.curselection()), inputListBox, outputLabel, diaryList, imagelabel)).place(x=550, y=435)

    for i, word in enumerate(loadFileList):  # 리스트박스에 파일 제목 띄우기
        if search in word:  # 만약 리스트 내 원소에 search변수 문자열이 존재하면
            loadFileList[i] = word.strip(search)  # 그 문자열만 삭제해서
        inputListBox.insert(i, loadFileList[i])  # 리스트박스에 추가
        inputListBox.place(x=30, y=80)  # grid(row=3, column=1,padx=10,pady=30)#place(x=0,y=0)#grid(row=3, column=1)
    diaryList.mainloop()

# dump : 파이썬 객체를 json 형식으로 변환
def writeToJson(filename, data): #json 파일 생성 후 저장
    with open(diary_path + filename, 'w', encoding='utf-8')as make_file:
        json.dump(data, make_file, ensure_ascii=False, indent="\t")
    #json.dump(data, path, ensure_ascii=False) #ensure_ascii를 False로 선언해주면 유니코드가 아닌 한글로 저장됨

def check(Name,Role,Date,weekDay,feeling): #딕셔너리에 일기장 데이터를 저장하고, json 파일을 생성하는 함수
    a = Name.get("1.0", 'end-1c')  # 제목
    c = Role.get("1.0", 'end-1c')  # 내용
    d = Date.get("1.0", 'end-1c')  # 날짜
    #dictionary index
    data['Title'] = a
    data['Content'] = c
    data['Date'] = d
    data['dayOfWeek'] = weekDay
    data['feeling'] = feeling
    files = [('Json File', '*.json')]  # 파일 형식
    fileName = a  # 파일명 = 제목으로.
    writeToJson(fileName, data)
    registerOk = tkinter.messagebox.showinfo("Message", "Diary is registered.")

def writeDiary(): #일기 작성 함수
    wdDisplay = tkinter.Tk()
    wdDisplay.geometry('570x438')
    wdDisplay.title('Please fill in all fields')
    warnLabel = tkinter.Label(wdDisplay, text="The created diary will be updated only when the program is restarted.", fg='black').place(x=10, y=7)
    Date = tkinter.Text(wdDisplay, width=30, height=2, relief="solid")
    Date.insert(1.0, "Date")
    Date.place(x=12, y=50)
    dayofWeek = tkinter.ttk.Combobox(wdDisplay, width=12, font="Arial")  # 요일 선택 콤보박스
    dayofWeek['values'] = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    dayofWeek.place(x=236, y=50)
    dayofWeek.current(0)  # value의 가장 첫번째 데이터를 디폴트 텍스트로 선언
    feeling = tkinter.ttk.Combobox(wdDisplay, width=12, font="Arial")  # 기분 선택 콤보박스
    feeling['value'] = ('Happy', 'Soso', 'Fresh', 'Depressed', 'Annoyed', 'Angry')
    feeling.place(x=400, y=50)
    feeling.current(0)
    Name = tkinter.Text(wdDisplay, width=77, height=2, relief="solid")
    Name.insert(1.0, "title")
    Name.place(x=12, y=95)
    Role = tkinter.Text(wdDisplay, width=77, height=10, relief="solid")
    Role.insert(1.0, "content")
    Role.place(x=12, y=140)
    imageLinkLabel = tkinter.Label(wdDisplay, text="Image link").place(x=12, y=280)
    photoUtl = tkinter.Label(wdDisplay, fg="black")
    loadPhoto = tkinter.Button(wdDisplay, text='Upload photo', width=30, fg='white', bg='gray63', font=("Arial", "15"), command=lambda: loadPhotoFile(photoUtl)).place(x=120,y=310)
    submit = tkinter.Button(wdDisplay, text='Save Diary', fg='white', bg='gray40', font=("Arial", "15"), command=lambda: check(Name, Role, Date, dayofWeek.get(), feeling.get()), width=30).place(x=120, y=360)
    wdDisplay.mainloop()

def playEmotion():  # 표정 인식 함수
    camera = cv2.VideoCapture(0)  # 웹캠 open
    name = 1  # 캡쳐된 사진파일명에 붙을 정, 캡쳐할 때마다 1씩 증가
    while True:
        ret, frame = camera.read()  # 캡쳐 프레임
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_classifier.detectMultiScale(gray,
                                                 scaleFactor=1.1,
                                                 minNeighbors=5,
                                                 minSize=(30, 30))
        canvas = np.zeros((250, 300, 3), dtype="uint8")

        if len(faces) > 0:
            face = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = face
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]

            cv2.putText(frame, label, (fX, fY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH), (0, 0, 255), 2)

            for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
                text = "{}: {:.2f}%".format(emotion, prob * 100)
                w = int(prob * 300)
                cv2.rectangle(canvas, (7, (i * 35) + 5), (w, (i * 35) + 35), (0, 0, 255), -1)
                cv2.putText(canvas, text, (10, (i * 35) + 23), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)

        cv2.imshow('Enter R for few seconds if you want Exit', frame)
        cv2.imshow("Probabilities", canvas)

        if cv2.waitKey(1) & 0xFF == ord('c'):  # c를 누르면 캡쳐, FaceRecognition.py가 있는 곳과 동일한 디렉토리에 캡쳐사진이 저장됩니다!
            ret, frame = camera.read()
            cv2.imwrite("user" + str(name) + ".jpg", frame)  # 저장되는 캡쳐사진 파일명 예시) user1.png
            print("save image")
            name += 1

        if cv2.waitKey(1) & 0xFF == ord('r'):  # q를 누르면 표정인식 종료
            break

    camera.release()
    cv2.destroyAllWindows()

def goMainWindow():  # 메인화면으로 이동하는 함수
    mainWindow = tkinter.Tk()  # 메인화면 생성
    mainWindow.geometry("755x405")  # 화면 크기 조절
    mainWindow.title("PicamDiary")  # 화면 타이틀
    subLabel = tkinter.Label(mainWindow, text="Welcome to", fg="black", font=("Arial", "17")).place(x=310, y=60)
    mainLabel1 = tkinter.Label(mainWindow, text="PiCamDiary", fg="black", font=("Arial", "30")).place(x=270, y=100)
    bt3 = tkinter.Button(mainWindow, text="Face Recognition", width=20, height=1, fg='black', bg="white", font=("Arial", "15"),
                         command=playEmotion).place(x=260, y=170)
    bt4 = tkinter.Button(mainWindow, text="Write Diary", width=20, height=1, fg='white', bg="gray63", font=("Arial", "15"),
                         command=writeDiary).place(x=260, y=220)
    bt5 = tkinter.Button(mainWindow, text="View Diary", width=20, height=1, fg='black', bg="gray40", font=("Arial", "15"), command=viewDiaryList).place(x=260, y=270)
    mainWindow.mainloop()


# 전체 사진에서 얼굴만 잘라 리턴하는 함수
def face_extractor(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 흑백처리
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)  # 얼굴 찾기
    # detectMultiScale : 입력 이미지에서 크기가 다른 객체 검출

    if faces is ():  # 찾는 얼굴이 없으면 none 리턴
        return None

    for (x, y, w, h) in faces:  # 얼굴이 있으면
        cropped_face = img[y:y + h, x:x + w]  # 해당 얼굴 크기만큼 cropped_face에 잘라넣기

    return cropped_face


def playWebCam(tk):  # 최초 등록 시 얼굴을 추출하기 위한 함수
    cap = cv2.VideoCapture(0)  # 웹캠  실행
    count = 0  # 저장할 이미지 카운트 변수
    while True:
        ret, frame = cap.read()  # 카메라로부터 사진 1장 얻기
        if face_extractor(frame) is not None:  # 얼굴을 감지해서 얼굴만 가져옴, 얼굴이 존재한다면
            count += 1  # 사진 한장 증가할 때마다 count도 1씩 증가
            face = cv2.resize(face_extractor(frame), (200, 200))  # 이미지 크기를 200X200으로 조절
            # resize : 이미지 크기 조절 함수
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)  # 조정된 이미지를 흑백으로 변환

            file_name_path = 'faces/user' + str(count) + '.jpg'  # 이미지 저장 경로 및 이미지명 설정
            cv2.imwrite(file_name_path, face)  # 위에서 저장한 경로와 이름대로 face 이미지 저장

            # 텍스트 출력 및 폰트 지정
            cv2.putText(face, str(count), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
            # 웹캠의 창을 띄움, 프로그램 명은 Face Cropper
            cv2.imshow('Face Cropper', face)
        else:  # 얼굴이 존재하지 않는다면
            print("Face not Found")
            pass  # 실행할 코드 없음

        # waitKey() : 키 입력 대기 함수, 입력값이 0이면 무한대기, 13ms초 대기 또는 저장된 이미지가 100장이면
        if cv2.waitKey(1) == 13 or count == 100:
            messagebox.showinfo('Message', 'Registered. Please restart.')  # 등록 후 팝업창 띄우기
            root.destroy()  # 메인화면 닫기
            tk.destroy()  # 회원가입 화면 닫기
            cap.release()  # 할당된 자원 반납
            con.close()  # db 해제
            cv2.destroyAllWindows()


def JoinRegister(user_name, user_dp, user_stdnum, tk):  # 회원가입 등록 함수, 회원가입 화면 객체를 전달받고, 입력받은 id와 pw를 db에 저장
    cur.execute("INSERT INTO newUser (name,dp,stdNUm) VALUES (?,?,?)", (user_name, user_dp, user_stdnum))  # db에 삽입
    con.commit()  # db에 반영
    print("Save UserInfo")
    playWebCam(tk)  # 회원가입 화면을 닫기 위해 회원가입 창 tkinter객체 전달


def Join():  # 회원가입 함수 + 폴더 생성
    join = tkinter.Tk()  # 회원가입 창 생성
    join.geometry("400x200")
    join.title("PicamDiary")
    name_text = tkinter.Entry(join, width=30, bg='white')  # 이름 입력
    name_text.insert(0, "Name")
    name_text.pack(pady=5)
    department_text = tkinter.Entry(join, width=30, bg='white')  # 학과 입력
    department_text.insert(0, "Department")
    department_text.pack(pady=5)
    st_num = tkinter.Entry(join, width=30, bg='white')  # 학번 입력
    st_num.insert(0, "Student ID")
    st_num.pack(pady=5)
    bt5 = tkinter.Button(join, text="Register", width=18, height=1, fg="white", bg='gray40', font=("Arial", "15"),
                         command=lambda: JoinRegister(name_text.get(), department_text.get(), st_num.get(), join)).pack(side="bottom", expand=1)
    join.mainloop()

def face_detector(img, size=0.5):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, 1.3, 5)

    if faces is ():  # 얼굴이 존재하면 img 리턴
        return img, []

    for (x, y, w, h) in faces:  # 이미지 내에서 얼굴 추출
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 2)
        roi = img[y:y + h, x:x + w]
        roi = cv2.resize(roi, (200, 200))

    return img, roi


def callCam():  # 웹캡 실행 및 얼굴 인식 시작 함수
    Training_Data, Labels = [], []
    for i, files in enumerate(onlyfiles):  # 이미지 개수만큼 반복, enumerate : 열거 함수, for문과 자주 쓰임
        image_path = data_path + onlyfiles[i]  # 이미지가 저장된 경로
        images = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)  # image_path에 저장된 이미지를 흑백으로 불러옴
        Training_Data.append(np.asarray(images, dtype=np.uint8))  # Training_Data 리스트에 이미지를 바이트 배열로 추가
        Labels.append(i)  # Labels 리스트엔 카운트 번호 추가
    Labels = np.asarray(Labels, dtype=np.int32)  # Labels를 32비트 정수로 변환
    model = cv2.face.LBPHFaceRecognizer_create()  # 값을 2진수로 표현한 뒤 계산, 모델 생성
    model.train(np.asarray(Training_Data), np.asarray(Labels))  # 학습 시작
    print("Model Training Complete!!!!!")  # 학습 완료 시 출력
    cap = cv2.VideoCapture(0)  # 웹캠 open
    while True:
        ret, frame = cap.read()
        image, face = face_detector(frame)

        try:
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            result = model.predict(face)

            if result[1] < 500:  # result는 신뢰도, 0에 가까울수록 자신과 같다는 뜻
                confidence = int(100 * (1 - (result[1]) / 300))
                display_string = str(confidence) + '% Confidence it is user'  # 유사도
            cv2.putText(image, display_string, (100, 120), cv2.FONT_HERSHEY_COMPLEX, 1, (250, 120, 255), 2)

            if confidence > 75:  # 75보다 크면 동일 인물로 간주해 unlocked 표시, 사용자 인증되면 카메라 off
                cv2.putText(image, "Unlocked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Face Cropper', image)
                print("Recognition OK")
                cap.release()
                cv2.destroyAllWindows()
                root.destroy()
                goMainWindow()

            else:  # 75 이하면 타인.. Locked!!!
                cv2.putText(image, "Locked", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                cv2.imshow('Face Cropper', image)

        except:
            cv2.putText(image, "Face Not Found", (250, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
            cv2.imshow('Face Cropper', image)
            pass

        # 등록된 사용자가 아니면 카메라를 수동으로 꺼야함
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 키보드로 q 입력 시 팝업창
            msgBox = messagebox.askyesno('Message', '얼굴 인식을 종료할까요?')
            if msgBox == 1:  # yes 눌렀을 시
                cap.release()  # 카메라 off
                con.close()  # db 해제
                cv2.destroyAllWindows()  # 창 off


root.geometry("755x405")  # 화면 크기 조절
root.title("PicamDiary")  # 화면 타이틀
subLabel = tkinter.Label(root, text="Welcome to", fg="black", font=("Arial", "17")).place(x=310, y=80)
mainLabel1 = tkinter.Label(root, text="PiCamDiary", fg="black", font=("Arial", "30")).place(x=270, y=120)
bt1 = tkinter.Button(text="Face ID", width=20, height=1, bg="white", font=("Arial", "15"), command=callCam).place(x=260, y=200)
bt2 = tkinter.Button(text="User Registration", width=20, height=1, fg="white", bg="gray40", font=("Arial", "15"), command=Join).place(x=260, y=250)

root.mainloop()
con.close()  # db 해제

print("database is free")
