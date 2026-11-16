// TechnoVault Client Interaction Script
document.addEventListener('DOMContentLoaded', () => {
    // Copy link helper
    window.copyToClipboard = function(text, btnElement) {
        navigator.clipboard.writeText(text).then(() => {
            const originalHTML = btnElement.innerHTML;
            btnElement.innerHTML = '<i class="fa-solid fa-check text-emerald-400"></i> Copied!';
            setTimeout(() => {
                btnElement.innerHTML = originalHTML;
            }, 2000);
        }).catch(err => {
            console.error('Failed to copy link: ', err);
        });
    };
});
