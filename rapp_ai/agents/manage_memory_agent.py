# PASTE THE CONTENT OF manage_memory_agent.py HERE
# From the artifact "manage_memory_agent.py - Memory Management Agent"
import uuid
from datetime import datetime
from agents.basic_agent import BasicAgent
from utils.storage_factory import get_storage_manager

class ManageMemoryAgent(BasicAgent):
    def __init__(self):
        self.name = 'ManageMemory'
        self.metadata = {
            "name": self.name,
            "description": "Manages memories in the conversation system. This agent allows me to save important information to our memory system for future reference.",
            "parameters": {
                "type": "object",
                "properties": {
                    "memory_type": {
                        "type": "string",
                        "description": "Type of memory to store. Can be 'fact', 'preference', 'insight', or 'task'.",
                        "enum": ["fact", "preference", "insight", "task"]
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to store in memory. This should be a concise statement that captures the important information."
                    },
                    "importance": {
                        "type": "integer",
                        "description": "Importance rating from 1-5, where 5 is most important.",
                        "minimum": 1,
                        "maximum": 5
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional list of tags to categorize this memory."
                    },
                    "user_guid": {
                        "type": "string",
                        "description": "Optional unique identifier of the user to store memory in a user-specific location."
                    }
                },
                "required": ["memory_type", "content"]
            }
        }
        self.storage_manager = get_storage_manager()
        super().__init__(name=self.name, metadata=self.metadata)

    def perform(self, **kwargs):
        memory_type = kwargs.get('memory_type', 'fact')
        content = kwargs.get('content', '')
        importance = kwargs.get('importance', 3)
        tags = kwargs.get('tags', [])
        user_guid = kwargs.get('user_guid')
        
        if not content:
            return "Error: No content provided for memory storage."
        
        # Explicitly set memory context to the user's GUID if provided
        # This ensures consistent storage location with ContextMemoryAgent
        self.storage_manager.set_memory_context(user_guid)
        
        # Store the memory
        return self.store_memory(memory_type, content, importance, tags)

    def store_memory(self, memory_type, content, importance, tags):
        """Store a memory with consistent data structure"""
        # Read the current memory file
        memory_data = self.storage_manager.read_json()
        
        # Initialize memory structure if needed
        if not memory_data:
            memory_data = {}
        
        # Generate a new UUID for the memory
        memory_id = str(uuid.uuid4())
        
        # Create a new memory in the legacy format
        memory_data[memory_id] = {
            "conversation_id": self.storage_manager.current_guid or "current",
            "session_id": "current",
            "message": content,
            "mood": "neutral",
            "theme": memory_type,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M:%S")
        }
        
        # Write back to storage
        self.storage_manager.write_json(memory_data)
        
        # Return success message
        memory_location = f"for user {self.storage_manager.current_guid}" if self.storage_manager.current_guid else "in shared memory"
        return f"Successfully stored {memory_type} memory {memory_location}: \"{content}\""
    
    def retrieve_memories_by_tags(self, tags, user_guid=None):
        """Retrieve memories that match specific tags"""
        # Ensure using the same memory context as store operations
        if user_guid:
            self.storage_manager.set_memory_context(user_guid)
            
        memory_data = self.storage_manager.read_json()
        
        if not memory_data:
            return f"No memories found for this session."
        
        # Process legacy format (UUIDs as keys)
        legacy_matches = []
        for key, value in memory_data.items():
            if isinstance(value, dict) and 'theme' in value and 'message' in value:
                theme = str(value.get('theme', '')).lower()
                if any(tag.lower() in theme for tag in tags):
                    legacy_matches.append(value)
        
        if legacy_matches:
            results = []
            for memory in legacy_matches:
                results.append(f"• {memory['message']} (Theme: {memory['theme']})")
            
            return f"Found {len(legacy_matches)} memories matching tags {', '.join(tags)}:\n" + "\n".join(results)
        
        return f"No memories found matching tags: {', '.join(tags)}"
            
    def retrieve_memories_by_importance(self, min_importance=4, max_importance=5, user_guid=None):
        """Retrieve memories within a specified importance range"""
        if user_guid:
            self.storage_manager.set_memory_context(user_guid)
            
        memory_data = self.storage_manager.read_json()
        
        if not memory_data:
            return "No important memories found for this session."
        
        # For legacy format, we don't have importance ratings
        # So we'll just return all memories sorted by date
        legacy_memories = []
        for key, value in memory_data.items():
            if isinstance(value, dict) and 'message' in value and 'theme' in value:
                legacy_memories.append(value)
        
        if legacy_memories:
            # Sort by date if available
            try:
                legacy_memories.sort(
                    key=lambda x: (x.get('date', ''), x.get('time', '')),
                    reverse=True
                )
            except:
                pass  # If sorting fails, just use the order we found them
            
            results = []
            for memory in legacy_memories[:5]:  # Limit to most recent 5 as proxy for importance
                date_str = f", Date: {memory.get('date', 'Unknown')}" if memory.get('date') else ""
                results.append(f"• {memory['message']} (Theme: {memory['theme']}{date_str})")
            
            return f"Most recent memories:\n" + "\n".join(results)
        
        return f"No memories found."
    
    def retrieve_recent_memories(self, limit=5, user_guid=None):
        """Retrieve the most recently created memories"""
        if user_guid:
            self.storage_manager.set_memory_context(user_guid)
            
        memory_data = self.storage_manager.read_json()
        
        # Check if we have any memories
        has_memories = any(isinstance(key, str) and isinstance(memory_data[key], dict) 
                       for key in memory_data.keys() if memory_data.get(key))
        
        if not has_memories:
            return "No recent memories found for this session."
        
        # Process legacy memories
        legacy_memories = []
        for key, value in memory_data.items():
            if isinstance(value, dict) and 'date' in value and 'time' in value and 'message' in value:
                legacy_memories.append(value)
        
        # Sort by date and time
        legacy_memories.sort(
            key=lambda x: (x.get('date', ''), x.get('time', '')),
            reverse=True
        )
        
        # Take only what we need to reach the limit
        recent_legacy = legacy_memories[:limit]
        
        # Format results
        results = []
        for memory in recent_legacy:
            results.append(f"• {memory['message']} (Theme: {memory['theme']}, Date: {memory['date']})")
        
        if not results:
            return "No recent memories found."
            
        return f"Recent memories:\n" + "\n".join(results)
            
    def retrieve_all_memories(self, user_guid=None):
        """Retrieve all memories"""
        if user_guid:
            self.storage_manager.set_memory_context(user_guid)
            
        memory_data = self.storage_manager.read_json()
        
        # Check if we have any memories
        has_memories = len(memory_data) > 0
        
        if not has_memories:
            return "No memories found for this session."
        
        # Process legacy memories
        legacy_memories = []
        for key, value in memory_data.items():
            if isinstance(value, dict) and 'message' in value and 'theme' in value:
                legacy_memories.append(value)
        
        if legacy_memories:
            # Sort by date if available, otherwise just list them
            try:
                legacy_memories.sort(
                    key=lambda x: (x.get('date', ''), x.get('time', '')),
                    reverse=True
                )
            except:
                pass  # If sorting fails, just use the order we found them
            
            results = []
            for memory in legacy_memories:
                date_str = f", Date: {memory.get('date', 'Unknown')}" if memory.get('date') else ""
                results.append(f"• {memory['message']} (Theme: {memory['theme']}{date_str})")
        
        if not legacy_memories:
            return "No memories found for this session."
        
        total_count = len(legacy_memories)
        return f"All memories ({total_count}):\n" + "\n".join(results)