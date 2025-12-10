/**
 * Translation Module
 * Handles language selection and translation of page content using Gemini API
 */

// Translation configuration
const TRANSLATION_CONFIG = {
    // API endpoints - Backend developer should implement these endpoints
    API_ENDPOINT: '/api/translate',
    LANGUAGES_ENDPOINT: '/api/languages', // New endpoint to fetch available languages

    // Default language
    DEFAULT_LANGUAGE: 'en',

    // Storage key for language preference
    STORAGE_KEY: 'selectedLanguage',

    // Default language mappings (fallback if API fails)
    DEFAULT_LANGUAGES: {
        'en': { name: 'English', flag: '🇬🇧' },
        'es': { name: 'Spanish', flag: '🇪🇸' },
        'fr': { name: 'French', flag: '🇫🇷' },
        'de': { name: 'German', flag: '🇩🇪' },
        'hi': { name: 'Hindi', flag: '🇮🇳' },
        'zh': { name: 'Chinese', flag: '🇨🇳' },
        'ja': { name: 'Japanese', flag: '🇯🇵' },
        'ar': { name: 'Arabic', flag: '🇸🇦' }
    }
};

// Available languages (will be populated from API)
let availableLanguages = { ...TRANSLATION_CONFIG.DEFAULT_LANGUAGES };

// Original text storage for translation
const originalTexts = new Map();

// Current selected language
let currentLanguage = TRANSLATION_CONFIG.DEFAULT_LANGUAGE;

/**
 * Initialize the translation module
 */
async function initTranslation() {
    // Fetch available languages from API
    await fetchAvailableLanguages();

    // Populate language dropdown with available languages
    populateLanguageDropdown();

    // Load saved language preference
    const savedLanguage = localStorage.getItem(TRANSLATION_CONFIG.STORAGE_KEY);
    if (savedLanguage && availableLanguages[savedLanguage]) {
        currentLanguage = savedLanguage;
    }

    // Store original texts
    storeOriginalTexts();

    // Setup event listeners
    setupEventListeners();

    // Mark current language as selected
    updateSelectedLanguage();

    // If saved language is not English, translate the page
    if (currentLanguage !== TRANSLATION_CONFIG.DEFAULT_LANGUAGE) {
        translatePage(currentLanguage);
    }
}

/**
 * Fetch available languages from the backend API
 */
async function fetchAvailableLanguages() {
    try {
        const response = await fetch(TRANSLATION_CONFIG.LANGUAGES_ENDPOINT);

        if (response.ok) {
            const data = await response.json();

            // Expected format: { languages: { 'en': { name: 'English', flag: '🇬🇧' }, ... } }
            if (data.languages && typeof data.languages === 'object') {
                availableLanguages = data.languages;
                console.log('Loaded available languages from API:', Object.keys(availableLanguages));
            } else {
                console.warn('Invalid language data format, using defaults');
            }
        } else {
            console.warn('Failed to fetch languages from API, using defaults');
        }
    } catch (error) {
        console.warn('Error fetching available languages, using defaults:', error);
        // Will use DEFAULT_LANGUAGES as fallback
    }
}

/**
 * Populate the language dropdown with available languages
 */
function populateLanguageDropdown() {
    const dropdown = document.getElementById('languageDropdown');
    if (!dropdown) {
        console.error('Language dropdown element not found');
        return;
    }

    // Clear existing options
    dropdown.innerHTML = '';

    // Add language options dynamically
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
 * Store original text content for all translatable elements
 */
function storeOriginalTexts() {
    // Store text content elements
    const textElements = document.querySelectorAll('[data-translate]');
    textElements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (!originalTexts.has(key)) {
            originalTexts.set(key, element.textContent.trim());
        }
    });

    // Store placeholder text
    const placeholderElements = document.querySelectorAll('[data-translate-placeholder]');
    placeholderElements.forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (!originalTexts.has(key)) {
            originalTexts.set(key, element.placeholder);
        }
    });
}

/**
 * Setup event listeners for language selector
 */
function setupEventListeners() {
    const languageBtn = document.getElementById('languageBtn');
    const languageDropdown = document.getElementById('languageDropdown');
    const languageOptions = document.querySelectorAll('.language-option');

    // Toggle dropdown
    languageBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        languageBtn.classList.toggle('active');
        languageDropdown.classList.toggle('active');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.language-selector-container')) {
            languageBtn.classList.remove('active');
            languageDropdown.classList.remove('active');
        }
    });

    // Handle language selection
    languageOptions.forEach(option => {
        option.addEventListener('click', () => {
            const selectedLang = option.getAttribute('data-lang');
            if (selectedLang !== currentLanguage) {
                selectLanguage(selectedLang);
            }
            // Close dropdown
            languageBtn.classList.remove('active');
            languageDropdown.classList.remove('active');
        });
    });
}

/**
 * Update the selected language indicator in the dropdown
 */
function updateSelectedLanguage() {
    const languageOptions = document.querySelectorAll('.language-option');
    languageOptions.forEach(option => {
        const lang = option.getAttribute('data-lang');
        if (lang === currentLanguage) {
            option.classList.add('selected');
        } else {
            option.classList.remove('selected');
        }
    });
}

/**
 * Select a new language and translate the page
 * @param {string} language - Language code (e.g., 'es', 'fr')
 */
function selectLanguage(language) {
    if (!availableLanguages[language]) {
        console.error('Unsupported language:', language);
        return;
    }

    currentLanguage = language;
    localStorage.setItem(TRANSLATION_CONFIG.STORAGE_KEY, language);
    updateSelectedLanguage();

    // If English, restore original texts
    if (language === TRANSLATION_CONFIG.DEFAULT_LANGUAGE) {
        restoreOriginalTexts();
    } else {
        translatePage(language);
    }
}

/**
 * Restore original English texts
 */
function restoreOriginalTexts() {
    // Restore text content
    const textElements = document.querySelectorAll('[data-translate]');
    textElements.forEach(element => {
        const key = element.getAttribute('data-translate');
        if (originalTexts.has(key)) {
            element.textContent = originalTexts.get(key);
        }
    });

    // Restore placeholders
    const placeholderElements = document.querySelectorAll('[data-translate-placeholder]');
    placeholderElements.forEach(element => {
        const key = element.getAttribute('data-translate-placeholder');
        if (originalTexts.has(key)) {
            element.placeholder = originalTexts.get(key);
        }
    });
}

/**
 * Translate the entire page to the selected language
 * @param {string} targetLanguage - Target language code
 */
async function translatePage(targetLanguage) {
    try {
        // Show loading state
        document.body.classList.add('translating');

        // Collect all texts to translate
        const textsToTranslate = [];
        const textKeys = [];

        originalTexts.forEach((text, key) => {
            textsToTranslate.push(text);
            textKeys.push(key);
        });

        // Call translation API
        const translations = await callTranslationAPI(textsToTranslate, targetLanguage);

        // Update DOM with translations
        updatePageWithTranslations(translations, textKeys);

        // Remove loading state
        document.body.classList.remove('translating');

    } catch (error) {
        console.error('Translation error:', error);
        document.body.classList.remove('translating');

        // Show error message to user
        showTranslationError(error);
    }
}

/**
 * Call the translation API
 * @param {Array<string>} texts - Array of texts to translate
 * @param {string} targetLanguage - Target language code
 * @returns {Promise<Array<string>>} - Array of translated texts
 */
async function callTranslationAPI(texts, targetLanguage) {
    /**
     * BACKEND DEVELOPER: Implement this endpoint
     * 
     * Endpoint: POST /api/translate
     * 
     * Request Body:
     * {
     *   "texts": ["Text 1", "Text 2", ...],
     *   "targetLanguage": "es"  // ISO 639-1 language code
     * }
     * 
     * Response:
     * {
     *   "translations": ["Translated text 1", "Translated text 2", ...],
     *   "targetLanguage": "es"
     * }
     * 
     * The translations array should be in the same order as the input texts array.
     * 
     * Use Gemini API for translation with a prompt like:
     * "Translate the following texts to {targetLanguage}. Return only the translations in the same order, separated by newlines."
     */

    const response = await fetch(TRANSLATION_CONFIG.API_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            texts: texts,
            targetLanguage: targetLanguage
        })
    });

    if (!response.ok) {
        throw new Error(`Translation API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();

    if (!data.translations || !Array.isArray(data.translations)) {
        throw new Error('Invalid response format from translation API');
    }

    if (data.translations.length !== texts.length) {
        throw new Error('Translation count mismatch');
    }

    return data.translations;
}

/**
 * Update the page with translated texts
 * @param {Array<string>} translations - Array of translated texts
 * @param {Array<string>} keys - Array of element keys
 */
function updatePageWithTranslations(translations, keys) {
    translations.forEach((translation, index) => {
        const key = keys[index];

        // Update text content elements
        const textElement = document.querySelector(`[data-translate="${key}"]`);
        if (textElement) {
            textElement.textContent = translation;
        }

        // Update placeholder elements
        const placeholderElement = document.querySelector(`[data-translate-placeholder="${key}"]`);
        if (placeholderElement) {
            placeholderElement.placeholder = translation;
        }
    });
}

/**
 * Show translation error message to user
 * @param {Error} error - The error object
 */
function showTranslationError(error) {
    // Create a simple error notification
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: #e74c3c;
        color: white;
        padding: 16px 20px;
        border-radius: 8px;
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        font-family: 'Martel Sans', sans-serif;
        max-width: 300px;
    `;
    errorDiv.textContent = 'Translation failed. Please try again later.';

    document.body.appendChild(errorDiv);

    // Remove error message after 5 seconds
    setTimeout(() => {
        errorDiv.remove();
    }, 5000);

    // Restore original language
    currentLanguage = TRANSLATION_CONFIG.DEFAULT_LANGUAGE;
    localStorage.setItem(TRANSLATION_CONFIG.STORAGE_KEY, currentLanguage);
    updateSelectedLanguage();
    restoreOriginalTexts();
}

// Initialize translation when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTranslation);
} else {
    initTranslation();
}
