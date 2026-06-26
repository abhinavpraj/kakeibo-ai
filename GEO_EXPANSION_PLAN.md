# Geographical Expansion Strategy

## Vision

KakeiboAI is designed to support users across different regions using localization and AI. By leveraging scalable web architectures and language translation modules, KakeiboAI aims to democratize mindful personal finance tracking for students and young professionals worldwide, removing linguistic and regional barriers.

---

## Phased Expansion Roadmap

### Phase 1: India (Current Phase)
* **Target Audience**: Students, interns, and young professionals entering the workforce.
* **Languages Supported**: English, Hindi (हिन्दी), Marathi (मराठी), and Telugu (తెలుగు).
* **Currency**: Indian Rupee (INR - ₹).

### Phase 2: South Asia
* **Target Audience**: Students and young professionals in neighboring South Asian countries.
* **Countries**: Nepal, Sri Lanka, and Bangladesh.
* **Linguistic Additions**: Nepali, Sinhala, and Bengali.
* **Feature Support**: Currency localization, regional financial calendars, and local payment integration notes.

### Phase 3: Global Expansion
* **Target Audience**: International students, digital nomads, freelancers, and young professionals.
* **Regions**: North America, Europe, and global markets.
* **Linguistic Additions**: Spanish, French, and German.
* **Feature Support**: Multi-currency budgeting, currency conversion, and foreign exchange tracking (USD, EUR, GBP, etc.).

---

## Localization Strategy

Our localization strategy implements **i18n** (internationalization) and **l10n** (localization) standards to ensure the user interface adjusts seamlessly based on locale preferences:
* **Current Translation Suite**: Configured JSON-based translation dictionaries dynamically fetched at runtime in `i18n.py`.
* **Future Language Support**:
  * **Indic Languages**: Tamil, Kannada, Malayalam, Bengali.
  * **Global Languages**: Spanish, French, German.
* **Cultural Contextualization**: Adapting AI reflection prompts to reflect regional saving habits, local financial terminology, and cultural views on spending.

---

## User Acquisition Strategy

To scale user adoption across regions, KakeiboAI employs a multi-channel growth plan:
* **University Partnerships**: Collaborating with campus student clubs and college administrations to introduce KakeiboAI as a financial literacy tool.
* **Hackathons**: Sponsoring and presenting at college hackathons (e.g., Swecha Hackathons) to engage developer-users.
* **Financial Literacy Workshops**: Organizing free seminars on budgeting fundamentals, debt management, and mindful saving.
* **Social Media Campaigns**: Running visual educational content on TikTok, Instagram, and LinkedIn highlighting budgeting tips.
* **Referral Program**: Encouraging users to invite peers to budget concurrently in exchange for unlocking advanced AI advisor features.
* **Community Ambassadors**: Recruiting campus representatives to champion KakeiboAI and host local user onboarding drives.

---

## AI Expansion

* **Local AI using Ollama**: Offline model support using lightweight open weights (`llama3`).
* **Cloud AI using Gemini BYOK**: Utilizing high-efficiency, multi-modal capabilities via `gemini-1.5-flash` API.
* **Future Model Integrations**: Adding support for alternative local open weights (e.g., Mistral, Phi-3, Gemma) and regional-language finetuned models (e.g., Llama3-Indic) to handle queries in local scripts.

---

## Roadmap

| Phase | Region | Languages | Features |
| :--- | :--- | :--- | :--- |
| **Phase 1** | India | English, Hindi, Marathi, Telugu | Local SQLite database, offline-first dashboard, Ollama & Gemini BYOK integrations. |
| **Phase 2** | South Asia | English, Nepali, Sinhala, Bengali | South Asian currency support (NPR, LKR, BDT), remote cloud feedback synchronization. |
| **Phase 3** | Global | English, Spanish, French, German | Multi-currency conversions (USD, EUR, GBP), OCR receipts scanning, and custom local AI configurations. |
