// Get a list of your products and pop them into a dropdownlist
function GetProducts() {
  var products = V12.getFinanceProducts();
  var ddlProducts = document.getElementById("productsList");
  for (var i = 0; i < products.length; i++) {
    var newItem = new Option(products[i].name, products[i].productId);
    ddlProducts.appendChild(newItem);
  }
}
// Get details of repayments for the product selected
function CalculateRepayments() {
  var productId = $("#productsList").val(); // selected product
  var financeProduct = V12.getFinanceProduct(productId); // get the object
  var cashPrice = $("#cashPrice").val();
  var depositFactor = $("#deposit").val();
  //	var deposit = cashPrice * (depositFactor / 100);					// 9/1/2018 V12
  var deposit = parseInt(Math.ceil(cashPrice * depositFactor)) / 100; // 9/1/2018 V12
  deposit = parseFloat(deposit.toFixed(2)); // 9/1/2018 V12

  var payments = V12.calculate(financeProduct, cashPrice, deposit);

  PopulateDescription(payments);
}

function UpdateLoanInfo() {
  $("#cashPrice").val($("#cpRange").val());
  $("#deposit").val($("#depRange").val());
  CalculateRepayments();
}

// Show repayment plan details in the description
function PopulateDescription(payments) {
  $("#lblCashPrice").html(
    "Total cash price: &pound;" + payments.cashPrice + ". "
  );

  if (payments.deposit > 0) {
    $("#lblDeposit").html("&pound;" + payments.deposit + " deposit. ");
    $("#lblDeposit").css("display", "");
  } else {
    $("#lblDeposit").css("display", "none");
  }

  $("#lblAmountCredit").html(
    "Amount of credit: &pound;" + payments.loanAmount + ". "
  );

  var repayableText = "";
  if (payments.monthsDeferred > 0) {
    repayableText =
      "Non-payment period " + payments.monthsDeferred + " months, followed by ";
  } else {
    repayableText = "Repayable by ";
  }

  if (
    payments.initialPayments != payments.finalPayment &&
    payments.finalPayment > 0
  ) {
    repayableText +=
      payments.months -
      1 +
      " monthly repayments of &pound;" +
      payments.initialPayments +
      " and a final payment of &pound;" +
      payments.finalPayment +
      ". ";
  } else {
    repayableText +=
      payments.months +
      " monthly repayments of &pound;" +
      payments.initialPayments +
      ". ";
  }

  $("#lblRepayable").html(repayableText);

  $("#lblApr").html("Representative APR " + payments.apr + "%. ");

  $("#lblAnnualRate").html(
    "Annual rate of interest " + payments.annualRate + "% fixed. "
  );

  if (payments.documentFee > 0) {
    $("#lblArrangementFee").html(
      "Arrangement fee &pound;" + payments.documentFee + ". "
    );
    $("#lblArrangementFee").css("display", "");
  } else {
    $("#lblArrangementFee").css("display", "none");
  }

  if (payments.settlementFee > 0) {
    $("#lblSettlementFee").html(
      "Settlement fee &pound;" + payments.settlementFee + ". "
    );
    $("#lblSettlementFee").css("display", "");
  } else {
    $("#lblSettlementFee").css("display", "none");
  }

  $("#lblTotalRepayable").html(
    "Total amount repayable &pound;" +
      payments.amountPayable +
      " including total interest of &pound;" +
      payments.interest +
      "."
  );

  if (
    payments.monthsDeferred > 0 &&
    payments.name.indexOf("Buy Now Pay Later") >= 0
  ) {
    $("#lblBnpl").html(
      "Buy Now Pay Later Option: If you pay the amount of credit plus the settlement fee of &pound;" +
        payments.settlementFee +
        " by the end of the non-payment period, you will pay no interest. If you have not paid the amount of credit in full before the end of the non-payment period the &pound;" +
        payments.settlementFee +
        " fee will not be payable but interest (at the rate specified above) will be charged on the outstanding credit amount, from the date we told you your agreement was live."
    );
    $("#lblBnpl").css("display", "");
  } else {
    $("#lblBnpl").css("display", "none");
  }
}

// Firing this will loop through your V12 products and grab the product with the lowest
// possible monthly payments.
function GetLowestMonthlyPayments() {
  var products = V12.getFinanceProducts();
  var lowestMonthlyPayment = 0;
  var lowestMonthlyPaymentProductId = 0;

  for (var i = 0; i < products.length; i++) {
    var product = V12.getFinanceProduct(products[i].productId);
    var cashPrice = $("#cashPrice").val();
    var depositFactor = $("#deposit").val();
    //		var deposit = cashPrice * (depositFactor / 100);					// 9/1/2018 V12
    var deposit = parseInt(Math.ceil(cashPrice * depositFactor)) / 100; // 9/1/2018 V12
    deposit = parseFloat(deposit.toFixed(2)); // 9/1/2018 V12

    var payments = V12.calculate(product, cashPrice, deposit);
    var monthlyPayment = payments.initialPayments;

    if (
      parseFloat(lowestMonthlyPayment) > parseFloat(monthlyPayment) ||
      lowestMonthlyPayment == 0
    ) {
      lowestMonthlyPayment = payments.initialPayments;
      lowestMonthlyPaymentProductId = product.productId;
    }
  }

  $("#productsList").val(lowestMonthlyPaymentProductId);
  CalculateRepayments();
}

$(document).ready(function () {
  GetProducts();
  CalculateRepayments();
  $("#productsList").on("change", function () {
    CalculateRepayments();
  });
  $("#cpRange, #depRange").on("input", function () {
    UpdateLoanInfo();
  });
  $("#lowestMonthlyPayments").click(function () {
    GetLowestMonthlyPayments();
  });
  $("#cashPrice, #deposit").keyup(function () {
    var cp = $("#cashPrice").val();
    var dep = $("#deposit").val();
    $("#cpRange").val(cp);
    $("#depRange").val(dep);
    CalculateRepayments();
  });
});
