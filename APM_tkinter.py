#!/usr/bin/env python
# coding: utf-8

# # Automated Portfolio Analysis
# 
# With this program I want to:
# 
# 1. Scan through a folder with project offers
# 2. Filter those that contain a certain keyword
# 3. Create an Excel Table with certain parameters that will be extracted from the filtered files.

# ## Define Functions:
# 

# In[ ]:


# Import Libraries
from tkinter import *
import os 
import re
import docx2txt
import PyPDF2
from PIL import Image
import pytesseract
#import textract
import sys
from pdf2image import convert_from_path
import xlsxwriter
from glob import glob
import win32com.client as win32
from win32com.client import constants
from PIL import ImageTk, Image


# In[ ]:


# Function to create path list
def path_creator(path):
    path_list = []
    start_path = path
    overview = os.listdir(start_path)
    for item in overview:
        document_path = start_path + "/" + item
        path_list.append(document_path)
    return path_list  


# In[ ]:


# Function to extract text from word
def word_reader(path):
    word_document = docx2txt.process(path)
    return(word_document)


# In[ ]:


# Function to read text from regular pdfs

def pdf_reader (path, scanned_pdfs):
    pdfFile = open(path, "rb")
    pdfReader = PyPDF2.PdfFileReader(pdfFile)
    num_pages = pdfReader.numPages
    count = 0
    text = ""
    while count < num_pages:
        page = pdfReader.getPage(count)
        count += 1
        text += page.extractText()
        if text != "":
            text = text
        else:
            continue #text = textract.process("test.pdf", method="tesseract", language = "ger")
    text = text.replace('-\n', '')
    if text == "":
        scanned_pdfs.append(path)
    return(text)


# In[ ]:


def scanned_pdf_reader(path):
    PDF_file = path
    pages = convert_from_path(PDF_file, 500, poppler_path=r"C:\Users\User\poppler-0.68.0_x86\poppler-0.68.0\bin")
    image_counter = 1
    for page in pages:
        filename = "page_" + str(image_counter) + ".jpg"

        page.save(filename, 'JPEG')
        image_counter = image_counter + 1

    filelimit = image_counter - 1

    outfile = "out_text.txt"

    f = open(outfile, "a")

    for i in range(1, filelimit + 1):
 
        filename = "page_" + str(i) + ".jpg"

        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        text = str(((pytesseract.image_to_string(Image.open(filename)))))

        text = text.replace("-\n", "").replace("&", "ß")


        f.write(text)

    f.close()
    for picture in range(1, filelimit + 1): 
        filename = "page_" + str(picture) + ".jpg"
        if os.path.exists(filename):
            os.remove(filename)
        else:
            continue
            
    return text

#Source
#https://www.geeksforgeeks.org/python-reading-contents-of-pdf-using-ocr-optical-character-recognition/
# guide: https://github.com/Qiskit/qiskit-terra/issues/586
# https://stackoverflow.com/questions/53481088/poppler-in-path-for-pdf2image


# In[ ]:


#function to convert doc to docx https://stackoverflow.com/questions/38468442/multiple-doc-to-docx-file-conversion-using-python

def save_as_docx():
    path = path_var.get()
    paths = path_creator(path)
    for document in paths:
        if document.endswith(".doc"):
        # Opening MS Word
            word = win32.gencache.EnsureDispatch('Word.Application')
            doc = word.Documents.Open(document)
            doc.Activate()

        # Rename path with .docx
            new_file_abs = os.path.abspath(document)
            new_file_abs = re.sub(r'\.\w+$', '.docx', new_file_abs)

        # Save and Close
            word.ActiveDocument.SaveAs(new_file_abs, FileFormat=constants.wdFormatXMLDocument)
            doc.Close(False)
        else: continue


# ## Define Regex:

# In[ ]:


project_number = r"(PN|PN:|PN :|Projektnummer|Projektnummer:|Projektnummer :)\s\d{4}\.\d{4}\.\d{1}"


# In[ ]:


#Get Project number:
def fun_project_number(project_number, string):
    match = re.search(project_number, string)
# if not in text = no return. Finds only first instance
    try: 
        return match.group(0) # gets match out of match object
    except:
        return "error"


# In[ ]:


project_name = r"TZ(.+?)(PN|PN:|PN :|Projektnummer|Projektnummer:|Projektnummer :)"
project_name_ÜH = r"((.+?)(PN|PN:|PN :|Projektnummer|Projektnummer:|Projektnummer :))"


# In[ ]:


#Get Project name:
def fun_project_name(project_name, string):
    match = re.search(project_name, string)
# if not in text = no return. Finds only first instance
    try:
        if len(match.group(0)) <= 1000:
            try:
                return match.group(0).replace("PN", "").replace(",","").replace("Projektnummer", "") # gets match out of match object
            except:
                return "error"
        else:
            match = re.search(project_name_ÜH, string)
            try:
                return match.group(0).replace("PN", "").replace(",","").replace("Projektnummer", "") # gets match out of match object
            except:
                return "error"
    except:
        return "error"



# In[ ]:


project_start = r"(Von\s\d{2}\/d[4])|(d{2}/d{4}\s\bis\s\d{2}\d{4})"


# In[ ]:


search_term_content = r"[^.]*?B\s?e\s?h\s?i\s?n\s?d\s?e\s?r\s?u\s?n\s?g[^.]*\."


# In[ ]:

Kurzbeschreibung = re.compile("Kurzbeschreibung?")
Einordnung = re.compile("Einordnung\s?des\s?Vorhabens?")
Problemanalyse = re.compile("Problem-\s?und\s?(Potenzialanalyse?|Potentialanalyse?)")
Ziele = re.compile("Ziele, Wirkungshypothesen, Indikatoren?")
Gestaltung = re.compile("Gestaltung\s?des\s?TZ-Moduls?|Gestaltung des TZ-Moduls")
Bewertung = re.compile("Bewertung\s?der\s?Wirkungen\s?und\s?der\s?Risiken\s?des\s?Moduls?") 
Wirkungsmatrix = re.compile("Wirkungsmatrix erstellt am") 


# # Programm

# In[ ]:


def program():
    path = path_var.get()
    search_term_input = search_var.get()
    search_term_add = "[^.]*?"
    for letter in search_term_input:
        search_term_add = search_term_add + letter + r"\s?"
    search_term_add2 = search_term_add + r"[^.]*\."
    search_term = re.compile(search_term_add2)

    paths = path_creator(path)
    number_of_documents = len(paths)
    counter = -1

    while True:
        
        # not good to set global varialbes for maintainabiltiy rather use a class to store the call backs
        global liste_search_term
        global liste2_no_search_term
        global liste3_document_name
        global liste4_project_number
        global liste5_project_name 
        global liste6_not_searchable
        global liste7_Kurzbeschreibung
        global liste8_Einordnung
        global liste9_Problemanalyse
        global liste10_Ziele 
        global liste11_Gestaltung
        global liste12_Bewertung
        global liste13_Wirkungsmatrix
        global scanned_pdfs
        
        liste_search_term = [[] for x in range(number_of_documents)]
        liste2_no_search_term = []
        liste3_document_name = []
        liste4_project_number = []
        liste5_project_name = []
        liste6_not_searchable = []
        liste7_Kurzbeschreibung = [[] for x in range(number_of_documents)]
        liste8_Einordnung = [[] for x in range(number_of_documents)]
        liste9_Problemanalyse = [[] for x in range(number_of_documents)]
        liste10_Ziele = [[] for x in range(number_of_documents)]
        liste11_Gestaltung = [[] for x in range(number_of_documents)]
        liste12_Bewertung = [[] for x in range(number_of_documents)]
        liste13_Wirkungsmatrix = [[] for x in range(number_of_documents)]
        scanned_pdfs = []

        for document in paths:

            if ".docx" in document or ".DOCX" in document: # kein support für .doc, oder .DOC
                text = " ".join(word_reader(document).split())
                #add list of search term matches

                match = search_term.findall(text, re.IGNORECASE)
                match_Kurzbeschreibung = Kurzbeschreibung.findall(text, re.IGNORECASE)
                match_Einordnung = Einordnung.findall(text, re.IGNORECASE)
                match_Problemanalyse = Problemanalyse.findall(text, re.IGNORECASE)
                match_Ziele = Ziele.findall(text, re.IGNORECASE)
                match_Gestaltung = Gestaltung.findall(text, re.IGNORECASE)
                match_Bewertung = Bewertung.findall(text, re.IGNORECASE)
                match_Wirkungsmatrix = Wirkungsmatrix.findall(text, re.IGNORECASE)

                if match == []:
                    liste2_no_search_term.append(document.replace(path+"/", ""))

                else:
                    counter += 1
                    liste3_document_name.append(document.replace(path+"/", ""))
                    name = fun_project_name(project_name, text)
                    if len(name) < 1000:
                        liste5_project_name.append(name)
                    else:
                        liste5_project_name.append("Project name too long. Maybe KfW Project.")
                    number = fun_project_number(project_number, text)
                    liste4_project_number.append(number)

                    for item in match:
                        if len(match_Kurzbeschreibung) != 0 and text.find(item) < text.rfind(match_Kurzbeschreibung[0]):
                            liste7_Kurzbeschreibung[counter].append(item)
                        elif len(match_Einordnung) != 0 and text.find(item) < text.rfind(match_Einordnung[0]):
                            liste7_Kurzbeschreibung[counter].append(item)
                        elif len(match_Problemanalyse) != 0 and text.find(item) < text.rfind(match_Problemanalyse[0]):
                            liste8_Einordnung[counter].append(item)
                        elif len(match_Ziele) != 0 and text.find(item) < text.rfind(match_Ziele[0]):
                            liste9_Problemanalyse[counter].append(item)
                        elif len(match_Gestaltung) != 0 and text.find(item) < text.rfind(match_Gestaltung[0]):
                            liste10_Ziele[counter].append(item)    
                        elif len(match_Bewertung) != 0 and text.find(item) < text.rfind(match_Bewertung[0]):
                            liste11_Gestaltung[counter].append(item)    
                        elif len(match_Bewertung) != 0 and len(match_Wirkungsmatrix) == 0 and text.find(item) > text.rfind(match_Bewertung[0]):# funktioniert so nur wenn WiMa nicht in MV sonst > ändern
                            liste12_Bewertung[counter].append(item)
                        elif len(match_Wirkungsmatrix) != 0 and text.find(item) > text.rfind(match_Wirkungsmatrix[0]):
                            liste13_Wirkungsmatrix[counter].append(item)
                        else:
                            liste_search_term[counter].append(item)

            elif document.endswith(".pdf"):
                try:
                    text = " ".join(pdf_reader(document, scanned_pdfs).split())
                    if text == "":
                        scanned_pdfs.append(document)

                    match = search_term.findall(text, re.IGNORECASE)
                    match_Bewertung = Bewertung.findall(text, re.IGNORECASE)
                    match_Gestaltung = Gestaltung.findall(text, re.IGNORECASE)
                    match_Ziele = Ziele.findall(text, re.IGNORECASE)
                    match_Problemanalyse = Problemanalyse.findall(text, re.IGNORECASE)
                    match_Einordnung = Einordnung.findall(text, re.IGNORECASE)
                    match_Kurzbeschreibung = Kurzbeschreibung.findall(text, re.IGNORECASE)
                    match_Wirkungsmatrix = Wirkungsmatrix.findall(text, re.IGNORECASE)  

                    if match == []:
                        liste2_no_search_term.append(document.replace(path+"/", ""))

                    else:
                        counter += 1
                        liste3_document_name.append(document.replace(path+"/", ""))
                        name = fun_project_name(project_name, text)
                        if len(name) < 1000:
                            liste5_project_name.append(name)
                        else:
                            liste5_project_name.append("Project name too long. Maybe KfW Project.")
                        liste4_project_number.append(number)

                    for item in match:
                        if len(match_Kurzbeschreibung) != 0 and text.find(item) < text.rfind(match_Kurzbeschreibung[0]):
                            liste7_Kurzbeschreibung.append(item)
                        elif len(match_Einordnung) != 0 and text.find(item) < text.rfind(match_Einordnung[0]):
                            liste7_Kurzbeschreibung.append(item)
                        elif len(match_Problemanalyse) != 0 and text.find(item) < text.rfind(match_Problemanalyse[0]):
                            liste8_Einordnung.append(item)
                        elif len(match_Ziele) != 0 and text.find(item) < text.rfind(match_Ziele[0]):
                            liste9_Problemanalyse.append(item)
                        elif len(match_Gestaltung) != 0 and text.find(item) < text.rfind(match_Gestaltung[0]):
                            liste10_Ziele.append(item)    
                        elif len(match_Bewertung) != 0 and text.find(item) < text.rfind(match_Bewertung[0]):
                            liste11_Gestaltung.append(item)    
                        elif len(match_Wirkungsmatrix) != 0 and text.find(item) < text.rfind(match_Wirkungsmatrix[0]):# rfind teturns the highest index, -1 wenn nicht vorhanden!!!
                            liste12_Bewertung.append(item)
                        elif len(match_Wirkungsmatrix) != 0 and text.find(item) > text.rfind(match_Wirkungsmatrix[0]):
                            liste13_Wirkungsmatrix.append(item)
                        else:
                            liste_search_term[counter].append(item)

                except:
                    print("error", document)

        break   
        return liste_search_term, liste2_no_search_term, liste3_document_name, liste4_project_number, liste5_project_name, 
    liste6_not_searchable, liste7_Kurzbeschreibung, liste8_Einordnung, liste9_Problemanalyse, liste10_Ziele, 
    liste11_Gestaltung, liste12_Bewertung, liste13_Wirkungsmatrix, scanned_pdfs

# ## Create Excel File

# In[ ]:


#Create excel File
def excel_creator():
    
    workbook = xlsxwriter.Workbook("Portfolio-list.xlsx")
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})

    worksheet.write("A1", "File_Name", bold)
    worksheet.write("B1", "Project_Number", bold)
    worksheet.write("C1", "Project_Name", bold)
    worksheet.write("D1", "Unsortiert", bold)
    worksheet.write("E1", "Kurzbeschreibung", bold)
    worksheet.write("F1", "Einordnung", bold)
    worksheet.write("G1", "Problemanalyse", bold)
    worksheet.write("H1", "Ziele", bold)
    worksheet.write("I1", "Gestaltung", bold)
    worksheet.write("J1", "Bewertung", bold)
    worksheet.write("K1", "Wirkungsmatrix", bold)


    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 15)
    worksheet.set_column('G:G', 15)
    worksheet.set_column('H:H', 15)
    worksheet.set_column('I:I', 15)
    worksheet.set_column('J:J', 15)
    worksheet.set_column('K:K', 15)

    while True:
        row = 1
        col = 0

        for File_name in liste3_document_name:
            worksheet.write(row, col, File_name)
            row+=1
        break

    while True:
        row = 1
        col = 0

        for PN in liste4_project_number:
            worksheet.write(row, col + 1, PN)
            row+=1
        break

    while True:
        row = 1
        col = 0

        for Name in liste5_project_name:
            worksheet.write(row, col + 2, Name)
            row+=1
        break

    while True: 
        row = 1
        col = 0

        for Liste in liste_search_term:
            worksheet.write(row, col + 3, ";".join(Liste))
            row+=1
        break

    while True: 
        row = 1
        col = 0

        for Item in liste7_Kurzbeschreibung:
            worksheet.write(row, col + 4, ";".join(Item))
            row+=1
        break   

    while True: 
        row = 1
        col = 0

        for Item in liste8_Einordnung:
            worksheet.write(row, col + 5, ";".join(Item))
            row+=1
        break       

    while True: 
        row = 1
        col = 0

        for Item in liste9_Problemanalyse:
            worksheet.write(row, col + 6, ";".join(Item))
            row+=1
        break  

    while True: 
        row = 1
        col = 0

        for Item in liste10_Ziele:
            worksheet.write(row, col + 7, ";".join(Item))
            row+=1
        break    

    while True: 
        row = 1
        col = 0

        for Item in liste11_Gestaltung:
            worksheet.write(row, col + 8, ";".join(Item))
            row+=1
        break    

    while True: 
        row = 1
        col = 0

        for Item in liste12_Bewertung:
            worksheet.write(row, col + 9, ";".join(Item))
            row+=1
        break 

    while True: 
        row = 1
        col = 0

        for Item in liste13_Wirkungsmatrix:
            worksheet.write(row, col + 10, ";".join(Item))
            row+=1
        break 


    workbook.close()


# ## Creating a Excel File for the project progress report (number of matches per file is important

# In[ ]:


def pfb_numbers(): 
    path = path_var.get()
    search_term_input = search_var.get()
    search_term_add = "[^.]*?"
    for letter in search_term_input:
        search_term_add = search_term_add + letter + r"\s?"
    search_term_add2 = search_term_add + r"[^.]*\."
    search_term = re.compile(search_term_add2)
    
    global project_name
    global project_numbers
    global counters
    paths = path_creator(path)
    project_name = []
    project_numbers = []
    counters = []
    
    for document in paths:
        if ".docx" in document or ".DOCX" in document: 
            text = " ".join(word_reader(document).split()) 
            match = search_term.findall(text, re.IGNORECASE)
            number = fun_project_number(project_number, text)
            counter = 0
            for item in match: counter += 1
            if counter >= 1: 
                project_name.append(document.replace(path+"/", "")) 
                project_numbers.append(number) 
                counters.append(counter)
        elif document.endswith(".pdf"):
            text = " ".join(pdf_reader(document, scanned_pdfs).split()) 
            match = search_term.findall(text, re.IGNORECASE)
            number = fun_project_number(project_number, text)
            counter = 0
            for item in match: counter += 1
            if counter >= 1: 
                project_name.append(document.replace(path+"/", "")) 
                project_numbers.append(number) 
                counters.append(counter)


# In[ ]:


def pfb_numbers_xls():
    workbook = xlsxwriter.Workbook("Portfolio_PFB_Numbers.xlsx")
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})

    worksheet.write("A1", "File_Name", bold)
    worksheet.write("B1", "Project_Number", bold)
    worksheet.write("C1", "Counter", bold)

    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 15)

    while True:
        row = 1
        col = 0

        for File_name in project_name:
            worksheet.write(row, col, File_name)
            row+=1
        break

    while True:
        row = 1
        col = 0

        for PN in project_numbers:
            worksheet.write(row, col + 1, PN)
            row+=1
        break

    while True:
        row = 1
        col = 0

        for Counter in counters:
            worksheet.write(row, col + 2, Counter)
            row+=1
        break

    workbook.close()


# ## Scanned pdfs

# In[ ]:


def scanned_pdfs():
    for document in scanned_pdfs:   
        try:
            text = " ".join(scanned_pdf_reader(document).split())

            match = search_term.findall(text, re.IGNORECASE)
            match_Kurzbeschreibung = Kurzbeschreibung.findall(text, re.IGNORECASE)
            match_Einordnung = Einordnung.findall(text, re.IGNORECASE)
            match_Problemanalyse = Problemanalyse.findall(text, re.IGNORECASE)
            match_Ziele = Ziele.findall(text, re.IGNORECASE)
            match_Gestaltung = Gestaltung.findall(text, re.IGNORECASE)
            match_Bewertung = Bewertung.findall(text, re.IGNORECASE)
            match_Wirkungsmatrix = Wirkungsmatrix.findall(text, re.IGNORECASE)

            if match == []:
                liste2_no_search_term.append(document.replace(path+"/", ""))

            else:
                counter += 1
                liste3_document_name.append(document.replace(path+"/", ""))
                name = fun_project_name(project_name, text)
                if len(name) < 1000:
                    liste5_project_name.append(name)
                else:
                    liste5_project_name.append("Project name too long. Maybe KfW Project.")
                number = fun_project_number(project_number, text)
                liste4_project_number.append(number)

                for item in match:
                    if len(match_Kurzbeschreibung) != 0 and text.find(item) < text.rfind(match_Kurzbeschreibung[0]):
                        liste7_Kurzbeschreibung[counter].append(item)
                    elif len(match_Einordnung) != 0 and text.find(item) < text.rfind(match_Einordnung[0]):
                        liste7_Kurzbeschreibung[counter].append(item)
                    elif len(match_Problemanalyse) != 0 and text.find(item) < text.rfind(match_Problemanalyse[0]):
                        liste8_Einordnung[counter].append(item)
                    elif len(match_Ziele) != 0 and text.find(item) < text.rfind(match_Ziele[0]):
                        liste9_Problemanalyse[counter].append(item)
                    elif len(match_Gestaltung) != 0 and text.find(item) < text.rfind(match_Gestaltung[0]):
                        liste10_Ziele[counter].append(item)    
                    elif len(match_Bewertung) != 0 and text.find(item) < text.rfind(match_Bewertung[0]):
                        liste11_Gestaltung[counter].append(item)    
                    elif len(match_Bewertung) != 0 and len(match_Wirkungsmatrix) == 0 and text.find(item) > text.rfind(match_Bewertung[0]):# funktioniert so nur wenn WiMa nicht in MV sonst > ändern
                        liste12_Bewertung[counter].append(item)
                    elif len(match_Wirkungsmatrix) != 0 and text.find(item) > text.rfind(match_Wirkungsmatrix[0]):
                        liste13_Wirkungsmatrix[counter].append(item)
                    else:
                        liste_search_term[counter].append(item)
        except:
            liste6_not_searchable.append(document)


# In[ ]:


from tkinter import ttk


# ## Create GUI (tkinter)

# In[ ]:


root = Tk()
root.geometry("700x600")
root.title("GV Inclusion Portfolio Analysis")
    
path_var = StringVar()
search_var = StringVar()

# Put an Image in the GUI, can also be background of a button
my_img = ImageTk.PhotoImage(Image.open(r"path"))
myLabel_img = Label(root, image = my_img)
myLabel_img.place(x = 0 , y = 0)



explanation = Label(root, text ="""This Tool analyses Offers \n by search term and outputs and Excel File. \n 
First you need to enter the Path to the Offers \n Second please enter a search term and press "Click to start. \n
Lastly Press "Click to Create Excel File". The file will appear in the same directory as this programm. \n Please follow the instructions in the manual""")

path_entry = Entry(root, textvariable = path_var, width= 50)
path_label = Label(root, text ="Path")

path_tkinter = path_var.get()

entry_search_term = Entry(root, textvariable= search_var, width = 50)
search_term_label = Label(root, text ="Search Term")


my_Button_docx = Button(root, text = "Click to convert doc to docx. Needs MS Word installed!", command= save_as_docx)
myButton = Button(root, text = """Click to start. The program will freeze while processing. \n Please wait until it unfreezes! It might take a time so grab a coffee.""", command = lambda: [program(), enable()])

  
#Button(root, text = 'Start', command = bar).pack(pady = 10)

my_Button_out = Button(root, text ="Click to Create an Excel File", command = excel_creator, state = "disabled")

my_Button_numbers_pfb = Button(root, text ="Click here to create an analysis \n that counts instances of the search term \n", command = pfb_numbers)
my_Button_numbers_pfb_out= Button(root, text ="Click to Create Excel File for PfB Numbers",
                                 command = pfb_numbers_xls)


def enable():
    my_Button_out["state"] = "normal"
    my_Button_scanned_PDF["state"]= "normal"
    my_Button_Scanned_analysis["state"]= "normal"


def scanned_PDF():
    path = path_var.get()
    output = []
    for item in scanned_pdfs:
        output.append(item.replace(path+"/", ""))
    if len(output) == 0:
        output.append("There are no scanned PDFs found.")
    else:
        output = set(output)
    
    myLabel = Label(root, text= ("Number of Scanned files: " + str(len(set(scanned_pdfs))), output))
    myLabel.grid(row = 7, column = 0, columnspan = 4)

my_Button_scanned_PDF = Button(root, text= """Click to see the Documents identified as scanned PDFs. \n Scanned PDFs can be analysed with this programm, \n although this will take a long time and the contents will be less clean.""", command = scanned_PDF, state = "disabled")


my_Button_Scanned_analysis = Button(root, text="Click to analyse scanned PDFs. Warning: This will take long", command= scanned_pdfs, state = "disabled")

myLabel_PFB = Label(root, text ="The application can also just count the instances of the search term \n and output an excel file containing the document name and the number of search teram instances for each.")

myLabel_end = Label(root, text ="This application was programmed by a noob and is very unstable. \n Please reach out to .... if you have issues.")


explanation.grid(row = 1, column = 0, columnspan =3, padx = 10, pady = 10)

path_label.grid(row = 2, column = 0)
path_entry.grid(row =2 , column =1)
search_term_label.grid( row = 3, column =0)
entry_search_term.grid(row = 3, column = 1)

my_Button_docx.grid(row=4, column = 1)

myButton.grid(row = 5, column = 1)

my_Button_scanned_PDF.grid(row=6, column=1)
my_Button_Scanned_analysis.grid(row= 8, column =1)

my_Button_out.grid(row = 9, column = 1)

myLabel_PFB.grid(row = 10, column = 0, columnspan =3, padx = 10, pady = 10)
my_Button_numbers_pfb.grid(row = 11, column = 1)
my_Button_numbers_pfb_out.grid(row = 12, column =1)

myLabel_end.grid(row= 13, column =0, columnspan = 3, padx = 10, pady = 20)


# In[ ]:


root.mainloop()


# Create a windows application: Go to directory => python -m PyInstaller --onefile -w APM_tkinter.py



