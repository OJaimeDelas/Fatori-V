# =============================================================================
# FATORI-V • FI Targets
# File: board_interface.py
# -----------------------------------------------------------------------------
# Board interface abstraction for register-level fault injection.
#=============================================================================

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class BoardInterface(ABC):
    """
    Abstract base class for board-level register injection.
    
    Different platforms (Raspberry Pi GPIO, custom FPGA interface,
    SPI/I2C protocol, etc.) implement this interface to provide
    register-level fault injection.
    """
    
    @abstractmethod
    def inject_register(self, reg_id: int, bit_index: int = None) -> bool:
        """
        Inject fault into register.
        
        Args:
            reg_id: Register ID to inject into
            bit_index: Optional bit index within register (for bit-level injection)
        
        Returns:
            True if injection succeeded, False otherwise
        """
        pass


class NoOpBoardInterface(BoardInterface):
    """
    Stub implementation that logs but doesn't perform actual GPIO operations.
    
    This is the default implementation used when GPIO is disabled. It logs
    all injection requests but doesn't interact with actual hardware.
    
    Use Cases:
        - Testing without hardware
        - Dry-run mode
        - Development on systems without GPIO
    """
    
    def inject_register(self, reg_id: int, bit_index: int = None) -> bool:
        """
        Log injection request but don't perform actual injection.
        
        Args:
            reg_id: Register ID
            bit_index: Optional bit index
        
        Returns:
            Always True (simulation mode)
        """
        if bit_index is None:
            logger.info(f"[NoOp] Would inject reg_id={reg_id}")
        else:
            logger.info(f"[NoOp] Would inject reg_id={reg_id}, bit={bit_index}")
        return True


class GPIOBoardInterface(BoardInterface):
    """
    GPIO-based board interface for register injection.
    
    This implementation broadcasts the reg_id via GPIO pins and pulses
    a trigger pin to signal the injection. The FPGA board is expected
    to have hardware that:
    1. Reads the reg_id from GPIO pins (binary encoding)
    2. Detects the trigger pulse
    3. Performs the actual fault injection
    
    IMPORTANT: This is a PLACEHOLDER implementation. Actual GPIO control
    must be implemented based on your platform:
    
    Options:
        - Linux sysfs GPIO (/sys/class/gpio/)
        - libgpiod (Python gpiod library)
        - Custom kernel driver
        - SPI/I2C protocol to FPGA
        - Direct memory-mapped GPIO (embedded systems)
    
    Attributes:
        pin_start: First GPIO pin for reg_id encoding
        pin_count: Number of pins used for reg_id (supports 2^pin_count IDs)
        trigger_pin: GPIO pin to pulse for injection trigger
        device_path: Platform-specific GPIO device path
    """
    
    def __init__(self, config):
        """
        Initialize GPIO board interface.
        
        Args:
            config: Config object with GPIO settings
        """
        self.pin_start = config.gpio_pin_start
        self.pin_count = config.gpio_pin_count
        self.trigger_pin = config.gpio_trigger_pin
        self.device_path = config.gpio_device_path
        self.pulse_width_us = 10  # Pulse width in microseconds
        
        logger.warning(
            "GPIOBoardInterface initialized but GPIO control not yet implemented. "
            "See board_interface.py for implementation notes."
        )
        
        # TODO: Initialize GPIO hardware
        # Example for libgpiod:
        # import gpiod
        # self.chip = gpiod.Chip(self.device_path)
        # self.data_lines = [self.chip.get_line(self.pin_start + i) 
        #                     for i in range(self.pin_count)]
        # self.trigger_line = self.chip.get_line(self.trigger_pin)
        # for line in self.data_lines:
        #     line.request(consumer="fi", type=gpiod.LINE_REQ_DIR_OUT)
        # self.trigger_line.request(consumer="fi", type=gpiod.LINE_REQ_DIR_OUT)
    
    def inject_register(self, reg_id: int, bit_index: int = None) -> bool:
        """
        Broadcast reg_id via GPIO pins and pulse trigger.
        
        Algorithm:
        1. Encode reg_id as binary across pin_count GPIO pins
        2. Pulse the trigger pin
        3. Wait for acknowledgment (platform-specific)
        
        Args:
            reg_id: Register ID to inject (0 to 2^pin_count - 1)
            bit_index: Optional bit index (currently unused)
        
        Returns:
            True if injection succeeded (placeholder always returns True)
        """
        if bit_index is None:
            logger.info(f"[GPIO] Injecting reg_id={reg_id}")
        else:
            logger.info(f"[GPIO] Injecting reg_id={reg_id}, bit={bit_index}")
        
        # Validate reg_id fits in available pins
        max_reg_id = (1 << self.pin_count) - 1
        if reg_id > max_reg_id:
            logger.error(
                f"reg_id={reg_id} exceeds maximum {max_reg_id} "
                f"for {self.pin_count} GPIO pins"
            )
            return False
        
        # TODO: Implement actual GPIO writes
        #
        # Pseudocode:
        # 1. Set data pins according to reg_id binary encoding:
        #    for i in range(self.pin_count):
        #        bit = (reg_id >> i) & 1
        #        self.data_lines[i].set_value(bit)
        #
        # 2. Pulse trigger pin:
        #    self.trigger_line.set_value(1)
        #    time.sleep(self.pulse_width_us / 1_000_000)
        #    self.trigger_line.set_value(0)
        #
        # 3. Wait for acknowledgment (if applicable):
        #    # Platform-specific handshake logic
        #
        # Example using libgpiod:
        # values = [(reg_id >> i) & 1 for i in range(self.pin_count)]
        # for i, line in enumerate(self.data_lines):
        #     line.set_value(values[i])
        # self.trigger_line.set_value(1)
        # time.sleep(self.pulse_width_us / 1_000_000)
        # self.trigger_line.set_value(0)
        
        logger.warning("GPIO write not implemented - returning success (placeholder)")
        return True


def create_board_interface(cfg):
    """
    Factory function to create appropriate board interface.
    
    Creates either a real GPIO interface or a NoOp stub based on
    the cfg.gpio_enabled flag.
    
    Args:
        cfg: Config object with GPIO settings
    
    Returns:
        BoardInterface instance (either GPIOBoardInterface or NoOpBoardInterface)
    
    Example:
        >>> board_if = create_board_interface(cfg)
        >>> board_if.inject_register(reg_id=5)
    """
    if cfg.gpio_enabled:
        logger.info("Creating GPIO board interface (real GPIO control)")
        return GPIOBoardInterface(cfg)
    else:
        logger.info("Creating NoOp board interface (simulation mode)")
        return NoOpBoardInterface()