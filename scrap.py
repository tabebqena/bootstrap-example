import os
import requests
from urllib.parse import urljoin, urldefrag
# BeautifulSoup is imported with the name bas4 
import bs4
from bs4 import Tag
import json
file_path = "./file.json"
class_name = "bd-example"
page_examples = {}
examples_urls = []
  
remaining_links = set(['https://getbootstrap.com/docs/5.3/getting-started/introduction/',])
completed_links = set()
errors ={}

def is_valid_href(href):
  if not href :
    return False
  if "http" in href:
    return False
  return True

def get_href(link):
  href = link.get("href")
  if href:
    return   urldefrag(href)[0]
  return ""

def read_data():
  if os.path.exists(file_path):
    try:
      f = open("./file.json", "r") 
      data = json.loads( f.read() )
      completed_links.update( data.get("completed", [] ))
      errors.update( data.get("errors", {}))
      remaining_links.update( data.get("remaining", []))
      examples_urls.extend( data.get("examples", []))      
    except Exception as e:
      print(e)
      # return {"completed": [], "remaining": [], "errors": {}}
  
def write_data():
  data = json.dumps({ 
        "completed": list(completed_links), 
        "remaining": list(remaining_links) ,
        "errors": errors,
        "examples": examples_urls
         }, indent=4)
  try:
    with open(file_path+".new", "w") as f:
      f.write( data) 
    os.remove(file_path)
    os.rename( file_path+".new", file_path )
  except:
    os.remove(file_path+".new")
    pass
    

def soup_page(url):
  response = requests.get(url)
  return bs4.BeautifulSoup(response.text, 'html.parser')
   
def get_page_links(soup):    
    links = soup.select('a')
    rv = []
    for link in links: 
      href = get_href(link)
      if is_valid_href(href):
        rv.append( urljoin("https://getbootstrap.com/docs/5.3/",href))
    return rv


def get_all_links():
  while True:
    try:
      url = remaining_links.pop()
      if url in completed_links:
        write_data()
        continue
      
    except Exception as e:
      print("Error: ",e)
      break
    try:
      soup = soup_page(url)
      links = get_page_links(soup)
      remaining_links.update( links )
      completed_links.add(url)

    except Exception as e:
      print( e)
      errors[url]= str(e)
    write_data()

def write_html():
  soup = bs4.BeautifulSoup()
  
  html = Tag(soup, name="html")
  head = Tag(soup, name="head")
  style = Tag(soup, name="link")
  style.attrs["rel"] = "stylesheet"
  style.attrs["href"] = "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css"
  head.append(style)
  style = Tag(soup, name="link")
  style.attrs["rel"] = "stylesheet"
  style.attrs["href"] = "./docs.css"
  head.append(style)
  
  # 
  body = Tag(soup, name="body")
  for url, examples in page_examples.items():
    title = Tag(soup, name="a", attrs={"class": "text-center"})
    title.string = url
    div = Tag(soup, name="div")
    body.append(title)
    for example in examples:
      div.append(example)    
    body.append(div)
  html.append(head)
  html.append(body)
  soup.append(html)
  with open ("result.html", "w") as f:
    f.write(soup.prettify())

def get_all_examples(force = False):
  
  for url in completed_links:
    if not force and url in examples_urls:
      continue
    examples_urls.append(url)
    soup = soup_page(url)
    page_examples[url] = soup.find_all("div", {"class": class_name})
    write_data()
    write_html()

    

    


if __name__ == "__main__":
  read_data()
  get_all_links()

  get_all_examples()

 
  


