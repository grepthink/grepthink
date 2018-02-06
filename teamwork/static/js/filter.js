containerEl = null;
mixer = null;

var multiFilter = {

  $filterGroups: null,
  $filterUi: null,
  $reset: null,
  groups: [],
  outputArray: [],
  outputString: '',

  // The "init" method will run on document ready and cache any jQuery objects we will need.

  init: function () {
    var self = this; // As a best practice, in each method we will asign "this" to the variable "self" so that it remains scope-agnostic. We will use it to refer to the parent "checkboxFilter" object so that we can share methods and properties between all parts of the object.

    self.$filterUi = $('.cd-main-content');
    self.$filterGroups = $('.cd-filter-block');
    self.$container = $('.container');

    self.$filterGroups.each(function () {
      self.groups.push({
        $inputs: $(this).find('input'),
        active: [],
        tracker: false
      });
    });

    self.bindHandlers();
  },

  // The "bindHandlers" method will listen for whenever a form value changes.

  bindHandlers: function () {
    var self = this,
      typingDelay = 300,
      typingTimeout = -1,
      resetTimer = function () {
        clearTimeout(typingTimeout);

        typingTimeout = setTimeout(function () {
          self.parseFilters();
        }, typingDelay);
      };

    self.$filterGroups.filter('.checkboxes').on('change', function () {
      self.parseFilters();
    });


    self.$filterGroups.filter('.search').on('change keyup', function () {
      resetTimer();
    });

  },

  // The parseFilters method checks which filters are active in each group:

  parseFilters: function () {
    var self = this;

    // loop through each filter group and add active filters to arrays

    for (var i = 0, group; group = self.groups[i]; i++) {
      group.active = []; // reset arrays
      group.$inputs.each(function () {
        var searchTerm = '',
          $input = $(this),
          minimumLength = 1;

        if ($input.is(':checked')) {
          group.active.push(this.value);
        }

        if ($input.is('[type="search"]') && this.value.length >= minimumLength) {
          searchTerm = this.value
            .trim()
            .toLowerCase()
            .replace(' ', '-');

          group.active[0] = '[class*="' + searchTerm + '"]';
        }
      });
      group.active.length && (group.tracker = 0);
    }

    self.concatenate();
  },

  // The "concatenate" method will crawl through each group, concatenating filters as desired:

  concatenate: function () {
    var self = this,
      cache = '',
      crawled = false,
      checkTrackers = function () {
        var done = 0;

        for (var i = 0, group; group = self.groups[i]; i++) {
          (group.tracker === false) && done++;
        }

        return (done < self.groups.length);
      },
      crawl = function () {
        for (var i = 0, group; group = self.groups[i]; i++) {
          group.active[group.tracker] && (cache += group.active[group.tracker]);

          if (i === self.groups.length - 1) {
            self.outputArray.push(cache);
            cache = '';
            updateTrackers();
          }
        }
      },
      updateTrackers = function () {
        for (var i = self.groups.length - 1; i > -1; i--) {
          var group = self.groups[i];

          if (group.active[group.tracker + 1]) {
            group.tracker++;
            break;
          } else if (i > 0) {
            group.tracker && (group.tracker = 0);
          } else {
            crawled = true;
          }
        }
      };

    self.outputArray = []; // reset output array

    do {
      crawl();
    }
    while (!crawled && checkTrackers());

    self.outputString = self.outputArray.join();

    // If the output string is empty, show all rather than none:

    !self.outputString.length && (self.outputString = 'all');
    mixer.filter(self.outputString);
  }
};

// On document ready, initialise our code.

$(function () {

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

  // Initialize multiFilter code

  multiFilter.init();

  // Instantiate MixItUp
  containerEl = document.querySelector('.container');
  mixer = mixitup(containerEl, {
    controls: {
      enable: false // we won't be needing these
    },
    animation: {
      easing: 'cubic-bezier(0.86, 0, 0.07, 1)',
      queueLimit: 3,
      duration: 600
    }
  });
});


