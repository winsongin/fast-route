"use strict";

let customer = document.getElementById("customer-name");
let orderNumber = document.getElementById("order-number");
let scanItemButton = document.getElementById("scan-location");
let workspace = document.getElementById("workspace");
let replenishInventory = document.getElementById("replenish-inventory");

// If "Replanish Inventory" link is clicked, display a button
let replenishment = document.getElementById("replenishment");
replenishment.addEventListener("click", function () {
  workspace.classList.add("toggle"); // Toggle off the product info
  replenishInventory.classList.remove("toggle"); // Remove the toggle class will allow the Replenish Inventory button to be displayed
});

let goBacks = document.getElementById("go-backs");
goBacks.addEventListener("click", function () {
  if (workspace.classList.contains("toggle")) {
    workspace.classList.remove("toggle"); // Remove the toggle so that the product info will display
  }
  if (!workspace.classList.contains("toggle")) {
    replenishInventory.classList.add("toggle"); // Add the toggle back so that the Replenish Inventory button will be hidden
  }
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
  if (workspace.classList.contains("toggle")) {
    workspace.classList.remove("toggle"); // Remove the toggle so that the product info will display
  }
  if (!workspace.classList.contains("toggle")) {
    replenishInventory.classList.add("toggle"); // Add the toggle back so that the Replenish Inventory button will be hidden
  }
  while (scanItemButton.firstChild) {
    scanItemButton.removeChild(scanItemButton.firstChild);
  }
  scanItemButton.appendChild(document.createTextNode("Scan Product"));

  // Toggle on Customer Name and Order Number
  customer.classList.remove("toggle");
  orderNumber.classList.remove("toggle");
});

let shipFromStore = document.getElementById("ship-from-store");
shipFromStore.addEventListener("click", function () {
  if (workspace.classList.contains("toggle")) {
    workspace.classList.remove("toggle"); // Remove the toggle so that the product info will display
  }
  if (!workspace.classList.contains("toggle")) {
    replenishInventory.classList.add("toggle"); // Add the toggle back so that the Replenish Inventory button will be hidden
  }
  // Replace the text for the scan button
  while (scanItemButton.firstChild) {
    scanItemButton.removeChild(scanItemButton.firstChild);
  }
  scanItemButton.appendChild(document.createTextNode("Scan Product"));

  // Toggle on Customer Name and Order Number
  customer.classList.remove("toggle");
  orderNumber.classList.remove("toggle");
});