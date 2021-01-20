import math, re

class Inko:
    영어 = "rRseEfaqQtTdwWczxvgASDFGZXCVkoiOjpuPhynbmlYUIHJKLBNM"
    한글 = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎㅁㄴㅇㄹㅎㅋㅌㅊㅍㅏㅐㅑㅒㅓㅔㅕㅖㅗㅛㅜㅠㅡㅣㅛㅕㅑㅗㅓㅏㅣㅠㅜㅡ"
    초성 = "ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ"
    중성 = "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
    종성 = "ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"
    첫모음 = 28
    가 = 44032
    힣 = 55203
    ㄱ = 12593
    ㅣ = 12643

    영어index = (lambda en : {en[i]:i for i in range(len(en))})(영어)

    한글index = (lambda kr: {i:w for i, w in enumerate(kr)})(한글)

    connectableConsonant = {
        'ㄱㅅ': 'ㄳ',
        'ㄴㅈ': 'ㄵ',
        'ㄴㅎ': 'ㄶ',
        'ㄹㄱ': 'ㄺ',
        'ㄹㅁ': 'ㄻ',
        'ㄹㅂ': 'ㄼ',
        'ㄹㅅ': 'ㄽ',
        'ㄹㅌ': 'ㄾ',
        'ㄹㅍ': 'ㄿ',
        'ㄹㅎ': 'ㅀ',
        'ㅂㅅ': 'ㅄ'
    }

    connectableVowel = {
        'ㅗㅏ': 'ㅘ',
        'ㅗㅐ': 'ㅙ',
        'ㅗㅣ': 'ㅚ',
        'ㅜㅓ': 'ㅝ',
        'ㅜㅔ': 'ㅞ',
        'ㅜㅣ': 'ㅟ',
        'ㅡㅣ': 'ㅢ'
    }

    isVowel = lambda self, e: [k for k,v in self.한글index.items() if v == e][0] >= self.첫모음

    한글생성 = lambda self, *args: chr(44032 + args[0][0] * 588 + args[0][1] * 28 + args[0][2] + 1)

    def indexOf(self, val, _list):
        try:
            return _list.index(val)
        except ValueError:
            return -1    
    
    def __init__(self, **_option):
        option = {} if _option is None else _option
        self._allowDoubleConsonant = option["allowDoubleConsonant"] if "allowDoubleConsonant" in option else False
    
    def config(self, **_option):
        option = {} if _option is None else _option
        self._allowDoubleConsonant = option["allowDoubleConsonant"] if "allowDoubleConsonant" in option else False

    def en2ko(self, _input, **_option):
        option = {} if _option is None else _option
        self._allowDoubleConsonant = option["allowDoubleConsonant"] if "allowDoubleConsonant" in option else self._allowDoubleConsonant
        stateLength = [0, 1, 1, 2, 2, 2, 3, 3, 4, 4, 5]
        transitions = [
            [1, 1, 2, 2],   # 0, EMPTY
            [3, 1, 4, 4],   # 1, 자
            [1, 1, 5, 2],   # 2, 모
            [3, 1, 4, -1],  # 3, 자자
            [6, 1, 7, 2],   # 4, 자모
            [1, 1, 2, 2],   # 5, 모모
            [9, 1, 4, 4],   # 6, 자모자
            [9, 1, 2, 2],   # 7, 자모모
            [1, 1, 4, 4],   # 8, 자모자자
            [10, 1, 4, 4],  # 9, 자모모자
            [1, 1, 4, 4],   # 10, 자모모자자
        ]
        
        last = lambda _list: _list[len(_list) - 1]

        def combine(arr):
            group = []
            for i in range(len(arr)):
                h = self.한글[arr[i]]
                if i == 0 or self.isVowel(last(group)[0]) != self.isVowel(h):
                    group.append([])
                last(group).append(h)
            
            def connect(e):
                w = ''.join(e)
                if w in self.connectableConsonant: return self.connectableConsonant[w]
                elif w in self.connectableVowel: return self.connectableVowel[w]
                else: return w
            group = [connect(e) for e in group]
            
            if len(group) == 1:
                return group[0]
            
            charSet = [self.초성, self.중성, self.종성]
            try:
                code = [self.indexOf(w, charSet[i]) for i, w in enumerate(group)]
            except IndexError:
                pass

            if len(code) < 3:
                code.append(-1)
            
            return self.한글생성(code)

        
        def _():
            length = len(_input)
            last = -1
            result = []
            state = 0
            _vars = {
                'tmp' : []
            }

            def flush():
                if len(_vars['tmp']) > 0: result.append(combine(_vars['tmp']))
                _vars['tmp'] = []
            
            for i in range(length):
                char = _input[i]
                if char not in self.영어index:
                    state = 0
                    flush()
                    result.append(char)
                else:
                    curr = self.영어index[char]
                    def transition():
                        c = (self.한글[last] if last > -1 else '') + self.한글[curr]
                        lastIsVowel = self.isVowel(self.한글[last])
                        currIsVowel = self.isVowel(self.한글[curr])
                        if not currIsVowel:
                            if lastIsVowel:
                                return 0 if self.indexOf("ㄸㅃㅉ", self.한글[curr]) == -1 else 1
                            if state == 1 and not self._allowDoubleConsonant: 
                                return 1
                            return 0 if c in self.connectableConsonant else 1
                        elif lastIsVowel:
                            return 2 if c in self.connectableVowel else 3
                        
                        return 2
                    _transition = transition()
                    nextState = transitions[state][_transition]
                    _vars['tmp'].append(curr)
                    diff = len(_vars['tmp']) - stateLength[nextState]
                    if diff > 0:
                        result.append(combine(_vars['tmp'][0:diff]))
                        _vars['tmp'] = _vars['tmp'][diff:]
                    state = nextState
                    last = curr
            
            flush()

            return ''.join(result)

        return _()
        

    def ko2en(self, _input):
        result = ''
        if _input == '' or _input is None:
            return result
        _분리 = [-1, -1, -1, -1, -1]
        
        for i in range(len(_input)):
            _한글 = _input[i]
            _코드 = ord(_한글)
            # 가 ~ 힣 사이에 있는 한글이라면
            if ((_코드 >= self.가 and _코드 <= self.힣) or (_코드 >= self.ㄱ and _코드 <= self.ㅣ)):
                _분리 = self.한글분리(_한글)
            # 한글이 아니라면
            else:
                result += _한글
                _분리 = [-1, -1, -1, -1, -1]
            
            for j in range(len(_분리)):
                if _분리[j] != -1:
                    result += self.영어[_분리[j]]
        
        return result

    def 한글분리(self, _한글):
        코드 = ord(_한글)

        if 코드 >= self.가 and 코드 <= self.힣:
            초 = math.floor((코드 - self.가) / 588)
            중 = math.floor((코드 - self.가 - 초 * 588) / 28)
            종 = 코드 - self.가 - 초 * 588 - 중 * 28 - 1
            중1, 중2, 종1, 종2 = 중, -1, 종, -1

            if 중 == self.indexOf("ㅘ", self.중성): 중1, 중2 = self.indexOf("ㅗ", self.한글), self.indexOf("ㅏ",self.한글)
            elif 중 == self.indexOf("ㅙ", self.중성): 중1, 중2 = self.indexOf("ㅗ",self.한글), self.indexOf("ㅐ",self.한글)
            elif 중 == self.indexOf("ㅚ", self.중성): 중1, 중2 = self.indexOf("ㅗ",self.한글), self.indexOf("ㅣ",self.한글)
            elif 중 == self.indexOf("ㅝ", self.중성): 중1, 중2 = self.indexOf("ㅜ",self.한글), self.indexOf("ㅓ",self.한글)
            elif 중 == self.indexOf("ㅞ", self.중성): 중1, 중2 = self.indexOf("ㅜ",self.한글), self.indexOf("ㅔ",self.한글)
            elif 중 == self.indexOf("ㅟ", self.중성): 중1, 중2 = self.indexOf("ㅜ",self.한글), self.indexOf("ㅣ",self.한글)
            elif 중 == self.indexOf("ㅢ", self.중성): 중1, 중2 = self.indexOf("ㅡ",self.한글), self.indexOf("ㅣ",self.한글)

            if 종 == self.indexOf("ㄳ",self.종성): 종1, 종2 = self.indexOf("ㄱ",self.한글), self.indexOf("ㅅ",self.한글)
            elif 종 == self.indexOf("ㄵ",self.종성): 종1, 종2 = self.indexOf("ㄴ",self.한글), self.indexOf("ㅈ",self.한글)
            elif 종 == self.indexOf("ㄶ",self.종성): 종1, 종2 = self.indexOf("ㄴ",self.한글), self.indexOf("ㅎ",self.한글)
            elif 종 == self.indexOf("ㄺ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㄱ",self.한글)
            elif 종 == self.indexOf("ㄻ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㅁ",self.한글)
            elif 종 == self.indexOf("ㄼ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㅂ",self.한글)
            elif 종 == self.indexOf("ㄽ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㅅ",self.한글)
            elif 종 == self.indexOf("ㄾ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㅌ",self.한글)
            elif 종 == self.indexOf("ㄿ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㅍ",self.한글)
            elif 종 == self.indexOf("ㅀ",self.종성): 종1, 종2 = self.indexOf("ㄹ",self.한글), self.indexOf("ㅎ",self.한글)
            elif 종 == self.indexOf("ㅄ",self.종성): 종1, 종2 = self.indexOf("ㅂ",self.한글), self.indexOf("ㅅ",self.한글)
            
            if 중2 == -1 and 중 != -1: 중1 = self.indexOf(self.중성[중],self.한글)
            if 종2 == -1 and 종 != -1: 종1 = self.indexOf(self.종성[종],self.한글)

            return [초, 중1, 중2, 종1, 종2]
        elif 코드 >= self.ㄱ and 코드 <= self.ㅣ:
            if self.indexOf(_한글, self.초성) > -1:
                초 = self.indexOf(_한글,self.한글)
                return [초, -1, -1, -1, -1]
            elif self.indexOf(_한글, self.중성) > -1:
                중 = self.indexOf(_한글, self.중성)
                중1, 중2 = 중, -1
                if 중 == self.indexOf("ㅘ", self.중성): 중1, 중2 = self.indexOf("ㅗ",self.한글), self.indexOf("ㅏ",self.한글)
                elif 중 == self.indexOf("ㅙ", self.중성): 중1, 중2 = self.indexOf("ㅗ",self.한글), self.indexOf("ㅐ",self.한글)
                elif 중 == self.indexOf("ㅚ", self.중성): 중1, 중2 = self.indexOf("ㅗ",self.한글), self.indexOf("ㅣ",self.한글)
                elif 중 == self.indexOf("ㅝ", self.중성): 중1, 중2 = self.indexOf("ㅜ",self.한글), self.indexOf("ㅓ",self.한글)
                elif 중 == self.indexOf("ㅞ", self.중성): 중1, 중2 = self.indexOf("ㅜ",self.한글), self.indexOf("ㅔ",self.한글)
                elif 중 == self.indexOf("ㅟ", self.중성): 중1, 중2 = self.indexOf("ㅜ",self.한글), self.indexOf("ㅣ",self.한글)
                elif 중 == self.indexOf("ㅢ", self.중성): 중1, 중2 = self.indexOf("ㅡ",self.한글), self.indexOf("ㅣ",self.한글)
                
                if 중2 == -1: 중1 = self.indexOf(self.중성[중],self.한글)

                return [-1, 중1, 중2, -1, -1]
        
        return [-1, -1, -1, -1, -1]

    def is한글(self, char):
        if len(char) > 1:
            raise Exception("한 글자가 아닙니다.")
        return re.match("[ㄱ-ㅎ|ㅏ-ㅣ|가-힣]", char) is not None
