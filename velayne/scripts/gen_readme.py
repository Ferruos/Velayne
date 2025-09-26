import sys
import importlib
import pkg_resources
import inspect
import os
import re
from pathlib import Path

def get_version(pkg):
    try:
        return pkg_resources.get_distribution(pkg).version
    except Exception:
        return "?"

def get_bot_commands():
    cmds = []
    try:
        from velayne.bot import user, admin

        for router in [user.router, admin.router]:
            for handler in getattr(router, "handlers", []):
                cmd = getattr(handler, "commands", None)
                if cmd:
                    cmds.append(cmd)
    except Exception:
        pass
    return cmds

def get_strategies():
    from velayne.core.strategies import REGISTRY
    return list(REGISTRY.keys())

def get_published_strategies():
    try:
        from velayne.infra.db import SessionLocal, list_published_strategies
        session = SessionLocal()
        return [p.code for p in list_published_strategies(session)]
    except Exception:
        return []

def get_env_vars():
    from velayne.infra.config import Settings
    return [f for f in Settings.__annotations__]

def get_ml_features():
    from velayne.core.ml import extract_features
    return list(extract_features({"BTC": {"close": [100, 100]}}, {}, {}).keys())

def get_docs_sections():
    docs = Path("docs")
    files = sorted(f for f in docs.glob("offer_*.md") if f.is_file())
    faq = sorted(f for f in docs.glob("faq_*.md") if f.is_file())
    dsl = docs / "dsl_guide.md"
    out = []
    for f in files + faq + ([dsl] if dsl.exists() else []):
        out.append((f.name, f.read_text(encoding="utf-8")))
    return out

def main():
    print("# Velayne\n")
    print("## Версии библиотек\n")
    for pkg in [
        "aiogram", "pydantic", "pydantic-settings", "onnx", "onnxruntime",
        "skl2onnx", "scikit-learn", "pandas", "pyarrow", "sqlalchemy", "aiosqlite",
        "ccxt", "feedparser", "APScheduler", "tenacity", "cryptography", "loguru"
    ]:
        print(f"- {pkg}: {get_version(pkg)}")
    print("\n## Доступные команды бота\n")
    try:
        import velayne.bot.user as user
        import velayne.bot.admin as admin
        cmd_re = re.compile(r"@router\.(?:message|callback_query)\((?:Command\()?['\"]([^'\"]+)['\"]")
        for fname in [user.__file__, admin.__file__]:
            with open(fname, encoding="utf-8") as f:
                for line in f:
                    m = cmd_re.search(line)
                    if m:
                        print(f"- /{m.group(1)}")
    except Exception:
        print("- (не удалось получить команды)")
    print("\n## Стратегии\n")
    for strat in get_strategies():
        print(f"- {strat}")
    pubs = get_published_strategies()
    if pubs:
        print("\n## Опубликованные стратегии DSL\n")
        for code in pubs:
            print(f"- {code}")
    print("\n## .env переменные\n")
    for var in get_env_vars():
        print(f"- {var}")
    print("\n## ML/News/Retention/Diagnostics\n")
    print("ML-фичи:", ", ".join(get_ml_features()))
    print("\nRetention — политики в .env, диагностика через /admin и selftest.")
    print("\n## Документация\n")
    for name, content in get_docs_sections():
        print(f"### {name}\n")
        print(content)
        print("\n---\n")

if __name__ == "__main__":
    main()