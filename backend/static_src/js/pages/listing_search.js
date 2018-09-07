// listing search page specific javascript
// --------------------------------------- 

$(document).ready(function() {

    // submit form on view / sort change
    // ---------------------------------
    $('[name="view_as"], [name="order_by"]').change(function() {
        var $that = $(this);
        var $searchForm = $('#listing-search-form');
        var $per_page = $('[name="per_page"]');

        // hijack per page
        if ($that[0].value == 'map') {
            $per_page.val('9999');
        } else {
            $per_page.val('');
        }

        // submit the search form
        $searchForm.submit();
    });
    // END


    // update form type on listing_type change
    // ---------------------------------------
    $('[name="listing_type"]').change(function() {
        var $that = $(this);
        var $searchFields = $('#listing_fields');
        $searchFields.attr('data-listing-type',$that.val());
    });
    // END


    // Infinite scroll
    // ---------------
    // Uses built in pagination to load
    // infinite scrolling properties into
    // the page. Also spins up a loading
    // animation at the bottom (y)
    $listingScroller = $('.listing-scroll');
    $listingScroller.infiniteScroll({
        path: '.pag-next',
        append: '.listing-scroll-add',
        history: 'push'
    }).on( 'request.infiniteScroll', function() {
        console.log('request');
        $('body').addClass('ajax-loading');
    }).on( 'append.infiniteScroll', function() {
        setTimeout(function() {
            console.log('append');
            $('body').removeClass('ajax-loading');
            echo.render();
        }, 500);
    });


    // Print listings
    // --------------
    // Prints either all or selected listings
    $('.print-btn').click(function() {
        var $day = $(this).parent();
        var $listings = $day.nextUntil(".day-header");
        var $allListings = $('.listing-item');

        $allListings.removeClass('print');
        $listings.addClass('print');
        window.print();
    });

    
});