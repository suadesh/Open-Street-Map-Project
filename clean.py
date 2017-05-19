import xml.etree.cElementTree as ET
import re 



# using elemet tree to parse trhoug the OSM file 
tree = ET.parse('rome_italy.osm')
root = tree.getroot()

# Auudit of the Zip code , I will look for node where k value is = postal_code first 
zipcode = []
for item in root:
    for child in item: 
        if child.get('k') =='postal_code':
            zipcode.append(child.get('v'))

# I will also use iterpaser looking fo key = addr:postcode 
            
for elem, event in ET.iterparse('rome_italy.osm'):
    if event.get('k') == "addr:postcode":
        zipcode.append(event.get('v'))

# I will use this list to look all the diffrent value of ZIP code 
print (zipcode,len(zipcode))

# actually code for rome are from 00010 to 00199, with some exeption so I will make a dictionaty
# with the value that do not correspond to it using RE 
wrongzip = {}
test = re.compile(r"00[0-1][0-9][0-9]")
for item in zipcode: 
    if re.match(test,item):
        if len(item) > 5:
            wrongzip[item] = item
        else:
            continue
    else:
        wrongzip[item] = item


print (wrongzip)

# finally i will modify the dictionary with the corrected value, or at least the most evident error , i will not handle the rest in SQL  

wrongzip['I-00128'] ='00128'
wrongzip['00184 Roma'] ='00184'
wrongzip['00040 Rocca di Papa'] ='00040'
wrongzip['191'] ='00191'
wrongzip['00124 Roma'] ='00124'
wrongzip['159'] ='00159'
wrongzip['0186'] ='00186'
wrongzip['187'] ='00187'
wrongzip['000127'] ='00127'
wrongzip['01555'] ='00155'

# and now i have a dictionary with the corrected values 
print(wrongzip)


# using element Tree i will interparse throught the file looking for k value = add:street and make a list 
strade = []
for elem, event in ET.iterparse('rome_italy.osm'):
    if event.get('k') == "addr:street":
        strade.append(event.get('v'))

# this will createa a list and the a ditcionary with the first value of street name,
# this will help me find typo throught the file 
audit = set()
for strada in strade:
    diviso = strada.split()
    audit.add(diviso[0])
sorted(audit)

correctroad = {}
for item in audit :
    correctroad[item] = item
    
print(correctroad)

# This will show me specific strange values 
for item in strade :
    div = item.split()
    if div[0] == 'Alberto':
        print (item) 
# i modify the dictionaty. most of the errors are typo, but there are also a couple of missing value 

correctroad['piazzale'] = 'Piazzale'
correctroad['VIa'] = 'Via'
correctroad['Della'] = 'Via della'
correctroad['via'] = 'Via'
correctroad['Viai'] = 'Via'
correctroad['Plazza'] = 'Piazza'
correctroad['lungomare'] = 'Lungomare'
correctroad['Margutta'] = 'Via Margutta'
correctroad['campo'] = 'Campo'
correctroad['piazza'] = 'Piazza'
correctroad['viale'] = 'Viale'
correctroad['largo'] = 'Largo'
correctroad['di'] = 'Via di'
correctroad['Alberto'] = 'Via Alberto'
correctroad['corso'] = 'Corso'
correctroad['Vi'] = 'Via'
correctroad['P.za'] = 'Piazza'
correctroad['Vía'] = 'Via'

print(correctroad)

# I m now ready to clean it up while exporting to CSV files 
import csv
import codecs
import pprint

# all files to import and to export 
OSM_PATH = "rome_italy.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

# list that will help to correspond values from csv to the sql DB 
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

# this three function will clean for road name and zipcode the values before entering in the dictioanry and go to the CSV files 


def road(item,correctroad):
    local = item.get('v')    
    while True:
    	# I have to use try to avois to block the process in case of key error. this error can occour from utf-8 
        try:
            diviso = local.split(" ")
            first = diviso[0] 
            diviso[0] = correctroad[first]
            newlocal = " ".join(diviso)
            break 
        except KeyError:
            newlocal = local
            break
    return newlocal

def zipcode(item,wrongzip):
    postalcode = item.get('v')
    if postalcode in wrongzip:
        newcode = wrongzip[postalcode]
    else:
        newcode= postalcode
    return newcode 


def roadname(item,correctroad):
    local = item.get('v')
    while True:
        # te same as before but in way_tags name coantains also other thigs than only street name, so this function will avoid issue 
        try:
            diviso = local.split(" ")
            first = diviso[0]
            if first in correctroad:
                diviso[0] = correctroad[first]
                newlocal = " ".join(diviso)
                break
            else:
                newlocal = local 
                break 
        except KeyError:
            newlocal = local
            break
    return newlocal 

# this is the  function  create the dictionaries that will then exportd in CSV 
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, default_tag_type='regular',goodroad = correctroad, wrongzip = wrongzip):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  
    if element.tag == 'node':
        id = element.attrib['id']
        for i in node_attr_fields:
            node_attribs[i] = element.attrib[i]
        for child in element:
            if child.tag == "tag":
                tag = {}
                tag['id'] = element.attrib['id']
                key = child.attrib["k"]
                if ":" in key:
                    tag["key"] = key[(child.attrib["k"].find(":"))+1:]
                    tag["type"] = key[:(child.attrib["k"].find(":"))]
                    if key == "addr:street":
                        tag["value"] = road(child, goodroad)
                    elif key == "addr:postcode":
                        tag["value"] = zipcode(child,wrongzip) 
                    else:
                        tag["value"] = child.attrib["v"]
                elif key == 'postal_code':
                    tag["value"] = zipcode(child,wrongzip)
                else:
                    tag["value"] = child.attrib['v']
                    tag["key"] = child.attrib["k"]
                    tag["type"] = default_tag_type
                tags.append(tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        id = element.attrib['id']
        for x in way_attr_fields: 
            way_attribs[x] = element.attrib[x]
        # a so i have te position of each ways nodes 
        a = 0 
        for child  in element:
            if child.tag == 'nd':
                way_node={}
                way_node['id']= id 
                way_node['node_id'] = child.attrib['ref']
                way_node['position'] = a 
                a +=1 
                way_nodes.append(way_node)
            elif child.tag == "tag":
                tag = {}
                tag['id'] = element.attrib['id']
                key = child.attrib["k"]
                if ":" in key:
                    tag["key"] = key[(child.attrib["k"].find(":"))+1:]
                    tag["type"] = key[:(child.attrib["k"].find(":"))]
                    if key == "addr:street":
                        tag["value"] = road(child, goodroad)
                    elif key == "addr:postcode":
                        tag["value"] = zipcode(child,wrongzip) 
                    else:
                        tag["value"] = child.attrib["v"]
                elif key == 'postal_code':
                    tag["key"] = child.attrib["k"]
                    tag["value"] = zipcode(child,wrongzip)
                    tag["type"] = default_tag_type
                elif key == 'name':
                    tag["key"] = child.attrib["k"]
                    tag["value"] = roadname(child,goodroad)
                    tag["type"] = default_tag_type
                else:    
                    tag["value"] = child.attrib['v']
                    tag["key"] = child.attrib["k"]
                    tag["type"] = default_tag_type
                tags.append(tag)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}     

# this will do the parsing 
def get_element(osm_file, tags=('node', 'way', 'relation')):

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


class UnicodeDictWriter(csv.DictWriter, object):

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow(row)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

#finally the main function that will use all that is above to omplete the export to the CSV 
 def process_map(file_in):
    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
        codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:
        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


process_map(OSM_PATH)