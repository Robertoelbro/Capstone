from pathlib import Path
notice=Path('frontend/public/third-party-notices.txt')
notice.parent.mkdir(exist_ok=True)
notice.write_text('country-flag-icons\n\n'+Path('frontend/node_modules/country-flag-icons/LICENSE').read_text(encoding='utf-8'),encoding='utf-8')
