// Agent index page specific javascript
// ------------------------------------

$(document).ready(function() {

    // sort by auto submit
    var searchForm = $('#search-form');
    $('#id_sort_by').on('change', function () {
        searchForm.submit();
    });

    // set office housing
    function setOfficeHousing() {
        var officeHousing = $('.location-housing');
        var officeInput = $('#id_office');
        if (officeInput.val()) {
            officeHousing.text(
                officeInput.find('option[value=' + officeInput.val() + ']').text()
            );
        }
    }
    setOfficeHousing();
    
    // show + hide advanced on mobile
    var advancedOptionsToggle = $('#advanced-options-toggle');
    var advancedOptions = $('#advanced-options-wrapper');
    advancedOptionsToggle.on('click', function () {
        advancedOptions.slideToggle();
        advancedOptionsToggle.toggleClass('opened');
    });

    // handle click on agent tile
    // prevent redirect to profile if email icon clicked
    var agentList = $('#agent-list');
    agentList.on('click', '.agent-wrapper', function (e) {
        var el = e.target;
        if (!(el.getAttribute('data-open') || el.parentNode.getAttribute('data-open'))) {
            window.location.href = $(this).find('.profile-link').attr('href');
        }
    });

    // agent housing
    var personHousing = $('.person-housing');
    var withPersonHousing = $('.with-person-housing');
    var agentInput = $('#contact-form input[name="agent"]');
    agentList.on('click', 'a[data-open="contact-form-modal"]', function () {
        var thiss = $(this);
        personHousing.text(thiss.data('name'));
        withPersonHousing.text('with ' + thiss.data('name'));
        agentInput.val(thiss.data('id'));
    });


    // Infinite scroll
    // ---------------
    // Uses built in pagination to load
    // infinite scrolling properties into
    // the page. Also spins up a loading
    // animation at the bottom (y)
    $agentScroller = $('.agent-scroll');
    $agentScroller.infiniteScroll({
        path: '.pag-next',
        append: '.agent-scroll-add',
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

});