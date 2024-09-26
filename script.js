/* script.js */
document.addEventListener('DOMContentLoaded', () => {
  const links = document.querySelectorAll('.nav-links a');
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  // Function to handle scroll animation
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('show-element');
      } else {
        entry.target.classList.remove('show-element'); // Remove class when not in view
      }
    });
  });

  // Observe each animated element
  animatedElements.forEach(el => observer.observe(el));

  // Handle navigation clicks
  links.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault(); // Prevent default anchor click behavior

      const targetId = e.target.getAttribute('href'); // Fetch the target section’s ID
      const targetSection = document.querySelector(targetId);

      // Scroll to the target section with smooth behavior
      window.scrollTo({
        top: targetSection.offsetTop,
        behavior: 'smooth'
      });

      // Reset animation classes
      animatedElements.forEach(el => {
        el.classList.remove('show-element'); // Remove any visible classes before scrolling
      });

      // Timeout to ensure the animation restarts when elements come into view
      setTimeout(() => {
        targetSection.classList.add('show-element'); // Re-add class to animate when back in view
      }, 100);
    });
  });
});