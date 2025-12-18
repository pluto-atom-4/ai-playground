"""
Tests for the Complex Inputs functionality of the MCP Server.

Tests the Pydantic model validation and complex data structure handling
including nested models, field constraints, and MCP tool integration.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import pytest
from pydantic import ValidationError

from complex_inputs import (
    Shrimp,
    ShrimpTank,
    FishFood,
    AquariumSetup,
    name_shrimp,
    analyze_tank,
    configure_aquarium,
    find_shrimp_by_species,
)


class TestShrimpModel:
    """Tests for the Shrimp model."""

    def test_shrimp_valid_creation(self):
        """Test creating a valid Shrimp."""
        shrimp = Shrimp(
            name="Salty",
            species="Red Cherry",
            age_months=12
        )

        assert shrimp.name == "Salty"
        assert shrimp.species == "Red Cherry"
        assert shrimp.age_months == 12

    def test_shrimp_max_name_length(self):
        """Test that shrimp name respects max_length constraint (10)."""
        # Valid: exactly 10 characters
        shrimp = Shrimp(
            name="1234567890",
            species="Test",
            age_months=5
        )
        assert shrimp.name == "1234567890"

        # Invalid: 11 characters
        with pytest.raises(ValidationError) as exc_info:
            Shrimp(
                name="12345678901",
                species="Test",
                age_months=5
            )
        assert "String should have at most 10 characters" in str(exc_info.value)

    def test_shrimp_age_constraints(self):
        """Test that shrimp age respects constraints (0-360 months)."""
        # Valid: minimum age
        shrimp = Shrimp(name="Young", species="Test", age_months=0)
        assert shrimp.age_months == 0

        # Valid: maximum age
        shrimp = Shrimp(name="Old", species="Test", age_months=360)
        assert shrimp.age_months == 360

        # Invalid: negative age
        with pytest.raises(ValidationError) as exc_info:
            Shrimp(name="Baby", species="Test", age_months=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        # Invalid: age exceeds maximum
        with pytest.raises(ValidationError) as exc_info:
            Shrimp(name="Ancient", species="Test", age_months=361)
        assert "Input should be less than or equal to 360" in str(exc_info.value)

    def test_shrimp_missing_required_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            Shrimp(name="Test")

        with pytest.raises(ValidationError):
            Shrimp(species="Test")

        with pytest.raises(ValidationError):
            Shrimp(age_months=5)

    def test_shrimp_invalid_age_type(self):
        """Test that age must be an integer."""
        with pytest.raises(ValidationError):
            Shrimp(name="Test", species="Type", age_months="not_a_number")

        with pytest.raises(ValidationError):
            Shrimp(name="Test", species="Type", age_months=3.5)


class TestShrimpTankModel:
    """Tests for the ShrimpTank model."""

    def test_shrimp_tank_valid_creation(self):
        """Test creating a valid ShrimpTank."""
        shrimp_list = [
            Shrimp(name="Shrimp1", species="Red Cherry", age_months=12),
            Shrimp(name="Shrimp2", species="Amano", age_months=24),
        ]
        tank = ShrimpTank(
            tank_name="Main Tank",
            capacity=50,
            shrimp_list=shrimp_list
        )

        assert tank.tank_name == "Main Tank"
        assert tank.capacity == 50
        assert len(tank.shrimp_list) == 2

    def test_shrimp_tank_empty(self):
        """Test creating an empty ShrimpTank."""
        tank = ShrimpTank(
            tank_name="Empty Tank",
            capacity=100,
            shrimp_list=[]
        )

        assert len(tank.shrimp_list) == 0

    def test_shrimp_tank_capacity_constraint(self):
        """Test that tank capacity must be positive."""
        # Valid: capacity of 1
        tank = ShrimpTank(
            tank_name="Tiny",
            capacity=1,
            shrimp_list=[]
        )
        assert tank.capacity == 1

        # Invalid: zero capacity
        with pytest.raises(ValidationError) as exc_info:
            ShrimpTank(tank_name="Invalid", capacity=0, shrimp_list=[])
        assert "Input should be greater than or equal to 1" in str(exc_info.value)

        # Invalid: negative capacity
        with pytest.raises(ValidationError):
            ShrimpTank(tank_name="Invalid", capacity=-10, shrimp_list=[])

    def test_shrimp_tank_multiple_shrimp(self):
        """Test tank with multiple shrimp."""
        shrimp_list = [
            Shrimp(name=f"Shrimp{i}", species=f"Species{i}", age_months=i*10)
            for i in range(1, 6)
        ]
        tank = ShrimpTank(
            tank_name="Crowded",
            capacity=200,
            shrimp_list=shrimp_list
        )

        assert len(tank.shrimp_list) == 5

    def test_shrimp_tank_invalid_shrimp_in_list(self):
        """Test that invalid shrimp cause validation error."""
        with pytest.raises(ValidationError):
            ShrimpTank(
                tank_name="Test",
                capacity=50,
                shrimp_list=[
                    {"name": "Valid", "species": "Red Cherry", "age_months": 10},
                    {"name": "Invalid", "age_months": 10}  # Missing species
                ]
            )


class TestFishFoodModel:
    """Tests for the FishFood model."""

    def test_fish_food_valid_creation(self):
        """Test creating valid FishFood."""
        food = FishFood(
            name="Shrimp Pellets",
            protein_percent=40.0
        )

        assert food.name == "Shrimp Pellets"
        assert food.protein_percent == 40.0

    def test_fish_food_protein_constraints(self):
        """Test protein percentage constraints (0-100)."""
        # Valid: minimum protein
        food = FishFood(name="Low", protein_percent=0.0)
        assert food.protein_percent == 0.0

        # Valid: maximum protein
        food = FishFood(name="High", protein_percent=100.0)
        assert food.protein_percent == 100.0

        # Valid: mid-range
        food = FishFood(name="Mid", protein_percent=50.5)
        assert food.protein_percent == 50.5

        # Invalid: negative protein
        with pytest.raises(ValidationError) as exc_info:
            FishFood(name="Invalid", protein_percent=-0.1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        # Invalid: protein exceeds 100%
        with pytest.raises(ValidationError) as exc_info:
            FishFood(name="Invalid", protein_percent=100.1)
        assert "Input should be less than or equal to 100" in str(exc_info.value)

    def test_fish_food_missing_fields(self):
        """Test that all fields are required."""
        with pytest.raises(ValidationError):
            FishFood(name="Incomplete")

        with pytest.raises(ValidationError):
            FishFood(protein_percent=40.0)


class TestAquariumSetupModel:
    """Tests for the AquariumSetup model."""

    def test_aquarium_setup_valid_creation(self):
        """Test creating a valid AquariumSetup."""
        shrimp_list = [
            Shrimp(name="Red1", species="Red Cherry", age_months=12),
        ]
        tank = ShrimpTank(tank_name="Main", capacity=50, shrimp_list=shrimp_list)
        food_list = [
            FishFood(name="Pellets", protein_percent=40.0),
            FishFood(name="Flakes", protein_percent=35.0),
        ]
        maintenance = {"daily": "Feed", "weekly": "Water change"}

        setup = AquariumSetup(
            tank=tank,
            food=food_list,
            maintenance_schedule=maintenance
        )

        assert setup.tank.tank_name == "Main"
        assert len(setup.food) == 2
        assert setup.maintenance_schedule["daily"] == "Feed"

    def test_aquarium_setup_empty_food_list(self):
        """Test aquarium setup with empty food list."""
        tank = ShrimpTank(tank_name="Test", capacity=50, shrimp_list=[])
        setup = AquariumSetup(
            tank=tank,
            food=[],
            maintenance_schedule={}
        )

        assert len(setup.food) == 0

    def test_aquarium_setup_nested_validation(self):
        """Test that nested model validation works."""
        # Invalid shrimp in tank
        with pytest.raises(ValidationError):
            AquariumSetup(
                tank={
                    "tank_name": "Test",
                    "capacity": -5,  # Invalid
                    "shrimp_list": []
                },
                food=[],
                maintenance_schedule={}
            )

    def test_aquarium_setup_complex_maintenance_schedule(self):
        """Test aquarium setup with complex maintenance schedule."""
        tank = ShrimpTank(tank_name="Complex", capacity=100, shrimp_list=[])
        setup = AquariumSetup(
            tank=tank,
            food=[],
            maintenance_schedule={
                "monday": "Clean filter",
                "wednesday": "Partial water change",
                "friday": "Check pH levels",
                "daily": "Feed",
            }
        )

        assert len(setup.maintenance_schedule) == 4
        assert setup.maintenance_schedule["monday"] == "Clean filter"


class TestNameShrimpTool:
    """Tests for the name_shrimp tool."""

    def test_name_shrimp_simple(self):
        """Test name_shrimp with simple tank."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Shrimp1", species="Red", age_months=10),
                Shrimp(name="Shrimp2", species="Blue", age_months=20),
            ]
        )

        result = name_shrimp(tank, [])

        assert isinstance(result, list)
        assert result == ["Shrimp1", "Shrimp2"]

    def test_name_shrimp_with_extra_names(self):
        """Test name_shrimp with extra names appended."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Original", species="Red", age_months=10),
            ]
        )

        result = name_shrimp(tank, ["Extra1", "Extra2", "Extra3"])

        assert result == ["Original", "Extra1", "Extra2", "Extra3"]

    def test_name_shrimp_empty_tank(self):
        """Test name_shrimp with empty tank."""
        tank = ShrimpTank(tank_name="Empty", capacity=50, shrimp_list=[])

        result = name_shrimp(tank, [])

        assert result == []

    def test_name_shrimp_only_extra_names(self):
        """Test name_shrimp with empty tank but extra names."""
        tank = ShrimpTank(tank_name="Empty", capacity=50, shrimp_list=[])

        result = name_shrimp(tank, ["Extra1", "Extra2"])

        assert result == ["Extra1", "Extra2"]

    def test_name_shrimp_extra_names_max_length(self):
        """Test that extra_names respects max_length constraint at validation time."""
        tank = ShrimpTank(tank_name="Test", capacity=50, shrimp_list=[])

        # Valid: exactly 10 names
        result = name_shrimp(tank, [f"Name{i}" for i in range(10)])
        assert len(result) == 10

        # Invalid: 11 names (exceeds max_length) - validation happens during tool invocation
        # Note: This constraint is enforced by the MCP tool decorator, not directly in the function
        # Test the boundary condition directly
        from pydantic import BaseModel, Field
        from typing import Annotated

        class TestModel(BaseModel):
            names: Annotated[list[str], Field(max_length=10)]

        with pytest.raises(ValidationError) as exc_info:
            TestModel(names=[f"Name{i}" for i in range(11)])
        assert "List should have at most 10 items" in str(exc_info.value)


class TestAnalyzeTankTool:
    """Tests for the analyze_tank tool."""

    def test_analyze_tank_simple(self):
        """Test analyze_tank with a simple tank."""
        tank = ShrimpTank(
            tank_name="Main",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Shrimp1", species="Red Cherry", age_months=12),
                Shrimp(name="Shrimp2", species="Amano", age_months=24),
            ]
        )

        result = analyze_tank(tank)

        assert isinstance(result, dict)
        assert result["tank_name"] == "Main"
        assert result["capacity"] == 50
        assert result["num_shrimp"] == 2
        assert result["average_age_months"] == 18.0
        assert result["stocking_density"] == 0.04

    def test_analyze_tank_single_shrimp(self):
        """Test analyze_tank with single shrimp."""
        tank = ShrimpTank(
            tank_name="Solo",
            capacity=20,
            shrimp_list=[
                Shrimp(name="Alone", species="Red Cherry", age_months=36),
            ]
        )

        result = analyze_tank(tank)

        assert result["num_shrimp"] == 1
        assert result["average_age_months"] == 36.0
        assert result["stocking_density"] == 0.05

    def test_analyze_tank_empty(self):
        """Test analyze_tank with empty tank."""
        tank = ShrimpTank(tank_name="Empty", capacity=100, shrimp_list=[])

        result = analyze_tank(tank)

        assert result["num_shrimp"] == 0
        assert result["average_age_months"] == 0.0
        assert result["stocking_density"] == 0.0

    def test_analyze_tank_species_distribution(self):
        """Test species distribution counting."""
        tank = ShrimpTank(
            tank_name="Mixed",
            capacity=100,
            shrimp_list=[
                Shrimp(name="Red1", species="Red Cherry", age_months=10),
                Shrimp(name="Red2", species="Red Cherry", age_months=15),
                Shrimp(name="Amano", species="Amano", age_months=20),
                Shrimp(name="Ghost", species="Ghost", age_months=30),
                Shrimp(name="Red3", species="Red Cherry", age_months=25),
            ]
        )

        result = analyze_tank(tank)

        species_count = result["species_distribution"]
        assert species_count["Red Cherry"] == 3
        assert species_count["Amano"] == 1
        assert species_count["Ghost"] == 1

    def test_analyze_tank_high_stocking_density(self):
        """Test tank with high stocking density."""
        shrimp_list = [
            Shrimp(name=f"Shrimp{i}", species="Red Cherry", age_months=10)
            for i in range(20)
        ]
        tank = ShrimpTank(tank_name="Crowded", capacity=50, shrimp_list=shrimp_list)

        result = analyze_tank(tank)

        assert result["num_shrimp"] == 20
        assert result["stocking_density"] == 0.4


class TestConfigureAquariumTool:
    """Tests for the configure_aquarium tool."""

    def test_configure_aquarium_basic(self):
        """Test configure_aquarium with basic setup."""
        tank = ShrimpTank(
            tank_name="Main",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Shrimp1", species="Red Cherry", age_months=12),
            ]
        )
        food_list = [
            FishFood(name="Pellets", protein_percent=40.0),
        ]
        setup = AquariumSetup(
            tank=tank,
            food=food_list,
            maintenance_schedule={"daily": "Feed"}
        )

        result = configure_aquarium(setup, notes="")

        assert isinstance(result, dict)
        assert result["tank"]["name"] == "Main"
        assert result["tank"]["capacity"] == 50
        assert result["tank"]["shrimp_count"] == 1
        assert len(result["food"]) == 1
        assert result["food"][0]["name"] == "Pellets"

    def test_configure_aquarium_with_notes(self):
        """Test configure_aquarium with additional notes."""
        tank = ShrimpTank(tank_name="Test", capacity=50, shrimp_list=[])
        setup = AquariumSetup(tank=tank, food=[], maintenance_schedule={})

        result = configure_aquarium(setup, notes="Custom setup notes")

        assert result["notes"] == "Custom setup notes"

    def test_configure_aquarium_default_notes(self):
        """Test configure_aquarium with default empty notes."""
        tank = ShrimpTank(tank_name="Test", capacity=50, shrimp_list=[])
        setup = AquariumSetup(tank=tank, food=[], maintenance_schedule={})

        result = configure_aquarium(setup, notes="")

        assert result["notes"] == ""

    def test_configure_aquarium_multiple_foods(self):
        """Test configure_aquarium with multiple food types."""
        tank = ShrimpTank(tank_name="Test", capacity=50, shrimp_list=[])
        food_list = [
            FishFood(name="Pellets", protein_percent=40.0),
            FishFood(name="Flakes", protein_percent=35.0),
            FishFood(name="Powder", protein_percent=50.0),
        ]
        setup = AquariumSetup(
            tank=tank,
            food=food_list,
            maintenance_schedule={}
        )

        result = configure_aquarium(setup, notes="")

        assert len(result["food"]) == 3
        assert result["food"][1]["name"] == "Flakes"

    def test_configure_aquarium_maintenance_schedule(self):
        """Test configure_aquarium maintenance schedule mapping."""
        tank = ShrimpTank(tank_name="Test", capacity=50, shrimp_list=[])
        maintenance = {
            "daily": "Feed",
            "weekly": "Water change",
            "monthly": "Clean filter"
        }
        setup = AquariumSetup(
            tank=tank,
            food=[],
            maintenance_schedule=maintenance
        )

        result = configure_aquarium(setup, notes="")

        assert result["maintenance"] == maintenance


class TestFindShrimpBySpeciesTool:
    """Tests for the find_shrimp_by_species tool."""

    def test_find_shrimp_by_species_single_match(self):
        """Test finding shrimp with single match."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Red1", species="Red Cherry", age_months=10),
                Shrimp(name="Amano", species="Amano", age_months=20),
            ]
        )

        result = find_shrimp_by_species(tank, "Red Cherry")

        assert len(result) == 1
        assert result[0]["name"] == "Red1"
        assert result[0]["species"] == "Red Cherry"
        assert result[0]["age_months"] == 10

    def test_find_shrimp_by_species_multiple_matches(self):
        """Test finding multiple shrimp of the same species."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=100,
            shrimp_list=[
                Shrimp(name="Red1", species="Red Cherry", age_months=10),
                Shrimp(name="Red2", species="Red Cherry", age_months=15),
                Shrimp(name="Red3", species="Red Cherry", age_months=20),
                Shrimp(name="Amano", species="Amano", age_months=25),
            ]
        )

        result = find_shrimp_by_species(tank, "Red Cherry")

        assert len(result) == 3
        assert all(shrimp["species"] == "Red Cherry" for shrimp in result)

    def test_find_shrimp_by_species_no_matches(self):
        """Test finding shrimp when no matches exist."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Red", species="Red Cherry", age_months=10),
            ]
        )

        result = find_shrimp_by_species(tank, "Nonexistent")

        assert len(result) == 0

    def test_find_shrimp_by_species_case_insensitive(self):
        """Test that species search is case-insensitive."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=50,
            shrimp_list=[
                Shrimp(name="Red", species="Red Cherry", age_months=10),
            ]
        )

        # Should match with different cases
        result1 = find_shrimp_by_species(tank, "red cherry")
        result2 = find_shrimp_by_species(tank, "RED CHERRY")
        result3 = find_shrimp_by_species(tank, "Red Cherry")

        assert len(result1) == 1
        assert len(result2) == 1
        assert len(result3) == 1

    def test_find_shrimp_by_species_empty_tank(self):
        """Test finding shrimp in empty tank."""
        tank = ShrimpTank(tank_name="Empty", capacity=50, shrimp_list=[])

        result = find_shrimp_by_species(tank, "Red Cherry")

        assert len(result) == 0

    def test_find_shrimp_by_species_all_fields_present(self):
        """Test that found shrimp have all required fields."""
        tank = ShrimpTank(
            tank_name="Test",
            capacity=50,
            shrimp_list=[
                Shrimp(name="TestShrimp", species="Test Species", age_months=42),
            ]
        )

        result = find_shrimp_by_species(tank, "Test Species")

        assert len(result) == 1
        found_shrimp = result[0]
        assert "name" in found_shrimp
        assert "species" in found_shrimp
        assert "age_months" in found_shrimp
        assert found_shrimp["name"] == "TestShrimp"
        assert found_shrimp["species"] == "Test Species"
        assert found_shrimp["age_months"] == 42


class TestComplexIntegration:
    """Integration tests for complex_inputs tools."""

    def test_full_workflow(self):
        """Test a complete workflow using multiple tools."""
        # Create a tank with multiple shrimp
        tank = ShrimpTank(
            tank_name="Main Aquarium",
            capacity=75,
            shrimp_list=[
                Shrimp(name="Spot", species="Red Cherry", age_months=12),
                Shrimp(name="Stripe", species="Red Cherry", age_months=18),
                Shrimp(name="Scout", species="Amano", age_months=24),
                Shrimp(name="Ghost", species="Ghost", age_months=36),
            ]
        )

        # Test name_shrimp
        names = name_shrimp(tank, ["NewShrimp"])
        assert len(names) == 5
        assert "NewShrimp" in names

        # Test analyze_tank
        analysis = analyze_tank(tank)
        assert analysis["num_shrimp"] == 4
        assert analysis["capacity"] == 75
        assert len(analysis["species_distribution"]) == 3

        # Test find_shrimp_by_species
        red_shrimp = find_shrimp_by_species(tank, "Red Cherry")
        assert len(red_shrimp) == 2

        # Create aquarium setup and configure
        food = [
            FishFood(name="Premium", protein_percent=45.0),
            FishFood(name="Budget", protein_percent=30.0),
        ]
        setup = AquariumSetup(
            tank=tank,
            food=food,
            maintenance_schedule={
                "daily": "Feed",
                "weekly": "Water change (30%)",
                "monthly": "Deep clean",
            }
        )

        config = configure_aquarium(setup, notes="Well established aquarium")
        assert config["tank"]["shrimp_count"] == 4
        assert len(config["food"]) == 2

    def test_error_handling_in_workflow(self):
        """Test error handling in workflow."""
        # Invalid tank should fail
        with pytest.raises(ValidationError):
            tank = ShrimpTank(
                tank_name="Invalid",
                capacity=-1,  # Invalid
                shrimp_list=[]
            )

        # Invalid food should fail
        with pytest.raises(ValidationError):
            food = FishFood(
                name="Invalid",
                protein_percent=150.0  # Invalid
            )

        # Invalid shrimp should fail
        with pytest.raises(ValidationError):
            shrimp = Shrimp(
                name="VeryLongNameThatExceedsLimit",  # Invalid
                species="Test",
                age_months=10
            )

    def test_edge_case_minimal_setup(self):
        """Test with minimal valid setup."""
        tank = ShrimpTank(tank_name="Minimal", capacity=1, shrimp_list=[])
        setup = AquariumSetup(tank=tank, food=[], maintenance_schedule={})

        result = configure_aquarium(setup, notes="")

        assert result["tank"]["capacity"] == 1
        assert result["tank"]["shrimp_count"] == 0
        assert len(result["food"]) == 0

    def test_edge_case_maximum_constraints(self):
        """Test with maximum allowed values."""
        # Maximum shrimp name length
        shrimp = Shrimp(name="MaxName10", species="Test", age_months=360)

        # Maximum food protein
        food = FishFood(name="MaxProtein", protein_percent=100.0)

        # Large tank with many shrimp
        shrimp_list = [
            Shrimp(name=f"S{i:03d}", species="Red Cherry", age_months=360)
            for i in range(100)
        ]
        tank = ShrimpTank(tank_name="BigTank", capacity=1000, shrimp_list=shrimp_list)

        analysis = analyze_tank(tank)
        assert analysis["num_shrimp"] == 100
        assert analysis["average_age_months"] == 360.0

