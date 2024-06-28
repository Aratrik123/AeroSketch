let valueDisplays = document.querySelectorAll(".num");
let interval = 5000;

valueDisplays.forEach((valueDisplay) => {
  let startValue = 0;
  let endValue = parseInt(valueDisplay.getAttribute("data-val"));
  console.log(endValue);
  let duration = Math.floor(interval / endValue);
  let counter = setInterval(function () {
    startValue += 1;
    valueDisplay.textContent = startValue;
    if (startValue == endValue) {
      clearInterval(counter);
    }
  }, duration);
});





// Initialize EmailJS with your user ID
(function () {
  emailjs.init("X-Geqx5tgRNS_FihE"); // Replace 'YOUR_USER_ID' with your actual EmailJS user ID
})();

document
  .getElementById("contact-form")
  .addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Get form values
    const email = event.target.user_email.value;
    const name = event.target.user_name.value;
    const message = event.target.user_message.value;

    // Send the email using EmailJS
    emailjs
      .send("service_jn4vxim", "template_3gb4xsx", {
        user_email: email,
        user_name: name,
        user_message: message,
      })
      .then(
        function (response) {
          console.log("SUCCESS!", response.status, response.text);
          alert("Message sent successfully!");
        },
        function (error) {
          console.error("FAILED...", error);
          alert("Message failed to send.");
        }
      );

    // Optionally, reset the form after submission
    event.target.reset();
  });

const filled = document.querySelector(".filled");
function update() {
  filled.style.width = `${
    (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100
  }%`;
  requestAnimationFrame(update);
}
update();
const navbar = document.getElementById("navbar");
window.onscroll = function () {
  scrollFunction();
};
function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    navbar.classList.add("active");
  } else {
    navbar.classList.remove("active");
  }
}

// Get the button
var scrollTopBtn = document.getElementById("scrollTopBtn");

// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function () {
  scrollFunction();
};

function scrollFunction() {
  if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
    scrollTopBtn.style.display = "block";
  } else {
    scrollTopBtn.style.display = "none";
  }
}

// When the user clicks on the button, scroll to the top of the document
scrollTopBtn.onclick = function () {
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const scrollrevealOption = {
  distance: "50px",
  origin: "bottom",
  duration: 1000,
};

ScrollReveal().reveal(".home h1", scrollrevealOption);
ScrollReveal().reveal(".home h4", {
  ...scrollrevealOption,
  delay: 500,
});
ScrollReveal().reveal(".home .btn-explore", {
  ...scrollrevealOption,
  delay: 2000,
});

ScrollReveal().reveal(".about .about-title", scrollrevealOption);
ScrollReveal().reveal(".about .about-desc", {
  ...scrollrevealOption,
  delay: 600,
});
ScrollReveal().reveal(".about .item-data", {
  ...scrollrevealOption,
  delay: 800,
});
ScrollReveal().reveal(".btn-explore", {
  ...scrollrevealOption,
  delay: 1000,
});
ScrollReveal().reveal(".btn-more", {
  ...scrollrevealOption,
  delay: 2000,
});
ScrollReveal().reveal(".card", scrollrevealOption);

ScrollReveal().reveal(".card .image", {
  ...scrollrevealOption,
  delay: 600,
});
ScrollReveal().reveal(".card .content-card h4", {
  ...scrollrevealOption,
  delay: 1000,
});
ScrollReveal().reveal(".next .card .content-card  p", {
  ...scrollrevealOption,
  delay: 1000,
});

ScrollReveal().reveal(".next .card .content-card p", {
  ...scrollrevealOption,
  delay: 500,
});

ScrollReveal().reveal("form .input", scrollrevealOption);
ScrollReveal().reveal("row .card", scrollrevealOption);
