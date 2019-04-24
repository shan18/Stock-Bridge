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
