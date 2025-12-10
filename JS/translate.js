/**
 * Translation Module
 * Handles language selection and translation of page content
 */

// Translation configuration
const TRANSLATION_CONFIG = {
    API_ENDPOINT: CONFIG.API_BASE_URL + '/translate',
    DEFAULT_LANGUAGE: 'en',
    STORAGE_KEY: 'selectedLanguage',

    // Indian languages supported by both Whisper STT and Indic Parler TTS
    DEFAULT_LANGUAGES: {
        'en': { name: 'English', flag: '🇬🇧' },
        'hi': { name: 'हिंदी (Hindi)', flag: '🇮🇳' },
        'bn': { name: 'বাংলা (Bengali)', flag: '🇮🇳' },
        'ta': { name: 'தமிழ் (Tamil)', flag: '🇮🇳' },
        'te': { name: 'తెలుగు (Telugu)', flag: '🇮🇳' },
        'mr': { name: 'मराठी (Marathi)', flag: '🇮🇳' },
        'gu': { name: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
        'kn': { name: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
        'ml': { name: 'മലയാളം (Malayalam)', flag: '🇮🇳' },
        'pa': { name: 'ਪੰਜਾਬੀ (Punjabi)', flag: '🇮🇳' },
        'or': { name: 'ଓଡ଼ିଆ (Odia)', flag: '🇮🇳' }
    }
};

let availableLanguages = { ...TRANSLATION_CONFIG.DEFAULT_LANGUAGES };
const originalTexts = new Map();
let currentLanguage = TRANSLATION_CONFIG.DEFAULT_LANGUAGE;

/**
 * Initialize translation module
 */
async function initTranslation() {
    populateLanguageDropdown();

    const savedLanguage = localStorage.getItem(TRANSLATION_CONFIG.STORAGE_KEY);
    if (savedLanguage && availableLanguages[savedLanguage]) {
        currentLanguage = savedLanguage;
    }

    storeOriginalTexts();
    setupTranslationEventListeners();
    updateSelectedLanguage();

    if (currentLanguage !== TRANSLATION_CONFIG.DEFAULT_LANGUAGE) {
        translatePage(currentLanguage);
    }
}

/**
 * Populate language dropdown
 */
function populateLanguageDropdown() {
    const dropdown = document.getElementById('languageDropdown');
    if (!dropdown) return;

    dropdown.innerHTML = '';

    Object.entries(availableLanguages).forEach(([code, info]) => {
        const option = document.createElement('div');
        option.className = 'language-option';
        option.setAttribute('data-lang', code);

        const flag = document.createElement('span');
        flag.className = 'lang-flag';
        flag.textContent = info.flag || '🌐';

        const name = document.createElement('span');
        name.className = 'lang-name';
        name.textContent = info.name || code.toUpperCase();

        option.appendChild(flag);
        option.appendChild(name);
        dropdown.appendChild(option);
    });
}

/**
 * Store original texts for translation
 */
function storeOriginalTexts() {
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (!originalTexts.has(key)) {
            originalTexts.set(key, element.textContent.trim());
        }
    });

    document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (!originalTexts.has(key)) {
            originalTexts.set(key, element.placeholder);
        }
    });
}

/**
 * Setup event listeners
 */
function setupTranslationEventListeners() {
    const languageBtn = document.getElementById('languageBtn');
    const languageDropdown = document.getElementById('languageDropdown');

    if (!languageBtn || !languageDropdown) return;

    languageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        languageBtn.classList.toggle('active');
        languageDropdown.classList.toggle('active');
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.language-selector-container')) {
            languageBtn.classList.remove('active');
            languageDropdown.classList.remove('active');
        }
    });

    document.querySelectorAll('.language-option').forEach(option => {
        option.addEventListener('click', () => {
            const selectedLang = option.getAttribute('data-lang');
            if (selectedLang !== currentLanguage) {
                selectLanguage(selectedLang);
            }
            languageBtn.classList.remove('active');
            languageDropdown.classList.remove('active');
        });
    });
}

/**
 * Update selected language indicator
 */
function updateSelectedLanguage() {
    document.querySelectorAll('.language-option').forEach(option => {
        const lang = option.getAttribute('data-lang');
        if (lang === currentLanguage) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

/**
 * Select a language
 */
function selectLanguage(language) {
    if (!availableLanguages[language]) return;

    currentLanguage = language;
    localStorage.setItem(TRANSLATION_CONFIG.STORAGE_KEY, language);
    updateSelectedLanguage();

    if (language === TRANSLATION_CONFIG.DEFAULT_LANGUAGE) {
        restoreOriginalTexts();
    } else {
        translatePage(language);
    }
}

/**
 * Restore original texts
 */
function restoreOriginalTexts() {
    document.querySelectorAll('[data-translate]').forEach(element => {
        const key = element.getAttribute('data-translate');
        if (originalTexts.has(key)) {
            element.textContent = originalTexts.get(key);
        }
    });

    document.querySelectorAll('[data-translate-placeholder]').forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (originalTexts.has(key)) {
            element.placeholder = originalTexts.get(key);
        }
    });
}

/**
 * Translate page
 */
async function translatePage(targetLanguage) {
    try {
        document.body.classList.add('translating');

        const textsToTranslate = [];
        const textKeys = [];

        originalTexts.forEach((text, key) => {
            textsToTranslate.push(text);
            textKeys.push(key);
        });

        const translations = await callTranslationAPI(textsToTranslate, targetLanguage);
        updatePageWithTranslations(translations, textKeys);

        document.body.classList.remove('translating');
    } catch (error) {
        console.error('Translation error:', error);
        document.body.classList.remove('translating');
        showTranslationError(error);
    }
}

/**
 * Call translation API
 */
async function callTranslationAPI(texts, targetLanguage) {
    const translations = [];

    for (const text of texts) {
        try {
            const data = await translateText(text, targetLanguage);
            translations.push(data.translated_text);
        } catch (error) {
            console.error('Translation error for text:', text, error);
            translations.push(text);
        }
    }

    return translations;
}

/**
 * Update page with translations
 */
function updatePageWithTranslations(translations, keys) {
    translations.forEach((translation, index) => {
        const key = keys[index];

        const textElement = document.querySelector(`[data-translate="${key}"]`);
        if (textElement) {
            textElement.textContent = translation;
        }

        const placeholderElement = document.querySelector(`[data-translate-placeholder="${key}"]`);
        if (placeholderElement) {
            placeholderElement.placeholder = translation;
        }
    });
}

/**
 * Show translation error
 */
function showTranslationError(error) {
    currentLanguage = TRANSLATION_CONFIG.DEFAULT_LANGUAGE;
    localStorage.setItem(TRANSLATION_CONFIG.STORAGE_KEY, currentLanguage);
    updateSelectedLanguage();
    restoreOriginalTexts();
}

// Initialize when DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTranslation);
} else {
    initTranslation();
}
