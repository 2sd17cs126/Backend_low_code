import re
def func_generator(keyword,argument):
    
    structure=keyword+'(\''+argument+'\',()=>{'+'\n'+'})'+'\n'
    result_file.write(structure)

def func_generator_with_variable(keyword,line):
    variable_string="("
    removing_word_list=[]
    removing_word_list.append(keyword)
    removing_word_list.append(',')
    preced_place_holder=""
    for data in re.findall("<[a-z_0-9]*>", line):
        preced_place_holder=preced_place_holder+"{"+"string"+"},"
        print(preced_place_holder)
        variable_string=variable_string+data[1:-1]+','
        temp="\"<"+data[1:-1]+">\""
        removing_word_list.append(temp)
    preced_place_holder=preced_place_holder[:-1]
    variable_string=variable_string[:-1]+')'
    for rem in removing_word_list:
        if rem in line:
            print("rem:"+rem)
            line=line.replace(rem,"")
    print("precedence:"+preced_place_holder)
    structure=keyword+'(\''+line+preced_place_holder+'\','+variable_string+'=>{'+'\n'+'})'+'\n'
    result_file.write(structure)
file=open('backend\sample.feature','rt')
content=file.read()
file.close()
content=content[:content.find("Examples:")]

to_iter=content.split("\n")[2:]
result_file=open('backend/Orthogonal_array/result.js','w')
for line in to_iter:
    if "Given" in line and len(re.findall("<[a-z_0-9]*>", line))==0 :
        func_generator("Given",line[len("Given"):])
    elif "And" in line and len(re.findall("<[a-z_0-9]*>", line))==0:
        func_generator("And",line[len("And"):])
    elif "When" in line and len(re.findall("<[a-z_0-9]*>", line))==0:
        func_generator("When",line[len("When"):])
    elif "And" in line and len(re.findall("<[a-z_0-9]*>", line))!=0:
        func_generator_with_variable("And",line)
result_file.close()
file=open('backend/Orthogonal_array/result.js','rt')
print(file.read())

    
