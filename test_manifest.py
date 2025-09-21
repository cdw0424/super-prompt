#!/usr/bin/env python3
import yaml
from pathlib import Path

def test_manifest():
    manifest_path = Path('personas/manifest.yaml')
    print(f'Manifest path: {manifest_path.absolute()}')
    print(f'Exists: {manifest_path.exists()}')

    if manifest_path.exists():
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = yaml.safe_load(f)

        personas = manifest.get('personas', {})
        print(f'Loaded {len(personas)} personas')
        print(f'First 5 personas: {list(personas.keys())[:5]}')

        # Check analyzer
        if 'analyzer' in personas:
            analyzer = personas['analyzer']
            print(f'Analyzer has model_overrides: {"model_overrides" in analyzer}')
            if 'model_overrides' in analyzer:
                overrides = analyzer['model_overrides']
                grok_guidance = overrides.get('grok', {}).get('guidance', '')
                gpt_guidance = overrides.get('gpt', {}).get('guidance', '')
                print(f'Analyzer grok guidance length: {len(grok_guidance)}')
                print(f'Analyzer gpt guidance length: {len(gpt_guidance)}')
                print(f'Grok guidance preview: {grok_guidance[:100]}...')

if __name__ == '__main__':
    test_manifest()
