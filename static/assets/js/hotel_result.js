// Open/Close modals
function showModal(id) {
    const modal = document.getElementById(id);
    if(modal) modal.style.display = "flex";
}

function closeModal(id) {
    const modal = document.getElementById(id);
    if(modal) modal.style.display = "none";
}

// Close modal on background click
window.onclick = function(event) {
    if(event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
};