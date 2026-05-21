import { ProposalState } from "../payload.js";


export class Step4DeliverablesManager {
    constructor() {
        this.state = ProposalState;
        this.container = document.getElementById('deliverables-roles-container');
        this.activeAccordionRoleId = null;
    }

    init() {
        this.registerGlobalStepListener();
    }

    /**
     * Intercepts coordinator step updates to build state components reactively
     */
    registerGlobalStepListener() {
        document.addEventListener('stepChanged', (e) => {
            if (e.detail && e.detail.step === 4) {
                this.normalizeStateStructures();
                this.renderDeliverableAccordions();
            }
        });
    }

    /**
     * Guarantees all active roles have an initialized deliverables collection array
     */
    normalizeStateStructures() {
        if (!this.state.applied_roles) return;
        this.state.applied_roles.forEach(role => {
            if (!role.deliverables) {
                role.deliverables = [];
            }
        });
    }

    /**
     * Renders high-end interactive accordion sheets for every active assignment role.
     * This runs once when stepping into Step 4.
     */
    renderDeliverableAccordions() {
        if (!this.container) return;
        this.container.innerHTML = '';

        if (!this.state.applied_roles || this.state.applied_roles.length === 0) {
            this.container.innerHTML = `
                <div class="text-center py-12 border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-3xl p-8 max-w-md mx-auto">
                    <span class="text-sm font-medium text-gray-900 dark:text-white block">No active tracks found</span>
                    <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Please return to Step 2 to select execution tracks.</p>
                </div>`;
            return;
        }

        this.state.applied_roles.forEach((role, idx) => {
            if (this.activeAccordionRoleId === null && idx === 0) {
                this.activeAccordionRoleId = role.niche_id;
            }

            const isOpen = this.activeAccordionRoleId === role.niche_id;
            const accordionNode = document.createElement('div');
            accordionNode.className = "border border-gray-200 dark:border-gray-800 rounded-2xl bg-white dark:bg-gray-900 overflow-hidden transition-all duration-300 shadow-xs";
            accordionNode.id = `deliverable-accordion-${role.niche_id}`;

            accordionNode.innerHTML = `
                <button type="button" 
                        class="w-full px-5 py-4 flex items-center justify-between text-left bg-gray-50/50 dark:bg-gray-950/20 hover:bg-gray-50 dark:hover:bg-gray-950/40 transition-colors focus:outline-none"
                        data-toggle-role-id="${role.niche_id}">
                    <div class="min-w-0">
                        <span class="text-[10px] tracking-wider font-bold uppercase text-brand-500 dark:text-brand-400 block">Deliverables Milestone Log</span>
                        <h4 class="text-sm font-semibold text-gray-900 dark:text-white truncate mt-0.5">${role.niche_name}</h4>
                    </div>
                    <div class="flex items-center gap-3">
                        <span id="pct-badge-${role.niche_id}" class="text-[11px] font-mono px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 transition-all font-semibold">0% / 100%</span>
                        <svg class="h-4 w-4 transform transition-transform duration-300 text-gray-400 ${isOpen ? 'rotate-180' : ''}" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                        </svg>
                    </div>
                </button>

                <div id="drawer-${role.niche_id}" class="transition-all duration-300 ${isOpen ? 'block' : 'hidden'} border-t border-gray-100 dark:border-gray-800/60 p-5 space-y-4">
                    <div id="deliverables-scroll-area-${role.niche_id}" class="max-h-[380px] overflow-y-auto space-y-4 pr-1 scrollbar-thin scrollbar-thumb-gray-200 dark:scrollbar-thumb-gray-800">
                    </div>

                    <button type="button"
                            id="btn-add-deliverable-${role.niche_id}"
                            class="w-full py-3 border border-dashed border-gray-300 dark:border-gray-700 hover:border-brand-500 dark:hover:border-brand-500 rounded-xl flex items-center justify-center gap-2 text-xs font-semibold text-gray-600 dark:text-gray-400 hover:text-brand-600 dark:hover:text-brand-400 transition-all bg-gray-25 dark:bg-gray-950/40 hover:bg-brand-50/20 dark:hover:bg-brand-950/10">
                        <svg class="h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                        </svg>
                        Append Strategy Deliverable Phase
                    </button>
                </div>
            `;

            this.container.appendChild(accordionNode);

            this.renderDeliverableCards(role.niche_id);
            this.bindAccordionInteractions(role.niche_id);
            this.evaluateAccordionCompletionStatus(role.niche_id);
        });
    }

    /**
     * Iterates and maps existing deliverable state metrics inside an open active track scroll box
     */
    renderDeliverableCards(roleId) {
        const scrollArea = document.getElementById(`deliverables-scroll-area-${roleId}`);
        if (!scrollArea) return;
        scrollArea.innerHTML = '';

        const role = this.state.applied_roles.find(r => r.niche_id === roleId);
        if (!role || role.deliverables.length === 0) {
            scrollArea.innerHTML = `
                <div id="empty-state-${roleId}" class="text-center py-8 border border-dashed border-gray-100 dark:border-gray-800 rounded-xl bg-gray-25/50 dark:bg-gray-950/10">
                    <span class="text-xs text-gray-400 dark:text-gray-500 block">No deliverables assigned to this track yet.</span>
                </div>`;
            return;
        }

        // Always guarantee strict rendering sorted order
        const sortedDeliverables = [...role.deliverables].sort((a, b) => a.rendering_order - b.rendering_order);
        sortedDeliverables.forEach((del) => {
            this.appendSingleDeliverableDOM(scrollArea, roleId, del);
        });
    }

    /**
     * Appends a single deliverable explicitly into the DOM container frame
     */
    appendSingleDeliverableDOM(scrollArea, roleId, del) {
        const card = document.createElement('div');
        card.className = "p-4 border border-gray-200 dark:border-gray-800 bg-gray-25/40 dark:bg-gray-950/20 rounded-xl relative space-y-3 transition-all duration-200";
        card.id = `del-card-${roleId}-${del.rendering_order}`;
        card.setAttribute('data-card-order', del.rendering_order);

        card.innerHTML = `
            <button type="button" 
                    class="btn-del-remove absolute top-3 right-3 text-rose-500/80 dark:text-rose-400/80 hover:text-rose-600 dark:hover:text-rose-500 transition-colors p-1.5 rounded-lg focus:outline-none focus:text-rose-600"
                    data-delete-order="${del.rendering_order}" data-role-id="${roleId}">
                <svg class="h-3.5 w-3.5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
            </button>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div class="sm:col-span-2 space-y-1 pr-6 sm:pr-0">
                    <div class="flex justify-between items-center">
                        <label class="text-[11px] font-semibold text-gray-600 dark:text-gray-400 block">Phase / Title</label>
                        <span id="char-counter-${roleId}-${del.rendering_order}" class="text-[9px] font-mono text-gray-400">${del.phase.length}/70</span>
                    </div>
                    <input type="text" 
                           class="del-input-phase w-full px-3 py-1.5 text-xs bg-white dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-lg focus:outline-none focus:border-brand-500 font-medium placeholder-gray-400"
                           placeholder="e.g., Database Schema & Backend Core Setup"
                           value="${del.phase}"
                           data-order="${del.rendering_order}">
                </div>

                <div class="space-y-1">
                    <label class="text-[11px] font-semibold text-gray-600 dark:text-gray-400 block">Release Allocation (%)</label>
                    <div class="relative rounded-lg">
                        <input type="text" 
                               class="del-input-pct w-full pl-3 pr-6 py-1.5 text-xs bg-white dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-lg focus:outline-none focus:border-brand-500 font-mono text-right"
                               placeholder="0"
                               value="${del.release_percentage || ''}"
                               data-order="${del.rendering_order}">
                        <div class="absolute inset-y-0 right-0 pr-2.5 flex items-center pointer-events-none text-gray-400 text-[10px] font-medium">%</div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                    <label class="text-[11px] font-semibold text-gray-600 dark:text-gray-400 block">Interval</label>
                    <select class="del-select-duration-unit w-full px-2.5 py-1.5 text-xs bg-white dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-lg focus:outline-none focus:border-brand-500 appearance-none cursor-pointer"
                            data-order="${del.rendering_order}"
                            style="background-image: url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 fill=%22none%22 viewBox=%220 0 20 20%22%3E%3Cpath stroke=%22%239ca3af%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22 stroke-width=%221.5%22 d=%22m6 8 4 4 4-4%22/%3E%3C/svg%3E'); background-position: right 0.4rem center; background-repeat: no-repeat; background-size: 1rem;">
                        <option value="days" ${del.duration_unit === 'days' ? 'selected' : ''}>Days</option>
                        <option value="weeks" ${del.duration_unit === 'weeks' ? 'selected' : ''}>Weeks</option>
                        <option value="months" ${del.duration_unit === 'months' ? 'selected' : ''}>Months</option>
                    </select>
                </div>

                <div class="space-y-1">
                    <label class="text-[11px] font-semibold text-gray-600 dark:text-gray-400 block">Duration</label>
                    <select class="del-select-duration-val w-full px-2.5 py-1.5 text-xs bg-white dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-lg focus:outline-none focus:border-brand-500 appearance-none cursor-pointer"
                            data-order="${del.rendering_order}"
                            style="background-image: url('data:image/svg+xml;charset=utf-8,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 fill=%22none%22 viewBox=%220 0 20 20%22%3E%3Cpath stroke=%22%239ca3af%22 stroke-linecap=%22round%22 stroke-linejoin=%22round%22 stroke-width=%221.5%22 d=%22m6 8 4 4 4-4%22/%3E%3C/svg%3E'); background-position: right 0.4rem center; background-repeat: no-repeat; background-size: 1rem;">
                        ${this.generateDurationOptionsHtml(del.duration_unit, del.duration_value)}
                    </select>
                </div>
            </div>

            <div class="space-y-1">
                <label class="text-[11px] font-semibold text-gray-600 dark:text-gray-400 block">Specification Description Scope</label>
                <textarea class="del-input-desc w-full px-3 py-2 text-xs bg-white dark:bg-gray-950 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-800 rounded-lg focus:outline-none focus:border-brand-500 resize-none h-16 placeholder-gray-400 leading-normal"
                          placeholder="Describe the objective deliverables included within this structural lifecycle phase..."
                          data-order="${del.rendering_order}">${del.description}</textarea>
            </div>
        `;
        scrollArea.appendChild(card);
    }

    /**
     * Binds handlers using clean event delegation to safely handle interactive mutations
     */
    bindAccordionInteractions(roleId) {
        const accordionContainer = document.getElementById(`deliverable-accordion-${roleId}`);
        if (!accordionContainer) return;

        const toggleBtn = accordionContainer.querySelector(`[data-toggle-role-id="${roleId}"]`);
        toggleBtn?.addEventListener('click', () => {
            const drawer = document.getElementById(`drawer-${roleId}`);
            const arrowSvg = toggleBtn.querySelector('svg');

            if (drawer) {
                const currentlyHidden = drawer.classList.contains('hidden');
                if (currentlyHidden) {
                    drawer.classList.remove('hidden');
                    drawer.classList.add('block');
                    arrowSvg?.classList.add('rotate-180');
                    this.activeAccordionRoleId = roleId;
                } else {
                    drawer.classList.remove('block');
                    drawer.classList.add('hidden');
                    arrowSvg?.classList.remove('rotate-180');
                    if (this.activeAccordionRoleId === roleId) this.activeAccordionRoleId = null;
                }
            }
        });

        const addBtn = document.getElementById(`btn-add-deliverable-${roleId}`);
        addBtn?.addEventListener('click', () => {
            const role = this.state.applied_roles.find(r => r.niche_id === roleId);
            if (!role) return;

            const scrollArea = document.getElementById(`deliverables-scroll-area-${roleId}`);
            const emptyState = document.getElementById(`empty-state-${roleId}`);
            if (emptyState) emptyState.remove();

            const nextOrderIndex = role.deliverables.length;
            const newDeliverable = {
                phase: '',
                description: '',
                duration_unit: 'days',
                duration_value: 1,
                release_percentage: 0,
                rendering_order: nextOrderIndex
            };

            role.deliverables.push(newDeliverable);
            // console.log(JSON.stringify(role, null, 2));

            this.appendSingleDeliverableDOM(scrollArea, roleId, newDeliverable);
            this.evaluateAccordionCompletionStatus(roleId);

            if (scrollArea) {
                scrollArea.scrollTop = scrollArea.scrollHeight;
            }
        });

        const scrollArea = document.getElementById(`deliverables-scroll-area-${roleId}`);
        if (!scrollArea) return;

        // Dynamic Field Updates via Input Delegation Pipeline
        scrollArea.addEventListener('input', (e) => {
            const target = e.target;
            const orderIdx = parseInt(target.getAttribute('data-order'), 10);
            if (isNaN(orderIdx)) return;

            const role = this.state.applied_roles.find(r => r.niche_id === roleId);
            if (!role) return;
            const deliverable = role.deliverables.find(d => d.rendering_order === orderIdx);
            if (!deliverable) return;

            if (target.classList.contains('del-input-phase')) {
                let currentText = target.value;
                if (currentText.length > 70) {
                    currentText = currentText.substring(0, 70);
                    target.value = currentText;
                }
                deliverable.phase = currentText;

                const indicator = document.getElementById(`char-counter-${roleId}-${orderIdx}`);
                if (indicator) indicator.textContent = `${currentText.length}/70`;

            } else if (target.classList.contains('del-input-pct')) {
                let sanitizedVal = target.value.replace(/[^0-9]/g, '');
                target.value = sanitizedVal;
                deliverable.release_percentage = parseInt(sanitizedVal, 10) || 0;
                this.evaluateAccordionCompletionStatus(roleId);

            } else if (target.classList.contains('del-input-desc')) {
                deliverable.description = target.value;
            }
        });

        // Dropdown Metric Updates via Change Event Delegation
        scrollArea.addEventListener('change', (e) => {
            const target = e.target;
            const orderIdx = parseInt(target.getAttribute('data-order'), 10);
            if (isNaN(orderIdx)) return;

            const role = this.state.applied_roles.find(r => r.niche_id === roleId);
            if (!role) return;
            const deliverable = role.deliverables.find(d => d.rendering_order === orderIdx);
            if (!deliverable) return;

            if (target.classList.contains('del-select-duration-unit')) {
                deliverable.duration_unit = target.value;
                deliverable.duration_value = 1;

                const matchingValSelect = target.closest('.grid').querySelector('.del-select-duration-val');
                if (matchingValSelect) {
                    matchingValSelect.innerHTML = this.generateDurationOptionsHtml(deliverable.duration_unit, 1);
                }
            } else if (target.classList.contains('del-select-duration-val')) {
                deliverable.duration_value = parseInt(target.value, 10) || 1;
            }
        });

        // Item deletion cleanly using state filtering followed by uniform cards redrawing
        scrollArea.addEventListener('click', (e) => {
            const deleteBtn = e.target.closest('[data-delete-order]');
            if (!deleteBtn) return;

            const orderIdx = parseInt(deleteBtn.getAttribute('data-delete-order'), 10);
            const role = this.state.applied_roles.find(r => r.niche_id === roleId);
            if (!role) return;

            // 1. Remove targeted entity out of state array metrics array loop
            role.deliverables = role.deliverables.filter(d => d.rendering_order !== orderIdx);

            // 2. Clear, normalize and linearly re-index remaining metrics rendering order fields
            role.deliverables.forEach((d, newIdx) => {
                d.rendering_order = newIdx;
            });

            // 3. Redraw view cards to lock clean structure synchronization without broken focus metrics
            this.renderDeliverableCards(roleId);
            this.evaluateAccordionCompletionStatus(roleId);
        });
    }

    /**
     * Generates structured step limit selection lists for duration units
     */
    generateDurationOptionsHtml(unit, currentSelectedValue) {
        let maxLimit = 12;
        if (unit === 'weeks') maxLimit = 6;

        let optionsMarkup = '';
        for (let i = 1; i <= maxLimit; i++) {
            optionsMarkup += `<option value="${i}" ${currentSelectedValue === i ? 'selected' : ''}>${i} ${unit}</option>`;
        }
        return optionsMarkup;
    }

    /**
     * Checks calculation values in real-time, highlighting status headers
     */
    evaluateAccordionCompletionStatus(roleId) {
        const role = this.state.applied_roles.find(r => r.niche_id === roleId);
        const cardHeader = document.getElementById(`deliverable-accordion-${roleId}`);
        const badgeElement = document.getElementById(`pct-badge-${roleId}`);
        if (!role || !cardHeader) return;

        const totalPctSum = role.deliverables.reduce((sum, d) => sum + (d.release_percentage || 0), 0);

        if (badgeElement) {
            badgeElement.textContent = `${totalPctSum}% / 100%`;
        }

        if (totalPctSum === 100) {
            cardHeader.classList.remove('border-gray-200', 'dark:border-gray-800', 'border-rose-500/50');
            cardHeader.classList.add('border-emerald-500', 'dark:border-emerald-500/80');
            if (badgeElement) {
                badgeElement.className = "text-[11px] font-mono px-2 py-0.5 rounded-md bg-emerald-50 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 font-bold";
            }
        } else {
            cardHeader.classList.remove('border-emerald-500', 'dark:border-emerald-500/80');
            cardHeader.classList.add('border-gray-200', 'dark:border-gray-800');
            if (badgeElement) {
                badgeElement.className = "text-[11px] font-mono px-2 py-0.5 rounded-md bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 font-semibold";
            }
        }
    }
}