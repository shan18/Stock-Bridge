$(document).ready(function() {
  // Loan Form

  function loanFormIndicator(submitButton, text, doSubmit) {
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

  // Loan Issue Form
  var loanIssueForm = $('.loan-issue-form');
  var loanIssueFormMethod = loanIssueForm.attr('method');
  var loanIssueFormEndpoint = loanIssueForm.attr('data-endpoint');

  loanIssueForm.submit(function(event) {
    event.preventDefault();
    var $this = $(this);
    var loanIssueFormButton = $this.find("[type='submit']");
    var loanIssueFormButtonText = loanIssueFormButton.text();
    var loanIssueFormData = loanIssueForm.serialize();
    loanFormIndicator(loanIssueFormButton, 'Issuing Loan', true);
    $.ajax({
      method: loanIssueFormMethod,
      url: loanIssueFormEndpoint,
      data: loanIssueFormData,
      success: function(responseData) {
        loanFormIndicator(loanIssueFormButton, loanIssueFormButtonText, false);
        window.location.href = responseData.next_path;
      },
      error: function(error) {
        alert('An error occured.');
        loanFormIndicator(loanIssueFormButton, loanIssueFormButtonText, false);
      }
    });
  });

  // Loan Repay Form
  var loanRepayForm = $('.loan-repay-form');
  var loanRepayFormMethod = loanRepayForm.attr('method');
  var loanRepayFormEndpoint = loanRepayForm.attr('data-endpoint');

  loanRepayForm.submit(function(event) {
    event.preventDefault();
    var $this = $(this);
    var loanRepayFormButton = $this.find("[type='submit']");
    var loanRepayFormButtonText = loanRepayFormButton.text();
    var loanRepayFormData = loanRepayForm.serialize();
    loanFormIndicator(loanRepayFormButton, 'Repaying Loan', true);
    $.ajax({
      method: loanRepayFormMethod,
      url: loanRepayFormEndpoint,
      data: loanRepayFormData,
      success: function(responseData) {
        loanFormIndicator(loanRepayFormButton, loanRepayFormButtonText, false);
        window.location.href = responseData.next_path;
      },
      error: function(error) {
        alert('An error occured.');
        loanFormIndicator(loanRepayFormButton, loanRepayFormButtonText, false);
      }
    });
  });
});
