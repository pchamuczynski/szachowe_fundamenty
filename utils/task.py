class Task:
    def __init__(self, tuple):
        self.__init__(self, tuple[1], tuple[2], tuple[3], tuple[4], tuple[5], tuple[6])
        
    def __init__(self, fen, chapter, lesson, number, tags, comment):
        self.FEN = fen
        self.chapter = chapter
        self.lesson = lesson
        self.number = number
        self.tags = tags
        self.comment = comment     
        # print('Task created ' + str(self))
    
    def __str__(self):
        return self.FEN + '\t(Chapter: ' + self.chapter + ', Lesson: ' + self.lesson + ', Task number: ' + str(self.number) + ', Tags: ' + str(self.tags) + ', Comment: ' + self.comment +')'       
