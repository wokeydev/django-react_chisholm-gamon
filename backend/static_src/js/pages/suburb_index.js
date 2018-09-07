// suburb index page specific javascript
// -------------------------------------

$(document).ready(function() {

  // init Owl Carousel
  $("#suburb-index-carousel").owlCarousel({
    loop: true,
    margin: 0,
    dots: false,
    nav: true,
    responsiveClass: true,
    responsive: {
      0: {
          items: 1,
          nav: true
      }
    }
  });

  // show suburbs index
  function showSuburbs() {
    var $index = $('#suburbs-index'),
    suburbs = $index.find('.suburb-list-suburb');

    // loop through groups
    $.each(suburbs,function() {
      var s = $(this),
      sIndex = s.data('index'),
      sGroup = $('[data-group="' + sIndex + '"]');

      sGroup.append(s).addClass('has-suburbs');

    });

    $index.addClass('has-suburbs');

  }
  showSuburbs();

});
