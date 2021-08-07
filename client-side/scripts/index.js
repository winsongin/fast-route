"use strict";

let customer = document.getElementById("customer-name");
let orderNumber = document.getElementById("order-number");
let scanItemButton = document.getElementById("scan-location");
let workspace = document.getElementById("workspace");
let replenishInventory = document.getElementById("replenish-inventory");

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

// If "Replenish Inventory" link is clicked, display a button
let replenishment = document.getElementById("replenishment");
replenishment.addEventListener("click", function () {
  workspace.classList.add("toggle"); // Toggle off the product info
  replenishInventory.classList.remove("toggle"); // Remove the toggle class will allow the Replenish Inventory button to be displayed
  replenishInventory.addEventListener("click", function () {
    // Utilize Fetch API to communicate with Flask back-end API
    fetch("http://127.0.0.1:5000/api/v1.0/inventory/backstock/checkDB") // Check to see if backstock table has existing rows
      .then((res) => res.json())
      // .then((res) => {
      // .then(res => console.log(res["message"]))
      //   if (res["message"] === "Table has not been initialized") {

      //   }
      // })
      .catch((err) => console.log(err));
  });
});

// Display the customer page when the Customer link is clicked
let customerLink = document.getElementById("customer");
let sectionA = document.getElementById("section-A");
let sectionB = document.getElementById("section-B");
customerLink.addEventListener("click", function () {
  // Alternate "toggle" class between section-A and section-B to display EITHER the employee view or the customer view
  if (!sectionA.classList.contains("toggle")) {
    // If section-A is currently displayed, toggle it off and display the customer view
    sectionA.classList.add("toggle");
    sectionB.classList.remove("toggle");
  } else if (sectionA.classList.contains("toggle")) {
    // If section-B is currently displayed, toggle it off and display the employee view
    sectionA.classList.remove("toggle");
    sectionB.classList.add("toggle");
  }
});

// Listen for Add to Cart button click
let addToCartBtn = document.getElementsByClassName("add-to-cart-btn");
for (let i = 0; i < addToCartBtn.length; i++) {
  // getElementsByClassName returns a collection; iterate through each element to add an event listener individually
  addToCartBtn[i].addEventListener("click", function () {
    alert("button pressed");
  });
}

let backBtn = document.getElementById("back-btn");
backBtn.addEventListener("click", function () {
  // Alternate "toggle" class between section-A and section-B to display EITHER the employee view or the customer view
  if (!sectionA.classList.contains("toggle")) {
    // If section-A is currently displayed, toggle it off and display the customer view
    sectionA.classList.add("toggle");
    sectionB.classList.remove("toggle");
  } else if (sectionA.classList.contains("toggle")) {
    // If section-B is currently displayed, toggle it off and display the employee view
    sectionA.classList.remove("toggle");
    sectionB.classList.add("toggle");
  }
});
