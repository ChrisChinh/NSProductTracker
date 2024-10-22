// Global variables
let url = "http://localhost:5000/";
let lookup_url = "http://localhost:5000/lookup";
let existingHeaders = [];
let imageWidth = "200";
let should_logout = true;

$(document).ready(function() {
    // Ensure that the user is logged in
    let token = localStorage.getItem('token');
    let username = localStorage.getItem('username');
    if (token == null || username == null) {
        alert("Please log in first");
        window.location.href = '/';
    }
});

// Clear local storage when the user logs out
$(window).on('beforeunload', function() {
    if (should_logout) {
        localStorage.clear();
    }
});

function edit() {
    should_logout = false;
    window.location.href = '/edit';
}

function createImage(imageLinks) {
    let imageList = imageLinks.split(",");
    imageList.map(val => val.trim());
    let cell = "<td>";
    for (image of imageList) {
        cell += "<img src='images/" + image + "' width=" + imageWidth + ">";
    }
    cell += "</td>";
    return cell;

}

function handleData(data) {
    console.log(data);
    // Fill the table with the data
    if (data == null) {
        alert("Serial number not found");
        return;
    }
    else if (data.success == false) {
        alert("Serial number not found");
        return;
    }
    $.each(data, function(key, value) {
        if (key == "success") {
            return;
        }
        if (!existingHeaders.includes(key)) {
        $("#headerRow").append("<th>" + key + "</th>");
        existingHeaders.push(key);
        }
    });

    function displayParameters(parameters) {
        let cell = "<td>";
        let params = JSON.parse(parameters);
        for (param in params) {
            cell += "<p>" + param + ":" + params[param] + "</p>";
        }
        cell += "</td>";
        return cell;
    }


    // Create a new row with each cell containing the data of the respective header
    // If a cell contains images, display them
    let newRow = $("<tr></tr>");
    $.each(existingHeaders, function(index, headerKey) {
        if (data.hasOwnProperty(headerKey)) {
            if (headerKey == "Images") {
                cell = createImage(data[headerKey]);
                newRow.append(cell);
                return;
            }
            else if (headerKey == "success") {
                return;
            }
            else if (headerKey == "PurchaseOrder" || headerKey == "DeliveryRecords") {
                newRow.append("<td><a href='" + url + "pdf/" + data[headerKey] + "' target='_blank'>PDF</a></td>");
                return;
            }
            else if (headerKey == 'CreationParameters') {
                cell = displayParameters(data[headerKey]);
                newRow.append(cell);
                return;
            }
            newRow.append("<td>" + data[headerKey] + "</td>");
        } else {
            newRow.append("<td></td>");
        }
    });

    $('#tableBody').append(newRow);

}

// When search button is pressed
function search() {
    var searchTerm = $('#searchInput').val();
    let serial = searchTerm;
    let token = localStorage.getItem('token');
    let username = localStorage.getItem('username');
    if (token == null || username == null) {
        alert("Please log in first");
        return;
    }
    let obj = {
        serial: serial,
        token: token,
        username: username
    };
    fetch(lookup_url, {
        method: 'POST',
        body: JSON.stringify(obj),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
    .then(data => handleData(data))
}

function reset() {
    $('#tableBody').empty();
    $('#headerRow').empty();
    existingHeaders = [];
}

function logout() {
    localStorage.clear();
    window.location.href = '/';
}