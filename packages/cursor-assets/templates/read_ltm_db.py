import sys
import os

# Add the utils directory to the Python path to allow for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
utils_path = os.path.abspath(os.path.join(script_dir, '../../.super-prompt/utils'))
if utils_path not in sys.path:
    sys.path.insert(0, utils_path)

try:
    from fallback_memory import MemoryController
except ImportError as e:
    print(f"Error importing MemoryController: {e}")
    print("Please ensure that the .super-prompt/utils directory is in your PYTHONPATH.")
    sys.exit(1)

def read_memory():
    """
    Initializes the MemoryController and prints the context block.
    """
    try:
        # The project root is determined by the MemoryController itself.
        memory_controller = MemoryController()
        context_block = memory_controller.build_context_block()
        
        print("--- LTM DB Context ---")
        print(context_block)
        print("--------------------")
        
    except Exception as e:
        print(f"An error occurred while reading from ltm.db: {e}")

if __name__ == "__main__":
    read_memory()
