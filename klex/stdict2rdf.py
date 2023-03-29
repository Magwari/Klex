import xml.etree.ElementTree as ET
from pathlib import Path
from rdflib import Graph, RDF, RDFS, OWL, SKOS, Literal, BNode, Namespace
from rdflib.namespace import FOAF, XSD
from utils import *
from tqdm import tqdm

# set graph and namespace
graph = Graph()
klex = Namespace('http://klex.org/ontology#')
ontolex = Namespace('http://www.w3.org/ns/lemon/ontolex#')
synsem = Namespace('http://www.w3.org/ns/lemon/synsem#')
decomp = Namespace('http://www.w3.org/ns/lemon/decomp#')
vartrans = Namespace('http://www.w3.org/ns/lemon/vartrans#')
lime = Namespace('http://www.w3.org/ns/lemon/lime#')

# get word items from stdict files
word_items = list()
stdict_path = Path(__file__).parent / 'data' / 'stdict'
xml_list = [file_path for file_path in stdict_path.glob("*.xml")]

print(f'find {len(xml_list)} XML files in "data/stdict/"')
print('extract word items from stdict XML files...')
for file in tqdm(xml_list):
    xml_tree = ET.parse(file.absolute())
    word_items.extend(xml_tree.findall('.//item'))

print('generating RDF graph...')
# issue: element.find method searches all childen from first. It could be optimized.
for word_item in tqdm(word_items):
    # Id number for non-unique object
    # issue: It should be functionalized. 
    form_id_num = 1

    word_code = word_item.find('target_code').text
    canonical_form_written_rep = word_item.find('word_info/word').text
    word_unit = word_item.find('word_info/word_unit').text
    # word_type = word_item.find('word_info/word_type').text
    # issue : if word_unit is "관용구, 속담", there is no word_type. Needs some exceptions.

    pronunciation_list = word_item.findall('word_info/pronunciation_info/pronunciation')
    conju_list = word_item.findall('word_info/conju_info')
    origin = word_item.find('word_info/origin')
    entry_relation_list = word_item.findall('word_info/lexical_info')

    # LexicalEntry
    lexicalEntry = klex.term('E'+word_code)
    graph.add((lexicalEntry, RDF.type, ontolex.LexicalEntry))
    # issue: need to be classified with word_unit. there are a lot of undefined relations.
    
    # LexicalForm(canonical form), representations
    lexicalForm = klex.term('F'+word_code+f'{form_id_num:03d}')
    form_id_num += 1
    graph.add((lexicalForm, RDF.type, ontolex.LexicalForm))
    graph.add((lexicalEntry, ontolex.canonicalForm, lexicalForm))
    graph.add((lexicalForm, ontolex.writtenRep, Literal(canonical_form_written_rep, lang="kr"))) #
    
    for pronunciation in pronunciation_list:
        pronun_written_rep = pronunciation.text
        graph.add((lexicalForm, ontolex.phoneticRep, Literal(pronun_written_rep, lang="kr"))) 

    for pos_info in word_item.findall('word_info/pos_info'):
        pos_code = pos_info.find('pos_code').text
        pos = pos_info.find('pos').text

        for comm_pattern_info in pos_info.findall('comm_pattern_code'):
            comm_patern_code = comm_pattern_info.find('comm_pattern_code')
            pattern_list = comm_pattern_info.findall('pattern_info/pattern')
            grammar_list = comm_pattern_info.findall('grammar_info/grammar')

            for sense_info in comm_pattern_info.findall('sense_info'):
                sense_code = sense_info.find('sense_code').text
                sense_type = sense_info.find('type').text
                definition = sense_info.find('definition_original').text
                sense_pattern_list = sense_info.findall('sense_pattern_info/pattern')
                sense_grammar_list = sense_info.findall('sense_grammar_info/grammar')
                example_list = sense_info.findall('example_info/example')
                sense_relation_list = sense_info.findall('lexical_info')

                # LexicalSense
                lexicalSense = klex.term('S'+sense_code)
                graph.add((lexicalEntry, ontolex.sense, lexicalSense))