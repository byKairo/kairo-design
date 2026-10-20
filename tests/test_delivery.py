"""Regression tests for composition tolerance and strict delivery contracts."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/kairo-design/scripts'))
from platform_images import matches_ratio,effective_ratio,inspect
from PIL import Image

class SizePolicyTests(unittest.TestCase):
    def test_native_rounding_is_accepted(self):
        self.assertTrue(matches_ratio(1915,821,'21:9'))
        self.assertTrue(matches_ratio(1915,821,'2.35:1'))
        self.assertTrue(matches_ratio(1921,819,'2.35:1'))
    def test_boundary_and_wrong_shape(self):
        self.assertTrue(matches_ratio(102,100,'1:1'))
        self.assertFalse(matches_ratio(103,100,'1:1'))
        self.assertFalse(matches_ratio(1920,1080,'21:9'))
        self.assertFalse(matches_ratio(821,1915,'21:9'))
    def test_strict_remains_exact(self):
        self.assertFalse(matches_ratio(1915,821,'21:9','strict'))
        self.assertTrue(matches_ratio(2100,900,'21:9','strict'))
        self.assertTrue(matches_ratio(2350,1000,'2.35:1','strict'))
    def test_tool_fallback_cannot_override_strict(self):
        p={'aspect_ratio':'5:2','generation_aspect_ratio':'21:9'}
        self.assertEqual(effective_ratio(p),'21:9')
        self.assertEqual(effective_ratio(dict(p,ratio_policy='strict')),'5:2')
    def test_bad_policy_and_ratio_are_rejected(self):
        for policy in ['ignore','loose',None]:
            with self.assertRaises(ValueError):matches_ratio(100,100,'1:1',policy)
        for ratio in ['0:1','-1:1','bad']:
            with self.assertRaises(ValueError):matches_ratio(100,100,ratio)
    def test_explicit_pixels_and_metadata(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'fixture.png';Image.new('RGB',(1915,821),'white').save(f)
            p={'aspect_ratio':'2.35:1','formats':['PNG'],'max_bytes':None,'note':'test'}
            r=inspect(f,p);self.assertTrue(r['passed']);self.assertEqual(r['actual'],[1915,821])
            self.assertLess(r['ratio_relative_error'],0.02)
            self.assertFalse(inspect(f,dict(p,ratio_policy='strict'))['passed'])
            self.assertFalse(inspect(f,dict(p,width=1920,height=820))['passed'])
if __name__=='__main__':unittest.main()
