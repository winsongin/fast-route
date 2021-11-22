"use strict";

let customer = document.getElementById("customer-name");
let orderNumber = document.getElementById("order-number");
let scanItemButton = document.getElementById("scan-location");
let workspace = document.getElementById("workspace");
let replenishInventory = document.getElementById("replenish-inventory");

let orderPickUps = document.getElementById("order-pick-ups");
orderPickUps.addEventListener("click", function () {
  taskList.classList.remove("toggle"); // Display task list when Order Pick-Ups tab is clicked on
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
  taskList.classList.remove("toggle"); // Display task list when Ship From Store tab is clicked on
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
  taskList.classList.add("toggle"); // Remove task list when replenishing inventory
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

// Add event listeners to increment and decrement buttons and perform action as needed
let decrementBtns = document.getElementsByClassName("decrement-btns");
let incrementBtns = document.getElementsByClassName("increment-btns");
let quantityInput = document.getElementsByClassName("qty-input");
for (let i = 0; i < quantityInput.length; i++) {
  let value = parseInt(quantityInput[i].value);
  // Listen for the '-' button clicks
  decrementBtns[i].addEventListener("click", function () {
    if (value > 1) {
      // Prevent user from decrementing past the minimum/default value: 1
      value = value - 1;
      quantityInput[i].setAttribute("value", value);
    }
  });
  // Listen for the '+' button clicks
  incrementBtns[i].addEventListener("click", function () {
    value = value + 1;
    quantityInput[i].setAttribute("value", value);
  });
}

// fetch() requests for fulfillment orders
async function updateFulfillment(list) {
  try {
    for (let i = 0; i < list.length; i++) {
      let requestMethod = list[i].requestMethod;
      let resource = list[i].resource;
      let product = list[i].product;
      let quantity = list[i].quantity.value;

      var currentQuantity;
      if (requestMethod === "GET") {
        // Retrieve existing quantity in order to be later used to check users' quantity input
        let queryString = `?product=${encodeURIComponent(
          product
        )}&quantity=${quantity}`;

        let URL = `http://localhost:5000/api/v1.0${resource}`;
        let response = await fetch(URL + queryString);
        let data = await response.json();
        currentQuantity = data.quantity;
      } else if (requestMethod === "POST") {
        console.log(currentQuantity);
        if (quantity > currentQuantity) {
          // Check the quantity that user enters does not exceed inventory quantity
          throw "Error: Quantity exceeds available quantity\n";
        }
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
          date: todayDate,
          product: product,
          barcode: 0,
          aisle: 5,
          quantity: quantity,
          status: "Not Started",
        };

        // options for fetch() requests
        let options = {
          method: requestMethod,
          headers: {
            "Content-Type": "application/json; charset=utf-8",
          },
          body: JSON.stringify(productInfo),
        };

        let response = await fetch(
          `http://localhost:5000/api/v1.0${resource}`,
          options
        );
        let data = await response.json();
        console.log(data);
      }
    }
  } catch (error) {
    console.log(error);
  }
}

// Add event listeners for "Pick It Up" and "Ship It" buttons
let pickItUp = document.getElementsByClassName("pick-it-up");
let shipIt = document.getElementsByClassName("ship-it");
for (let i = 0; i < pickItUp.length; i++) {
  pickItUp[i].addEventListener("click", function () {
    let list = [
      {
        requestMethod: "GET",
        resource: "/inventory/backstock",
        product: productNames[i].innerHTML,
        quantity: quantityInput[i],
      },
      {
        requestMethod: "POST",
        resource: "/fulfillment/OPU",
        product: productNames[i].innerHTML,
        quantity: quantityInput[i],
      },
    ];
    updateFulfillment(list);
  });

  shipIt[i].addEventListener("click", function () {
    let list = [
      {
        requestMethod: "GET",
        resource: "/inventory/backstock",
        product: productNames[i].innerHTML,
        quantity: quantityInput[i],
      },
      {
        requestMethod: "POST",
        resource: "/fulfillment/SFS",
        product: productNames[i].innerHTML,
        quantity: quantityInput[i],
      },
    ];

    updateFulfillment(list);
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

let taskBtn = document.getElementById("task-button");
var taskList = document.getElementById("task-list");
let batchCount = -1;
let batchLength;
var savedResult;
taskBtn.addEventListener("click", function () {
  fetch("http://localhost:5000/api/v1.0/fulfillment/SFS")
    .then((res) => res.json())
    .then((res) => {
      savedResult = res; // save the result so that it can later be used to display to the workspace
      for (const key in res) {
        batchLength = 0; // reset batchLength to count the number of products in each batch
        console.log("This is batch: " + key);
        for (const value in res) {
          if (res[key].hasOwnProperty(value)) {
            // console.log("(res[key])[value]: " + (res[key])[value]);
            if (res[key][value][0] > batchCount) {
              batchCount++;
              // Create new batch labels everytime a new batch is detected
              var newBatch = document.createElement("div");
              let batchLabel = document.createElement("label");
              let batchInput = document.createElement("input");
              var batchQtyLabel = document.createElement("label");
              var batchDiv = document.createElement("div");
              newBatch.setAttribute("class", "batches");
              batchLabel.setAttribute("class", "batch-label");
              batchInput.setAttribute("type", "radio");
              batchInput.setAttribute("name", "batch-list");
              batchInput.setAttribute("value", batchCount);
              batchQtyLabel.setAttribute("class", "batch-qty");
              let batchNumText = document.createTextNode("Batch " + batchCount);
              // console.log("This is batchNumText: " + batchNumText.textContent);
              batchLabel.appendChild(batchInput);
              batchLabel.appendChild(batchNumText);
              newBatch.appendChild(batchLabel);
              newBatch.appendChild(batchQtyLabel);
              batchDiv.appendChild(newBatch);
              let startBtn = document.getElementById("select-batch-btn");
              startBtn.parentNode.insertBefore(batchDiv, startBtn);
              // taskList.appendChild(newBatch);
            }
            if (res[key][value][0] == batchCount) {
              batchLength++;
            }
          }
        }
        console.log("batchLength: " + batchLength);
        let batchQtyLabelText = document.createTextNode("Qty: " + batchLength);
        batchQtyLabel.append(batchQtyLabelText);
        for (
          let i = 0;
          i < document.getElementsByClassName("batches").length;
          i++
        ) {
          // Style elements that are related to batch labels
          document.getElementsByClassName("batches")[i].style.backgroundColor =
            "#e6e6e6";
          document.getElementsByClassName("batches")[i].style.height = "30px";
          document.getElementsByClassName("batches")[i].style.border =
            "1px solid black";
          document.getElementsByClassName("batch-label")[i].style.color = "red";
          document.getElementsByClassName("batch-qty")[i].style.color = "red";
          document.getElementsByClassName("batch-qty")[i].style.marginLeft =
            "150px";
        }
      }
    })
    .catch((error) => console.log("Error: " + error));

  // // Toggle the drop-down list to show or hide batches
  // for (let i = 0; i < newBatch.length; i++) {
  //   if (!newBatch[i].classList.contains("toggle")) {
  //     newBatches[i].classList.add("toggle");
  //   } else {
  //     newBatches[i].classList.remove("toggle");
  //   }
  // }
});

let selectBatchBtn = document.getElementById("select-batch-btn");
let batchLabel = document.getElementsByClassName("batch-label");
let radios = document.getElementsByName("batch-list");
let orderInfo = document.getElementsByClassName("info");
let scanLocationBtn = document.getElementById("scan-location");
selectBatchBtn.addEventListener("click", function () {
  // Determine which batch the user selected when they click the start button
  for (let i = 0; i < radios.length; i++) {
    if (radios[i].checked) {
      // check which radio button was checked
      console.log("radio[" + i + "] has been selected!");
      for (let j = 0; j < radios.length; j++) {
        if (j == i) {
          radios[j].checked = true; // Visually set the batch that was selected to be checked
        }
        radios[j].disabled = true; // Make all other batches unable to be selected if one batch is already in progress
      }
      let order = 0;
      for (let s = 0; s < savedResult[i][order].length - 2; s++) {
        // Reduce length of for loop by 2 to avoid indices 7 and 8
        try {
          if (s == 6) {
            // Instead of having the status displayed at index 6, display the location as (longitude, latitude)
            let location =
              "(" +
              savedResult[i][order][7] +
              "," +
              savedResult[i][order][8] +
              ")";
            orderInfo[s].value = location;
          } else {
            orderInfo[s].value = savedResult[i][order][s];
          }
        } catch (err) {
          console.log("Index: " + s + " Error: " + err);
        }
      }

      scanLocationBtn.addEventListener("click", function () {
        if (order == Object.keys(savedResult[i]).length - 1) {
          for (let v = 0; v < savedResult[i][order].length - 2; v++) {
            try {
              orderInfo[v].value = "";
            } catch (err) {
              console.log("Index: " + v + " Error: " + err);
            }
          }
          scanLocationBtn.disabled = true;
          console.log("LAST PRODUCT IN BATCH");
        }
        order = order + 1;
        for (let v = 0; v < savedResult[i][order].length - 2; v++) {
          try {
            if (v == 6) {
              // Instead of having the status displayed at index 6, display the location as (longitude, latitude)
              let location =
                "(" +
                savedResult[i][order][7] +
                "," +
                savedResult[i][order][8] +
                ")";
              orderInfo[v].value = location;
              console.log(location);
            } else {
              console.log(savedResult[i][order][v]);
              orderInfo[v].value = savedResult[i][order][v];
            }
          } catch (err) {
            console.log("Index: " + v + " Error: " + err);
          }
        }
      });

      // Start displaying product information to workspace
    }
  }
});
