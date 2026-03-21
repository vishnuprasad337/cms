let currentBooking = {};

/* FILTER */
function normalize(str){
    return str.toLowerCase().replace(/\s+/g,'');
}

function filterType(type,btn){
    document.querySelectorAll("tbody tr").forEach(row=>{
        let rt = row.dataset.roomType;
        row.style.display = (type==="all" || normalize(rt)===normalize(type)) ? "" : "none";
    });

    document.querySelectorAll(".filter-btn").forEach(b=>b.classList.remove("active"));
    btn.classList.add("active");
}

/* MODALS */
function openCheckoutModal(id,source,name,extra){
    currentBooking={id,source};
    document.getElementById("checkoutModal").style.display="flex";
    document.getElementById("checkoutText").innerText =
        `${name} | Extra: ₹${extra}`;
}

function openCancelModal(id,source,name){
    currentBooking={id,source};
    document.getElementById("cancelModal").style.display="flex";
    document.getElementById("cancelText").innerText =
        `Cancel booking for ${name}?`;
}

function closeModal(){
    document.querySelectorAll(".modal").forEach(m=>m.style.display="none");
}

/* ACTIONS */
function checkoutGuest() {
    const roomNumber = document.getElementById("m_room").innerText;
    const guestName = document.getElementById("m_name").innerText;

    fetch("/checkout-guest/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken // pass dynamically from template if needed
        },
        body: JSON.stringify({
            room_number: roomNumber,
            guest_name: guestName
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert("Booking Cancelled Successfully!");
            location.reload(); 
        } else {
            alert(data.message);
        }
    });
}

function confirmCancel(){
    fetch("/cancel-booking/",{
        method:"POST",
        headers:{
            "Content-Type":"application/json",
            "X-CSRFToken": csrfToken
        },
        body:JSON.stringify(currentBooking)
    })
    .then(r=>r.json())
    .then(d=>{
        if(d.status==="success"){
            location.reload();
        } else alert(d.message);
    });
}