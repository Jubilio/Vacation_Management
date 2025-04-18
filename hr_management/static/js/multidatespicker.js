/*
 * Simple stub for jQuery UI MultiDatesPicker functionality.
 * This stub proxies to the standard datepicker, allowing selection of single dates.
 * Replace this stub with the full plugin from:
 * https://github.com/dubrox/Multiple-Dates-Picker-for-jQuery-UI
 */
(function($){
    if (!$.fn.multiDatesPicker) {
      $.fn.multiDatesPicker = function(options) {
        console.warn('multiDatesPicker stub called: using jQuery UI datepicker fallback.');
        // Fallback: initialize standard datepicker
        return this.datepicker(options);
      };
    }
  })(jQuery);
  