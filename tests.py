
import saper_logic as sl
import unittest

class Test(unittest.TestCase):
    def __init__(self, parent=None):
        super(Test, self).__init__(parent)
        self.board = sl.Board(10, 10, 9)

    def test_win_check(self):
        self.assertEqual(self.board.check_for_win(), False)

    def test_flag(self):
        self.board.flag(0, 1)
        self.assertEqual(self.board.fields[1][0][1], 'f')
    
    def test_unflag(self):
        self.board.unflag(0, 1)
        self.assertEqual(self.board.fields[1][0][1], 'c')

    def test_uncover(self):
        self.board.uncover(0, 0)
        self.assertEqual(self.board.fields[0][0][1], 'u')

unittest.main()