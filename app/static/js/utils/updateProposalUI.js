function updateProposalUI(summary) {
    const mappings = {
        'summary-subtotal': summary.subtotal,
        'summary-fee': summary.serviceFee,
        'summary-total': summary.total
    };

    const countEl = document.getElementById('summary-count');
    if (countEl) countEl.textContent = summary.count;

    const format = (val) => new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(val);

    // DRY loop to update all currency fields
    Object.entries(mappings).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = format(value);
    });


}