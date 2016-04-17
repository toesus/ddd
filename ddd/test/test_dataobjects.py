'''
Created on 05.12.2015

@author: killian
'''
import unittest

from ddd.dataobjects import DddConversion


class TestDddConversion(unittest.TestCase):

    def __init__(self,*args,**kwargs):
        unittest.TestCase.__init__(self,*args,**kwargs)
        self.longMessage=True
        
    def check_type_selection(self,data):
        d = DddConversion(**data['args'])
        msg = 'Conversion created with Arguments: '+str(data['args'])
        
        self.assertEqual(d.type,data['expected']['type'],'Wrong Type selected, '+msg)
        self.assertEqual(d.factor.numerator,data['expected']['num'],'Wrong Numerator selected, '+msg)
        self.assertEqual(d.factor.denominator,data['expected']['den'],'Wrong Denominator selected, '+msg)
        self.assertEqual(d.name,data['expected']['name'],'Wrong Name selected, '+msg)
        
    def testTypeSelectionNumDen(self):
        data = [{'args':{'numerator':1,'denominator':1},
                 'expected':{'type':'1to1',
                             'num':1,
                             'den':1,
                             'name':'1TO1'}},
                {'args':{'numerator':2,'denominator':1},
                 'expected':{'type':'binary',
                             'num':2,
                             'den':1,
                             'name':'BIN-1'}},
                {'args':{'numerator':1,'denominator':2},
                 'expected':{'type':'binary',
                             'num':1,
                             'den':2,
                             'name':'BIN1'}},
                {'args':{'numerator':10,'denominator':1},
                 'expected':{'type':'decimal',
                             'num':10,
                             'den':1,
                             'name':'DEC-1'}},
                {'args':{'numerator':1,'denominator':10},
                 'expected':{'type':'decimal',
                             'num':1,
                             'den':10,
                             'name':'DEC1'}},
                ]
        
        for d in data:
            self.check_type_selection(d)
        
    def testTypeBinary(self):
        d = DddConversion(type='binary', fraction=4)
        self.assertEqual(d.factor.numerator, 1)
        self.assertEqual(d.factor.denominator, 16)
        
        d = DddConversion(type='binary', fraction=-4)
        self.assertEquals(d.factor.numerator, 16)
        self.assertEqual(d.factor.denominator, 1)
        
    def testTypeDecimal(self):
        d = DddConversion(type='decimal', fraction=4)
        self.assertEqual(d.factor.numerator, 1)
        self.assertEqual(d.factor.denominator, 10000)
        
        d = DddConversion(type='decimal', fraction=-4)
        self.assertEqual(d.factor.numerator, 10000)
        self.assertEqual(d.factor.denominator, 1)
        self.assertEqual(d.get_name(),'DEC-4')

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()