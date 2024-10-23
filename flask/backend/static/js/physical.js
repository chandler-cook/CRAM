$(document).on('click', '#btnPhysical', function () {
    $('#divOverview').slideUp(function () {
        $('#divPhysical').slideDown();

        var physicalSmallNumber = $('#btnPhysical .small-number').text();

        $('#divPhysical').html(`
            <div class="big-circle">
                <span class="big-number">` + physicalSmallNumber + `</span>
            </div>
            <p class="mt-2">Physical Score</p>
        `);

        $('#divPhysical').html(`
            <form id="policyForm">
                <div class="mb-3">
                    <label for="policyInput" class="form-label">What policies would you like to update?</label>
                    <textarea class="form-control" id="policyInput" rows="5" placeholder="Enter policies here..."></textarea>
                </div>
                <button type="button" class="btn btn-primary" id="addPolicyButton">Add Policy</button>
            </form>
        `);
    });
});

// Handle the form submission via AJAX when the "Add Policy" button is pressed
$(document).on('click', '#addPolicyButton', function () {
    var policyText = $('#policyInput').val();  // Get the content from the text area

    if (policyText.trim() === "") {
        alert("Please enter some policies.");
        return;
    }

    // Send the policy data to the backend via AJAX
    $.ajax({
        url: '/add_policy',  // The Flask route where the data is sent
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ policy: policyText }),  // Send the text as JSON
        success: function (response) {
            alert("Policy added successfully!");
            // Optionally, you can clear the form after a successful submission
            $('#policyInput').val('');
        },
        error: function (xhr, status, error) {
            console.error("Error occurred: " + error);
            alert("Failed to add policy. Please try again later.");
        }
    });
});
