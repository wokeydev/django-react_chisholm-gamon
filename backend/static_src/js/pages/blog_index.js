// blog page specific javascript
// -----------------------------

$(document).ready(function() {

  // UTILITY :: get URL params
  function getParameterByName(name, url) {
      if (!url) url = window.location.href;
      name = name.replace(/[\[\]]/g, "\\$&");
      var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
          results = regex.exec(url);
      if (!results) return null;
      if (!results[2]) return '';
      return decodeURIComponent(results[2].replace(/\+/g, " "));
  }

  // check for query in URL
  var searchQuery = getParameterByName('q');

  // handle blog search form
  function blogSearch() {
    $('#blog-search-form').submit(function() {
      var $form = $(this);
      var $submitButton = $form.find('button[type="submit"]');
      var cat = $form.find('[name=category_select]').val();
      var q = $form.find('[name=q]').val();

      // add loader to form
      $submitButton.addClass('is-loading');

      if(cat) {
        $form.attr('action',cat);
        $('[name=category_select]').prop('disabled', true).attr("disabled", "disabled");
      }
      
      return true;
      
    });
  }
  blogSearch();

  // ajax more articles on scroll
  var laProcessing = false;

  // load articles function
  function loadArticles() {

    if (laProcessing) {
        return false;
    }

    // set vars
    laProcessing = true; //sets a processing AJAX request flag
    var $blogSection = $('.blog-posts');
    var laLength = $blogSection.attr('data-length');
    var laOffset = $blogSection.attr('data-offset');
    var laHasNext = $blogSection.attr('data-hasnext');

    // show loading spinner if more, stop if not
    if (laHasNext === 'true') {
      $('body').addClass('ajax-loading');
    } else {
      return false;
    }

    // ajax options string
    laOptions = '';
    laOptions += '&limit=' + laLength; // limit
    laOptions += '&offset=' + laOffset; // offset


    // AJAX all the things
    $.get('/api/v2/pages/?type=blog.BlogPage&fields=*' + laOptions, function(data) {

      // update html data settings
      var newOffset = parseInt(laOffset) + parseInt(data.items.length);
      $blogSection.attr('data-offset',newOffset);
      if (newOffset < data.meta.total_count) {
        $blogSection.attr('data-hasnext','true');
      } else {
        $blogSection.attr('data-hasnext','false');
      }

      // build the HTML
      var laHtml = '';
      laHtml += '<div class="grid-x grid-margin-x">';

      $.each(data.items, function(key,article) {

        laHtml += '<div class="large-6 cell card-wrapper">';
            laHtml += '<div class="card">';

                // title
                laHtml += '<div class="card-divider">';
                    laHtml += '<a href="' + article.meta.html_url + '">';
                        laHtml += '<h3 class="bold">' + article.title + '</h3>';
                    laHtml += '</a>';
                laHtml += '</div>';

                // image
                if (article.header_image) {
                  laHtml += '<a class="card-image" href="' + article.meta.html_url + '">';
                    laHtml += '<img src="' + article.header_image + '" alt="" />';
                  laHtml += '</a>';
                } else {
                  laHtml += '<a class="card-image no-img" href="' + article.meta.html_url + '">';
                      laHtml += '<img src="/static/img/mpc-logo-white@2x.png" alt="">';
                  laHtml += '</a>';
                }

                // details
                laHtml += '<div class="card-section grid-x">';
                    laHtml += '<div class="large-8 cell">';
                        laHtml += '<p class="bold">';

                          // author
                          if (article.author) {
                            laHtml += 'by <a href="' + article.author.author_blog_slug + '" class="color-black underline">';
                            if (article.author.first_name) {
                              laHtml += article.author.first_name + ' ' + article.author.last_name;
                            } else {
                              laHtml += article.author.username;
                            }
                          }

                          // date
                          laHtml += '</a> on ' + article.date;

                          // categories
                          if (article.blog_categories[0]) {
                            laHtml += '<span class="author-divider">|</span>';
                            var cat_url = article.blog_categories[0].toLowerCase();
                            laHtml += '<a href="/blog/category/' + cat_url + '" class="card-category font-sm uppercase">' + article.blog_categories[0] + '</a>';
                          }

                        laHtml += '</p>';
                    laHtml += '</div>';

                    // button
                    laHtml += '<div class="large-4 cell text-right">';
                        laHtml += '<a href="' + article.meta.html_url + '" class="button small ml-15">Read more</a>';
                    laHtml += '</div>';

                laHtml += '</div>'; // END details

            laHtml += '</div>';
        laHtml += '</div>';

      }); // END each

      laHtml += '</div>';
      // END build the html

       // hides loading spinner
      $('body').removeClass('ajax-loading');

      // append items to blog section
      $blogSection.append(laHtml);

      // resets the vars once the callback concludes
      laProcessing = false;

    }); // END Get

  } // END loadArticles function

  $('body').on('scrollme.zf.trigger', Foundation.util.throttle(function() {
    if ($(window).scrollTop() >= ($(document).height() - $(window).height() - 200)) {
      loadArticles();
    }
  }, 50));

  // init Owl Carousel
  $("#blog-index-carousel").owlCarousel({
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

});
