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

// async/await used to ensure that fetch() calls are in order
async function updateInventory(productNames, arraySize, requestMethod) {
  for (let i = 0; i < arraySize; i++) {
    console.log("Iteration: " + i);
    let product = productNames[i].innerHTML;
    let todayDate = new Date(); // Create new Date object
    let date = todayDate.getDate();
    let month = todayDate.getMonth() + 1;
    let year = todayDate.getFullYear();
    // Converting single digit for month and dates to double digit by concatenating a 0
    if (date < 10) {
      date = "0" + date;
    }
    if (month < 10) {
      month = "0" + month;
    }
    todayDate = year + "-" + month + "-" + date; // Format date to yyyy-mm-dd

    let productInfo = {
      // Create JSON data for each iteration of requests
      date: todayDate,
      product: product,
      barcode: i,
      aisle: 10 + i,
      quantity: 5,
    };

    let options = {
      // options for fetch() POST method
      method: requestMethod,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
      },
      body: JSON.stringify(productInfo),
    };
    try {
      let response = await fetch(
        "http://localhost:5000/api/v1.0/inventory/backstock",
        options
      );
      let data = await response.json();
      console.log("RESPONSE: " + JSON.stringify(data) + "\n");
      // return data;
    } catch (error) {
      console.log(error);
    }
  }
}

// If "Replenish Inventory" link is clicked, display a button
let replenishment = document.getElementById("replenishment");
let productNames = document.getElementsByClassName("product-name");
replenishment.addEventListener("click", function () {
  workspace.classList.add("toggle"); // Toggle off the product info
  replenishInventory.classList.remove("toggle"); // Remove the toggle class will allow the Replenish Inventory button to be displayed
  replenishInventory.addEventListener("click", function () {
    // Utilize Fetch API to communicate with Flask back-end API
    fetch("http://127.0.0.1:5000/api/v1.0/inventory/backstock/checkDB") // Check to see if backstock table has existing rows
      .then((res) => res.json())
      .then((res) => {
        if (res["message"] === "Table has not been initialized") {
          console.log("Calling postRequest()...\n");
          updateInventory(productNames, productNames.length, "POST");
        } else {
          console.log("Calling updateInventory function\n");
          updateInventory(productNames, productNames.length, "PUT");
        }
      })
      .catch((error) => console.log(error));
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
let purchaseOptionBtn = document.getElementsByClassName("purchase-option-btn");
for (let i = 0; i < purchaseOptionBtn.length; i++) {
  // getElementsByClassName returns a collection; iterate through each element to add an event listener individually
  purchaseOptionBtn[i].addEventListener("click", function () {
    if (purchaseOptionBtn[i].innerHTML === "Pick It Up") {
      alert("pick up button pressed!");
    } else if (purchaseOptionBtn[i].innerHTML === "Ship It") {
      alert("ship it button pressed!!");
    }
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