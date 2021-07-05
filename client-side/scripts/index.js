"use strict";

let customer = document.getElementById("customer-name");
let orderNumber = document.getElementById("order-number");
let scanItemButton = document.getElementById("scan-location");

let goBacks = document.getElementById("go-backs");
goBacks.addEventListener("click", function () {
  while (scanItemButton.firstChild) {
    scanItemButton.removeChild(scanItemButton.firstChild);
  }
  scanItemButton.appendChild(document.createTextNode("Scan Location"));
  // Toggle off Customer Name and Order Number
  customer.classList.add("toggle");
  orderNumber.classList.add("toggle");
});

let orderPickUps = document.getElementById("order-pick-ups");
orderPickUps.addEventListener("click", function () {
  while (scanItemButton.firstChild) {
    scanItemButton.removeChild(scanItemButton.firstChild);
  }
  scanItemButton.appendChild(document.createTextNode("Scan Product"));

  // Toggle off Customer Name and Order Number
  customer.classList.remove("toggle");
  orderNumber.classList.remove("toggle");
});

let shipFromStore = document.getElementById("ship-from-store");
shipFromStore.addEventListener("click", function () {
  // Replace the text for the scan button
  while (scanItemButton.firstChild) {
    scanItemButton.removeChild(scanItemButton.firstChild);
  }
  scanItemButton.appendChild(document.createTextNode("Scan Product"));

  // Toggle off the Customer Name and Order #
  customer.classList.remove("toggle");
  orderNumber.classList.remove("toggle");
});
