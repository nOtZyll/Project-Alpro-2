// Fade in when scrolling into section 
window.addEventListener("scroll", () => {
    const reveals = document.querySelectorAll(".feature-item, .testimonial");
  
    reveals.forEach((item) => {
      const windowHeight = window.innerHeight;
      const elementTop = item.getBoundingClientRect().top;
      const elementVisible = 150;
      
      // Add class to apply animation when item is in view
      if (elementTop < windowHeight - elementVisible) {
        item.classList.add("active");
      }
    });
  });
  
  // CSS Class for animation
  document.addEventListener("DOMContentLoaded", () => {
    const style = document.createElement('style');
    document.head.appendChild(style);
  
    style.sheet.insertRule(`
      .feature-item,
      .testimonial {
        opacity: 0;
        transform: translateY(20px);
        transition: 0.6s ease-in-out;
      }
    `);
  
    style.sheet.insertRule(`
      .feature-item.active,
      .testimonial.active {
        opacity: 1;
        transform: translateY(0);
      }
    `);
  });

/* script.js */
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
  
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('show-element');
        }
      });
    });
  
    animatedElements.forEach(element => observer.observe(element));
  });