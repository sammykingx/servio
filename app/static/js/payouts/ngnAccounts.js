/**
 * Advanced SOLID Payout Architecture with Clean Native AJAX JSON Submission
 */

class NgnApiService {
    constructor(endpoints = {}) {
        this.banksUrl = endpoints.banksUrl || '/ngn-banks/';
        this.verifyUrl = endpoints.verifyUrl || '/verify-bank-account/';
        this.submitUrl = endpoints.submitUrl || '';
    }

    async getBanks() {
        return this._request(this.banksUrl);
    }

    async verifyAccount(bankCode, accountNumber) {
        const query = new URLSearchParams({ bank_code: bankCode, account_number: accountNumber });
        return this._request(`${this.verifyUrl}?${query.toString()}`);
    }

    async submitPayoutPayload(payload, csrfToken) {
        return this._request(this.submitUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(payload)
        });
    }

    async _request(url, options = {}) {
        const response = await fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'application/json',
                ...options.headers
            },
            ...options
        });
        if (!response.ok) throw new Error(`API Error: ${response.statusText}`);
        return response.json();
    }
}

class BankSelectorUI {
    constructor(selectElement) { this.selectElement = selectElement; }
    populate(banks) {
        if (!this.selectElement) return;
        this.selectElement.innerHTML = '<option value="">Choose your bank...</option>';
        const fragment = document.createDocumentFragment();
        banks
            .filter(bank => bank.active && !bank.is_deleted)
            .sort((a, b) => a.name.localeCompare(b.name))
            .forEach(bank => {
                const option = document.createElement('option');
                option.value = bank.code;
                option.textContent = bank.name;
                fragment.appendChild(option);
            });
        this.selectElement.appendChild(fragment);
    }
}

class FormSubmitterUI {
    constructor(formContentWrapper, submitButton) {
        this.contentWrapper = formContentWrapper;
        this.submitButton = submitButton;
    }

    setProcessingState(isProcessing) {
        if (!this.contentWrapper || !this.submitButton) return;
        
        if (isProcessing) {
            this.contentWrapper.classList.add('blur-sm', 'pointer-events-none', 'opacity-60');
            this.submitButton.disabled = true;
            // Store original text content to restore it cleanly later
            this.submitButton.dataset.originalText = this.submitButton.innerHTML;
            this.submitButton.innerHTML = `
                <span>Saving Changes...</span>
                <svg class="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
            `;
        } else {
            this.contentWrapper.classList.remove('blur-sm', 'pointer-events-none', 'opacity-60');
            this.submitButton.disabled = false;
            if (this.submitButton.dataset.originalText) {
                this.submitButton.innerHTML = this.submitButton.dataset.originalText;
            }
        }
    }
}

class AlpineAdapter {
    static updateState(element, namespace, properties) {
        if (window.Alpine && element) {
            const dataState = Alpine.$data(element);
            if (dataState && dataState[namespace]) {
                Object.assign(dataState[namespace], properties);
            }
        }
    }
}

class PayoutManager {
    constructor(config = {}) {
        this.api = new NgnApiService(config.endpoints);
        this.selectors = config.selectors || {
            form: '#payout-settings-form',
            bankSelect: 'select[name="ngn_bank_code"]',
            bankNameHidden: '#ngn_bank_name',
            accountInput: 'input[name="ngn_account"]',
            submitButton: '#payout-submit-btn'
        };

        this.elements = {};
        this.ui = null;
        this.formUI = null;

        document.readyState === 'loading'
            ? document.addEventListener('DOMContentLoaded', () => this.boot())
            : this.boot();
    }

    async boot() {
        this.elements.form = document.querySelector(this.selectors.form);
        this.elements.bankSelect = document.querySelector(this.selectors.bankSelect);
        this.elements.bankNameHidden = document.querySelector(this.selectors.bankNameHidden);
        this.elements.accountInput = document.querySelector(this.selectors.accountInput);
        this.elements.submitButton = document.querySelector(this.selectors.submitButton);

        if (!this.elements.form || !this.elements.bankSelect || !this.elements.accountInput) return;

        this.ui = new BankSelectorUI(this.elements.bankSelect);

        // Target Alpine's structural reference for the content wrapper block
        if (window.Alpine) {
            const alpineComponent = Alpine.$data(this.elements.form);
            const contentRef = alpineComponent.$refs.formContent;
            this.formUI = new FormSubmitterUI(contentRef, this.elements.submitButton);
        }

        this.initListeners();
        await this.loadBankList();
    }

    initListeners() {
        const triggerVerification = () => this.executeVerificationLoop();

        this.elements.bankSelect.addEventListener('change', () => {
            this.syncBankNameHiddenField();
            triggerVerification();
        });
        this.elements.accountInput.addEventListener('input', triggerVerification);

        // Native Form Ajax Interceptor
        this.elements.form.addEventListener('submit', (e) => this.handleAjaxSubmit(e));
    }

    syncBankNameHiddenField() {
        const selectedOption = this.elements.bankSelect.options[this.elements.bankSelect.selectedIndex];
        this.elements.bankNameHidden.value = selectedOption ? selectedOption.textContent : '';
    }

    async loadBankList() {
        try {
            const banks = await this.api.getBanks();
            this.ui.populate(banks);
        } catch (error) {
            this.dispatchToast('Could not load lookup directory.', 'error');
        }
    }

    async executeVerificationLoop() {
        const bankCode = this.elements.bankSelect.value;
        const accountNumber = this.elements.accountInput.value.trim();

        if (accountNumber.length !== 10 || !bankCode) {
            this.syncUI({ account_name: '', error: '' });
            return;
        }

        this.syncUI({ account_name: 'Verifying details...', error: '', isVerifying: true });

        try {
            const data = await this.api.verifyAccount(bankCode, accountNumber);
            if (data?.account_name) {
                this.syncUI({ account_name: data.account_name, error: '', isVerifying: false });
            } else {
                this.handleFailure('Could not resolve account name.');
            }
        } catch (error) {
            this.handleFailure('Verification failed. Check account code.');
        }
    }

    async handleAjaxSubmit(event) {
        if (!window.Alpine) return;

        const dataState = Alpine.$data(this.elements.form);
        const activeCurrency = dataState.payoutMethod;

        // CRITICAL GATEWAY: If this is NOT an NGN payout, bypass completely!
        // This lets your CAD and USD tabs use HTMX or standard actions normally.
        if (activeCurrency !== 'ngn') {
            return; 
        }

        // From here on, we are explicitly processing NGN routing configurations
        event.preventDefault(); 
        event.stopImmediatePropagation();

        const { bank_code, account, account_name, error, isVerifying } = dataState.ngn;
        if (!bank_code || account.length !== 10 || !account_name || error || isVerifying) {
            this.dispatchToast('Please resolve and verify NGN account settings before saving.', 'error');
            return;
        }

        const payload = {
            currency: activeCurrency,
            bank_name: this.elements.bankNameHidden.value,
            bank_code: bank_code,
            account_number: account,
            account_name: account_name
        };

        const csrfToken = this.elements.form.querySelector('[name=csrfmiddlewaretoken]').value;

        // Engage visually processing states (Blur form dynamic layout content wrapper)
        if (this.formUI) this.formUI.setProcessingState(true);

        try {
            const response = await this.api.submitPayoutPayload(payload, csrfToken);
            this.dispatchToast('Payout configuration modified successfully.', 'success');

            if (dataState.activeTab) dataState.activeTab = 'overview';

        } catch (error) {
            this.dispatchToast('Failed to save payment destination rules.', 'error');
        } finally {
            // Restore input areas visibility and control tracking completely
            if (this.formUI) this.formUI.setProcessingState(false);
        }
    }

    handleFailure(msg) {
        this.syncUI({ account_name: '', error: msg, isVerifying: false });
        this.dispatchToast(msg, 'error');
    }

    syncUI(stateChanges) {
        AlpineAdapter.updateState(this.elements.accountInput, 'ngn', stateChanges);
    }

    dispatchToast(message, type = 'error') {
        const toast = window.showToast || Alpine.$data(this.elements.accountInput)?.showToast;
        if (typeof toast === 'function') {
            toast(message, type, type.toUpperCase());
        }
    }
}