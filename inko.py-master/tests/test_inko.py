import unittest
from inko import Inko

class TestInko(unittest.TestCase):
    def setUp(self):
        self.inko = Inko()

    def test_is한글(self):
        한글배열 = ['ㄱ', 'ㄴ', 'ㅇ', 'ㅎ','ㅍ', 'ㅋ', '기', '긹', '닙', 'ㅜ', 'ㅢ', '뷁', '챀', '팥', '가', '긯']
        다른배열 = ['s', '1', 'D', '#', 'R', 'B', 'C', '9', 'a', '', '=', '6', '3', 'P']
        for val in 한글배열:
            self.assertEqual(self.inko.is한글(val), True, "is한글(\"%s\")에 잘못된 값이 나왔습니다." % val)
        for val in 다른배열:
            self.assertEqual(self.inko.is한글(val), False, "is한글(\"%s\")에 잘못된 값이 나왔습니다." % val)

    def test_한글생성(self):
        self.assertEqual(self.inko.한글생성([0, 0, 0]), '각')
        self.assertEqual(self.inko.한글생성([3, 3, 3]), '댼')
        self.assertEqual(self.inko.한글생성([1, 10, 10]), '꽯')
        self.assertEqual(self.inko.한글생성([4, 6, 8]), '뗡')
        self.assertEqual(self.inko.한글생성([14, 15, 13]), '췚')

    def test_한글분리(self):
        self.assertListEqual(self.inko.한글분리('님'), [2, 41, -1, 6, -1])
        self.assertListEqual(self.inko.한글분리('가'), [0, 28, -1, -1, -1])
        self.assertListEqual(self.inko.한글분리('뷁'), [7, 38, 33, 5, 0])
        self.assertListEqual(self.inko.한글분리('없'), [11, 32, -1, 7, 9])

    def test_en2ko_no복자음(self):
        self.assertEqual(self.inko.en2ko('dkssud'), '안녕')
        self.assertEqual(self.inko.en2ko('dkssudgktpdy'), '안녕하세요')
        self.assertEqual(self.inko.en2ko('rkskekfk'), '가나다라')
        self.assertEqual(self.inko.en2ko('rldjrsktpdy?'), '기억나세요?')
        self.assertEqual(self.inko.en2ko('anjgoqnpfrqnpfr'), '뭐해뷁뷁')
        self.assertEqual(self.inko.en2ko('anjgktpdy'), '뭐하세요')
        self.assertEqual(self.inko.en2ko('apfhd'), '메롱')
        self.assertEqual(self.inko.en2ko('fnffnfkffk'), '룰루랄라')
        self.assertEqual(self.inko.en2ko('rldjr wjvusdp sjrk todrkrsk'), '기억 저편에 너가 생각나')
        self.assertEqual(self.inko.en2ko('dmlrlthcla'), '의기소침')
        self.assertEqual(self.inko.en2ko('dho wjgksxp rmfjtpdy?'), '왜 저한테 그러세요?')
        self.assertEqual(self.inko.en2ko('woalTwlaks woaldjqtek.'), '재밌지만 재미없다.')
        self.assertEqual(self.inko.en2ko('dbfrhrdldltjstodsladms djswpsk skgksxp clswjfgktuTek.'), '율곡이이선생님은 언제나 나한테 친절하셨다.')
        self.assertEqual(self.inko.en2ko('alclwldksgrhtjdi rmfjf tn djqtdmf rjtdlek.'), '미치지않고서야 그럴 수 없을 것이다.')
        self.assertEqual(self.inko.en2ko('difralqtWyfq'), '얅밊쬷')
        self.assertEqual(self.inko.en2ko('diffkfldiffkdtud'), '얄라리얄랑셩')
        self.assertEqual(self.inko.en2ko('DKSSUD'), '안녕')
        self.assertEqual(self.inko.en2ko('dUDn'), '여우')
        self.assertEqual(self.inko.en2ko('rrrr'), 'ㄱㄱㄱㄱ')
        self.assertEqual(self.inko.en2ko('hhhh'), 'ㅗㅗㅗㅗ')
        self.assertEqual(self.inko.en2ko('r s e f a q t d w c z x v g'), 'ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ')
        self.assertEqual(self.inko.en2ko('hlhl'), 'ㅚㅚ')
        self.assertEqual(self.inko.en2ko('QlEkrgkrp'), '삐딱하게')
        self.assertEqual(self.inko.en2ko('ekfkawnl gjs cptqkznldp xkrhvk'), '다람쥐 헌 쳇바퀴에 타고파')
        self.assertEqual(self.inko.en2ko('EKFKAWNL GJS CPTQKZNLDP XKRHVK'), '따람쮜 헌 촀빠퀴예 타꼬파')
        self.assertEqual(self.inko.en2ko('rtk'), 'ㄱ사')
        self.assertEqual(self.inko.en2ko('rtrt'), 'ㄱㅅㄱㅅ')
        self.assertEqual(self.inko.en2ko('rtrt', allowDoubleConsonant=False ), 'ㄱㅅㄱㅅ')
        self.assertEqual(self.inko.en2ko('rsefaqtdwczxvg', allowDoubleConsonant=False ), 'ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ')

    def test_en2ko_with복자음(self):
        _inko = Inko(allowDoubleConsonant=True)

        self.assertEqual(_inko.en2ko('dkssud'), '안녕')
        self.assertEqual(_inko.en2ko('dkssudgktpdy'), '안녕하세요')
        self.assertEqual(_inko.en2ko('rkskekfk'), '가나다라')
        self.assertEqual(_inko.en2ko('rldjrsktpdy?'), '기억나세요?')
        self.assertEqual(_inko.en2ko('anjgoqnpfrqnpfr'), '뭐해뷁뷁')
        self.assertEqual(_inko.en2ko('anjgktpdy'), '뭐하세요')
        self.assertEqual(_inko.en2ko('apfhd'), '메롱')
        self.assertEqual(_inko.en2ko('fnffnfkffk'), '룰루랄라')
        self.assertEqual(_inko.en2ko('rldjr wjvusdp sjrk todrkrsk'), '기억 저편에 너가 생각나')
        self.assertEqual(_inko.en2ko('dmlrlthcla'), '의기소침')
        self.assertEqual(_inko.en2ko('dho wjgksxp rmfjtpdy?'), '왜 저한테 그러세요?')
        self.assertEqual(_inko.en2ko('woalTwlaks woaldjqtek.'), '재밌지만 재미없다.')
        self.assertEqual(_inko.en2ko('dbfrhrdldltjstodsladms djswpsk skgksxp clswjfgktuTek.'), '율곡이이선생님은 언제나 나한테 친절하셨다.')
        self.assertEqual(_inko.en2ko('alclwldksgrhtjdi rmfjf tn djqtdmf rjtdlek.'), '미치지않고서야 그럴 수 없을 것이다.')
        self.assertEqual(_inko.en2ko('difralqtWyfq'), '얅밊쬷')
        self.assertEqual(_inko.en2ko('diffkfldiffkdtud'), '얄라리얄랑셩')
        self.assertEqual(_inko.en2ko('DKSSUD'), '안녕')
        self.assertEqual(_inko.en2ko('dUDn'), '여우')
        self.assertEqual(_inko.en2ko('rrrr'), 'ㄱㄱㄱㄱ')
        self.assertEqual(_inko.en2ko('hhhh'), 'ㅗㅗㅗㅗ')
        self.assertEqual(_inko.en2ko('r s e f a q t d w c z x v g'), 'ㄱ ㄴ ㄷ ㄹ ㅁ ㅂ ㅅ ㅇ ㅈ ㅊ ㅋ ㅌ ㅍ ㅎ')
        self.assertEqual(_inko.en2ko('hlhl'), 'ㅚㅚ')
        self.assertEqual(_inko.en2ko('QlEkrgkrp'), '삐딱하게')
        self.assertEqual(_inko.en2ko('ekfkawnl gjs cptqkznldp xkrhvk'), '다람쥐 헌 쳇바퀴에 타고파')
        self.assertEqual(_inko.en2ko('EKFKAWNL GJS CPTQKZNLDP XKRHVK'), '따람쮜 헌 촀빠퀴예 타꼬파')
        self.assertEqual(_inko.en2ko('rtk'), 'ㄱ사')
        self.assertEqual(_inko.en2ko('rtrt'), 'ㄳㄳ')
        self.assertEqual(_inko.en2ko('rsefaqtdwczxvg'), 'ㄱㄴㄷㄻㅄㅇㅈㅊㅋㅌㅍㅎ')
    
    def test_ko2en(self):
        self.assertEqual(self.inko.ko2en('ㅗ디ㅣㅐ'), 'hello')
        self.assertEqual(self.inko.ko2en('ㅗ디ㅣㅐ 재깅!'), 'hello world!')
        self.assertEqual(self.inko.ko2en('ㅡㅛ ㄹ갸둥 ㅑㄴ ㅗ뭉내ㅡㄷ'), 'my friend is handsome')
        self.assertEqual(self.inko.ko2en('애 ㅛㅐㅕ ㄱ드드ㅠㄷㄱ ㅡㄷ?'), 'do you remember me?')

if __name__ == '__main__':
    unittest.main(verbosity=2)