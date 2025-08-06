#!/usr/bin/env python3
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

class GameManager:
    def __init__(self):
        self.save_file = "game_save.json"
        self.game_data = None
        self.last_save_time = time.time()
        self.last_income_update = time.time()
        self.income_update_interval = 60  # Update income every 60 seconds (1 minute)
        self.load_game_data()
        
    def load_game_data(self) -> Dict[str, Any]:
        """Load game data from save file, create default if not exists"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    self.game_data = json.load(f)
                # Update last save time
                if self.game_data['player']['last_save_time']:
                    # Calculate offline earnings
                    self._calculate_offline_earnings()
                # Recalculate building levels based on structure levels
                self._recalculate_all_building_levels()
            except Exception as e:
                print(f"Error loading save file: {e}")
                self._create_default_save()
        else:
            self._create_default_save()
        
        return self.game_data
    
    def _recalculate_all_building_levels(self):
        """Recalculate building levels for all buildings based on structure levels"""
        for building_name in ['temple1', 'temple2', 'hotel1', 'restaurant1', 'apt1']:
            self._update_building_level(building_name)
            self._update_building_income(building_name)
            # Auto-assign workers to buildings with completion_count > 0
            building = self.get_building_data(building_name)
            if building.get('completion_count', 0) > 0:
                building['workers_assigned'] = 10  # Auto-assign 10 workers
        # Update island level after recalculating all building levels
        self._update_island_level()
    
    def _create_default_save(self):
        """Create default save file from the template"""
        with open(self.save_file, 'r') as f:
            self.game_data = json.load(f)
        self.save_game_data()
    
    def save_game_data(self):
        """Save current game data to file"""
        self.game_data['player']['last_save_time'] = datetime.now().isoformat()
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.game_data, f, indent=2)
            self.last_save_time = time.time()
        except Exception as e:
            print(f"Error saving game: {e}")
    
    def get_player_resources(self) -> Tuple[float, float]:
        """Get current MP and Coins"""
        return self.game_data['player']['mp'], self.game_data['player']['coins']
    
    def update_player_resources(self, mp_delta: float = 0, coins_delta: float = 0):
        """Update player MP and/or Coins"""
        self.game_data['player']['mp'] = max(0, self.game_data['player']['mp'] + mp_delta)
        self.game_data['player']['coins'] = max(0, self.game_data['player']['coins'] + coins_delta)
        
        # Update statistics
        if coins_delta > 0:
            self.game_data['statistics']['total_coins_earned'] += coins_delta
        elif coins_delta < 0:
            self.game_data['statistics']['total_coins_spent'] += abs(coins_delta)
            
        if mp_delta > 0:
            self.game_data['statistics']['total_mp_generated'] += mp_delta
        elif mp_delta < 0:
            self.game_data['statistics']['total_mp_consumed'] += abs(mp_delta)
        
        self.save_game_data()
    
    def get_building_data(self, building_name: str) -> Dict[str, Any]:
        """Get data for a specific building"""
        return self.game_data['buildings'].get(building_name, {})
    
    def get_structure_level(self, building_name: str, structure_id: str) -> int:
        """Get the level of a specific structure"""
        building = self.get_building_data(building_name)
        if building and 'structures' in building:
            structure = building['structures'].get(structure_id, {})
            return structure.get('level', 0)
        return 0
    
    def upgrade_structure(self, building_name: str, structure_id: str) -> bool:
        """Upgrade a structure if player has enough coins"""
        building = self.get_building_data(building_name)
        if not building or 'structures' not in building:
            return False
            
        structure = building['structures'].get(structure_id)
        if not structure:
            return False
            
        current_level = structure['level']
        if current_level >= 5:  # Max level for individual building structures
            return False
            
        # Calculate upgrade cost
        cost = self.calculate_upgrade_cost(building_name, structure_id, current_level + 1)
        
        # Check if player has enough coins
        mp, coins = self.get_player_resources()
        if coins < cost:
            return False
            
        # Perform upgrade
        structure['level'] = current_level + 1
        structure['is_built'] = True
        self.update_player_resources(coins_delta=-cost)
        
        # Update building level (minimum of all structures)
        self._update_building_level(building_name)
        
        # Update island level
        self._update_island_level()
        
        # Update statistics
        self.game_data['statistics']['total_upgrades'] += 1
        
        self.save_game_data()
        return True
    
    def calculate_upgrade_cost(self, building_name: str, structure_id: str, target_level: int) -> float:
        """Calculate the cost to upgrade building to target level, scaled by structure completion_count"""
        building_type = building_name.replace('1', '').replace('2', '')  # Remove numbers
        
        if building_type == 'apt':
            building_type = 'apt'
        elif building_type == 'temple':
            building_type = 'temple'
        elif building_type == 'hotel':
            building_type = 'hotel'
        elif building_type == 'restaurant':
            building_type = 'restaurant'
        else:
            return 0
            
        eco_data = self.game_data['economy']['upgrade_costs'].get(building_type)
        if not eco_data:
            return 0
            
        # Get structure index (1-5)
        structure_num = int(structure_id[-1]) - 1
        if structure_num < 0 or structure_num >= len(eco_data['base_costs']):
            return 0
            
        base_cost = eco_data['base_costs'][structure_num]
        multiplier = eco_data['cost_multiplier']
        
        # Get structure completion count to scale costs
        building_data = self.get_building_data(building_name)
        structure_level = building_data.get('completion_count', 0)
        
        # Scale cost based on structure level: cost increases by 50% per structure level
        structure_multiplier = 1.0 + (structure_level * 0.5)
        
        # Cost formula: base_cost * (multiplier ^ (building_level - 1)) * structure_multiplier
        building_cost = base_cost * (multiplier ** (target_level - 1))
        return building_cost * structure_multiplier
    
    def _update_building_level(self, building_name: str):
        """Update building level based on minimum structure level"""
        building = self.get_building_data(building_name)
        if not building or 'structures' not in building:
            return
            
        # Find minimum level among all structures
        min_level = 5  # Start with max
        for structure in building['structures'].values():
            min_level = min(min_level, structure.get('level', 0))
            
        old_level = building['building_level']
        building['building_level'] = min_level
        
        # Update building upgrade status
        building['is_upgraded'] = min_level >= 1
        
        # Update income if building level changed
        if old_level != min_level:
            self._update_building_income(building_name)
    
    def _update_building_income(self, building_name: str):
        """Update building income based on completion count"""
        building = self.get_building_data(building_name)
        if not building:
            return
            
        # Use completion_count for income calculation (how many times building was completed)
        level = building.get('completion_count', 0)
        if level == 0:
            building['income_per_hour'] = 0
            return
            
        building_type = building_name.replace('1', '').replace('2', '')
        
        # Get base income and multiplier
        base_income = self.game_data['economy']['base_income'].get(building_type, 0)
        multiplier = self.game_data['economy']['upgrade_multipliers'].get(building_type, 0)
        
        # Income formula: base * (1 + multiplier)^(level-1)
        if base_income > 0:
            building['income_per_hour'] = base_income * ((1 + multiplier) ** (level - 1))
    
    def _update_island_level(self):
        """Update island level based on minimum building level"""
        min_level = 25  # Start with max possible
        
        for building in self.game_data['buildings'].values():
            min_level = min(min_level, building.get('building_level', 0))
            
        old_level = self.game_data['island']['level']
        self.game_data['island']['level'] = min_level
        
        # Update speed multipliers
        if old_level != min_level:
            self.game_data['island']['spawn_speed_multiplier'] = 1.0 + (0.05 * min_level)
            self.game_data['island']['movement_speed_multiplier'] = 1.0 + (0.05 * min_level)
    
    def _calculate_offline_earnings(self):
        """Calculate earnings while player was offline"""
        if not self.game_data['player']['last_save_time']:
            return
            
        try:
            last_save = datetime.fromisoformat(self.game_data['player']['last_save_time'])
            current_time = datetime.now()
            hours_offline = (current_time - last_save).total_seconds() / 3600
            
            if hours_offline > 0:
                # Calculate total income
                total_income = 0
                for building_name, building in self.game_data['buildings'].items():
                    if building.get('income_per_hour', 0) > 0:
                        # Check if building has workers
                        if building.get('workers_assigned', 0) >= 10:
                            total_income += building['income_per_hour'] * hours_offline
                
                # Calculate MP consumption (Workers House)
                apt_data = self.game_data['buildings'].get('apt1', {})
                if apt_data.get('workers_assigned', 0) >= 10:
                    mp_consumed = self.game_data['economy']['apt_mp_consumption'] * hours_offline
                else:
                    mp_consumed = 0
                
                # Check if we have enough MP
                current_mp = self.game_data['player']['mp']
                if current_mp >= mp_consumed:
                    # Full earnings
                    self.update_player_resources(mp_delta=-mp_consumed, coins_delta=total_income)
                    print(f"Welcome back! You earned {total_income:.0f} coins while away.")
                else:
                    # Partial earnings based on available MP
                    if mp_consumed > 0:
                        earning_ratio = current_mp / mp_consumed
                        actual_income = total_income * earning_ratio
                        self.update_player_resources(mp_delta=-current_mp, coins_delta=actual_income)
                        print(f"Welcome back! You earned {actual_income:.0f} coins (limited by MP).")
                        
        except Exception as e:
            print(f"Error calculating offline earnings: {e}")
    
    def collect_income(self, building_name: str) -> float:
        """Collect income from a building (real-time calculation)"""
        building = self.get_building_data(building_name)
        if not building:
            return 0
            
        # Check if building has income
        income_rate = building.get('income_per_hour', 0)
        if income_rate <= 0:
            return 0
            
        # Check if building has workers
        if building.get('workers_assigned', 0) < 10:
            return 0
            
        # Calculate time since last collection
        current_time = time.time()
        last_collected = building.get('last_income_collected', current_time)
        hours_elapsed = (current_time - last_collected) / 3600
        
        # Calculate income
        income = income_rate * hours_elapsed
        
        # Update last collection time
        building['last_income_collected'] = current_time
        
        # Add to player coins
        if income > 0:
            self.update_player_resources(coins_delta=income)
            
        return income
    
    def consume_mp(self, building_name: str) -> float:
        """Consume MP for Workers House (real-time calculation)"""
        if building_name != 'apt1':
            return 0
            
        building = self.get_building_data(building_name)
        if not building:
            return 0
            
        # Check if building has workers
        if building.get('workers_assigned', 0) < 10:
            return 0
            
        # Calculate time since last consumption
        current_time = time.time()
        last_consumed = building.get('last_mp_consumed')
        if last_consumed is None:
            last_consumed = current_time
        hours_elapsed = (current_time - last_consumed) / 3600
        
        # Calculate MP to consume
        mp_rate = self.game_data['economy']['apt_mp_consumption']
        mp_needed = mp_rate * hours_elapsed
        
        # Check if we have enough MP
        current_mp = self.game_data['player']['mp']
        if current_mp >= mp_needed:
            # Update last consumption time
            building['last_mp_consumed'] = current_time
            # Consume MP
            self.update_player_resources(mp_delta=-mp_needed)
            return mp_needed
        else:
            # Partial consumption
            if mp_rate > 0:
                partial_hours = current_mp / mp_rate
                building['last_mp_consumed'] = last_consumed + (partial_hours * 3600)
                self.update_player_resources(mp_delta=-current_mp)
            return current_mp
    
    def generate_mp(self, mp_amount: float):
        """Generate MP from prayer wheel"""
        # Calculate temple bonus
        temple1_level = self.game_data['buildings']['temple1']['building_level']
        temple2_level = self.game_data['buildings']['temple2']['building_level']
        avg_temple_level = (temple1_level + temple2_level) / 2
        
        # Apply temple bonus (5% per average level)
        bonus_multiplier = 1 + (0.05 * avg_temple_level)
        total_mp = mp_amount * bonus_multiplier
        
        # Update player MP
        self.update_player_resources(mp_delta=total_mp)
        
        # Update prayer wheel stats
        self.game_data['prayer_wheel']['total_mp_generated'] += total_mp
        self.game_data['prayer_wheel']['temple_level_bonus'] = avg_temple_level
        
        self.save_game_data()
        return total_mp
    
    def get_island_level(self) -> int:
        """Get current island level"""
        return self.game_data['island']['level']
    
    def get_movement_speed_multiplier(self) -> float:
        """Get movement speed multiplier based on island level"""
        return self.game_data['island']['movement_speed_multiplier']
    
    def get_spawn_speed_multiplier(self) -> float:
        """Get spawn speed multiplier based on island level"""
        return self.game_data['island']['spawn_speed_multiplier']
    
    def assign_workers(self, building_name: str, workers: int):
        """Assign workers to a building"""
        building = self.get_building_data(building_name)
        if building:
            building['workers_assigned'] = workers
            self.save_game_data()
    
    def get_total_workers(self) -> int:
        """Get total worker capacity from all Workers Houses"""
        total = 0
        apt_data = self.game_data['buildings'].get('apt1', {})
        if apt_data.get('building_level', 0) > 0:
            level = apt_data['building_level']
            base_capacity = self.game_data['economy']['apt_base_capacity']
            multiplier = self.game_data['economy']['upgrade_multipliers']['apt']
            total = base_capacity * ((1 + multiplier) ** (level - 1))
        return int(total)
    
    def get_workers_assigned(self) -> int:
        """Get total workers currently assigned"""
        total = 0
        for building in self.game_data['buildings'].values():
            total += building.get('workers_assigned', 0)
        return total
    
    def get_available_workers(self) -> int:
        """Get number of unassigned workers"""
        return max(0, self.get_total_workers() - self.get_workers_assigned())
    
    def update_passive_income(self):
        """Update passive income every minute for all buildings"""
        current_time = time.time()
        
        # Check if it's time to update income (every minute)
        if current_time - self.last_income_update < self.income_update_interval:
            return
            
        # Calculate time elapsed since last update in hours
        minutes_elapsed = (current_time - self.last_income_update) / 60
        hours_elapsed = minutes_elapsed / 60
        
        total_income = 0
        total_mp_consumed = 0
        
        # Process income for all buildings with assigned workers
        for building_name, building in self.game_data['buildings'].items():
            # Check if building has income and workers
            income_rate = building.get('income_per_hour', 0)
            workers_assigned = building.get('workers_assigned', 0)
            
            if income_rate > 0 and workers_assigned >= 10:
                # Calculate income for this building
                building_income = income_rate * hours_elapsed
                total_income += building_income
                
                # Update last collection time
                building['last_income_collected'] = current_time
        
        # Handle MP consumption for Workers House
        apt_data = self.game_data['buildings'].get('apt1', {})
        if apt_data.get('workers_assigned', 0) >= 10:
            mp_rate = self.game_data['economy']['apt_mp_consumption']
            mp_needed = mp_rate * hours_elapsed
            
            # Check if we have enough MP
            current_mp = self.game_data['player']['mp']
            if current_mp >= mp_needed:
                total_mp_consumed = mp_needed
                apt_data['last_mp_consumed'] = current_time
            else:
                # Partial consumption - reduce income proportionally
                if mp_needed > 0:
                    consumption_ratio = current_mp / mp_needed
                    total_income *= consumption_ratio
                    total_mp_consumed = current_mp
                    # Update partial consumption time
                    partial_hours = current_mp / mp_rate if mp_rate > 0 else 0
                    apt_data['last_mp_consumed'] = self.last_income_update + (partial_hours * 3600)
                else:
                    total_mp_consumed = 0
        
        # Apply income and MP changes
        if total_income > 0 or total_mp_consumed > 0:
            self.update_player_resources(mp_delta=-total_mp_consumed, coins_delta=total_income)
        
        # Update the last income update time
        self.last_income_update = current_time


# Global instance
game_manager = GameManager()