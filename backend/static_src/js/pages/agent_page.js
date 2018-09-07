// Agent page specific javascript
// -----------------------------

$(document).ready(function () {

    // Testimonial Carousel on Agent page
    function updateTestimonials() {
        if (window.innerWidth < 1024) {
            console.log("Init testimonials owl carousel");
            $("#testimonials-agentpage-carousel").owlCarousel({
                loop: false,
                margin: 10,
                dots: false,
                nav: true,
                responsiveClass: true,
                responsive: {
                    0: {
                        items: 1,
                        nav: true
                    },
                    640: {
                        items: 2,
                        nav: true
                    }
                }
            });
        } else {
            $("#testimonials-agentpage-carousel").trigger('destroy.owl.carousel');
        }

    }
    updateTestimonials();

    $(window).resize(function () {
        updateTestimonials();
    });

});
