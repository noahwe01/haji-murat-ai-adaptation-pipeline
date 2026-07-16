"""Entry point für HM — lädt KI-Adapter-Framework aus Mono-Repo-Wurzel.

Post Phase J (Mono-Repo-Migration): Framework lebt am KI-Adapter-Repo-Root,
nicht mehr als Submodul. Wurzel ist ../.. relativ zu diesem File.
Config-Loader liest aus cwd/config/projekt.yaml, state_store aus cwd/state/ —
daher chdir auf dieses Projekt-Verzeichnis vor dem Framework-Import.
"""
import os
import sys
from pathlib import Path

project_dir = Path(__file__).resolve().parent
framework_root = project_dir.parent.parent  # KI-Adapter/

if not (framework_root / "main.py").exists():
    print(f"Framework missing at {framework_root}", file=sys.stderr)
    sys.exit(1)

os.chdir(project_dir)
sys.path.insert(0, str(framework_root))

from main import main  # noqa: E402

if __name__ == "__main__":
    main()
