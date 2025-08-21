#!/usr/bin/env python3
"""
Automated Test Runner for Amazon Review Optimizer
Runs comprehensive unit tests with coverage reporting and automatic failure detection
"""

import unittest
import sys
import os
import subprocess
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    """Automated test execution and reporting"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.test_dir = self.project_root / "tests"
        self.src_dir = self.project_root / "src"
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'error_tests': 0,
            'skipped_tests': 0,
            'test_results': [],
            'coverage': {},
            'status': 'UNKNOWN'
        }
    
    def discover_and_run_tests(self):
        """Discover and run all unit tests"""
        print("🧪 Amazon Review Optimizer - Automated Test Suite")
        print("=" * 60)
        
        # Add src to Python path for imports
        sys.path.insert(0, str(self.src_dir))
        
        # Discover tests
        loader = unittest.TestLoader()
        start_dir = str(self.test_dir)
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True,
            resultclass=DetailedTestResult
        )
        
        print(f"\n🔍 Discovered tests in: {start_dir}")
        print(f"📊 Running test suite...\n")
        
        result = runner.run(suite)
        
        # Collect results
        self.results['total_tests'] = result.testsRun
        self.results['passed_tests'] = result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        self.results['failed_tests'] = len(result.failures)
        self.results['error_tests'] = len(result.errors)
        self.results['skipped_tests'] = len(result.skipped)
        
        # Process detailed results
        for test, error in result.failures:
            self.results['test_results'].append({
                'test': str(test),
                'status': 'FAILED',
                'error': error
            })
        
        for test, error in result.errors:
            self.results['test_results'].append({
                'test': str(test),
                'status': 'ERROR',
                'error': error
            })
        
        for test, reason in result.skipped:
            self.results['test_results'].append({
                'test': str(test),
                'status': 'SKIPPED',
                'reason': reason
            })
        
        # Determine overall status
        if result.failures or result.errors:
            self.results['status'] = 'FAILED'
        else:
            self.results['status'] = 'PASSED'
        
        return result
    
    def run_coverage_analysis(self):
        """Run code coverage analysis if coverage.py is available"""
        try:
            import coverage
            print("\n📈 Running coverage analysis...")
            
            # Initialize coverage
            cov = coverage.Coverage(source=[str(self.src_dir)])
            cov.start()
            
            # Re-run tests for coverage
            loader = unittest.TestLoader()
            suite = loader.discover(str(self.test_dir), pattern='test_*.py')
            runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
            runner.run(suite)
            
            cov.stop()
            cov.save()
            
            # Generate coverage report
            coverage_data = {}
            for filename in cov.get_data().measured_files():
                if str(self.src_dir) in filename:
                    rel_path = os.path.relpath(filename, self.src_dir)
                    analysis = cov.analysis2(filename)
                    total_lines = len(analysis[1]) + len(analysis[2])
                    covered_lines = len(analysis[1])
                    if total_lines > 0:
                        coverage_percentage = (covered_lines / total_lines) * 100
                        coverage_data[rel_path] = {
                            'covered_lines': covered_lines,
                            'total_lines': total_lines,
                            'coverage_percentage': round(coverage_percentage, 2),
                            'missing_lines': analysis[2]
                        }
            
            self.results['coverage'] = coverage_data
            
            # Print coverage summary
            if coverage_data:
                print("\n📊 Coverage Summary:")
                print("-" * 40)
                for file, data in coverage_data.items():
                    print(f"{file}: {data['coverage_percentage']:.1f}% ({data['covered_lines']}/{data['total_lines']} lines)")
                
                overall_covered = sum(data['covered_lines'] for data in coverage_data.values())
                overall_total = sum(data['total_lines'] for data in coverage_data.values())
                overall_percentage = (overall_covered / overall_total * 100) if overall_total > 0 else 0
                print(f"\nOverall Coverage: {overall_percentage:.1f}%")
            
        except ImportError:
            print("\n⚠️ Coverage.py not available. Install with: pip install coverage")
            print("   Skipping coverage analysis...")
        except Exception as e:
            print(f"\n⚠️ Coverage analysis failed: {e}")
    
    def print_summary(self):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("📋 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        print(f"Total Tests: {self.results['total_tests']}")
        print(f"✅ Passed: {self.results['passed_tests']}")
        print(f"❌ Failed: {self.results['failed_tests']}")
        print(f"🚨 Errors: {self.results['error_tests']}")
        print(f"⏭️ Skipped: {self.results['skipped_tests']}")
        
        if self.results['status'] == 'PASSED':
            print(f"\n🎉 Overall Status: {self.results['status']}")
        else:
            print(f"\n💥 Overall Status: {self.results['status']}")
        
        # Show failures and errors
        if self.results['failed_tests'] > 0 or self.results['error_tests'] > 0:
            print("\n🔍 Failed/Error Details:")
            print("-" * 40)
            for result in self.results['test_results']:
                if result['status'] in ['FAILED', 'ERROR']:
                    print(f"\n{result['status']}: {result['test']}")
                    print(f"Error: {result['error'][:200]}...")
    
    def save_results(self):
        """Save test results to JSON file"""
        results_file = self.project_root / "test_results.json"
        
        try:
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"\n💾 Test results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️ Failed to save results: {e}")
    
    def check_critical_components(self):
        """Check that critical components have tests"""
        critical_components = [
            'smart_router_v2',
            'cost_reporter', 
            'main_components'
        ]
        
        missing_tests = []
        for component in critical_components:
            test_file = self.test_dir / f"test_{component}.py"
            if not test_file.exists():
                missing_tests.append(component)
        
        if missing_tests:
            print(f"\n⚠️ Missing tests for critical components: {missing_tests}")
            return False
        else:
            print(f"\n✅ All critical components have tests")
            return True
    
    def run_full_suite(self):
        """Run complete test suite with all checks"""
        start_time = datetime.now()
        
        # Check for missing tests
        self.check_critical_components()
        
        # Run tests
        test_result = self.discover_and_run_tests()
        
        # Run coverage if available
        self.run_coverage_analysis()
        
        # Print summary
        self.print_summary()
        
        # Save results
        self.save_results()
        
        duration = datetime.now() - start_time
        print(f"\n⏱️ Total execution time: {duration.total_seconds():.2f} seconds")
        
        # Return exit code
        return 0 if self.results['status'] == 'PASSED' else 1


class DetailedTestResult(unittest.TextTestResult):
    """Enhanced test result class with detailed reporting"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_start_time = None
    
    def startTest(self, test):
        super().startTest(test)
        self.test_start_time = datetime.now()
        if self.verbosity > 1:
            self.stream.write(f"🧪 {test._testMethodName} ... ")
            self.stream.flush()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.verbosity > 1:
            duration = datetime.now() - self.test_start_time
            self.stream.writeln(f"✅ ({duration.total_seconds():.3f}s)")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            duration = datetime.now() - self.test_start_time
            self.stream.writeln(f"❌ FAILED ({duration.total_seconds():.3f}s)")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            duration = datetime.now() - self.test_start_time
            self.stream.writeln(f"🚨 ERROR ({duration.total_seconds():.3f}s)")


def main():
    """Main entry point"""
    runner = TestRunner()
    exit_code = runner.run_full_suite()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()