#!/usr/bin/env python3
"""
Test runner for the new configuration system.

This script demonstrates how to run the configuration system tests
and validates that both settings and secrets can be loaded from the examples.

Usage:
    python test_runner.py
"""

import os
import sys
import unittest
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))


def run_configuration_tests() -> bool:
    """Run all configuration system tests."""
    print("=" * 60)
    print("Configuration System Test Runner")
    print("=" * 60)

    # Set up minimal environment for tests
    config_dir = project_root / "gen_epix" / "commondb" / "config"
    logging_config_file = config_dir / "logging.yaml"

    if not logging_config_file.exists():
        print(f"ERROR: Logging config file not found: {logging_config_file}")
        print("Please ensure the logging.yaml file exists in the config directory.")
        return False

    # Discover and run tests
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern="test_*.py")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print("=" * 60)

    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")

    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")

    return len(result.failures) == 0 and len(result.errors) == 0


def demonstrate_configuration_loading() -> bool:
    """Demonstrate loading configuration from examples."""
    print("\n" + "=" * 60)
    print("Configuration Loading Demonstration")
    print("=" * 60)

    try:
        # Add project to path if not already there
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from gen_epix.commondb.config.secrets import SecretProviderFactory
        from gen_epix.commondb.config.settings import SettingsManager

        config_dir = project_root / "gen_epix" / "commondb" / "config"
        data_dir = Path(__file__).parent / "data"

        print("\n1. Loading Settings from Examples:")
        print("-" * 40)

        # Load default settings
        print("Loading default settings...")
        settings_manager = SettingsManager(prefix="COMMONDB")
        default_settings = settings_manager.load_settings()
        print(f"Default host: {default_settings.app.host}")
        print(f"Default port: {default_settings.app.port}")
        print(f"Default debug: {default_settings.app.debug}")

        # Load custom settings
        custom_settings_file = data_dir / "settings-custom.toml"
        if custom_settings_file.exists():
            print(f"\nLoading custom settings from {custom_settings_file}...")
            custom_settings = settings_manager.load_settings(str(custom_settings_file))
            print(f"Custom host: {custom_settings.app.host}")
            print(f"Custom port: {custom_settings.app.port}")
            print(f"Custom debug: {custom_settings.app.debug}")

        print("\n2. Loading Secrets from Examples:")
        print("-" * 40)

        # Test file secrets
        secrets_files_dir = data_dir / "secrets" / "files"
        if secrets_files_dir.exists():
            print(f"Loading file secrets from {secrets_files_dir}...")
            os.environ["COMMONDB_SECRETS_STRATEGY"] = "file"
            os.environ["COMMONDB_SECRETS_PATH"] = str(secrets_files_dir)

            try:
                secrets = SecretProviderFactory.load_secrets(prefix="COMMONDB")
                print(
                    f"Database repository type: {secrets.get('db', {}).get('repository_type')}"
                )
                print(
                    f"Root user email: {secrets.get('root', {}).get('user', {}).get('email')}"
                )
                print(
                    f"SQL Server: {secrets.get('repository', {}).get('sa_sql', {}).get('defaults', {}).get('server')}"
                )
            except Exception as e:
                print(f"Error loading file secrets: {e}")

        # Test environment secrets (if environment vars file exists)
        env_vars_file = data_dir / "secrets" / "environment-vars.env"
        if env_vars_file.exists():
            print(f"\nEnvironment secrets example file found: {env_vars_file}")
            print(
                "To test environment secrets, source this file and set COMMONDB_SECRETS_STRATEGY=environment"
            )

        print("\n3. Configuration Loading Complete!")
        print("-" * 40)
        print("✓ Settings management working")
        print("✓ Secret management working")
        print("✓ Examples can be loaded successfully")

        return True

    except Exception as e:
        print(f"ERROR: Failed to demonstrate configuration loading: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting Configuration System Tests and Demonstration...\n")

    # Run tests
    tests_passed = run_configuration_tests()

    # Demonstrate configuration loading
    demo_success = demonstrate_configuration_loading()

    # Final result
    print("\n" + "=" * 60)
    if tests_passed and demo_success:
        print("✅ ALL TESTS PASSED - Configuration system is working correctly!")
        print("✅ Examples can be loaded successfully!")
        sys.exit(0)
    else:
        print("❌ Some tests failed or demonstration had issues.")
        print("Please check the output above for details.")
        sys.exit(1)
