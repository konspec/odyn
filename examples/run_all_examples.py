#!/usr/bin/env python3
"""Run All Examples Script.

This script runs all odyn examples in sequence, demonstrating the full range
of capabilities and use cases. Each example is run independently and includes
its own error handling.
"""

import importlib.util
import os
import sys
import time
from typing import Any


def run_example(example_file: str) -> dict[str, Any]:
    """Run a single example file and return results."""
    print(f"\n{'=' * 80}")
    print(f"🚀 Running: {example_file}")
    print(f"{'=' * 80}")

    start_time = time.time()
    success = False
    error_message = None

    try:
        # Import and run the example
        spec = importlib.util.spec_from_file_location("example", example_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if the module has a main function
        if hasattr(module, "main"):
            module.main()

        success = True
        print(f"✅ {example_file} completed successfully")

    except Exception as e:
        success = False
        error_message = str(e)
        print(f"❌ {example_file} failed: {e}")

    duration = time.time() - start_time

    return {"file": example_file, "success": success, "duration": duration, "error": error_message}


def main():
    """Run all examples and provide a summary."""
    print("🚀 Odyn Examples Runner")
    print("=" * 80)
    print("This script will run all odyn examples in sequence.")
    print("Each example demonstrates different aspects of the library.")
    print()

    # List of example files to run
    example_files = [
        "01_basic_setup.py",
        "02_authentication_methods.py",
        "03_odata_queries.py",
        "04_error_handling.py",
        "05_business_scenarios.py",
        "06_advanced_configuration.py",
        "07_integration_patterns.py",
        "08_testing_examples.py",
    ]

    # Check if we're in the examples directory
    if not os.path.exists("01_basic_setup.py"):
        print("❌ Error: Please run this script from the examples directory.")
        print("   cd examples")
        print("   python run_all_examples.py")
        print("   or")
        print("   python -m examples.run_all_examples")
        sys.exit(1)

    # Run all examples
    results = []
    total_start_time = time.time()

    for example_file in example_files:
        if os.path.exists(example_file):
            result = run_example(example_file)
            results.append(result)
        else:
            print(f"⚠️  Warning: {example_file} not found, skipping...")

    total_duration = time.time() - total_start_time

    # Print summary
    print(f"\n{'=' * 80}")
    print("📊 EXAMPLES SUMMARY")
    print(f"{'=' * 80}")

    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    print(f"Total Examples: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Success Rate: {(successful / len(results) * 100):.1f}%")

    if failed > 0:
        print("\n❌ Failed Examples:")
        for result in results:
            if not result["success"]:
                print(f"  • {result['file']}: {result['error']}")

    print("\n✅ Successful Examples:")
    for result in results:
        if result["success"]:
            print(f"  • {result['file']} ({result['duration']:.2f}s)")

    print("\n📝 Note: Some examples may fail if you haven't configured")
    print("   your Business Central credentials. This is expected behavior.")
    print("   Update the configuration in each example file to use")
    print("   your actual credentials for full functionality.")

    print("\n🔗 For more information, see the README.md file in this directory.")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
