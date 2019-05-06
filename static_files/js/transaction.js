$(document).ready(function() {
  // Transaction mode buttons hover
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

  // Transaction mode buttons click
  var formPurchaseBtn = $('.purchase-btn');
  var formScheduleBtn = $('.schedule-btn');
  var modeInput = $('.mode-input');
  var formPurchaseHeading = $('.purchase-heading');
  var formQuantityInput = $('.quantity-input');
  var formPriceInput = $('.price-input');

  formPurchaseBtn.click(function() {
    var $this = $(this);
    $this.addClass('btn-info');
    modeInput.val($this[0].innerText.toLowerCase());
    formScheduleBtn.removeClass('btn-info');
    $this.blur();
    formPurchaseHeading.html('<b>Transact Stocks</b>');
    formQuantityInput.removeClass('mb-2');
    formPriceInput.attr('type', 'hidden');
  });

  formScheduleBtn.click(function() {
    var $this = $(this);
    $this.addClass('btn-info');
    modeInput.val($this[0].innerText.toLowerCase());
    formPurchaseBtn.removeClass('btn-info');
    $this.blur();
    formPurchaseHeading.html('<b>Schedule Transaction<b/>');
    formQuantityInput.addClass('mb-2');
    formPriceInput.attr('type', 'text');
  });

  // Purchase mode buttons click
  var formBuyBtn = $('.buy-btn');
  var formSellBtn = $('.sell-btn');
  var purchaseModeInput = $('.p-mode-input');
  var formQuantityInput = $('.quantity-input');

  formBuyBtn.click(function() {
    var $this = $(this);
    $this.addClass('btn-info');
    purchaseModeInput.val($this[0].innerText.toLowerCase());
    formSellBtn.removeClass('btn-info');
    formPriceInput.attr('placeholder', 'Maximum price to buy stocks');
    formQuantityInput.attr('placeholder', 'Number of stocks to buy');
    $this.blur();
  });

  formSellBtn.click(function() {
    var $this = $(this);
    $this.addClass('btn-info');
    purchaseModeInput.val($this[0].innerText.toLowerCase());
    formBuyBtn.removeClass('btn-info');
    formPriceInput.attr('placeholder', 'Minimum price to sell stocks');
    formQuantityInput.attr('placeholder', 'Number of stocks to sell');
    $this.blur();
  });

  // Transaction mode submit
  function transactionFormIndicator(submitButton, text, doSubmit) {
    if (doSubmit) {
      submitButton.addClass('disabled');
      submitButton.html(
        "<i class='fas fa-spinner fa-spin'></i> " + text + '...'
      );
    } else {
      submitButton.removeClass('disabled');
      submitButton.html(text);
    }
  }

  var transactionForm = $('.transaction-form');
  var transactionFormMethod = transactionForm.attr('method');
  var transactionFormEndpoint = transactionForm.attr('data-endpoint');

  transactionForm.submit(function(event) {
    event.preventDefault();
    var $this = $(this);
    var transactionFormButton = $this.find("[type='submit']");
    var transactionFormButtonText = transactionFormButton.text();
    var transactionFormData = transactionForm.serialize();
    transactionFormIndicator(transactionFormButton, 'Submitting', true);
    $.ajax({
      method: transactionFormMethod,
      url: transactionFormEndpoint,
      data: transactionFormData,
      success: function(responseData) {
        transactionFormIndicator(
          transactionFormButton,
          transactionFormButtonText,
          false
        );
        window.location.href = responseData.next_path;
      },
      error: function(error) {
        alert('An error occured.');
        transactionFormIndicator(
          transactionFormButton,
          transactionFormButtonText,
          false
        );
      }
    });
  });
});
