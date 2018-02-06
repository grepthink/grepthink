containerEl = null;
mixer = null;

jQuery(document).ready(function ($) {

  containerEl = document.querySelector('.container');
  mixer = mixitup(containerEl, {
    controls: {
      toggleLogic: 'and'
    }
  });

  //open/close lateral filter
  $('.cd-filter-trigger').on('click', function () {
    triggerFilter(true);
  });
  $('.cd-filter .cd-close').on('click', function () {
    triggerFilter(false);
  });

  function triggerFilter($bool) {
    var elementsToTrigger = $([$('.cd-filter-trigger'), $('.cd-filter'), $('.cd-tab-filter'), $('.cd-gallery')]);
    elementsToTrigger.each(function () {
      $(this).toggleClass('filter-is-visible', $bool);
    });
  }

  $('.cd-filter-block h4').on('click', function () {
    $(this).toggleClass('closed').siblings('.cd-filter-content').slideToggle(300);
  });

  //fix lateral filter and gallery on scrolling
  $(window).on('scroll', function () {
    (!window.requestAnimationFrame) ? fixGallery() : window.requestAnimationFrame(fixGallery);
  });

  function fixGallery() {
    var offsetTop = $('.cd-main-content').offset().top,
      scrollTop = $(window).scrollTop();
    (scrollTop >= offsetTop) ? $('.cd-main-content').addClass('is-fixed') : $('.cd-main-content').removeClass('is-fixed');
  }


  buttonFilter.init();

  //search filtering
  //credits http://codepen.io/edprats/pen/pzAdg
  var inputText;
  var $matching = $();

  var delay = (function () {
    var timer = 0;
    return function (callback, ms) {
      clearTimeout(timer);
      timer = setTimeout(callback, ms);
    };
  })();

  $(".cd-filter-content input[type='search']").keyup(function () {

    // Delay function invoked to make sure user stopped typing
    delay(function () {
      inputText = $(".cd-filter-content input[type='search']").val().toLowerCase();
      // Check to see if input field is empty
      if ((inputText.length) > 0) {
        $('.mix').each(function () {
          var $this = $(this);

          // add item to be filtered out if input text matches items inside the title
          if ($this.attr('class').toLowerCase().match(inputText)) {
            $matching = $matching.add(this);
          } else {
            // removes any previously matched item
            $matching = $matching.not(this);
          }
        });
        mixer.filter($matching);
      } else {
        mixer.filter('filter', 'all');
      }
    }, 200);
  });
});

var buttonFilter = {
  // Declare any variables we will need as properties of the object
  $filters: null,
  groups: [],
  outputArray: [],
  outputString: '',

  // The "init" method will run on document ready and cache any jQuery objects we will need.
  init: function () {
    var self = this; // As a best practice, in each method we will asign "this" to the variable "self" so that it remains scope-agnostic. We will use it to refer to the parent "buttonFilter" object so that we can share methods and properties between all parts of the object.

    self.$filters = $('.cd-main-content');

    self.$filters.find('.cd-filters').each(function () {
      var $this = $(this);

      self.groups.push({
        $inputs: $this.find('.filter'),
        active: '',
        tracker: false
      });
    });

    self.bindHandlers();
  },

  // The "bindHandlers" method will listen for whenever a button is clicked.
  bindHandlers: function () {
    var self = this;

    self.$filters.on('click', 'a', function (e) {
      self.parseFilters();
    });
    self.$filters.on('change', function () {
      self.parseFilters();
    });
  },

  parseFilters: function () {
    var self = this;

    // loop through each filter group and grap the active filter from each one.
    for (var i = 0, group; group = self.groups[i]; i++) {
      group.active = [];
      group.$inputs.each(function () {
        var $this = $(this);
        if ($this.is('input[type="radio"]') || $this.is('input[type="checkbox"]')) {
          if ($this.is(':checked')) {
            group.active.push($this.attr('data-filter'));
          }
        }
      });
    }
    self.concatenate();
  },

  concatenate: function () {
    var self = this;

    self.outputString = ''; // Reset output string

    for (var i = 0, group; group = self.groups[i]; i++) {
      self.outputString += group.active;
    }
    self.outputString = self.outputString.toString().replace(',', '');
    // If the output string is empty, show all rather than none:
    !self.outputString.length && (self.outputString = 'all');

    mixer.filter(self.outputString);
  }

};
