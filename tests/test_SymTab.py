import unittest
from src.model.SymTab import SymTab
from src.model.types import Int, FunctionType

class TestSymTab(unittest.TestCase):
    def test_define_and_lookup_function(self):
        symtab = SymTab()
        params = [Int(), Int()]
        return_type = Int()
        symtab.define_function("add", params, return_type)

        # Lookup the function
        func_type, _ = symtab.lookup_variable("add")

        self.assertIsInstance(func_type, FunctionType)
        self.assertEqual(func_type.param_types, params)
        self.assertEqual(func_type.return_type, return_type)

if __name__ == "__main__":
    unittest.main()
