$(document).ready(function() {
    // Handler for form submission with id 'myForm'
    $('#myForm').submit(function(event) {
        // Prevent the default form submission
        event.preventDefault();
        // Code to execute when the form is submitted
        console.log('Form submitted!');
        var username = $('#username').val();
        var password = $('#password').val();
        var data = {
            username: username,
            password: password
        };

        // Fetch the URL from the form's action attribute
        var url = "localho.st:5000/login"; //$(this).attr('action') + '/login';
        console.log('URL:', url);
        // Send the data using POST method
        function handleData(response) {
            console.log('Response:', response);
            if (response.success) {
                // Redirect to the dashboard
                localStorage.setItem('token', response.token);
                localStorage.setItem('username', username);
                window.location.href = '/dashboard';
            }
            else {
                alert('Invalid username or password');
            }
        }
        fetch('http://localhost:5000/login', {
            method:'POST',
            body: JSON.stringify(data),
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => response.json())
        .then(data => handleData(data))
        .catch(error => console.error('Error:', error));

    });
});