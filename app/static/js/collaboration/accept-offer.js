async function sendProposal() {
    const deliverablesEl = document.querySelector('[x-ref="deliverablesUnit"]');
    const deliverablesPayload = Alpine.$data(deliverablesEl).buildPayload();

    // const clientPayload = Alpine.$data(document.querySelector('[x-ref="clientUnit"]')).buildPayload();

    // 3. Construct the master payload
    const masterPayload = {
        deliverables: deliverablesPayload,
        // client: clientPayload,
        sent_at: new Date().toISOString()
    };

    console.log("Master Payload ready for Backend:", JSON.stringify(masterPayload, null, 2));

    // await fetch('/api/proposals', { method: 'POST', body: JSON.stringify(masterPayload) });
}