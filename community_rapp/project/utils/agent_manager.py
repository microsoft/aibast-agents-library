"""
Agent Manager - Local Agent Registry

Provides a centralized registry for managing agent instances.
Supports manual registration and auto-discovery of agents.

Usage:
    from utils.agent_manager import AgentManager

    # Get singleton instance
    manager = AgentManager()

    # Register an agent
    from agents.email_agent import EmailAgent
    manager.register_agent('EmailAgent', EmailAgent())

    # Get an agent
    agent = manager.get_agent('EmailAgent')

    # Auto-discover agents from agents directory
    manager.discover_agents()

    # List all registered agents
    agents = manager.list_agents()
"""

import logging
import os
import sys
import importlib.util
from threading import Lock
from typing import Dict, Optional, List, Any


class AgentManager:
    """
    Centralized registry for managing agent instances.

    Features:
    - Manual agent registration
    - Auto-discovery from agents directory
    - Thread-safe operations
    - Singleton pattern support
    """

    # Singleton instance
    _instance = None
    _lock = Lock()

    def __new__(cls):
        """Singleton pattern - only one AgentManager instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the agent registry"""
        if self._initialized:
            return

        self._agents: Dict[str, Any] = {}
        self._agent_metadata: Dict[str, Dict] = {}
        self._registry_lock = Lock()
        self._initialized = True

        logging.debug("AgentManager initialized")

    def register_agent(self, name: str, agent_instance: Any, metadata: Optional[Dict] = None) -> None:
        """
        Register an agent instance.

        Args:
            name: Unique name for the agent (e.g., 'EmailAgent', 'WealthInsightsGeneratorAgent')
            agent_instance: The instantiated agent object
            metadata: Optional metadata about the agent (description, version, etc.)

        Example:
            from agents.email_agent import EmailAgent
            manager.register_agent('EmailAgent', EmailAgent())
        """
        with self._registry_lock:
            if name in self._agents:
                logging.warning(f"Agent '{name}' already registered, overwriting")

            self._agents[name] = agent_instance
            self._agent_metadata[name] = metadata or {}
            logging.info(f"Registered agent: {name}")

    def get_agent(self, name: str) -> Optional[Any]:
        """
        Get an agent instance by name.

        Args:
            name: Name of the agent to retrieve

        Returns:
            Agent instance or None if not found

        Example:
            agent = manager.get_agent('EmailAgent')
            if agent:
                result = agent.perform(action='send', ...)
        """
        with self._registry_lock:
            agent = self._agents.get(name)
            if agent:
                logging.debug(f"Retrieved agent: {name}")
            return agent

    def unregister_agent(self, name: str) -> bool:
        """
        Remove an agent from the registry.

        Args:
            name: Name of the agent to remove

        Returns:
            True if agent was removed, False if not found
        """
        with self._registry_lock:
            if name in self._agents:
                del self._agents[name]
                if name in self._agent_metadata:
                    del self._agent_metadata[name]
                logging.info(f"Unregistered agent: {name}")
                return True
            return False

    def list_agents(self) -> List[str]:
        """
        Get list of all registered agent names.

        Returns:
            List of agent names

        Example:
            agents = manager.list_agents()
            print(f"Available agents: {', '.join(agents)}")
        """
        with self._registry_lock:
            return list(self._agents.keys())

    def get_agent_metadata(self, name: str) -> Optional[Dict]:
        """
        Get metadata for a specific agent.

        Args:
            name: Name of the agent

        Returns:
            Metadata dict or None if not found
        """
        with self._registry_lock:
            return self._agent_metadata.get(name)

    def discover_agents(self, agents_directory: str = "agents") -> int:
        """
        Auto-discover and register agents from a directory.

        Scans the specified directory for Python files ending with '_agent.py',
        dynamically imports them, and registers any agent classes found.

        Args:
            agents_directory: Path to directory containing agent files (default: "agents")

        Returns:
            Number of agents discovered and registered

        Example:
            count = manager.discover_agents()
            print(f"Discovered {count} agents")

        Note:
            - Only files matching *_agent.py are scanned
            - Classes must end with 'Agent' and have a 'perform' method
            - Skips BasicAgent base class
        """
        discovered_count = 0

        # Get absolute path to agents directory
        if not os.path.isabs(agents_directory):
            # Assume relative to current working directory
            agents_directory = os.path.join(os.getcwd(), agents_directory)

        if not os.path.exists(agents_directory):
            logging.warning(f"Agents directory not found: {agents_directory}")
            return 0

        logging.info(f"Discovering agents in: {agents_directory}")

        # Scan directory for agent files
        for filename in os.listdir(agents_directory):
            if not filename.endswith('_agent.py'):
                continue

            if filename == 'basic_agent.py':
                continue  # Skip base class

            agent_file = os.path.join(agents_directory, filename)

            try:
                # Load the module
                module_name = filename[:-3]  # Remove .py
                agent_instance = self._load_agent_from_file(agent_file, module_name)

                if agent_instance:
                    # Extract agent name from class or use module name
                    agent_name = getattr(agent_instance, 'name', module_name)

                    # Register the agent
                    metadata = {
                        'source': 'auto_discovery',
                        'file': agent_file,
                        'module': module_name
                    }

                    # Add agent metadata if available
                    if hasattr(agent_instance, 'metadata'):
                        metadata['agent_metadata'] = agent_instance.metadata

                    self.register_agent(agent_name, agent_instance, metadata)
                    discovered_count += 1

            except Exception as e:
                logging.warning(f"Failed to load agent from {filename}: {str(e)}")

        logging.info(f"Discovery complete: {discovered_count} agents registered")
        return discovered_count

    def _load_agent_from_file(self, file_path: str, module_name: str) -> Optional[Any]:
        """
        Dynamically load an agent from a Python file.

        Args:
            file_path: Path to the agent file
            module_name: Name to use for the module

        Returns:
            Instantiated agent or None if loading fails
        """
        try:
            # Add parent directory to sys.path so agent imports work
            parent_dir = os.path.dirname(os.path.dirname(file_path))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)

            # Create module spec
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if not spec or not spec.loader:
                return None

            # Load the module
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find the agent class
            for name, obj in module.__dict__.items():
                if (isinstance(obj, type) and
                    name.endswith('Agent') and
                    name != 'BasicAgent' and
                    hasattr(obj, 'perform')):

                    # Instantiate the agent
                    agent_instance = obj()
                    logging.debug(f"Loaded agent class: {name} from {file_path}")
                    return agent_instance

            logging.debug(f"No agent class found in {file_path}")
            return None

        except Exception as e:
            logging.error(f"Error loading agent from {file_path}: {str(e)}")
            return None

    def clear_registry(self) -> None:
        """
        Clear all registered agents.
        Useful for testing or resetting the registry.
        """
        with self._registry_lock:
            count = len(self._agents)
            self._agents.clear()
            self._agent_metadata.clear()
            logging.info(f"Cleared {count} agents from registry")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the agent registry.

        Returns:
            Dict with registry statistics
        """
        with self._registry_lock:
            auto_discovered = sum(
                1 for meta in self._agent_metadata.values()
                if meta.get('source') == 'auto_discovery'
            )
            manually_registered = len(self._agents) - auto_discovered

            return {
                'total_agents': len(self._agents),
                'auto_discovered': auto_discovered,
                'manually_registered': manually_registered,
                'agent_names': list(self._agents.keys())
            }

    def __repr__(self) -> str:
        """String representation of the AgentManager"""
        stats = self.get_stats()
        return f"AgentManager(total={stats['total_agents']}, auto={stats['auto_discovered']}, manual={stats['manually_registered']})"


# Convenience function for getting the singleton instance
def get_manager() -> AgentManager:
    """
    Get the singleton AgentManager instance.

    Returns:
        AgentManager instance

    Example:
        from utils.agent_manager import get_manager

        manager = get_manager()
        manager.register_agent('MyAgent', agent_instance)
    """
    return AgentManager()


if __name__ == "__main__":
    # Example usage / testing
    logging.basicConfig(level=logging.DEBUG)

    manager = AgentManager()

    # Test auto-discovery
    print("Discovering agents...")
    count = manager.discover_agents()
    print(f"Discovered {count} agents")

    # List agents
    print(f"\nRegistered agents: {manager.list_agents()}")

    # Get stats
    print(f"\nStats: {manager.get_stats()}")
    print(f"\nManager: {manager}")
