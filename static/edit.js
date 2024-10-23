//Globals
let lookup_url = "http://localhost:5000/lookup";
let edit_url = "http://localhost:5000/edit_item";


function checkKeys(obj) {
 let keys = ['PartNumber', 'DesignVersion', 'MFGSuccess', 'PerfSuccess', 
    'CustomerSuccess', 'Feedback', 'PurchaseOrder', 'DeliveryRecords', 'CreationParameters'];
 for (const key of keys) {
        if (!obj.hasOwnProperty(key)) {
            console.log('Key not found: ' + key);
            return false;
        }
 }
 return true;
}

function submitData() {
    let token = localStorage.getItem('token');
    let username = localStorage.getItem('username');
    let serial = $('#serial-number').val();
    let part_number = $('#part-number').val();
    let design_version = $('#design-version').val();
    let mfg_success = $('#manufacture-success').prop('checked');
    let perf_success = $('#performance-success').prop('checked');
    let customer_success = $('#customer-success').prop('checked');
    let delivery_records = $('#delivery-records').val();
    let purchase_order = $('#purchase-order').val();
    let feedback = $('#feedback').val();
    let critical_frequency = $('#critical-frequency').val();
    let bandwidth = $('#bandwidth').val();
    let obj = {
        token: token,
        username: username,
        serial: serial,
        PartNumber: part_number,
        DesignVersion: design_version,
        MFGSuccess: mfg_success,
        PerfSuccess: perf_success,
        CustomerSuccess: customer_success,
        DeliveryRecords: delivery_records,
        PurchaseOrder: purchase_order,
        Feedback: feedback,
        CriticalFrequency: critical_frequency,
        Bandwidth: bandwidth
    };
    fetch(edit_url, {
        method: 'POST',
        body: JSON.stringify(obj),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(response => response.json())
    .then(data => {
        console.log(data);
        if (data.success) {
            alert("Data successfully submitted");
        } else {
            alert("Data submission failed");
        }
    });
}

function populateFields(data) {
    if (data.success == false) {
        alert("Serial number not found");
        return;
    }
    if (!checkKeys(data)) {
        console.log(data);
        alert("Object does not have all necessary keys");
        return;
    }
    $('#part-number').val(data['PartNumber']);
    $('#design-version').val(data['DesignVersion']);
    $('#manufacture-success').prop('checked', data['MFGSuccess']);
    $('#performance-success').prop('checked', data['PerfSuccess']);
    $('#customer-success').prop('checked', data['CustomerSuccess']);
    $('#delivery-records').val(data['DeliveryRecords']);
    $('#purchase-order').val(data['PurchaseOrder']);
    $('#feedback').val(data['Feedback']);
    $('#critical-frequency').val(data['CriticalFrequency']);
    $('#bandwidth').val(data['Bandwidth']);
}

function searchSerial() {
    let serial = $('#serial-number').val();
    let token = localStorage.getItem('token');
    let username = localStorage.getItem('username');
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
    .then(data => populateFields(data))
}

$(document).ready(function() {
    // Ensure that the user is logged in
    if (localStorage.getItem('token') == null || localStorage.getItem('username') == null) {
        alert("Please log in first");
        window.location.href = '/';
    }

    $('#search-button').click(function() {
        searchSerial();
    });

    $('#submit-button').click(function() {
        submitData();
    });
});



