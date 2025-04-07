import unittest
from blockes import *


class MainTest(unittest.TestCase):
    def setUp(self):
        # Reset state before each test
        reset_state()
    
    def test_case0(self):
        hp = get_hitpoint()
        self.assertEqual(hp, 10)

    def test_case1(self):
        add_block(BlockColors.GREEN)
        block = remove_block()
        self.assertEqual(block, BlockColors.GREEN)

    def test_case2(self):
        add_block(BlockColors.GREEN)
        add_block(BlockColors.RED)
        block = remove_block()
        self.assertEqual(block, BlockColors.RED)

    def test_case3(self):
        add_block(BlockColors.RED)
        add_block(BlockColors.GREEN)
        add_block(BlockColors.YELLOW)
        block = remove_block()
        self.assertEqual(block, BlockColors.YELLOW)

    def test_case4(self):
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 9)

    def reduce_hp(self):
        add_block(BlockColors.RED)
        add_block(BlockColors.GREEN)
        add_block(BlockColors.YELLOW)
        add_block(BlockColors.YELLOW)
        block = remove_block()
        self.assertEqual(block, None)

    def reduce_hp_other_colors(self):
        add_block(BlockColors.GREEN)
        add_block(BlockColors.YELLOW)
        add_block(BlockColors.RED)
        add_block(BlockColors.YELLOW)
        block = remove_block()
        self.assertEqual(block, None)
        

    def test_case5(self):
        add_block(BlockColors.RED)
        add_block(BlockColors.GREEN)
        add_block(BlockColors.YELLOW)
        add_block(BlockColors.YELLOW)
        add_block(BlockColors.GREEN)
        block = remove_block()
        self.assertEqual(block, BlockColors.GREEN)
        hp = get_hitpoint()
        self.assertEqual(hp, 9)

    def test_case6(self):
        block = remove_block()
        self.assertEqual(block, None)
        hp = get_hitpoint()
        self.assertEqual(hp, 10)

    def test_case7(self):
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 9)
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 8)
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 7)
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 6)
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 5)

    def test_case8(self):
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 9)
        self.reduce_hp_other_colors()
        hp = get_hitpoint()
        self.assertEqual(hp, 8)
        self.reduce_hp_other_colors()
        hp = get_hitpoint()
        self.assertEqual(hp, 7)
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 6)
        self.reduce_hp()
        hp = get_hitpoint()
        self.assertEqual(hp, 5)


if __name__ == "__main__":
    unittest.main()