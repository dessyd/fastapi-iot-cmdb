#!/usr/bin/env python3
"""
Test suite for FastAPI IoT CMDB API
Tests location CRUD operations with server startup and API calls
"""

import random
import string
import subprocess
import sys
import time
from typing import Optional

import requests


class APITestSuite:
    """Test suite for the FastAPI IoT CMDB API"""

    def __init__(self, base_url: str = "http://127.0.0.1:8002"):
        self.base_url = base_url
        self.server_process: Optional[subprocess.Popen] = None
        self.location_id: Optional[int] = None
        self.initial_location_count: int = 0
        self.updated_lat: float = 0.0
        self.updated_lon: float = 0.0

    def generate_random_name(self, length: int = 8) -> str:
        """Generate a random string for location name"""
        return "Test_" + "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def generate_random_coordinates(self) -> tuple[float, float]:
        """Generate random latitude and longitude coordinates"""
        lat = round(random.uniform(-90, 90), 6)
        lon = round(random.uniform(-180, 180), 6)
        return lat, lon

    def start_server(self) -> bool:
        """Start the FastAPI server"""
        try:
            print("🚀 Starting FastAPI server...")
            self.server_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--port", "8002"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=".",
            )

            # Wait for server to start
            for attempt in range(30):  # 30 second timeout
                try:
                    response = requests.get(f"{self.base_url}/", timeout=1)
                    if response.status_code == 200:
                        print("✅ Server started successfully")
                        return True
                except requests.exceptions.RequestException:
                    time.sleep(1)

            print("❌ Server failed to start within 30 seconds")
            return False
        except Exception as e:
            print(f"❌ Failed to start server: {e}")
            return False

    def stop_server(self) -> None:
        """Stop the FastAPI server"""
        if self.server_process:
            print("🛑 Stopping server...")
            self.server_process.terminate()
            self.server_process.wait()
            print("✅ Server stopped")

    def test_get_all_locations_initial(self) -> bool:
        """Test GET /locations returns a list (may contain existing data)"""
        try:
            print("📋 Testing GET /locations (initial state)...")
            response = requests.get(f"{self.base_url}/locations")

            if response.status_code != 200:
                print(f"❌ Expected status 200, got {response.status_code}")
                return False

            locations = response.json()
            if not isinstance(locations, list):
                print(f"❌ Expected list, got {type(locations)}")
                return False

            initial_count = len(locations)
            print(f"✅ GET /locations returns list with {initial_count} existing locations")
            self.initial_location_count = initial_count
            return True
        except Exception as e:
            print(f"❌ Error testing GET /locations: {e}")
            return False

    def test_create_location(self) -> bool:
        """Test POST /locations to create a new location"""
        try:
            # Generate random data
            name = self.generate_random_name()
            lat, lon = self.generate_random_coordinates()

            print(f"📝 Creating location: {name} at ({lat}, {lon})...")

            location_data = {"name": name, "lat": lat, "lon": lon}

            response = requests.post(
                f"{self.base_url}/locations",
                json=location_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 201:
                print(f"❌ Expected status 201, got {response.status_code}")
                print(f"Response: {response.text}")
                return False

            created_location = response.json()

            # Validate response structure
            required_fields = ["id", "name", "lat", "lon", "created_at"]
            for field in required_fields:
                if field not in created_location:
                    print(f"❌ Missing field '{field}' in response")
                    return False

            # Validate data matches
            if created_location["name"] != name:
                print(f"❌ Name mismatch: expected {name}, got {created_location['name']}")
                return False

            if abs(created_location["lat"] - lat) > 0.000001:
                print(f"❌ Latitude mismatch: expected {lat}, got {created_location['lat']}")
                return False

            if abs(created_location["lon"] - lon) > 0.000001:
                print(f"❌ Longitude mismatch: expected {lon}, got {created_location['lon']}")
                return False

            # Store location ID for subsequent tests
            self.location_id = created_location["id"]
            print(f"✅ Location created successfully with ID: {self.location_id}")
            return True

        except Exception as e:
            print(f"❌ Error creating location: {e}")
            return False

    def test_get_location_by_id(self) -> bool:
        """Test GET /locations/{id} to retrieve the created location"""
        try:
            if self.location_id is None:
                print("❌ No location ID available for testing")
                return False

            print(f"🔍 Retrieving location by ID: {self.location_id}...")

            response = requests.get(f"{self.base_url}/locations/{self.location_id}")

            if response.status_code != 200:
                print(f"❌ Expected status 200, got {response.status_code}")
                return False

            location = response.json()

            # Validate ID matches
            if location["id"] != self.location_id:
                print(f"❌ ID mismatch: expected {self.location_id}, got {location['id']}")
                return False

            print(
                f"✅ Retrieved location: {location['name']} at ({location['lat']}, {location['lon']})"
            )
            return True

        except Exception as e:
            print(f"❌ Error retrieving location by ID: {e}")
            return False

    def test_update_location(self) -> bool:
        """Test PUT /locations/{id} to update the created location"""
        try:
            if self.location_id is None:
                print("❌ No location ID available for testing")
                return False

            # Generate new random coordinates
            new_lat, new_lon = self.generate_random_coordinates()
            print(
                f"🔄 Updating location ID {self.location_id} to new coordinates ({new_lat}, {new_lon})..."
            )

            update_data = {"lat": new_lat, "lon": new_lon}

            response = requests.put(
                f"{self.base_url}/locations/{self.location_id}",
                json=update_data,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                print(f"❌ Expected status 200, got {response.status_code}")
                print(f"Response: {response.text}")
                return False

            updated_location = response.json()

            # Validate coordinates were updated
            if abs(updated_location["lat"] - new_lat) > 0.000001:
                print(f"❌ Latitude not updated: expected {new_lat}, got {updated_location['lat']}")
                return False

            if abs(updated_location["lon"] - new_lon) > 0.000001:
                print(
                    f"❌ Longitude not updated: expected {new_lon}, got {updated_location['lon']}"
                )
                return False

            # Validate ID remains the same
            if updated_location["id"] != self.location_id:
                print(
                    f"❌ ID changed during update: expected {self.location_id}, got {updated_location['id']}"
                )
                return False

            # Store new coordinates for subsequent verification
            self.updated_lat = new_lat
            self.updated_lon = new_lon

            print(f"✅ Location updated successfully to ({new_lat}, {new_lon})")
            return True

        except Exception as e:
            print(f"❌ Error updating location: {e}")
            return False

    def test_get_updated_location_by_id(self) -> bool:
        """Test GET /locations/{id} to verify the updated location"""
        try:
            if self.location_id is None:
                print("❌ No location ID available for testing")
                return False

            print(f"🔍 Retrieving updated location by ID: {self.location_id}...")

            response = requests.get(f"{self.base_url}/locations/{self.location_id}")

            if response.status_code != 200:
                print(f"❌ Expected status 200, got {response.status_code}")
                return False

            location = response.json()

            # Validate ID matches
            if location["id"] != self.location_id:
                print(f"❌ ID mismatch: expected {self.location_id}, got {location['id']}")
                return False

            # Validate coordinates match the updated values
            if abs(location["lat"] - self.updated_lat) > 0.000001:
                print(
                    f"❌ Updated latitude not persisted: expected {self.updated_lat}, got {location['lat']}"
                )
                return False

            if abs(location["lon"] - self.updated_lon) > 0.000001:
                print(
                    f"❌ Updated longitude not persisted: expected {self.updated_lon}, got {location['lon']}"
                )
                return False

            print(
                f"✅ Retrieved updated location: {location['name']} at ({location['lat']}, {location['lon']})"
            )
            return True

        except Exception as e:
            print(f"❌ Error retrieving updated location by ID: {e}")
            return False

    def test_get_all_locations_with_data(self) -> bool:
        """Test GET /locations returns the created location"""
        try:
            print("📋 Testing GET /locations (should contain created location)...")

            response = requests.get(f"{self.base_url}/locations")

            if response.status_code != 200:
                print(f"❌ Expected status 200, got {response.status_code}")
                return False

            locations = response.json()

            if not isinstance(locations, list):
                print(f"❌ Expected list, got {type(locations)}")
                return False

            expected_count = self.initial_location_count + 1
            if len(locations) != expected_count:
                print(f"❌ Expected {expected_count} locations, got {len(locations)} locations")
                return False

            # Validate our created location is in the list
            found_location = None
            for location in locations:
                if location["id"] == self.location_id:
                    found_location = location
                    break

            if found_location is None:
                print(f"❌ Created location with ID {self.location_id} not found in locations list")
                return False

            print(
                f"✅ GET /locations returns {len(locations)} locations including our created location ID: {self.location_id}"
            )
            return True

        except Exception as e:
            print(f"❌ Error testing GET /locations with data: {e}")
            return False

    def run_test_suite(self) -> bool:
        """Run the complete test suite"""
        print("🧪 Starting FastAPI IoT CMDB Test Suite")
        print("=" * 50)

        try:
            # Start server
            if not self.start_server():
                return False

            # Run tests in sequence
            tests = [
                ("Test initial locations list", self.test_get_all_locations_initial),
                ("Test create location", self.test_create_location),
                ("Test get location by ID", self.test_get_location_by_id),
                ("Test update location", self.test_update_location),
                ("Test get updated location by ID", self.test_get_updated_location_by_id),
                ("Test locations list with data", self.test_get_all_locations_with_data),
            ]

            passed = 0
            failed = 0

            for test_name, test_func in tests:
                print(f"\n🧪 {test_name}")
                if test_func():
                    passed += 1
                else:
                    failed += 1

            # Print summary
            print("\n" + "=" * 50)
            print("📊 Test Results:")
            print(f"✅ Passed: {passed}")
            print(f"❌ Failed: {failed}")
            print(f"📈 Success Rate: {passed}/{len(tests)} ({100 * passed // len(tests)}%)")

            return failed == 0

        finally:
            self.stop_server()


def main():
    """Main entry point for the test suite"""
    test_suite = APITestSuite()

    try:
        success = test_suite.run_test_suite()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
        test_suite.stop_server()
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test suite failed with error: {e}")
        test_suite.stop_server()
        sys.exit(1)


if __name__ == "__main__":
    main()
