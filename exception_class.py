class invalidInput(Exception):
    def __str__(self):
        return '점수 입력을 형식에 맞춰 제대로 해주세요.'

class invalidWind(Exception):
    def __str__(self):
        return '동장/반장을 제대로 입력해 주세요.'
    
class invalidName(Exception):
    def __str__(self):
        return '이름을 올바르게 입력해 주세요.'