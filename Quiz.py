
import copy
import json
import random



class Quiz(object):
    def __init__(self, word, connection, num_choices=4):
        self.word = word
        self.conn = connection
        self.num_choices = num_choices

        self.indexes = self.__indexesGenerate()
        
        self.corr_ans = self.__answerGenerate()
        self.choices = self.__choicesGenerate()

    def check(self, answer):
        if self.corr_ans.has_key(answer):
            return True
        else:
            return False
            
    def get_correctChoice(self):
        result = ""

        for choice in self.corr_ans.keys():
            result += choice 
        
        return result

    def get_word(self):
        return self.word

    def get_question(self):
        return "Please choose the meaining of " + self.word + "."
    
    def get_choices(self):
        return self.choices

    def __answerGenerate(self):
        meaning = ""
        with self.conn.cursor() as cursor:
            sql = "SELECT meaning FROM dict WHERE word = %s;"
            cursor.execute(sql, (self.word))
            #process json
            meaning = cursor.fetchone()['meaning']
        return {random.choice(self.indexes):meaning}

    def __choicesGenerate(self):
        result = dict(self.corr_ans)
        indexes = copy.copy(self.indexes)

        for key in self.corr_ans.keys():
            indexes.remove(key)

        wordId = self.__get_wordId(self.word)
        curr = wordId - self.num_choices//2

        for i in xrange(self.num_choices-1):
            if curr <= 0:
                curr = 1
                tmp = self.__choicesGenerateHelper(curr, wordId, indexes)
                result.update(tmp[0])
                curr += tmp[1] 
            else:
                tmp = self.__choicesGenerateHelper(curr, wordId, indexes)
                result.update(tmp[0])
                curr += tmp[1]
            curr += 1
        return result


        
    def __choicesGenerateHelper(self, curr, wordId, indexes):
        if curr != wordId:
             index = random.choice(indexes)
             indexes.remove(index)
             return [{index:self.__fetchMeaning(curr)},0]
        else:
            curr = curr + 1
            index = random.choice(indexes)
            indexes.remove(index)
            return [{index:self.__fetchMeaning(curr)},1]
        
    
    def __fetchMeaning(self, wordId):
        meaning = ""
        with self.conn.cursor() as cursor:
            sql = "SELECT meaning FROM dict WHERE id = %s;"
            cursor.execute(sql, (wordId))

            #process json
            meaning = cursor.fetchone()
        if meaning == None:
            with self.conn.cursor() as cursor:
                sql = "SELECT meaning FROM dict WHERE id = %s;"
                cursor.execute(sql, (1))
                meaning = cursor.fetchone()

        return meaning['meaning']

    def __get_wordId(self, word):
        with self.conn.cursor() as cursor:
            sql = "SELECT id FROM dict WHERE word = %s;"
            cursor.execute(sql, (word))
            return cursor.fetchone()['id']

    def __indexesGenerate(self):
        result = []
        for i in xrange(self.num_choices):
            result.append(chr(ord('A') + i))

        return result

    
