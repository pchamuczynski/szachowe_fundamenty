class Task:
    def __init__(self, tuple):
        self.__init__(self, tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6])
        
    def __init__(self, fen, chapter, lesson, number, tags, url, comment):
        self.FEN = fen
        self.chapter = chapter
        self.lesson = lesson
        self.number = number
        self.tags = tags
        self.url = url
        self.comment = comment     
    
    def __str__(self):
        return 'Chapter: ' + self.chapter + ', Lesson: ' + self.lesson + ', Task number: ' + str(self.number) +  \
           '\nTags: ' + str(self.tags) + '\nurl: ' + self.url + '\nComment: ' + self.comment + '\n' + self.FEN
