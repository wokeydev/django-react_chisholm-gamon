// Office page specific javascript
// -------------------------------

$(document).ready(function () {

    // Testimonial Carousel on Office page
    function updateTestimonials() {
        if (window.innerWidth < 1024) {
            console.log("Init testimonials owl carousel");
            $("#testimonials-officepage-carousel").owlCarousel({
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
            $("#testimonials-officepage-carousel").trigger('destroy.owl.carousel');
        }

    }
    updateTestimonials();
    $(window).resize(function () {
        updateTestimonials();
    });

    // description
    function officeDescription() {
        var descriptionWrapper = $('#description-wrapper');
        var descriptionFull = $('#description-full');
        var descriptionPartial = $('#description-partial');
        var descriptionToggle = $('#description-wrapper .toggle-btn');
        descriptionToggle.on('click', function () {
            descriptionFull.slideToggle();
            descriptionPartial.slideToggle();
            descriptionToggle.find('span').toggle();
        });
    }
    officeDescription();

    // video modal
    var videoModalFrame = $('#video-modal iframe');
    $('.testimonial-image-wrapper .ion-play').on('click', function () {
        el = $(this);
        videoModalFrame.attr('src', el.data('src'));
    });
    $(document).on('closed.zf.reveal', '#video-modal', function () {
        // stop playing video on close
        videoModalFrame.attr('src', '');
    });

});