// Saves options to chrome.storage
const saveOptions = () => {
    const key = document.getElementById('key').value;

    chrome.storage.local.set({ 'OPENAI_API_KEY': key }, () => {
        console.log("setting key", key);
        const status = document.getElementById('status');
        status.textContent = 'Options saved.';
        setTimeout(() => {
            status.textContent = '';
        }, 750);
    });
};

// Restores select box and checkbox state using the preferences
// stored in chrome.storage.
const restoreOptions = () => {
    chrome.storage.local.get('OPENAI_API_KEY', (key) => {
        // if empty object
        if (Object.keys(key).length === 0) {
            key = { 'OPENAI_API_KEY': '' };
        }
        document.getElementById('key').value = key.OPENAI_API_KEY;
    });
};

document.addEventListener('DOMContentLoaded', restoreOptions);
document.getElementById('save').addEventListener('click', saveOptions);