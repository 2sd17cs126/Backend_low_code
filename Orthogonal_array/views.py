import pandas as pd
import os
import glob
import javalang
import json
import pyautogui
import requests
import re
import os
from django.http import HttpResponse
import webbrowser
from pymongo import MongoClient
import csv
from django.views.decorators.csrf import csrf_exempt
import tkinter as tk
from tkinter import filedialog
from lxml import etree
from bs4 import BeautifulSoup,Comment
home_dir = os.path.expanduser("~")
feature_file = None
directory = ''
dictionary = []
STEPT_DEF={}
ALL_UI_OBJ_SELECTOR_VALUE={}
CSS_SELECTOR_UI_OBJECT=set()
CSS_SELECTOR_LABEL_OBJECT=set()
XPATH_UI_OBJECT=set()
XPATH_LABEL_ObJECT=set()
MAP_UI_OBJECT_TO_SELECTOR={}
MAP_LABEL_OBJECT_TO_SELECTOR={}
MAP_UI_OBJECT_SELECTOR_TO_LABEL_SELECTOR={}
XPATH_UI_TO_LABEL={}
all_content = {
    'directory' : '',
    'dictionary' : [],
    'fieldnames' : [],
    'table_dictionary' : [],
    'feature_string' : '',
    'scenario_string' : ''
}

def calculate_distance(xpath1, xpath2):
    """Calculate the distance between two XPaths."""
    # Convert XPaths to lists of tag names
    tags1 = xpath1.strip('/').split('/')
    tags2 = xpath2.strip('/').split('/')

    # Find the common prefix between the two XPaths
    common_prefix = []
    for tag1, tag2 in zip(tags1, tags2):
        if tag1 == tag2:
            common_prefix.append(tag1)
        else:
            break

    # Calculate the distance as the sum of the remaining tags
    distance = len(tags1) - len(common_prefix) + len(tags2) - len(common_prefix)
    return distance


@csrf_exempt
def capture_working(request):
    
    return HttpResponse("ok")

def remove_comments():
    html_file = "Temporary_Data/page.html"

    # Read the contents of the HTML file
    with open(html_file, "r", encoding='utf-8') as file:
        html = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Find all comment nodes in the HTML
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    # Remove comment nodes from the HTML
    for comment in comments:
        comment.extract()

    # Get the modified HTML without comments
    html_without_comments = str(soup)

    return html_without_comments

def pull_label_object(css_selector):
    html =remove_comments()

    soup = BeautifulSoup(html, "html.parser")

    # Find the UI object using the CSS selector
    
    ui_object = soup.select(css_selector)
    for node in ui_object:
        print(node.string.strip())
        return node.string.strip()

def pull_ui_object_new_label(xpath_selector):
    # Parse the HTML document using lxml
    html_file="Temporary_Data/page.html"
    with open(html_file, "r", encoding='utf-8') as file:
        html = file.read()
    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)

    # Find the UI object using the XPath selector
    label_element = tree.xpath(xpath_selector)

    # Extract the content of the label element
    if len(label_element) > 0:
        label_content = label_element[0].text.strip()
        return label_content

def pull_ui_object_new(xpath_selector):
    # Parse the HTML document using lxml
    html_file="Temporary_Data/page.html"
    with open(html_file, "r", encoding='utf-8') as file:
        html = file.read()
    parser = etree.HTMLParser()
    tree = etree.fromstring(html, parser)

    # Find the UI object using the XPath selector
    ui_objects = tree.xpath(xpath_selector)
    print("ui objects:")
    print(ui_objects)
    # Extract the content of the UI objects
    child_content = []
    for obj in ui_objects:
        if obj.xpath('./*'):  # Check if the element has child nodes
            for child in obj.xpath('./*'):
                if child.text and child.text.strip():
                    child_content.append(child.text.strip())
        elif obj.text and obj.text.strip():
            child_content.append(obj.text.strip())

    # Print the extracted content
    print(child_content)
    return child_content


def pull_ui_object(css_selector):
    # Parse the HTML document
    html =remove_comments()

    soup = BeautifulSoup(html, "html.parser")

    

    # Find the UI object using the CSS selector
    ui_object = soup.select(css_selector)
    print()
    # Extract the child node content
    child_content = []
    for node in ui_object:
    # If the node has child nodes, extract their content
        if node.contents:
            for child in node.children:
                if child.string and child.string.strip():  # Exclude empty strings and whitespace-only strings
                    child_content.append(child.string.strip())
        # If the node has no child nodes, extract its own text content
        elif node.string and node.string.strip():  # Exclude empty strings and whitespace-only strings
            child_content.append(node.string.strip())

    # Print the extracted content
    print(child_content)
    return child_content

@csrf_exempt
def capture_label_xpath(request):  
    global CSS_SELECTOR_LABEL_OBJECT
    global XPATH_LABEL_ObJECT
    global XPATH_UI_OBJECT
    global MAP_LABEL_OBJECT_TO_SELECTOR
    data = json.loads(request.body.decode('utf-8'))
    #print("mydata")
    
    if data['xpath1'] not in XPATH_LABEL_ObJECT and data['actual_xpath'] not in CSS_SELECTOR_LABEL_OBJECT and data['xpath1'] not in XPATH_UI_OBJECT:
        CSS_SELECTOR_LABEL_OBJECT.add(data['actual_xpath'])
        XPATH_LABEL_ObJECT.add(data['xpath1'])
        MAP_LABEL_OBJECT_TO_SELECTOR[data['xpath1']]=data['actual_xpath']
    
    return HttpResponse("ok")

@csrf_exempt
def capture_xpath(request):
    global CSS_SELECTOR_UI_OBJECT
    global XPATH_UI_OBJECT
    data = json.loads(request.body.decode('utf-8'))
    #print("mydata")
    
    if data['xpath1'] not in XPATH_UI_OBJECT and data['actual_xpath'] not in CSS_SELECTOR_UI_OBJECT:
        CSS_SELECTOR_UI_OBJECT.add(data['actual_xpath'])
        XPATH_UI_OBJECT.add(data['xpath1'])
        MAP_UI_OBJECT_TO_SELECTOR[data['xpath1']]=data['actual_xpath']
  
    
    return HttpResponse("ok")

@csrf_exempt
def automatic_fetch(request):
    
    global CSS_SELECTOR_UI_OBJECT
    global CSS_SELECTOR_LABEL_OBJECT
    global XPATH_LABEL_ObJECT
    global XPATH_UI_OBJECT
    global ALL_UI_OBJ_SELECTOR_VALUE
    global MAP_UI_OBJECT_TO_SELECTOR
    global MAP_LABEL_OBJECT_TO_SELECTOR
    global XPATH_UI_TO_LABEL
    for xpath1 in XPATH_UI_OBJECT:
        min_distance = float('inf')
        min_xpath = ''

        for xpath2 in XPATH_LABEL_ObJECT:
            distance = calculate_distance(xpath1, xpath2)
            if distance < min_distance:
                min_distance = distance
                min_xpath = xpath2
        XPATH_UI_TO_LABEL[xpath1]=min_xpath
    print("Xpath ui to label:")
    print(XPATH_UI_TO_LABEL)
    for d in XPATH_UI_TO_LABEL:
        MAP_UI_OBJECT_SELECTOR_TO_LABEL_SELECTOR[MAP_UI_OBJECT_TO_SELECTOR[d]]=MAP_LABEL_OBJECT_TO_SELECTOR[XPATH_UI_TO_LABEL[d]]
    print("automatic fetch")
    for d in MAP_UI_OBJECT_SELECTOR_TO_LABEL_SELECTOR:
        ALL_UI_OBJ_SELECTOR_VALUE[pull_ui_object_new_label(MAP_UI_OBJECT_SELECTOR_TO_LABEL_SELECTOR[d])]=pull_ui_object_new(d)
    print("csv data:")
    print(ALL_UI_OBJ_SELECTOR_VALUE)
    data={
        'Factor_name':[],
        'Level_count':[],
        'Level_values':[]
    }
    df = pd.DataFrame(data)
    
    for value in ALL_UI_OBJ_SELECTOR_VALUE:
        new_row={}
        new_row['Factor_name']=value
        new_row['Level_count']=len(ALL_UI_OBJ_SELECTOR_VALUE[value])
        new_row['Level_values']=','.join(str(item) for item in ALL_UI_OBJ_SELECTOR_VALUE[value] )
        df = df.append(new_row, ignore_index=True)
    df.to_csv('Temporary_Data/inputData.csv', index=False)
    d=[]
    with open('Temporary_Data/inputData.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            d.append(row)
    rows = []
    for row in d:
        factor_name = row['Factor_name']
        level_count = row['Level_count']
        level_values = row['Level_values'].split(',')

        level_value = [{'value': value} for value in level_values]
        
        rows.append({
        'Factor_name': factor_name,
            'Level_count': level_count,
            'Level_value': level_value,
            'Level_values': ''
        })
    return HttpResponse(json.dumps({'rows': rows}))
    

@csrf_exempt
def open_popup(request):
    global CSS_SELECTOR_UI_OBJECT
    global ALL_UI_OBJ_SELECTOR_VALUE
    global CSS_SELECTOR_LABEL_OBJECT
    global XPATH_LABEL_ObJECT
    global XPATH_UI_OBJECT
    global MAP_LABEL_OBJECT_TO_SELECTOR
    global MAP_UI_OBJECT_TO_SELECTOR
    global MAP_UI_OBJECT_SELECTOR_TO_LABEL_SELECTOR
    global XPATH_UI_TO_LABEL
    ALL_UI_OBJ_SELECTOR_VALUE={}
    CSS_SELECTOR_UI_OBJECT=set()
    CSS_SELECTOR_LABEL_OBJECT=set()
    XPATH_UI_OBJECT=set()
    XPATH_LABEL_ObJECT=set()
    MAP_UI_OBJECT_TO_SELECTOR={}
    MAP_LABEL_OBJECT_TO_SELECTOR={}
    MAP_UI_OBJECT_SELECTOR_TO_LABEL_SELECTOR={}
    XPATH_UI_TO_LABEL={}
    pyautogui.hotkey('ctrl', 'b')
    return HttpResponse("ok")

@csrf_exempt
def extract_page(request):
    data = json.loads(request.body.decode('utf-8'))
    
    page_content = data['htmlContent']
    
    save_path = "Temporary_Data/page.html"
    
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(page_content)  
    return HttpResponse("ok")
def func_generator_js(keyword,argument,result_file):
    func1=''
    if 'launch' in argument.split(" ") and keyword=="Given":
        func1='ApplicationLaunch()'
    if 'logout' in argument.split(" ") and keyword=="And":
        func1='ApplicationExit()'
    if 'login' in argument.split(" ") and keyword=="When":
        func1='ApplicationLogin()'
    structure=keyword+'(\''+argument.strip()+'\',()=>{'+'\n'+ func1 +'\n'+'})'+'\n'
    result_file.write(structure)

def func_generator_java(keyword,argument,o_w_f='',param='',returnparam='',flag=False,return_type='void'):
    if flag==True:
        if returnparam == 'nan' or returnparam==' ':
            returnparam=''
        else:
            o_w_f=returnparam+'='+o_w_f
        if param=='nan':
            param=''
        result_str=''
        if param !='':
            parts = param.split(',')

            # Extract variable names from each part
            variable_names = [part.split()[-1] for part in parts]

            # Create a comma-separated string
            result_str = ','.join(variable_names)
        structure='@'+keyword+'(\"^'+argument.strip()+'$\")\n\t'+'public '+return_type+' '+argument.replace(" ", "_")[1:]+'('+param+') throws InterruptedException { '+'\n\t\t'+o_w_f+'('+result_str+')\n\n\t}\n\n\t'
    else:
        structure='@'+keyword+'(\"^'+argument.strip()+'$\")\n\t'+'public '+return_type+argument.replace(" ", "_")[1:-1]+'() throws InterruptedException { \n\n\t'+returnparam+'}\n\n\t'
    all_content['scenario_string']+=structure

def func_generator_cs(keyword,argument,result_file):
    structure='['+keyword+'(@\"'+argument.strip()+'\")]\n\t\t'+'public void '+keyword+argument.replace(" ", "")+'() \n\t\t{\n\n\t\t}\n\n\t\t'
    result_file.write(structure)

def func_generator_with_variable_cs(keyword,line,result_file):
    preced_place_holder=""
    variable_string="("
    removing_word_list=[]
    removing_word_list.append(keyword)
    removing_word_list.append(',')
    for data in re.findall("<[A-Za-z_0-9]*>", line):
        preced_place_holder=preced_place_holder+"\"\"([^\"\"]*)\"\","
        variable_string=variable_string+'String '+data[1:-1]+','
        temp="\"<"+data[1:-1]+">\""
        removing_word_list.append(temp)
    preced_place_holder=preced_place_holder[:-1]
    variable_string=variable_string[:-1]+')'
    for rem in removing_word_list:
        if rem in line:
            line=line.replace(rem,"")
    structure='['+keyword+'(@\"'+line.strip()+preced_place_holder+'\")]\n\t\t'+'public void '+keyword+line.replace(" ", "")+variable_string+' \n\t\t{\n\n\t\t}\n\n\t\t'
    result_file.write(structure)

def func_generator_with_variable_java(keyword,line):
    preced_place_holder=""
    variable_string="("
    removing_word_list=[]
    removing_word_list.append(keyword)
    removing_word_list.append(',')
    for data in re.findall("<[A-Za-z_0-9]*>", line):
        preced_place_holder=preced_place_holder+"(.*)"
        variable_string=variable_string+'String '+data[1:-1]+','
        temp="\"<"+data[1:-1]+">\""
        removing_word_list.append(temp)
    variable_string=variable_string[:-1]+')'
    for rem in removing_word_list:
        if rem in line:
            line=line.replace(rem,"")
    structure='@'+keyword+'(\"^'+line.strip()+preced_place_holder+'$\")\n\t'+'public void '+line.replace(" ", "_")[1:-1]+variable_string+' throws InterruptedException {\n\n\t}\n\t\n\t'
    all_content['scenario_string'] +=structure

def func_generator_with_variable_js(keyword,line,result_file,func1):
    variable_string="("
    removing_word_list=[]
    removing_word_list.append(keyword)
    removing_word_list.append(',')
    preced_place_holder=""
    for data in re.findall("<[A-Za-z_0-9]*>", line):
        preced_place_holder=preced_place_holder+"{"+"string"+"},"
        variable_string=variable_string+data[1:-1]+','
        temp="\"<"+data[1:-1]+">\""
        removing_word_list.append(temp)
    preced_place_holder=preced_place_holder[:-1]
    variable_string=variable_string[:-1]+')'
    for rem in removing_word_list:
        if rem in line:
            line=line.replace(rem,"")
    structure=keyword+'(\''+line.strip()+' '+preced_place_holder+'\','+variable_string+'=>{'+'\n'+func1+variable_string+'\n'+'})'+'\n'
    result_file.write(structure)

# Create your views here.
@csrf_exempt
def myFunc(e):
  return e['rows']

# get suggestion for steps
@csrf_exempt
def get_suggestions(request):
    if request.method=='POST':
        cluster = MongoClient("mongodb+srv://newuser1:Abuzarm2@cluster0.qqe5xei.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["test"]
        collection=db["suggestion"]
        data=json.loads(request.body.decode('utf-8'))
        query = data['query']
        suggestions = collection.find({'_id': {'$regex': f'{query}', '$options': 'i'}})
        suggestion_list = [suggestion['_id'] for suggestion in suggestions]
        return HttpResponse(json.dumps({"result":(False,suggestion_list)}))

#store suggestion for steps if not included in mongodb
@csrf_exempt
def store_suggestions(request):
    if request.method=='POST':
        cluster = MongoClient("mongodb+srv://newuser1:Abuzarm2@cluster0.qqe5xei.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["test"]
        collection=db["suggestion"]
        data=json.loads(request.body.decode('utf-8'))
        for dat in data['pre_req']:
            # Check if the string exists in MongoDB
            existing_doc = collection.find_one({'_id': dat['pre']})
            if existing_doc is None:
                # String does not exist, so add it
                collection.insert_one({'_id': dat['pre']})
        
        for dat in data['post_req']:
            # Check if the string exists in MongoDB
            existing_doc = collection.find_one({'_id': dat['post']})
            if existing_doc is None:
                # String does not exist, so add it
                collection.insert_one({'_id': dat['post']})
    return HttpResponse('ok') 

@csrf_exempt
def data_operation(request):
    if request.method=='POST':
        data=json.loads(request.body.decode('utf-8'))
        global dictionary
        all_content['dictionary'] = data['row']
        for item in all_content['dictionary']:
            del item['Level_value']
        id=data['pattern'] 
        cluster = MongoClient("mongodb+srv://newuser1:Abuzarm2@cluster0.qqe5xei.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["test"]
        collection=db["test"]
        result = collection.find_one({"id":id} )
        list_=[]
        if result:
            return HttpResponse(json.dumps({"result":(True,id,result['tab'])}))
        else:
            E_total_factor=0
            list_of_level_pattern=[]
            for i in range(0,len(str(id))):
                if id[i]=='^':
                    list_of_level_pattern.append(int(id[i-1]))
                    E_total_factor+=int(id[i+1])
            list_of_level_pattern.sort()
            
            for doc in collection.find({}):
                F_total_factor=0
                for i in range(0,len(doc['id'])):
                    
                    if doc['id'][i]=='^' and int(doc['id'][i-1])>=list_of_level_pattern[0]:

                        F_total_factor+=int(doc['id'][i+1])
                    else:
                        continue
                if F_total_factor>=E_total_factor:
                    list_.append({'id':doc['id'],'tab':doc['tab'],'E_factor':int(E_total_factor),'F_factor':int(F_total_factor),'rows':len(doc['tab'].split("\n"))})
            
            list_.sort(key=myFunc)
            return HttpResponse(json.dumps({"result":(False,list_)}))


@csrf_exempt
def bdd(request):
    if request.method=='POST':
        global directory
        data=json.loads(request.body.decode('utf-8'))
        
        all_content['directory'] = home_dir+'\Ortho App saves'+'\\'+data['feature']

        
        all_content['fieldnames'] = data['names_factor']
        all_content['table_dictionary'] = data['table_data']
        
        values=[]
        variables=[]
        message = ''
        
        table_data=data['table_data']
        factor_name=data['column_data']
        
        # declare json object and add tag and scenario
        json_object = {}
        json_object["_id"] = data['feature']
        json_object["elements"]=[]
        
        elements_data = {} 
        elements_data["name"] = data['scenerio']
        elements_data["tag"] = "@"+data['tag']
        elements_data["type"] = "scenario_outline"
        elements_data.setdefault("steps", [])

        scenerio="Feature:"+data['feature']+"\n\n@"+data['tag']+"\nScenario Outline:"
        scenerio+=data['scenerio']
        scenerio=scenerio+'\n'

        string1=''
        string_variables=''
        string_values=''
        for dat in data['pre_req']:
            string1+=dat['pre']+' '
            if(dat['pre_variables']!=''):
                string_variables=dat['pre_variables'].split(',')
                string_values=(dat['pre_values']).split(',')
                for i in string_variables:
                    string1+='\"<'+i+'>\",'
                    variables.append(i)
                for j in string_values:
                    values.append(j)
                string1=string1[:-1]
            string1+='\n'
            # add the key and text to jsondata
            key,text=separator(dat['pre'])
            steps_data= {}
            steps_data["keyword"] = key
            steps_data["text"] = text
            elements_data["steps"].append(steps_data)    
        string1+='\n'

        string2="""And Funrnish the information """
        for factor in factor_name:
            string2+="\"<"
            string2+=factor
            string2+=">\","
        string2=string2[:-1]
        # add the key and text to jsondata
        key,text=separator(string2)
        steps_data= {}
        steps_data["keyword"] = key
        steps_data["text"] = text
        elements_data["steps"].append(steps_data)
        string2=string2+'\n\n'

        string3=''
        string_variables=''
        string_values=''
        for dat in data['post_req']:
            string3+=dat['post']+' '
            if(dat['post_variables']!=''):
                string_variables=dat['post_variables'].split(',')
                string_values=(dat['post_values']).split(',')
                for i in string_variables:
                    string3+='\"<'+i+'>\",'
                    variables.append(i)
                for j in string_values:
                    values.append(j)
                string3=string3[:-1]
            string3+='\n'
            # add the key and text to jsondata
            key,text=separator(dat['post'])
            steps_data= {}
            steps_data["keyword"] = key
            steps_data["text"] = text
            elements_data["steps"].append(steps_data)   
        string3+='\n'


        string3=string3+'\n'+'Examples:'+'\n'
        for i in factor_name:
            string3+='|'
            string3+=i
        for i in variables:
            string3+='|'
            string3+=i
        string3+='|'
        string3+='\n'

        
        for line in table_data:
            for i in line:
                if i == 'isEdit':
                    continue
                string3+='|'
                string3+=line[i]
            for j in values:
                string3+='|'
                string3+=j  
            string3+='|'
            string3+='\n'
        
        #append all data to json 
        json_object["elements"].append(elements_data) 
        all_content['result']=scenerio+string1+string2+string3
        
        
        # # Call the API to store data and recieve a response
        # response = requests.post("http://127.0.0.1:8084/",json=json_object)
        # if response.status_code == 200:
        #     # Request was successful
        #     response_data = response.json()
        #     # Process the response data as needed
        #     message = response_data["message"]
        # else:
        #     # Request failed
        #     print("Request failed with status code:", response.status_code)
            
    return HttpResponse(json.dumps({"file_content":all_content['result'],"message":"success"}))

def separator(string):
    if "Given" in string:
        return "Given",string[len("Given"):]
    elif "And" in string:
        return "And",string[len("And"):]
    elif "When" in string:
        return "When",string[len("When"):]
    

@csrf_exempt
def step_def(request):
    file=json.loads(request.body.decode('utf-8'))
    content=file['file_data']
    language=file['lang']
    content=content[:content.find("Examples:")]
    to_iter=content.split("\n")[2:]
    
    if language=='JavaScript':
        folder = os.path.join(all_content['directory'],'BddScenario.js')
        result_file=open(folder,'w')
        for line in to_iter: 
            if "Given" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0 :
                func_generator_js("Given",line[len("Given"):],result_file)

            elif "And" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_js("And",line[len("And"):],result_file)

            elif "When" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_js("When",line[len("When"):],result_file)

            elif "And" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func1="userDefinedFunction"
                func_generator_with_variable_js("And",line,result_file,func1)

            elif "Given" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func1='ApplicationLaunch'
                func_generator_with_variable_js("Given",line,result_file,func1)

            elif "When" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func1='ApplicationLogin'
                func_generator_with_variable_js("When",line,result_file,func1)
        
        folder = os.path.join(all_content['directory'],'BddScenario.js')
        result_file=open(folder,'r')
        
    elif language=='Java':
        all_content['scenario_string'] = ''
        all_content['scenario_string'] +='public class seatbooking  {'+'\n'+'\n'+'\t'
        # result_file.write('public class seatbooking  {'+'\n'+'\n'+'\t')
        for line in to_iter: 
            if "Given" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_java("Given",line[len("Given"):])
        
            elif "And" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_java("And",line[len("And"):])

            elif "When" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_java("When",line[len("When"):])
        
            elif "And" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func_generator_with_variable_java("And",line)
        
            elif "Given" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func_generator_with_variable_java("Given",line)

            elif "When" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func_generator_with_variable_java("When",line)
        all_content['scenario_string']+='}'

    elif language=='C#':
        folder = os.path.join(all_content['directory'],'BddScenario.cs')
        result_file=open(folder,'w')
        result_file.write('namespace TestingPractice.ProjectName.TA.Steps\n{\n\t[Binding]\n\tpublic sealed class BDDScenarios : TestSteps\n\t{\n\t\t')
        for line in to_iter: 
            if "Given" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
               
                func_generator_cs("Given",line[len("Given"):],result_file)
                
            elif "And" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_cs("And",line[len("And"):],result_file)

            elif "When" in line and len(re.findall("<[A-Za-z_0-9]*>", line))==0:
                func_generator_cs("When",line[len("When"):],result_file)

            elif "And" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func_generator_with_variable_cs("And",line,result_file)        

            elif "Given" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func_generator_with_variable_cs("Given",line,result_file)

            elif "When" in line and len(re.findall("<[A-Za-z_0-9]*>", line))!=0:
                func_generator_with_variable_cs("When",line,result_file)
        result_file.write('}\n}')
        folder = os.path.join(all_content['directory'],'BddScenario.cs')
        result_file=open(folder,'r')
         
    return HttpResponse(json.dumps({"file_content":all_content['scenario_string']}))


@csrf_exempt
def automatic(request):
    df = pd.read_csv('file.csv')
    return_list=[]
    fetched=json.loads(request.body.decode('utf-8'))
    for data in fetched['row']:
        temp=[]
        for i in df[data['Factor_name']]:
            temp.append(i)
        return_list.append(temp)
    return HttpResponse(json.dumps({"result":return_list}))

@csrf_exempt
def automatic_pre_post(request):
    df = pd.read_csv('pre_post.csv')
    fetched=json.loads(request.body.decode('utf-8'))
    row1=fetched['row1']
    row2=fetched['row2']
    return_list_pre=[]
    return_list_post=[]
   
    for data in df['pre']:
        
        return_list_pre.append(data)
    
    for data in df['post']:
        return_list_post.append(data)
      
    return HttpResponse(json.dumps({"result_pre":return_list_pre,"result_post":return_list_post,"tag":df['tag'][0],"scenerios":df['scenerio'][0]}))

@csrf_exempt
def enhance(request):
    global STEPT_DEF
    STEPT_DEF={}





    java_folder_path = 'C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/BDD_JAVA_Selenium_Latest/QA_UIAutomation_Selenium/src/main/java/com/evry/pageobjects'

    class_methods_dict = {}

    # Iterate through all files in the directory
    for filename in os.listdir(java_folder_path):
        if filename.endswith(".java"):
            # Open the Java file and parse it
            file_path = os.path.join(java_folder_path, filename)
            with open(file_path, 'r') as file:
                java_code = file.read()
                tree = javalang.parse.parse(java_code)

                class_name = None
                for path, node in tree:
                    if isinstance(node, javalang.tree.ClassDeclaration):
                        class_name = node.name
                        class_methods_dict[class_name] = {}
                    elif class_name and isinstance(node, javalang.tree.MethodDeclaration):
                        method_name = node.name
                        method_args = []
                        for param in node.parameters:
                            param_type = param.type.name if param.type else 'unknown'
                            param_name = param.name
                            method_args.append(f'{param_type} {param_name}')
                        return_type = node.return_type.name if node.return_type else 'void'
                        class_methods_dict[class_name][method_name] = {
                            'arguments': ', '.join(method_args),
                            'return_type': return_type
                        }
                        
    data=class_methods_dict
    STEPT_DEF=data
    print(STEPT_DEF)
    class_names=[]
    class_method_functions={}
    for class_name, methods in data.items():
        class_names.append(class_name)
        class_method_functions[class_name] = list(methods.keys())

    df = pd.read_csv('LowCodeApp.csv')

    return_list=[]
    for i in df['FunctionName']:
        return_list.append(i)
    return HttpResponse(json.dumps({"class_name":class_names,"class_functions":class_method_functions}))

# Run automation framework
@csrf_exempt
def integrate(request):
    os.chdir("C:/Users/Ei12974/Downloads/new_automation_framework/TechUtsav")
    cwd = os.getcwd()
    os.system("mvn clean install")
    return HttpResponse("ok")

@csrf_exempt
def enhanced_step_def(request):
    global STEPT_DEF
    df = pd.read_csv('LowCodeApp.csv')
    data=json.loads(request.body.decode('utf-8'))
    language=data['language']
    flag=data['flag']
    tag=data['tag']
    if language=='Java':
        class_names=[]
        for class_name, methods in STEPT_DEF.items():
            class_names.append(class_name)
        class_name_to_object = {class_name: class_name.lower() for class_name in class_names}
        java_folder_path_step_def= 'C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/BDD_JAVA_Selenium_Latest/QA_UIAutomation_Selenium/src/test/java/com/evry/stepdefs/'
# Find the first Java file
        first_java_file = None
        for filename in os.listdir(java_folder_path_step_def):
            if filename.endswith(".java"):
                first_java_file = os.path.join(java_folder_path_step_def, filename)
                break

        if first_java_file:
            with open(first_java_file, 'r') as file:
                java_code = file.read()
                tree = javalang.parse.parse(java_code)

                # Initialize a list to store the import statements
                imports = []

                # Iterate through the nodes and extract import statements
                for path, node in tree:
                    if isinstance(node, javalang.tree.Import):
                        import_statement = "".join(node.path).replace(';', '')  # Remove the semicolon
                        imports.append(import_statement)

                # Print the import statements
                print("Import Statements:")
                import_lines = [f'import {import_item};' for import_item in imports]

        # Combine all import statements into a single string
                combined_imports = '\n'.join(import_lines)
                print(combined_imports)
        else:
            print("No Java files found in the directory.")



        all_content['scenario_string'] = ''
        all_content['scenario_string'] +='import com.evry.pageobjects.*;'+'\n'+combined_imports+'\n'+'public class LowCode  {'+'\n'+'\n'+'\t'
        for class_name, lowercase_name in class_name_to_object.items():
            class_reference = f"{class_name} {lowercase_name}"
            all_content['scenario_string']+=class_reference+';'+'\n'+'\t'
        # result_file.write('public class seatbooking  {'+'\n'+'\n'+'\t')
        all_content['scenario_string']+='public LowCode(TestContext context){'+'\n'+'\t'+'\t'+'testContext = context;'+'\n'+'\t'+'\t'
        
        with open("C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/object.java", "r") as file:
            java_code = file.read()

        tree = javalang.parse.parse(java_code)

        # Define a dictionary to store the return types and their corresponding method names
        return_type_method_dict = {}

        # Iterate through the parse tree to find method names and return types
        for path, node in tree:
            if isinstance(node, javalang.tree.MethodDeclaration):
                method_name = node.name
                return_type = node.return_type.name

                # Add the return type and method name to the dictionary
                return_type_method_dict[return_type] = method_name

        for class_name, lowercase_name in  class_name_to_object.items():
            code = f"{lowercase_name} = testContext.getPageObjectManager().{return_type_method_dict.get(class_name)}();"
            all_content['scenario_string']+=code
            all_content['scenario_string']+='\n'
            all_content['scenario_string']+='\t'+'\t'
       
        all_content['scenario_string']+='}'+'\n'+'\t'
        for line in data['pre_req']: 
            print("line:"+line['pre'][len("And"):])
            if "And" in line['pre']:
                # row=df.loc[df['FunctionName'] == line['selectedCar']]
                # for index, i in row.iterrows():
                #     object_with_func=i['ObjectName']+'.'+i['FunctionName']
                #     param=str(i['param1'])
                #     returnparam=i['FunctionReturnParam']
                class_name=line['selectedCar']
                func_name=line['selectedCar_option']
                if class_name in STEPT_DEF and func_name in STEPT_DEF[class_name]:
                    method_info = STEPT_DEF[class_name][func_name]
                    arguments = method_info['arguments']
                    return_type = method_info['return_type']
                print("arguments:"+arguments)
                print("return type:"+return_type)
                object_with_func=class_name_to_object[line['selectedCar']]+'.'+line['selectedCar_option']
                func_generator_java("And",line['pre'][len("And"):],object_with_func,arguments,str(' '),flag,return_type)
        
            elif "Given" in line['pre']:
                # row=df.loc[df['FunctionName'] == line['selectedCar']]
                # for index, i in row.iterrows():
                #     object_with_func=i['ObjectName']+'.'+i['FunctionName']
                #     param=str(i['param1'])
                #     returnparam=i['FunctionReturnParam']
                class_name=line['selectedCar']
                func_name=line['selectedCar_option']
                if class_name in STEPT_DEF and func_name in STEPT_DEF[class_name]:
                    method_info = STEPT_DEF[class_name][func_name]
                    arguments = method_info['arguments']
                    return_type = method_info['return_type']
                object_with_func=class_name_to_object[line['selectedCar']]+'.'+line['selectedCar_option']
                print("arguments:"+arguments)
                print("return type:"+return_type)
                func_generator_java("Given",line['pre'][len("Given"):],object_with_func,arguments,str(' '),flag,return_type)
        
            elif "When" in line['pre']:
                # row=df.loc[df['FunctionName'] == line['selectedCar']]
                # for index, i in row.iterrows():
                #     object_with_func=i['ObjectName']+'.'+i['FunctionName']
                #     param=str(i['param1'])
                #     returnparam=i['FunctionReturnParam']
                class_name=line['selectedCar']
                func_name=line['selectedCar_option']
                if class_name in STEPT_DEF and func_name in STEPT_DEF[class_name]:
                    method_info = STEPT_DEF[class_name][func_name]
                    arguments = method_info['arguments']
                    return_type = method_info['return_type']
                object_with_func=class_name_to_object[line['selectedCar']]+'.'+line['selectedCar_option']
                func_generator_java("When",line['pre'][len("When"):],object_with_func,arguments,str(' '),flag,return_type)
        for line in data['post_req']: 
            if "And" in line['post']:
                # row=df.loc[df['FunctionName'] == line['selectedCar']]
                # for index, i in row.iterrows():
                #     object_with_func=i['ObjectName']+'.'+i['FunctionName']
                #     param=str(i['param1'])
                #     returnparam=i['FunctionReturnParam']
                if class_name in STEPT_DEF and func_name in STEPT_DEF[class_name]:
                    method_info = STEPT_DEF[class_name][func_name]
                    arguments = method_info['arguments']
                    return_type = method_info['return_type']
                object_with_func=class_name_to_object[line['selectedCar']]+'.'+line['selectedCar_option']
                func_generator_java("And",line['post'][len("And"):],object_with_func,arguments,str(' '),flag,return_type)
        
            elif "Given" in line['post']:
                # row=df.loc[df['FunctionName'] == line['selectedCar']]
                # for index, i in row.iterrows():
                #     object_with_func=i['ObjectName']+'.'+i['FunctionName']
                #     param=str(i['param1'])
                #     returnparam=i['FunctionReturnParam']
                if class_name in STEPT_DEF and func_name in STEPT_DEF[class_name]:
                    method_info = STEPT_DEF[class_name][func_name]
                    arguments = method_info['arguments']
                    return_type = method_info['return_type']
                print("arguments:"+arguments)
                print("return type:"+return_type)
                object_with_func=class_name_to_object[line['selectedCar']]+'.'+line['selectedCar_option']
                
                func_generator_java("Given",line['post'][len("Given"):],object_with_func,arguments,str(' '),flag,return_type)
            
            elif "When" in line['post']:
                # row=df.loc[df['FunctionName'] == line['selectedCar']]
                # for index, i in row.iterrows():
                #     object_with_func=i['ObjectName']+'.'+i['FunctionName']
                #     param=str(i['param1'])
                #     returnparam=i['FunctionReturnParam']
                if class_name in STEPT_DEF and func_name in STEPT_DEF[class_name]:
                    method_info = STEPT_DEF[class_name][func_name]
                    arguments = method_info['arguments']
                    return_type = method_info['return_type']
                object_with_func=class_name_to_object[line['selectedCar']]+'.'+line['selectedCar_option']
                func_generator_java("When",line['post'][len("When"):],object_with_func,arguments,str(' '),flag,return_type)
        all_content['scenario_string']+='\n}'
    # Read the contents of Runner.java file
    with open("C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/Runner.java", "r") as file:
        java_code = file.read()

    # Define a regular expression pattern to match the @CucumberOptions annotation
    pattern = r'@CucumberOptions\([^)]*\)'

    # Search for the annotation in the Java code
    match = re.search(pattern, java_code)

    if match:
        annotation_text = match.group(0)
        # Extract the value of the 'tags' attribute if it exists
        tags_match = re.search(r'tags\s*=\s*"([^"]*)"', annotation_text)
        if tags_match:
            current_tags = tags_match.group(1)
            print(f"Current Tags: {current_tags}")
            new_tags = tag
            modified_annotation = re.sub(r'tags\s*=\s*"[^"]*"', f'tags = "{new_tags}"', annotation_text)
            
            # Replace the original annotation with the modified one in the Java code
            java_code = re.sub(pattern, modified_annotation, java_code)

            # Write the modified Java code back to the file
            with open("C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/Runner.java", "w") as file:
                file.write(java_code)
            
            print(f"Modified Tags: {new_tags}")
        else:
            with open("C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/pom.xml", "r") as pom_file:
                pom_xml = pom_file.read()
            
            new_pom_xml = re.sub(r'<tags>.*</tags>', '<tags>{}</tags>'.format(tag), pom_xml)
            
            # Write the modified pom.xml back to the file
            with open("C:/Users/Ei12974/Downloads/BDD_JAVA_Selenium_Latest/pom.xml", "w") as pom_file:
                pom_file.write(new_pom_xml)
    else:
        print("No @CucumberOptions annotation found in the Java code")
    print(all_content['scenario_string'])
    return HttpResponse(json.dumps({"file_content":all_content['scenario_string']}))


@csrf_exempt
def report(request):
    webbrowser.open_new_tab('C:/Users/Ei12974/Downloads/new_automation_framework/TechUtsav/target/cucumber-reports/AutomationResults.html')
    return HttpResponse("ok")

@csrf_exempt
def get_inputdata(request):
    data = []
    root = tk.Tk()
    root.wm_attributes('-topmost', True)
    root.withdraw()
    filetypes = (
    ('CSV Files', '*.csv'),)
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    root.destroy()
    if not file_path:
        return HttpResponse(json.dumps({'message':'please select a file'}))
    
    with open(file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(row)
    rows = []
    for row in data:
        factor_name = row['Factor_name']
        level_count = row['Level_count']
        level_values = row['Level_values'].split(',')

        level_value = [{'value': value} for value in level_values]
        
        rows.append({
            'Factor_name': factor_name,
            'Level_count': level_count,
            'Level_value': level_value,
            'Level_values': ''
        })
    return HttpResponse(json.dumps({'rows': rows}))

@csrf_exempt
def save_data(request):
        os.makedirs(all_content['directory'], exist_ok=True)
        folder = os.path.join(all_content['directory'],'inputData.csv')
        fieldnames = list(all_content['dictionary'][0].keys())
        with open(folder, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_content['dictionary'])
        
        folder = os.path.join(all_content['directory'],'TableData.csv')
        with open(folder, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(all_content['fieldnames'])
        with open(folder, 'a', newline='') as file:
            writer = csv.writer(file)
            for entry in all_content['table_dictionary']:
                row_values = [value for _, value in entry.items()]
                writer.writerow(row_values)

        folder = os.path.join(all_content['directory'],'BDDscenario.feature')
        feature_file=open(folder,'w')
        feature_file.write(all_content['result'])
        
        folder = os.path.join(all_content['directory'],'BddScenario.java')
        result_file=open(folder,'w')
        result_file.write(all_content['scenario_string'])
        
        return HttpResponse('ok')


    