import os

os.chdir("C:/Users/Ei12974/Downloads/TechUtsav (5)/TechUtsav")
cwd = os.getcwd()
 
# print the current directory
print("Current working directory is:", cwd)
os.system("mvn test clean")