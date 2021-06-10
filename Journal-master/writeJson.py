import tkinter
import json
import os
import tkinter.filedialog
from os import listdir
from os.path import isfile, join
from PIL import ImageTk
from PIL import Image
from tkinter import *
from tkinter.filedialog import asksaveasfile #filedialog : 파일 선택 대화창, asksavefile : 파일 저장
#date time 객체는 파일 합치고 나서 합시다

root = tkinter.Tk()
root.geometry('423x330')
root.title("일기")

test = 1
data_path = 'faces/' # 사진이 저장될 폴더명
diary_path = 'diary/' # 일기장이 저장될 폴더명
data = {}  # json_dictionary

# C:/Users/hamin/journalll - 복사본2 -> json파일이 저장되는 경로(내 PC 기준!!)
loadFileList = [f for f in listdir(diary_path) if isfile(join(diary_path, f))]
print(loadFileList) #해당 폴더에 있는 파일 목록 출력
search = 'Journal-master'
#pfilename = "" #표정 사진이 저장된 경로
data = {}  # dictionary

def loadPhotoFile(text): #jpg 형식만 가능한듯
    pfilename = tkinter.filedialog.askopenfilename(initialdir="/", title="사진 불러오기",  filetypes=(("JPG files", "*.jpg"),("all files", "*.*")))
    text.config(text = pfilename)
    text.place(x=70, y=230) #라벨을 이미지경로로 업데이트, 사진 줄이기 #이거 위치야
    data['image'] = pfilename #해당 json 파일에 image key를 추가하고, value로 이미지경로 + 이미지명 저장

def readToJson(index,text,tk): #일기, 이미지 위젯에 로드
    with open(diary_path + loadFileList[index], 'r', encoding='utf-8') as json_file: #해당 파일명으로
        global image1
        json_data = json.load(json_file) #json파일 불러오기
        json_string = json_data["Content"] #일기장 내용(Content)을 추출하여 string 변수에 저장
        json_image = json_data["image"] #이미지 경로(image)를 추출하여 string 변수에 저장
        text.config(text = json_string) #라벨을 일기장 내용으로 업데이트
        text.place(x=290, y=30)# text.grid(row=3, column=3) #일기장 내용
        imageFrame1 = Image.open(json_image)
        imageFrame2 = imageFrame1.resize((265, 159), Image.ANTIALIAS)  # 이미지 크기 조절
        image1 = ImageTk.PhotoImage(imageFrame2, master=tk) #master 설정 안해주면 오류
        imageLabel = tkinter.Label(tk, image=image1).place(x=10, y=210)

def printIndex(ta): #선택된 리스트박스 데이터의 인덱스를 반환받는 함수, json 데이터를 로드하기 위해 필요!
    index = ta.index(ta.curselection())
    print(index)

def viewDiaryList():
    diaryList = tkinter.Tk()
    diaryList.geometry('570x400')
    diaryList.title('일기 보기')
    showtitle = tkinter.Label(diaryList, text="목록")
    showtitle.place(x=10,y=7)

    showdiary = tkinter.Label(diaryList, text="일기 내용")
    showdiary.place(x=285,y=7)

    showimage = tkinter.Label(diaryList,text= "이미지 파일")
    showimage.place(x=10, y=190)

    inputListBox = tkinter.Listbox(diaryList,relief='sunken',fg = 'black', selectmode='extended', width=38, height=8) #저장된 파일들을 보여줄 리스트박스 객체, 왼쪽 꽉 채우기

    # 스크롤바 생성
    scrollBar = tkinter.Scrollbar(diaryList,orient=VERTICAL,command=inputListBox.yview)
    scrollBar.pack(side="right", fill="y")
    inputListBox.pack(side="left", fill="both", expand=True)
    inputListBox.config(yscrollcommand=scrollBar.set)

    loadBtn = tkinter.Button(diaryList, text='내용 보기', command=lambda:readToJson(inputListBox.index(inputListBox.curselection()), outputLabel, diaryList)).place(x=215, y=165)
    outputLabel = tkinter.Label(diaryList, anchor='nw',justify='left',wraplength = 0,
                                           text="내용",relief='solid', fg="black", bg='white', bd=1,
                                           width=36, height=23) #각 파일의 내용만 출력해서 보여줄 라벨
    #outputLabel.pack()
    outputLabel.place(x=290,y=30)#grid(row=3, column=2,padx=10)

    for i, word in enumerate(loadFileList): #리스트박스에 파일 제목 띄우기
        if search in word: #만약 리스트 내 원소에 search변수 문자열이 존재하면
            loadFileList[i] = word.strip(search) #그 문자열만 삭제해서
        inputListBox.insert(i,loadFileList[i]) #리스트박스에 추가
        inputListBox.place(x=10,y=30)#grid(row=3, column=1,padx=10,pady=30)#place(x=0,y=0)#grid(row=3, column=1)
        print(loadFileList)
    diaryList.mainloop()

#dump : 파이썬 객체를 json 형식으로 변환
def writeToJson(filename, data): #json 파일 생성 후 저장
    with open(diary_path + filename, 'w', encoding='utf-8')as make_file:
        json.dump(data, make_file, ensure_ascii=False, indent="\t")
    #json.dump(data, path, ensure_ascii=False) #ensure_ascii를 False로 선언해주면 유니코드가 아닌 한글로 저장됨

def check():
    a = Name.get() #제목
    c = Role.get() #내용
    print(a)
    print(c)
    #dictionary index
    data['Title'] = a
    data['Content'] = c
    files = [('Json File', '*.json')] #파일 형식
    fileName = a #파일명 = 제목으로.
    writeToJson(fileName, data)

name = tkinter.Label(root, text="제목")
Name = tkinter.Entry(root)
role = tkinter.Label(root, text="내용")
Role = tkinter.Entry(root)
photoUtl = tkinter.Label(root, bg='white')
loadPhoto = tkinter.Button(root, text='사진 불러오기', width=30, command=lambda:loadPhotoFile(photoUtl)).place(x=100, y=200)
submit = tkinter.Button(root, text='일기 등록', command=check, width=30).place(x=100, y=260)
loadDiary = tkinter.Button(root, text='일기 목록', command=viewDiaryList, width=30).place(x=100, y=290)

print(os.path.dirname(os.path.realpath(__file__))) #파일의 현재경로 출력

name.place(x=200, y=10)
role.place(x=200, y=60)
Name.place(x=10, y=35, width=400)
Role.place(x=10, y=92, width=400, height=100)

root.mainloop()


