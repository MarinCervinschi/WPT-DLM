
from .base import NodeInterface
from typing import Dict, Optional
import logging


logger = logging.getLogger(__name__)


class I2CNode(NodeInterface):
    """Physical node communicating via I2C (Arduino)."""
    
    def __init__(self, node_id: str, max_power_kw: float, i2c_address: int, i2c_bus):
        super().__init__(node_id, max_power_kw)
        self.i2c_address = i2c_address
        self.bus = i2c_bus
        logger.info(f"Initialized I2C node {node_id} at address 0x{i2c_address:02X}")
    
    def read_telemetry(self) -> Optional[Dict]:
        """Read telemetry from Arduino via I2C."""
        try:
            # Read 5 bytes from Arduino
            data = self.bus.read_i2c_block_data(self.i2c_address, 0, 5)
            
            is_present = bool(data[0])
            current_ma = (data[1] << 8) | data[2]
            voltage_v = ((data[3] << 8) | data[4]) / 10.0
            
            # Convert to proper units
            voltage = float(voltage_v)  # Volts
            current = float(current_ma) / 1000.0  # Amps
            power_kw = (voltage * current) / 1000.0  # kW
            
            telemetry = {
                "voltage": voltage,
                "current": current,
                "power_kw": power_kw,
                "power_limit_kw": self.power_limit_kw,
                "is_occupied": is_present
            }
            
            # Add optional vehicle info
            if is_present and self.connected_vehicle_id:
                telemetry["connected_vehicle_id"] = self.connected_vehicle_id
                if self.vehicle_soc is not None:
                    telemetry["current_vehicle_soc"] = self.vehicle_soc
            
            return telemetry
            
        except Exception as e:
            logger.error(f"Error reading I2C node {self.node_id} (0x{self.i2c_address:02X}): {e}")
            return None
    
    def write_command(self, power_limit_kw: float, authorized: bool):
        """Send command to Arduino via I2C."""
        try:
            # Map power limit 0-max_power_kw to 0-255
            power_byte = min(255, int((power_limit_kw / self.max_power_kw) * 255))
            auth_byte = 1 if authorized else 0
            
            self.bus.write_i2c_block_data(self.i2c_address, 0, [power_byte, auth_byte])
            self.power_limit_kw = power_limit_kw
            self.authorized = authorized
            
            logger.debug(
                f"Command sent to {self.node_id}: "
                f"power={power_byte} ({power_limit_kw:.2f}kW), auth={auth_byte}"
            )
            
        except Exception as e:
            logger.error(f"Error writing to I2C node {self.node_id}: {e}")
