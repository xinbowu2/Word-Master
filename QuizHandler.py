

import pymysql
import math
from random import randint
from Quiz import *

class QuizHandler(object):

    def __init__(self, username, connection, num_quizes=10):
        self.username = username
        self.conn = connection
        self.num_quizes = num_quizes
        candidates = self.__candidatesGenerate()
        self.quizes = self.__quizesGenerate(candidates)

    def get_quizes(self):
        if not self.quizes:
            raise "Error no quizes generated"
        else:
            return self.quizes

    def updateCorrectness(self, username, results):
        print(results)
        for r in results:
            self.__updateCorrectnessHelper(username, r[0], r[1])

                
    def __updateCorrectnessHelper(self, username, word, answer):
        
        with self.conn.cursor() as cursor:
            sql = "UPDATE wordlist SET correctness = correctness + %s WHERE username = %s AND word = %s;"
            cursor.execute(sql, ((-1)**(answer+1), username, word))

        self.conn.commit()
            

    def __quizesGenerate(self, candidates):
        quizes = []
        
        for candidate in candidates:
            quizes.append(Quiz(candidate, self.conn))

        return quizes
        
    def __candidatesGenerate(self):
        with self.conn.cursor() as cursor:
            result = []
                
            sql = "SELECT word, orig_count, correctness, test_count FROM wordlist WHERE username = %s ;"
            cursor.execute(sql, (self.username))

            rows = []
            
            for row in cursor:
                rows.append(row)

        

            if self.num_quizes >= len(rows):
                candidates = []
                for row in rows:
                    candidates.append(row['word'])
                
                self.__incrementTestCounts(candidates)
                
            else:
                candidates = self.__candidatesGenerateHelper(rows)
                self.__incrementTestCounts(candidates)

            return candidates  

            
    def __candidatesGenerateHelper(self, rows):
        scores = dict()
        dom = len(rows)
        
        #implement calculating mean and sd
        nom = 0
        for row in rows:
           nom +=  row['test_count']

        mean = nom/dom

        nom = 0
        for row in rows:
           nom += (row['test_count']-mean)**2

        sd = math.sqrt(nom/dom)

        for row in rows:
            scores.update({row['word']:self.__get_score(row, mean, sd)})

        return sorted(scores, key=scores.__getitem__, reverse=True)[0:self.num_quizes]


    def __get_score(self, row, mean, sd, lenience=5):
        if row['test_count'] <= lenience:
            return math.floor(scale(row['orig_count'], row['correctness'])*row['orig_count'])*normpdf(mean, mean, sd)
        else:
            return math.floor(scale(row['orig_count'], row['correctness'])*row['orig_count'])*normpdf(row['test_count'], mean, sd)

    def __incrementTestCounts(self, candidates):
        with self.conn.cursor() as cursor:
            sql = "UPDATE wordlist SET test_count = test_count + 1 WHERE word IN %s AND username = %s ;"
            cursor.execute(sql, (tuple(candidates), self.username))

        self.conn.commit()

         
def normpdf(x, mean, sd):
    var = float(sd)**2
    denom = (2*math.pi*var)**.5
    num = math.exp(-(float(x)-float(mean))**2/(2*var))
    return num/denom


def scale(a, b):
    if a-b <= 0:
        return 0
    else:
        x = (float(a-b))/a
        if x <= 1:
            return x
        else:
            return float(2*(a-b))/a
        

    
"""
def __randomCandidates(self, generated_candidates, num_candidates):

        num_words = 0
        with self.conn.cursor as cursor:
            sql = "SELECT COUNT(*) FROM dictionary"
            cursor.execute(sql)
        
            num_words = cursor.fetchone()

        candidates = []
        while num_candidates <= 0:
            wordId = randint(0, num_words)
            fetchedWord = self.__fetchAWord(wordId)
            if fetchedWord not in generated_candidates and fetchedWord not in candidates:
                candidates.append(fetchedWord)
                

                
                num_candidates -= 1

        return candidates
            
        
        
            

    def __fetchAWord(self, wordId):
        
    def __initializeUnknownWord(self, word):
        with self.conn.cursor as cursor:
            sql = "INSERT INTO wordlist(orig_count, correctness, test_count)  "
            cursor.execute(sql, (tuple(candidates), self.username))

        self.conn.commit()
"""

    



            

        
