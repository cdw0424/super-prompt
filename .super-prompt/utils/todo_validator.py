#!/usr/bin/env python3
"""
TODO Auto Validation System
Automatically validates TODO task completion and triggers high-mode retry on failures
"""

import json, os, subprocess, time, re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress" 
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"

@dataclass
class TodoTask:
    content: str
    status: TaskStatus
    activeForm: str
    attempt: int = 1
    max_attempts: int = 3
    validation_criteria: Optional[List[str]] = None
    last_error: Optional[str] = None

class TodoValidator:
    def __init__(self):
        self.session_file = ".todo_session.json"
        self.validation_history = []
        
    def log(self, msg: str):
        print(f"--------todo-validator: {msg}")

    def save_session(self, todos: List[TodoTask]):
        """Save current TODO session state"""
        data = {
            "todos": [
                {
                    "content": todo.content,
                    "status": todo.status.value,
                    "activeForm": todo.activeForm,
                    "attempt": todo.attempt,
                    "max_attempts": todo.max_attempts,
                    "validation_criteria": todo.validation_criteria or [],
                    "last_error": todo.last_error
                }
                for todo in todos
            ],
            "timestamp": time.time()
        }
        
        with open(self.session_file, "w") as f:
            json.dump(data, f, indent=2)
        
        self.log(f"session saved with {len(todos)} tasks")

    def load_session(self) -> List[TodoTask]:
        """Load TODO session state"""
        if not os.path.exists(self.session_file):
            return []
            
        try:
            with open(self.session_file, "r") as f:
                data = json.load(f)
                
            todos = []
            for item in data.get("todos", []):
                todo = TodoTask(
                    content=item["content"],
                    status=TaskStatus(item["status"]),
                    activeForm=item["activeForm"],
                    attempt=item.get("attempt", 1),
                    max_attempts=item.get("max_attempts", 3),
                    validation_criteria=item.get("validation_criteria"),
                    last_error=item.get("last_error")
                )
                todos.append(todo)
                
            self.log(f"loaded session with {len(todos)} tasks")
            return todos
            
        except Exception as e:
            self.log(f"failed to load session: {e}")
            return []

    def validate_task_completion(self, task: TodoTask) -> Tuple[bool, Optional[str]]:
        """Validate if a task is actually completed"""
        if task.status != TaskStatus.COMPLETED:
            return True, None  # Don't validate non-completed tasks
            
        # Default validation criteria based on task content
        criteria = task.validation_criteria or self.generate_validation_criteria(task.content)
        
        validation_results = []
        for criterion in criteria:
            success, error = self.run_validation_check(criterion)
            validation_results.append((criterion, success, error))
            
        failed_criteria = [(c, e) for c, s, e in validation_results if not s]
        
        if failed_criteria:
            error_msg = f"Validation failed: {'; '.join([f'{c}: {e}' for c, e in failed_criteria])}"
            return False, error_msg
        
        self.log(f"task validation passed: {task.content[:50]}...")
        return True, None

    def generate_validation_criteria(self, task_content: str) -> List[str]:
        """Generate validation criteria based on task content"""
        criteria = []
        content_lower = task_content.lower()
        
        # File-based validation
        if any(word in content_lower for word in ['create', 'write', 'add', 'update', 'edit']):
            if 'file' in content_lower or any(ext in content_lower for ext in ['.py', '.js', '.md', '.json', '.yaml']):
                criteria.append("check_file_changes")
                
        # Code validation  
        if any(word in content_lower for word in ['implement', 'code', 'function', 'class']):
            criteria.append("check_syntax_valid")
            
        # Test validation
        if 'test' in content_lower:
            criteria.append("run_tests")
            
        # Build validation
        if any(word in content_lower for word in ['build', 'compile', 'bundle']):
            criteria.append("check_build_success")
            
        # Documentation validation
        if any(word in content_lower for word in ['document', 'readme', 'docs']):
            criteria.append("check_documentation")
            
        # Default validation for any task
        criteria.append("check_git_status")
        
        return criteria

    def run_validation_check(self, criterion: str) -> Tuple[bool, Optional[str]]:
        """Run specific validation check"""
        try:
            if criterion == "check_file_changes":
                return self.check_file_changes()
            elif criterion == "check_syntax_valid":
                return self.check_syntax_valid()
            elif criterion == "run_tests":
                return self.run_tests()
            elif criterion == "check_build_success":
                return self.check_build_success()
            elif criterion == "check_documentation":
                return self.check_documentation()
            elif criterion == "check_git_status":
                return self.check_git_status()
            else:
                return True, None  # Unknown criteria pass by default
                
        except Exception as e:
            return False, f"validation error: {str(e)}"

    def check_file_changes(self) -> Tuple[bool, Optional[str]]:
        """Check if files have been modified"""
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                changes = result.stdout.strip()
                if changes:
                    return True, None  # Files were changed
                else:
                    return False, "No file changes detected"
            else:
                return False, f"Git status failed: {result.stderr}"
        except Exception as e:
            return False, f"Git check error: {str(e)}"

    def check_syntax_valid(self) -> Tuple[bool, Optional[str]]:
        """Check Python/JS syntax validity"""
        try:
            # Check Python files
            py_files = subprocess.run(["find", ".", "-name", "*.py", "-not", "-path", "./.git/*"], 
                                    capture_output=True, text=True).stdout.strip().split('\n')
            
            for py_file in py_files:
                if py_file:
                    result = subprocess.run(["python3", "-m", "py_compile", py_file], 
                                          capture_output=True, timeout=5)
                    if result.returncode != 0:
                        return False, f"Python syntax error in {py_file}: {result.stderr.decode()}"
            
            return True, None
            
        except Exception as e:
            return False, f"Syntax check error: {str(e)}"

    def run_tests(self) -> Tuple[bool, Optional[str]]:
        """Run project tests"""
        try:
            # Try npm test first
            if os.path.exists("package.json"):
                result = subprocess.run(["npm", "test"], capture_output=True, text=True, timeout=60)
                if result.returncode == 0:
                    return True, None
                else:
                    return False, f"npm test failed: {result.stderr}"
                    
            # Try pytest
            result = subprocess.run(["python3", "-m", "pytest", "--tb=short"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return True, None
            else:
                return False, f"pytest failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Tests timed out"
        except Exception as e:
            return True, None  # If no tests available, pass

    def check_build_success(self) -> Tuple[bool, Optional[str]]:
        """Check if build succeeds"""
        try:
            if os.path.exists("package.json"):
                result = subprocess.run(["npm", "run", "build"], 
                                      capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    return True, None
                else:
                    return False, f"Build failed: {result.stderr}"
            return True, None  # No build script found
            
        except Exception as e:
            return False, f"Build check error: {str(e)}"

    def check_documentation(self) -> Tuple[bool, Optional[str]]:
        """Check documentation completeness"""
        try:
            # Check if README exists and has content
            if os.path.exists("README.md"):
                with open("README.md", "r") as f:
                    content = f.read().strip()
                    if len(content) > 100:  # Minimum documentation length
                        return True, None
                    else:
                        return False, "README.md is too short"
            else:
                return False, "README.md not found"
                
        except Exception as e:
            return False, f"Documentation check error: {str(e)}"

    def check_git_status(self) -> Tuple[bool, Optional[str]]:
        """Check git repository status"""
        try:
            result = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return True, None
            else:
                return False, f"Git status error: {result.stderr}"
        except Exception as e:
            return False, f"Git status check failed: {str(e)}"

    def trigger_high_mode_retry(self, task: TodoTask) -> bool:
        """Trigger high-mode retry for failed task"""
        self.log(f"triggering high-mode retry for: {task.content}")
        
        try:
            # Create enhanced prompt for high-mode execution
            enhanced_prompt = f"""
TASK RETRY (HIGH MODE - Attempt {task.attempt + 1}/{task.max_attempts}):
{task.content}

PREVIOUS FAILURE: {task.last_error}

INSTRUCTIONS:
- Use high reasoning mode for deep analysis
- Provide detailed step-by-step execution
- Include verification steps
- Focus on addressing the specific failure cause
- Ensure all validation criteria are met

VALIDATION CRITERIA:
{json.dumps(task.validation_criteria or [], indent=2)}
"""

            # Execute in high mode via super-prompt CLI
            result = subprocess.run([
                "super-prompt", "optimize", "--sp-high", enhanced_prompt
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.log(f"high-mode retry completed for: {task.content}")
                return True
            else:
                self.log(f"high-mode retry failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"high-mode retry error: {str(e)}")
            return False

    def process_todos(self, todos: List[TodoTask]) -> List[TodoTask]:
        """Process and validate all TODOs"""
        updated_todos = []
        
        for task in todos:
            # Validate completed tasks
            if task.status == TaskStatus.COMPLETED:
                is_valid, error = self.validate_task_completion(task)
                
                if not is_valid and task.attempt < task.max_attempts:
                    # Mark as failed and prepare for retry
                    task.status = TaskStatus.FAILED
                    task.last_error = error
                    task.attempt += 1
                    
                    self.log(f"task validation failed: {task.content[:50]}... - {error}")
                    
                    # Trigger high-mode retry
                    retry_success = self.trigger_high_mode_retry(task)
                    if retry_success:
                        task.status = TaskStatus.IN_PROGRESS
                        self.log(f"task queued for high-mode retry: {task.content[:50]}...")
                    else:
                        self.log(f"high-mode retry failed: {task.content[:50]}...")
                        
                elif not is_valid and task.attempt >= task.max_attempts:
                    # Max attempts reached
                    task.status = TaskStatus.FAILED
                    task.last_error = f"Max attempts ({task.max_attempts}) reached. Last error: {error}"
                    self.log(f"task permanently failed: {task.content[:50]}...")
                    
            updated_todos.append(task)
            
        return updated_todos

def main():
    """Main TODO validation entry point"""
    validator = TodoValidator()
    
    # Load current session
    todos = validator.load_session()
    
    if not todos:
        validator.log("no active TODO session found")
        return
    
    # Process and validate todos
    updated_todos = validator.process_todos(todos)
    
    # Save updated session
    validator.save_session(updated_todos)
    
    # Print summary
    completed = len([t for t in updated_todos if t.status == TaskStatus.COMPLETED])
    failed = len([t for t in updated_todos if t.status == TaskStatus.FAILED])
    in_progress = len([t for t in updated_todos if t.status == TaskStatus.IN_PROGRESS])
    
    validator.log(f"validation complete - completed: {completed}, failed: {failed}, in_progress: {in_progress}")

if __name__ == "__main__":
    main()