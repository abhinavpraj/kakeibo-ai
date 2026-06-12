## [unreleased]

### 🚀 Features

- Make Quick Expense reflection and Quick Income custom source render dynamically

### 🐛 Bug Fixes

- Avoid KeyError by formatting and filtering columns before renaming
- Resolve StreamlitDuplicateElementId by adding unique keys to date_inputs and submit buttons
- Resolve StreamlitAPIException when clearing inputs by deferring state reset to script start

### 💼 Other

- CI and pre-commit files

### 🎨 Styling

- Align donut chart text horizontally for better readability
## [0.2.0] - 2026-06-11

### 🚀 Features

- *(i18n)* Fix NameError in app.py and complete translations for en, hi, mr, and te
- Add Total Monthly Income metric and localizations
- Add month selection controls in header for dashboard stats
- Implement month-specific goal isolation and auto-default form input dates
- Use linear extrapolation for projected savings and clarify remaining spend budget label
- Log transaction times in Indian Standard Time (IST)

### 🐛 Bug Fixes

- History table appearance
- Calculate Budget Left and AI insights using Total Monthly Income
- Reload database module on import to prevent Streamlit hot-reload cache error

### 💼 Other

- Add income feature
- Edit UI feature

### 📚 Documentation

- Add AGPLv3 license
- Add installation usage and contributing sections

### ⚙️ Miscellaneous Tasks

- Add bandit security scanning
- Improve compliance and code quality
## [0.1.0] - 2026-06-10

### 🚀 Features

- Initialize KakeiboAI project

### 📚 Documentation

- Update KakeiboAI spec, plan and tasks

### ⚙️ Miscellaneous Tasks

- Rename spec feature directory
- Rename spec directory to 001-kakeiboai
