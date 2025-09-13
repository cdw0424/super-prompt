#!/usr/bin/env python3
"""
Enhanced Auto-Setup Utility for Super Prompt v3
Upgraded based on persona rules and system architecture improvements
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any


class EnhancedAutoSetup:
    """
    Enhanced auto-setup utility implementing v3 architecture patterns
    """

    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.setup_log = []
        self.detected_features = {}

    def log(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamp and structure"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        self.setup_log.append(log_entry)
        print(f"-------- {log_entry}")

    def detect_project_type(self) -> Dict[str, Any]:
        """Enhanced project detection with v3 architecture awareness"""
        self.log("🔍 Analyzing project architecture...")

        detection_result = {
            "project_type": "unknown",
            "frameworks": [],
            "languages": [],
            "build_tools": [],
            "architecture_patterns": [],
            "complexity_score": 0,
            "recommended_personas": []
        }

        # Check for various project indicators
        project_files = {
            "package.json": {"type": "nodejs", "framework": "node", "complexity": 2},
            "pyproject.toml": {"type": "python", "framework": "python", "complexity": 2},
            "requirements.txt": {"type": "python", "framework": "python", "complexity": 1},
            "Cargo.toml": {"type": "rust", "framework": "rust", "complexity": 3},
            "go.mod": {"type": "go", "framework": "go", "complexity": 2},
            "pom.xml": {"type": "java", "framework": "maven", "complexity": 3},
            "build.gradle": {"type": "java", "framework": "gradle", "complexity": 3},
            "docker-compose.yml": {"type": "containerized", "pattern": "microservices", "complexity": 4},
            "Dockerfile": {"type": "containerized", "pattern": "containerized", "complexity": 3},
            "terraform": {"type": "infrastructure", "pattern": "iac", "complexity": 4},
            ".github/workflows": {"type": "cicd", "pattern": "automation", "complexity": 2}
        }

        for file_pattern, properties in project_files.items():
            if (self.project_root / file_pattern).exists():
                detection_result["complexity_score"] += properties.get("complexity", 1)

                if "type" in properties:
                    detection_result["languages"].append(properties["type"])
                if "framework" in properties:
                    detection_result["frameworks"].append(properties["framework"])
                if "pattern" in properties:
                    detection_result["architecture_patterns"].append(properties["pattern"])

        # Analyze package.json for frontend/backend patterns
        if (self.project_root / "package.json").exists():
            try:
                with open(self.project_root / "package.json", 'r') as f:
                    package_data = json.load(f)

                deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}

                # Frontend framework detection
                frontend_frameworks = ["react", "vue", "angular", "@angular", "svelte", "next", "nuxt", "gatsby"]
                for fw in frontend_frameworks:
                    if any(fw in dep for dep in deps):
                        detection_result["frameworks"].append(fw)
                        detection_result["recommended_personas"].append("frontend")

                # Backend framework detection
                backend_frameworks = ["express", "koa", "fastify", "nest", "apollo"]
                for fw in backend_frameworks:
                    if any(fw in dep for dep in deps):
                        detection_result["frameworks"].append(fw)
                        detection_result["recommended_personas"].append("backend")

                # Testing framework detection
                test_frameworks = ["jest", "mocha", "cypress", "playwright", "@testing-library"]
                if any(any(fw in dep for dep in deps) for fw in test_frameworks):
                    detection_result["recommended_personas"].append("qa")

            except Exception as e:
                self.log(f"Error parsing package.json: {e}", "WARNING")

        # Determine primary project type
        if "nodejs" in detection_result["languages"]:
            detection_result["project_type"] = "nodejs"
        elif "python" in detection_result["languages"]:
            detection_result["project_type"] = "python"
        elif len(detection_result["languages"]) > 0:
            detection_result["project_type"] = detection_result["languages"][0]

        # Add complexity-based persona recommendations
        if detection_result["complexity_score"] >= 5:
            detection_result["recommended_personas"].extend(["architect", "devops"])
        if "microservices" in detection_result["architecture_patterns"]:
            detection_result["recommended_personas"].extend(["architect", "performance", "security"])

        self.detected_features = detection_result
        self.log(f"📊 Project complexity score: {detection_result['complexity_score']}")
        self.log(f"🎯 Recommended personas: {', '.join(set(detection_result['recommended_personas']))}")

        return detection_result

    def setup_enhanced_personas(self) -> bool:
        """Setup enhanced personas based on project analysis"""
        self.log("🎭 Setting up enhanced personas...")

        try:
            # Ensure persona processor is available
            processor_path = self.project_root / ".super-prompt" / "utils" / "cursor-processors" / "enhanced_persona_processor.py"
            if not processor_path.exists():
                self.log("❌ Enhanced persona processor not found", "ERROR")
                return False

            # Generate persona commands
            generator_path = self.project_root / ".super-prompt" / "utils" / "cursor-processors" / "simple_persona_generator.py"
            if generator_path.exists():
                result = subprocess.run([sys.executable, str(generator_path)],
                                      capture_output=True, text=True, cwd=self.project_root)
                if result.returncode == 0:
                    self.log("✅ Enhanced personas generated successfully")
                else:
                    self.log(f"⚠️ Persona generation warning: {result.stderr}", "WARNING")
            else:
                self.log("⚠️ Persona generator not found, personas may need manual setup", "WARNING")

            # Create persona recommendations file
            recommendations = {
                "project_analysis": self.detected_features,
                "recommended_workflow": self.generate_workflow_recommendations(),
                "setup_timestamp": str(Path(__file__).stat().st_mtime),
                "enhanced_features": [
                    "Multi-agent role-playing personas",
                    "Specialized expertise domains",
                    "Adaptive interaction styles",
                    "Goal-oriented behavior patterns",
                    "Quality gates and validation",
                    "Cross-persona collaboration"
                ]
            }

            recommendations_file = self.project_root / ".super-prompt" / "persona_recommendations.json"
            with open(recommendations_file, 'w', encoding='utf-8') as f:
                json.dump(recommendations, f, indent=2)

            self.log("📋 Generated persona recommendations")
            return True

        except Exception as e:
            self.log(f"❌ Error setting up personas: {e}", "ERROR")
            return False

    def generate_workflow_recommendations(self) -> Dict[str, Any]:
        """Generate workflow recommendations based on project analysis"""
        workflow = {
            "primary_personas": list(set(self.detected_features.get("recommended_personas", []))),
            "workflow_patterns": [],
            "collaboration_suggestions": []
        }

        complexity = self.detected_features.get("complexity_score", 0)
        project_type = self.detected_features.get("project_type", "unknown")

        # Workflow patterns based on complexity and type
        if complexity >= 4:
            workflow["workflow_patterns"].append("architect_led_design")
            workflow["workflow_patterns"].append("security_review_required")
            workflow["workflow_patterns"].append("performance_validation")

        if project_type in ["nodejs", "python"]:
            if "frontend" in workflow["primary_personas"] and "backend" in workflow["primary_personas"]:
                workflow["collaboration_suggestions"].append("fullstack_coordination")

        if "microservices" in self.detected_features.get("architecture_patterns", []):
            workflow["collaboration_suggestions"].append("distributed_system_design")
            workflow["workflow_patterns"].append("service_boundary_analysis")

        # Add QA workflow for test-heavy projects
        if "qa" in workflow["primary_personas"]:
            workflow["workflow_patterns"].append("test_driven_development")
            workflow["collaboration_suggestions"].append("quality_gates_integration")

        return workflow

    def create_project_configuration(self) -> bool:
        """Create enhanced project configuration"""
        self.log("⚙️ Creating enhanced project configuration...")

        try:
            config = {
                "super_prompt_version": "3.0.0",
                "setup_type": "enhanced_auto_setup",
                "project_analysis": self.detected_features,
                "persona_system": {
                    "enabled": True,
                    "auto_detection": True,
                    "multi_persona_collaboration": True,
                    "research_based_behaviors": True
                },
                "quality_gates": {
                    "enabled": True,
                    "persona_specific_validation": True,
                    "cross_domain_review": True
                },
                "features": {
                    "enhanced_context_collection": True,
                    "yaml_driven_configuration": True,
                    "adaptive_interaction_styles": True,
                    "goal_oriented_personas": True
                }
            }

            config_file = self.project_root / ".super-prompt" / "config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)

            self.log("✅ Enhanced configuration created")
            return True

        except Exception as e:
            self.log(f"❌ Error creating configuration: {e}", "ERROR")
            return False

    def validate_setup(self) -> bool:
        """Validate the enhanced setup"""
        self.log("🔍 Validating enhanced setup...")

        validation_checks = [
            (".super-prompt/utils/cursor-processors/enhanced_persona_processor.py", "Enhanced persona processor"),
            (".cursor/commands/super-prompt/architect.py", "Architect persona command"),
            (".cursor/commands/super-prompt/README.md", "Persona documentation"),
            (".super-prompt/config.json", "Enhanced configuration"),
            (".super-prompt/persona_recommendations.json", "Persona recommendations")
        ]

        all_valid = True
        for file_path, description in validation_checks:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.log(f"✅ {description}")
            else:
                self.log(f"❌ Missing: {description}", "ERROR")
                all_valid = False

        if all_valid:
            self.log("🎉 Enhanced setup validation passed!")
        else:
            self.log("⚠️ Some validation checks failed", "WARNING")

        return all_valid

    def generate_setup_report(self) -> str:
        """Generate comprehensive setup report"""
        report = f"""
# 🚀 Super Prompt Enhanced Setup Report

## Project Analysis
- **Type**: {self.detected_features.get('project_type', 'unknown')}
- **Complexity Score**: {self.detected_features.get('complexity_score', 0)}/10
- **Languages**: {', '.join(self.detected_features.get('languages', []))}
- **Frameworks**: {', '.join(self.detected_features.get('frameworks', []))}
- **Architecture Patterns**: {', '.join(self.detected_features.get('architecture_patterns', []))}

## Enhanced Personas Setup
- **Research-Based Design**: Multi-agent role-playing strategies implemented
- **Specialized Expertise**: Domain-specific persona behaviors
- **Adaptive Interaction**: Context-aware communication styles
- **Quality Gates**: Built-in validation for each persona domain

## Recommended Personas
{chr(10).join(f'- **{persona}**: Specialized for your project needs' for persona in set(self.detected_features.get('recommended_personas', [])))}

## Next Steps
1. **Test Personas**: Try `/architect`, `/security`, `/performance` commands
2. **Review Configuration**: Check `.super-prompt/config.json`
3. **Read Documentation**: See `.cursor/commands/super-prompt/README.md`
4. **Customize Workflow**: Modify persona recommendations as needed

## Setup Log
{chr(10).join(self.setup_log)}

---
*Enhanced setup based on LLM coding assistant research (2022-2025)*
"""

        report_file = self.project_root / "SUPER_PROMPT_SETUP_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report.strip())

        self.log(f"📊 Setup report generated: {report_file}")
        return str(report_file)

    def run_enhanced_setup(self) -> bool:
        """Run the complete enhanced setup process"""
        self.log("🚀 Starting Super Prompt Enhanced Setup...")

        # Step 1: Detect project characteristics
        project_analysis = self.detect_project_type()

        # Step 2: Setup enhanced personas
        if not self.setup_enhanced_personas():
            self.log("❌ Persona setup failed", "ERROR")
            return False

        # Step 3: Create enhanced configuration
        if not self.create_project_configuration():
            self.log("❌ Configuration creation failed", "ERROR")
            return False

        # Step 4: Validate setup
        validation_passed = self.validate_setup()

        # Step 5: Generate report
        report_path = self.generate_setup_report()

        if validation_passed:
            self.log("🎉 Enhanced setup completed successfully!")
            self.log(f"📊 See report: {report_path}")
            return True
        else:
            self.log("⚠️ Setup completed with warnings", "WARNING")
            return False


def main():
    """Main entry point for enhanced auto-setup"""
    import argparse

    parser = argparse.ArgumentParser(description="Enhanced Auto-Setup for Super Prompt v3")
    parser.add_argument("--project-root", "-p", help="Project root directory (default: current directory)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    setup = EnhancedAutoSetup(args.project_root)

    try:
        success = setup.run_enhanced_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n-------- Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"-------- Setup failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()