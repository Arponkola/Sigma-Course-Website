const name1 = document.getElementById("name");
const email = document.getElementById("email");
const message  = document.getElementById("message");
const submitButton = document.getElementById("submit-btn");
const BASE_URL = "/contact"

function handleContactUs(e) {
    e.preventDefault();
    const n = name1.value.trim();
    const e1 = email.value.trim();
    const m = message.value.trim();

    if(!n || !e1 || !m) {
        return;
    }

    const form = new FormData();
    form.append("name", n);
    form.append("email", e1);
    form.append("message", m);
    submitButton.innerText = "Processing..."
    submitButton.disabled = true;
    fetch(BASE_URL+"/submit", {
        method: "POST",
        body: form
    })
    .then(res=>res.json())
    .then((data)=>{
        if(data.status === "success")  {
            submitButton.innerText = "Submitted"
            submitButton.disabled = false;
        }
    })
    .catch((err)=>{
        console.error(err);
    })
    submitButton.innerText = "Submit"
    submitButton.disabled = false;
}