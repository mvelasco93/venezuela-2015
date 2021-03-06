# -*- coding: utf-8 -*-
# encoding: utf-8

__author__ = 'madevelasco'

import json
import re
import unicodedata
#import hunspell
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
import datetime
import time
from dateutil.parser import parse

def get_fields_tw():
    tw_file = open('../results/tweets_depurated.csv', 'w')
    tw_file_no_text = open('../results//tweets_depurated_noText.csv', 'w')
    tw_file_users = open('../results/tweets_users.csv', 'w')
    cabecera = 'id_tweet,id_user,longitude,latitude,words,timestamp_ms,n_retw,hashtags,dia,hora,isDay,isWeekDay,count,provincia\n'
    cabecera_no_text = 'id_tweet,id_user_str,longitude,latitude,timestamp_ms,n_retw,dia,hora,isDay,isWeekDay,count\n'
    # Information about users is going to be taken care after
    # cabecera_users = 'id_tweet,id_user8, statuses_count, followers_count, friends_count, location, lang,  geo_enabled, favourites_count'
    tw_file.write(cabecera)
    tw_file_no_text.write(cabecera_no_text)

    # Information about users is going to be taken care after
    # tw_file_users.write(cabecera_users)

    data = open('../data/venezuela_poblacion.json')

    for line in data:
        if (line.strip() != '\n'):
            hashtags = ''
            try:
                tweet = json.loads(line.decode('utf-8'))
                if tweet['coordinates']:
                    longitude = str(tweet['coordinates']['coordinates'][0])
                    latitude = str(tweet['coordinates']['coordinates'][1])
                    texto = tweet['text']

                    texto = re.sub(r'@(.+?)\s+', '', texto)
                    texto = re.sub(r'@(.+?)\Z', '', texto)
                    texto = re.sub(r'#(.+?)\s+', '', texto)
                    texto = re.sub(r'#(.+?)\Z', '', texto)
                    texto = re.sub(r'http(.+?)\s+', '', texto)
                    texto = re.sub(r'http(.+?)\Z', '', texto)
                    texto = re.sub(r'jaja{1,}?', '', texto)
                    texto = re.sub(r'j{2,}?', '', texto)
                    texto = re.sub(r'jeje{1,}?', '', texto)
                    content = normalization(texto)

                    # Time information
                    t_timestamp = time.mktime(parse(tweet['created_at']).timetuple())
                    esdia = isDay(t_timestamp)
                    entresemana = isWeekDay(t_timestamp)
                    dia = str(day(t_timestamp))
                    hora = str(hour(t_timestamp))

                    # Country information

                    if (is_ven(tweet) and has_province(tweet) and tweet['lang'] == 'es'):
                        if ('id_str' in tweet['user']):
                            user_id = str(tweet['user']['id_str'])
                        else:
                            user_id = str(tweet['user']['id'])

                        #No devuelve tweet si está vacío tras normalizar y eliminar stopwords
                        #No se esta aplicando Hunspell
                        if (content != "" ):
                            for h in tweet['entities']['hashtags']:
                                hashtags = hashtags + ' ' + h['text'].encode('ascii','ignore')
                            if not hashtags:
                                hashtags = ' '
                            line = tweet['id']['$numberLong']+','+user_id + ',' + longitude + ',' + latitude + ',' + content + ','+ str(t_timestamp)+ ',' + str(tweet['retweet_count']) + ',' + hashtags + ','+dia+',' +hora+','+esdia+','+entresemana+','+'1,'+str(tweet['provincia'])+ ',\n'
                            tw_file.write(line.encode('utf-8'))

                        line_noText = tweet['id']['$numberLong']+','+user_id + ',' + longitude + ','  + latitude + ',' + str(t_timestamp)+ ',' + str(tweet['retweet_count'])+','+dia+','+hora+','+esdia+','+entresemana+','+ '1 \n'
                        tw_file_no_text.write(line_noText)

                        # Information about users is going to be taken care after
                        """line_users = tweet['id']['$numberLong']+','+user_id + ','+str(tweet['user']['statuses_count'])+','+str(tweet['user']['followers_count'])+','+str(tweet['user']['friends_count'])+','+tweet['user']['location']+','+tweet['user']['lang']+','+str(tweet['user']['geo_enabled'])+','+str(tweet['user']['favourites_count'])
                        tw_file_users.write(line_users.encode('utf-8'))"""

            except ValueError:
                pass
    tw_file.close()

def normalization(text):
    text = text.lower()
    other = ''
    # Hunspell not incluided
    # hobj_spanish = hunspell.HunSpell('dic_spanish/Spanish.dic', 'dic_spanish/Spanish.aff')
    stemmer_english = SnowballStemmer("english")
    for element in text:
        other =other+remove_accents(element)
    text = other

    words = re.findall(r'\w+', text, flags=re.UNICODE | re.LOCALE)
    depured = ""
    for word in words:
        word = deleteConsecutives(word)
        #Won't pass if word lenght is lower than 2
        if (len(re.findall('[a-zA-Z]', word))>2):
            if word not in stopwords.words('spanish') and word not in stopwords.words('spanish'):
                depured = depured + " " + word
    return depured

def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def isDay(tiempo):
    fecha = datetime.datetime.fromtimestamp(tiempo)
    hora = fecha.hour
    #Entre 7 am y antes de las 18 pm
    if (hora > 7 and hora < 18):
        return '1'
    else:
        return '0'

def isWeekDay(tiempo):
    fecha = datetime.datetime.fromtimestamp(tiempo)
    dia = fecha.weekday()
    #Lunes, martes, miercoles y jueves
    if (dia >= 0 and dia <=3):
        return '1'
    else:
        return '0'

def day(tiempo):
    fecha = datetime.datetime.fromtimestamp(tiempo)
    return fecha.weekday()

def hour(tiempo):
    fecha = datetime.datetime.fromtimestamp(tiempo)
    return fecha.hour

def deleteConsecutives(word):
    if re.search(r'(.)\1\1', word):
        prev1 = ''
        prev2 = ''
        result = ''
        for ch in word:
            if (ch != prev1 and ch != prev2):
                if (prev2 != ''):
                    prev2 = prev1
                    prev1 = ch
                    result=result+ch
                else:
                    prev1 = ch
                    result = result + ch
        return result
    else:
        return word

def is_ven(tweet):
    if 'country' in tweet:
            if tweet['country'] == 'Venezuela':
                return True
            else:
                return False
    else:
        return False

def has_province(tweet):
    if 'provincia' in tweet:
        return True
    else:
        return False


if __name__ == '__main__':
    get_fields_tw()