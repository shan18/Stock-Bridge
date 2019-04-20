$(document).ready(function() {
  var formB = $('.mode-btn');
  formB.hover(
    function() {
      var $this = $(this);
      $this.addClass('btn-hover');
    },
    function() {
      var $this = $(this);
      $this.removeClass('btn-hover');
    }
  );

  var formBuyBtn = $('.buy-btn');
  var formSellBtn = $('.sell-btn');
  var modeInput = $('.mode-input');

  formBuyBtn.click(function() {
    var $this = $(this);
    $this.addClass('btn-info');
    modeInput.val($this[0].innerText);
    formSellBtn.removeClass('btn-info');
    $this.blur();
  });

  formSellBtn.click(function() {
    var $this = $(this);
    $this.addClass('btn-info');
    modeInput.val($this[0].innerText);
    formBuyBtn.removeClass('btn-info');
    $this.blur();
  });
});
