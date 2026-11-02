import unittest
from agrodigital.core import plan_execution

class ExecutionPlanTests(unittest.TestCase):
    def test_direct(self): self.assertEqual(plan_execution(["python"],["python"]).mode,"DIRECT")
    def test_assisted(self): self.assertEqual(plan_execution(["qgis"],["python"]).mode,"ASSISTED")
    def test_integrated_requires_flag(self):
        self.assertEqual(plan_execution(["remote_api"],[],integrated_service_available=True).mode,"INTEGRATED")

if __name__ == "__main__": unittest.main()
