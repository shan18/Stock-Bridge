$(document).ready(function() {
  var marketButton = $('.market-button');
  var marketButtonLink = marketButton.attr('href');
  marketButton.click(function(event) {
    event.preventDefault();
    marketButton.addClass('disabled');
    marketButton.html(
      "<i class='fas fa-spinner fa-spin'></i> " + 'Entering' + '...'
    );
    setTimeout(function() {
      window.location.href = marketButtonLink;
    }, 100);
  });
});
