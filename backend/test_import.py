#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test imports for the backend application"""

import sys
import traceback

# Test imports
try:
    print("Testing imports...")

    from app.config import settings
    print(f"1. Config OK - database_url: {settings.database_url[:20]}...")

    from app.database import get_db, init_db
    print("2. Database module OK")

    from app.models.models import User, Material, Subtitle, VideoInterpretation
    print("3. Models OK")

    from app.schemas.schemas import (
        PronunciationEvaluateRequest,
        PronunciationEvaluateResponse
    )
    print("4. Schemas OK")

    from app.services.deepseek import evaluate_pronunciation, translate_subtitles, generate_interpretation
    print("5. DeepSeek service OK")

    from app.routers import auth, materials, learning, favorites
    print("6. Routers OK")

    print("\nAll imports successful!")

except Exception as e:
    print(f"\nImport FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)
