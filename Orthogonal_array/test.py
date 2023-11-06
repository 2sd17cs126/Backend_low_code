from lxml import etree
from bs4 import BeautifulSoup
# Define your XPath expression
xpath_expression = "html[1]/body[1]/div[1]/p[1]"

# Specify the path to your HTML file
html_file = "C:/Users/Ei12974/Downloads/integrate_extension_with_lowcode_app/Lowcode-app-master/src/assets/page.html "  # Replace with the actual file path
with open(html_file, "r", encoding="utf-8") as file:
   
    html_data = file.read()

# Parse and format the HTML using Beautiful Soup
soup = BeautifulSoup(html_data, "html.parser")
formatted_html = soup.prettify()
# Parse the HTML file
tree = etree.HTML(formatted_html)

print(tree)
# Find the UI object using the XPath expression
ui_object = tree.xpath(xpath_expression)
print(ui_object)
# Extract the child node content
child_content = []
for node in ui_object:
    # Iterate over the child nodes of the UI object
    for child in node.getchildren():
        # Extract the content of each child node
        child_content.append(child.text)

# Print the extracted content
for content in child_content:
    print(content)
