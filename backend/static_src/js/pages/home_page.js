// home page specific javascript
// -----------------------------

$(document).ready(function () {

    // Fullscreen Hero that fits screen
    function fullscreen() {
        $('#hero').css({
            width: jQuery(window).width(),
            height: jQuery(window).height()
        });
    }
    fullscreen();

    // Run the function in case of window resize
    $(window).resize(function () {
        fullscreen();
    });

    // set homepage background image on mobile / desktop
    function homeBG() {
        var currentSize = Foundation.MediaQuery.current;
        var $hero = $('#herobg');
        var bgImg = '';

        if (currentSize != 'small') {
            bgImg = $hero.attr('data-featuredimg');
        } else {
            bgImg = $hero.attr('data-mobileimg');
        }

        $hero.attr('style','background-image:url("' + bgImg + '")');
    }
    // change image on window resize
    $(window).on('changed.zf.mediaquery', function(event, newSize, oldSize){
        if(newSize == 'small' || newSize == 'medium') {
            homeBG();
        }
    });


    // Homepage Advanced Search
    // ------------------------
    $("#id_listing_type").on('change', function () {
        var propertyType = this.value,
        $advancedSearch = $('#search-advanced');

        $advancedSearch.attr('data-listing-type',propertyType);
    });
    // END


    // appraisal popup show/not show
    if (!Cookies.get('noAppraisalPopup')) {
        setTimeout(function () {
            $('.appraisal-popup').fadeIn();
        }, 1000)
    }
    $('.appraisal-popup .close-button').on('click', function () {
        Cookies.set('noAppraisalPopup', 1);
    });

    // featured listings button.. show / hide / update
    $('.toggle-featured-button').click(function() {
        var that = $(this);
        var btn = $('#featured-button');
        var link = that.attr('data-button-link');
        var text = that.text().toLowerCase();
        
        if (link) {
            btn.removeClass('hide');
            btn.attr('href',link);
            btn.text('View ' + text + ' listings');
        } else {
            btn.addClass('hide');
        }

        return true;
    });

});
 

// run on window load
// ------------------
$(window).on('load', function() {
    
    // handle video loading
    function homeVideo() {
        var currentSize = Foundation.MediaQuery.current;
        var video = $('#home-video');
        var videoSrc = video.find('source').attr('data-src');

        if (currentSize != 'small') {
            video.attr('src',videoSrc);

            // restrict video looping
            var x = 4; // <- this many times
            var loopCount = 1;
            video.on('ended', function () {
                if (loopCount < x) {
                    this.currentTime = 0;
                    this.play();
                    loopCount ++;
                }
            });
        }

    }
    // this function will run after other js loads 
    // - function call is in 'home_page.html'
    homeVideo();

    // Testimonial Carousel on Homepage
    if ($("#testimonials-homepage-carousel")) {
        $("#testimonials-homepage-carousel").owlCarousel({
            loop: false,
            margin: 10,
            dots: false,
            items: 5,
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
                },
                1024: {
                    items: 4,
                    nav: true
                },
                1200: {
                    items: 5,
                    nav: true
                }
            }
        });
    }

});
