# -*- coding: utf-8 -*-
#
# python wrapper for word query from jeck.ru
# Author:       HE Chong [[chong.he.1989@gmail.com][E-mail]]
#
#
# Note: jeck.ru store words of their multiple forms, so not much stemming is
# needed(which is good, I don't want too much dependency to this plugin if I
# can avoid it).

import urllib2
import re
from tq_common_lib import decode_utf_8, encode_utf_8, fixurl

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

identifier="jeck_ru"
language="ru"

def query(target):
    ''' return result as list. relavance from high to low in each PoS.
Lookup routine for datamuse.com. When query_from_source is called, return:
   [status, [[PoS, [word_0, word_1, ...]],  [PoS, [word_0, word_1, ...]], ...]]
status:
    0: normal,  result found, list will be returned as a nested list
    1: normal, result not found, return empty list
    -1: unexpected result from query, return empty list
nested list = [PoS, list wordlist]
    Classifier('str'): Identifier to classify the resulting wordlist suits.
    wordlist = [word_0, word_1, ...]: list of words belonging to a same definition
    '''
    target=target.replace(u" ", u"+")
    result_list=jeck_ru_url_handler(target)
    if result_list == 1:
        return [1,[]]
    else:
        synonym_list = parser(result_list)
        if synonym_list:
            return [0, [[u"", synonym_list]]]
        else:
            return [1, []]

def jeck_ru_url_handler(target):
    '''
    Query jiport for sysnonym
    '''
    try:
        response = urllib2.urlopen(fixurl('http://jeck.ru/tools/SynonymsDictionary/{}'.format(encode_utf_8(target))), timeout=5)
        web_content = StringIO(decode_utf_8(response.read()))
        response.close()
    except urllib2.URLError, error:
#        print "The word \"{}\" has not been found on jeck.ru!\n".format(target)
        return 1
    return web_content


def parser(webcontent):
    end_tag_count=4
    synonym_list = []
    while True:
        line_curr = webcontent.readline()
        if not line_curr:
            break
#        if "no thesaurus results" in line_curr:
#            output = "The word \"{}\" has not been found on jeck.ru!\n".format(target)
#            break
#        if "Всего" in line_curr and ("синонимов" in line_curr or "синонима" in line_curr):
        if u"На странице нет нецензурных слов." in line_curr:
            end_tag_count=0
            continue
        elif end_tag_count<4:
            if u"</div>" in line_curr:
                end_tag_count+=1
                continue
            elif u"href" in line_curr:
                fields = re.split(u"<|>", line_curr)
                synonym_list.append(fields[2].lower())
                continue
#            fields = re.split("<|>", line_curr)
#            if len(fields)<3:
#                continue
#            elif len(fields)<10:
#                if "txt" in fields[1]:
#                    output+="\nDefinition: {}. ".format(fields[2])
#                    continue
#                elif "ttl" in fields[1]:
#                    output+="{}\nSynonyms:\n".format(fields[2])
#                    continue
#            elif "www.thesaurus.com" in fields[3]:
#                output+="{} {}\n".format(fields[6], fields[14])
    webcontent.close()
    return synonym_list
