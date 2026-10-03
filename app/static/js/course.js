const price = document.getElementById("price");
const priceshow = document.getElementById("priceshow");
const courses = document.getElementsByClassName('courseName');
const containers = document.getElementsByClassName('result-container');
const modalForm = document.getElementById("modal-form");
const result = document.getElementById("result");
const BASE_URL = "http://127.0.0.1:5000/course/";

function showPriceValue() {
    priceshow.value = "Price : ₹" + price.value
}

function closeBtn() {
    modalForm.style = `
        opacity: 0;
        pointer-events: none;
        transform: translate(-50%, -50%);
        transition: transform 0.2s linear, opacity 0.2s linear;
    `
}

function handleCourseChange(e) {
    if(e.target.checked) {
        const course_type = e.target.value;
        result.innerHTML = `
        <div id="loader-container">
                <div id="loader"></div>
            </div>
        `
        fetch(BASE_URL+`${course_type}`)
        .then(res=>res.json())
        .then((data)=>{
            if(data.message === "faliure") {
                result.innerHTML = "<h2  style='text-align: center;'>No Course Available Right Now.</h2>"
            } else {
                result.innerHTML = ''
                const courses = data.courses
                courses.forEach((course)=>{
                    result.innerHTML += `
                        <div class="result-container" id=${course.id}-${course.id}>
                            <div class="result-container-image"
                                style="background-image: url(${course.thumbnail});
                            ">
                            </div>
                            <div class="result-info">
                                <h4>${course.course_name}</h4>
                                <button onclick="showForm(event)" id=${course.id}>Apply</button>
                            </div>
                        </div>
                    `
                });
            }
        })
        .catch((err)=>{
            console.log(err);
        })
    }
}

function showForm(e) {
    modalForm.style = `
    opacity: 1;
    transform: translate(-50%, 0%);
    pointer-events: visible;
    `
    modalForm.setAttribute("data-courseID", e.target.id);
}

function applyForCourse(e) {
    const name = document.getElementById("name");
    const courseID = modalForm.getAttribute("data-courseID");
    console.log(courseID)
    fetch(BASE_URL+"enroll", {
        method: "POST",
        headers: {
            "Content-Type": "Application/json"
        },
        body: JSON.stringify({
            "username" : name.value,
            "course_id" : courseID
        })
    })
    .then(res=>res.json())
    .then((data)=>{
        if(data.message === "success") {
            const btn = document.getElementById(courseID);
            btn.innerText = "Applied"
            btn.style = `
                background-color: green;
            `
            btn.disabled = true;
            setTimeout(() => {
                const myCourseDiv = document.getElementById(`${courseID}-${courseID}`);
                myCourseDiv.style.display = "none";
            }, 1500);
        } else {
            btn.innerText = "Try Again"
        }
    })
    .catch((err)=>{
        console.error(err);
    })
    modalForm.removeAttribute("data-coureID");
    closeBtn();
}

function handleCourseSearch(e) {
    const searchQuery = document.getElementById("search-query");
    if(searchQuery.value.trim()) {
        result.innerHTML = `
        <div id="loader-container">
                <div id="loader"></div>
            </div>
        `
        fetch(BASE_URL+`search/${searchQuery.value}`)
        .then(res=>res.json())
        .then((data)=>{
            if(data.message === "success") {
                result.innerHTML = ''
                const courses = data.courses
                courses.forEach((course)=>{
                    result.innerHTML += `
                        <div class="result-container" id=${course.id}-${course.id}>
                            <div class="result-container-image"
                                style="background-image: url(${course.thumbnail});
                            ">
                            </div>
                            <div class="result-info">
                                <h4>${course.course_name}</h4>
                                <button onclick="showForm(event)" id=${course.id}>Apply</button>
                            </div>
                        </div>
                    `
                });
            } else {
                result.innerHTML = "<h2  style='text-align: center;'>Course Either Not Present or You already access it.</h2>"
            }
        })
        .catch((err)=>{
            console.error(err);
        })
    }
}