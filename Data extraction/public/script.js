document.getElementById("userForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Prevent actual form submission

    const formData = new FormData(this); // Create a FormData object

    // Log formData content for debugging
    for (const [key, value] of formData.entries()) {
        console.log(key, value);
    }

    fetch("http://localhost:3000/submit", {
        method: "POST",
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok: ' + response.statusText);
        }
        return response.text(); // Return response text
    })
    .then(data => {
        document.getElementById("response").innerText = data; // Display success message
    })
    .catch(error => {
        document.getElementById("response").innerText = 'Error: ' + error.message; // Handle errors
        console.error('Fetch error:', error); // Log error for debugging
    });
});
