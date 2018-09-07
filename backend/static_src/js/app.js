$(document).ready(function(){


    // init lazy loading
    // -----------------
    echo.init({
        offsetHorizontal: window.innerWidth,
        offsetVertical: window.innerHeight,
    });
    // END


    // Fullscreen Hero that fits screen
    // --------------------------------
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
    // END


    // mailto link doer
    // ----------------
    function showMailLinks() {
      var $mailLinks = $('.mailto');
      $mailLinks.click(function(e) {
        e.preventDefault();

        // set vars
        var mailTo = $(this).data('mailto') ? $(this).data('mailto') : '',
        mailSubject = $(this).data('subject') ? $(this).data('subject') : '';

        // send user to mailto
        if (mailTo !== '') {
          window.location = 'mailto:' + mailTo + '?subject=' + mailSubject;
        }

      });
    }
    showMailLinks();
    // END


    // add scrolled class to body
    // --------------------------
    function pageScroll() {
      var $win = $(window),
      $body = $('body'),
      $html = $('html'),
      threshold = 70;
      if ($win.scrollTop() > threshold) {
        $body.addClass('is-scrolled');
      }
      $(window).scroll(function() {
        if ($win.scrollTop() > threshold) {
          $body.addClass('is-scrolled');
        } else {
          $body.removeClass('is-scrolled');
        }
      });
    }
    pageScroll();
    // END


    // register property alerts
    // ------------------------
    function registerAlerts() {
      var subscriptionBlock = $('.myvip');
      var subscriptionForm = subscriptionBlock.find('form');
      var successMessage = subscriptionBlock.find('.success-message');
      var submitButton = subscriptionBlock.find('button[type="submit"]');

      subscriptionForm.on('submit', function (e) {
          e.preventDefault();
          e.stopPropagation();
          submitButton.addClass('is-loading');

          // build the data
          var alertName = subscriptionForm.find('input[name="name"]').val();
          var alertEmail = subscriptionForm.find('input[name="email"]').val();
          var formCriteria = subscriptionForm.find(':input[name!="name"][name!="email"][type!="submit"]').serializeArray();
          var alertCriteria = {};
          formCriteria.forEach(function(item) {
            alertCriteria[item.name] = {};
            alertCriteria[item.name] = item.value;
          });

          var alertData = {
            name: alertName,
            email: alertEmail,
            criteria: alertCriteria
          };

          // register alert via ajax
          $.ajax({
              url: '/api/alerts/',
              type: 'post',
              dataType: 'json',
              contentType: "application/json; charset=utf-8",
              data: JSON.stringify(alertData)
          }).done(function (r) {
              subscriptionBlock.addClass('success');
              var params = subscriptionForm.serialize()
                                          .replace(/(^|&)(name|email)[^&]+/g, '')
                                          .replace(/^&/, '');
              successMessage.find('a').attr('href', '/buying/?' + params);
          }).fail(function (r) {
              alert('Error, please contact us via email');
              console.log(r);
          });

          // remove loading spinner from button
          submitButton.removeClass('is-loading');
      });

      // close success message
      successMessage.find('button').on('click', function () {
          subscriptionBlock.removeClass('success');
      });

    }
    registerAlerts();
    // END


    // Search Submit
    // -------------
    // handle form submission, clean unused search
    // parameters from URL and fudge the per_page
    // to show all listings on map view
    var $searchForm = $('#listing-search-form');
    $searchForm.submit(function(e) {
        var $form = $(this);
        var fields = $form.find(':input:not([type="submit"])');
        var $submitButton = $form.find('button[type="submit"]');
        var propertyType = $("#id_listing_type").val();
        var searchFor = '';

        // add loader to form
        $submitButton.addClass('is-loading');

        // set action URL for listing types
        switch (propertyType) {
            case 'sale':
                searchFor = '/buying/'; // buying
                break;
            case 'lease':
                searchFor = '/renting/'; // renting
                $form.find('[name="property_class"]').prop('disabled', true).attr("disabled", "disabled");
                break;
            case 'commercial':
                searchFor = '/buying/commercial/'; // commercial
                break;
            case 'sold':
                searchFor = '/selling/sold-properties/'; // sold
                break;
            default:
                searchFor = '/buying/'; // buying
                break;
        }

        // check if inspections or auctions
        if (window.location.href.indexOf('upcoming') > -1) {
            $form.attr('action','');
         } else {
            $form.attr('action',searchFor);
         }

        // remove query attr if suburbs
        var $queryField = $('#id_query');
        var suburbFieldVal = $('#id_address_suburb').val();
        if (suburbFieldVal) $queryField.val('');
        
        // remove empty values
        $.each(fields,function() {
            var $that = $(this);
            if ($that[0].value == "") {
                $that.prop('disabled', true).attr("disabled", "disabled");
            }
        });

        return true;
    });
    // END


    // search query autocomplete
    // -------------------------
    // uses the api at /properties/autocomplete/
    // to return suggested items for suburb names,
    // properties and agents.
    function queryComplete() {
        var $queryField = $('#id_query');
        var $listingTypeField = $('#id_listing_type');
  
        // set up the select2 with our api
        $queryField.select2({
          width: '100%',
          placeholder: 'Search by Suburb, Postcode or Address',
          minimumInputLength: 3,
          ajax: {
            method: 'GET',
            url: '/properties/autocomplete/',
            dataType: 'json',
            data: function (params) {
                var query = params.term;
                var listingTypeVal = $listingTypeField.val();
                var listingType = '';
                var status = '';
                var propertyClass = '';

                switch(listingTypeVal) {
                    case 'sale':
                        listingType = 'sale';
                        status = 'current';
                        break;
                    case 'lease':
                        listingType = 'lease';
                        status = 'current';
                        break;
                    case 'commercial':
                        listingType = 'sale';
                        status = 'current';
                        propertyClass = 'commercial';
                        break;
                    case 'sold':
                        listingType = 'sale';
                        status = 'sold';
                        break;
                    default:
                        listingType = 'sale';
                        status = 'current';
                        break;
                }

                var q = { 
                    query: params.term,
                    listing_type: listingType,
                    status: status,
                    property_class: propertyClass
                };
                console.log(q);
                return q;
            },
            processResults: function (data) {
                var results = formatAutocomplete(data);
                return results;
            }
          }
        });

        // apply any URL query params to select2
        var urlParams = new URLSearchParams(window.location.search);
        var urlQuery = urlParams.get('query');
        var urlSuburbs = urlParams.get('address_suburb');
        if(urlQuery) {
            var urlQueryText = decodeURI(urlQuery);
            var option = new Option(urlQueryText, urlQueryText, true, true);
            $queryField.append(option).trigger('change');
            $queryField.trigger({
                type: 'select2:select'
            });
        }
        if(urlSuburbs) {
            var urlSuburbsText = decodeURI(urlSuburbs);
            var urlSuburbsArray = urlSuburbsText.split(',');
            $.map(urlSuburbsArray,function(elem,index) {
                if (elem == '') return false;
                var option = new Option(elem, elem, true, true);
                $queryField.append(option).trigger('change');
            })
            $queryField.trigger({
                type: 'select2:select'
            });
        }
  
    }
    queryComplete();

    // formats the autocomplete api results
    // into select2 readable JSON
    function formatAutocomplete(data) {
        var apiData = data.autocomplete;
        var results = { 'results': [] };
        var queryType = $('#id_querytype').val();

        $.map(apiData, function(elem,index) {
            if (queryType && (queryType != index)) return false;
            var type = { 'text': index, 'children': [] };
            results["results"].push(type);
            $.map(elem, function(e,i) {
                var child = ((index == 'suburbs') || (index == 'postcodes') ? e : e[1]);
                var upperChild = child.toUpperCase();
                var children = { 'id': upperChild, 'text': upperChild, 'type': index }
                type["children"].push(children);
            });
        });
        var jsonResults = JSON.stringify(results);
        return results;
    }

    // fiddle with the types of results
    function queryType() {
        var $queryField = $('#id_query');
        var $suburbField = $('#id_address_suburb');

        // adding suburbs
        $queryField.on('select2:select', function (e) {
            var data = e.params.data;
            var suburbFieldVal = $suburbField.val();
            if(data.type == 'suburbs') {
                var suburb = data.text;
                var newVal = suburbFieldVal + suburb + ',';
                $suburbField.val(newVal);
            }
            $('#id_querytype').val(data.type);
        });

        // removing suburbs
        $queryField.on('select2:unselect', function (e) {
            var data = e.params.data;
            if(data.type == 'suburbs') {
                var newVal = suburbFieldVal.replace(data.text + ',','');
                $suburbField.val(newVal);
            }
            selectData = $queryField.select2('data');
            console.log(selectData);
            if (selectData.length == 0) { 
                $('#id_querytype').removeAttr('value');
                $('#id_address_suburb').removeAttr('value');
            }
        });
    }
    queryType();
    

});
// END document.ready


// Load Google Maps API
// --------------------
function loadGoogleMapsAPI(api_key, callback_name, params) {
  params = params || '';
  var sc = document.createElement('script');
  var url = 'https://maps.googleapis.com/maps/api/js?key=' + api_key + params;
  if (callback_name) url += '&callback=' + callback_name;
  sc.setAttribute('type', 'text/javascript');
  sc.setAttribute('src', url);
  document.getElementsByTagName('head')[0].appendChild(sc);
}
// END